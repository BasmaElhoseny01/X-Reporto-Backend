from app.models import database
from app.models.study import Study
from app.models.patient import Patient
from app.models.employee import Employee
from app.models.result import Result
from app.models.template import Template
from app.models.activity import Activity
from app.models.enums import GenderEnum, RoleEnum, ResultTypeEnum, StatusEnum, OccupationEnum
from app.core.config import configs
import bcrypt

if __name__ == "__main__":
    if configs.ENVIRONMENT == "production":
        print("Cannot seed database in production")
        exit()
    print("Seeding database")
    database.create_database_if_not_exists()
    db = database.SessionLocal()
    password = "Aa123456*"

    try:
            
        # add admin user
        admin = Employee(
            username="sabry",
            email="ahmedsabry232345@gmail.com",
            password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
            role = RoleEnum.admin,
            employee_name="Ahmed Sabry",
            age=24,
            birth_date="2001-04-08",
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        # add doctor and admin employee
        employee = Employee(
            username="hosny",
            email="ahmedhosny@gmail.com",
            password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
            role = RoleEnum.manager,
            employee_name="Ahmed Hosny",
            age=24,
            birth_date="2001-04-08",
            employee_id=admin.id
        )

        db.add(employee)
        db.commit()
        db.refresh(employee)

        # add doctor
        doctor1 = Employee(
            employee_id=employee.id,
            username="basma",
            email="basma@gmail.com",
            password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
            employee_name="Basma",
            role = RoleEnum.admin,
            type = OccupationEnum.doctor,
            gender = GenderEnum.female,
            age=24,
            birth_date="2001-04-08",
        )

        db.add(doctor1)
        db.commit()
        db.refresh(doctor1)

        doctor2 = Employee(
            employee_id=employee.id,
            username="zeinab",
            email="zeinab@gmail.com",
            password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
            employee_name="Zeinab",
            role = RoleEnum.admin,
            type = OccupationEnum.doctor,
            gender = GenderEnum.female,
            age=24,
            birth_date="2001-04-08",
        )

        db.add(doctor2)
        db.commit()
        db.refresh(doctor2)

        # list of patients
        patients = [
            Patient(
                patient_name="Ahmed",
                age=24,
                birth_date="2001-04-08",
                gender=GenderEnum.male,
                phone_number="01000000000",
                employee_id=employee.id
            ),
            Patient(
                patient_name="Ali",
                age=24,
                birth_date="2001-04-08",
                gender=GenderEnum.male,
                phone_number="01000000000",
                employee_id=employee.id
            ),
            Patient(
                patient_name="Fatma",
                age=24,
                birth_date="2001-04-08",
                gender=GenderEnum.female,
                phone_number="01000000000",
                employee_id=employee.id
            )
        ]

        for patient in patients:
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # list of templates
        templates = [
            Template(
                doctor_id=doctor1.id,
                template_name="Template 1"
            ),
            Template(
                doctor_id=doctor1.id,
                template_name="Template 2"
            ),
            Template(
                doctor_id=doctor2.id,
                template_name="Template 3"
            )
        ]

        for template in templates:
            db.add(template)
            db.commit()
            db.refresh(template)

        # list of studies
        studies = [
            Study(
                patient_id=patients[0].id,
                doctor_id=doctor1.id,
                study_name="archived study",
                notes="Notes 1",
                severity=1,
                xray_path="xray.png",
                xray_type="type1",
                status = StatusEnum.archived,
                employee_id=employee.id
            ),
            Study(
                patient_id=patients[1].id,
                employee_id=employee.id,
                study_name="Study 2",
                notes="Notes 2",
                severity=2,
                xray_path="xray.png",
                xray_type="type2",
                status = StatusEnum.new
            ),
            Study(
                patient_id=patients[2].id,
                employee_id=employee.id,
                study_name="Study 3",
                notes="Notes 3",
                severity=3,
                xray_path="xray.png",
                xray_type="type3",
                status = StatusEnum.new
            ),
            Study(
                patient_id=patients[0].id,
                doctor_id=doctor1.id,
                employee_id=employee.id,
                study_name="completed study",
                notes="Notes 1",
                severity=1,
                xray_path="xray.png",
                xray_type="type1",
                status = StatusEnum.completed
            ),
            Study(
                patient_id=patients[0].id,
                doctor_id=doctor1.id,
                employee_id=employee.id,
                study_name="in progress study",
                notes="Notes 1",
                severity=1,
                xray_path="xray.png",
                xray_type="type1",
                status = StatusEnum.in_progress
            ),
            Study(
                patient_id=patients[0].id,
                employee_id=employee.id,
                study_name="new study",
                notes="Notes 1",
                severity=1,
                xray_path="xray.png",
                xray_type="type1",
                status = StatusEnum.new
            )
        ]

        for study in studies:
            db.add(study)
            db.commit()
            db.refresh(study)

        # list of results
        results = [
            Result(
                study_id=studies[0].id,
                result_name="Result 1",
                confidence="0.9",
                report_path="report.pdf",
                heatmap_path="heatmap.png",
                region_path="region.png",
                type= ResultTypeEnum.llm
            ),
            Result(
                study_id=studies[1].id,
                result_name="Result 2",
                confidence="0.8",
                report_path="report.pdf",
                heatmap_path="heatmap.png",
                region_path="region.png",
                type= ResultTypeEnum.custom
            ),
            Result(
                study_id=studies[2].id,
                result_name="Result 3",
                confidence="0.7",
                report_path="report.pdf",
                heatmap_path="heatmap.png",
                region_path="region.png",
                type= ResultTypeEnum.template
            )
        ]

        for result in results:
            db.add(result)
            db.commit()
            db.refresh(result)
    except Exception as e:
        print(e)
    finally:
        db.close()
        print("Database seeded")
    