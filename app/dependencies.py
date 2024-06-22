# app/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.repository.patient import PatientRepository
from app.services.patient import PatientService
from app.repository.employee import EmployeeRepository
from app.services.employee import EmployeeService
from app.services.authentication import AuthenticationService
from app.repository.doctor import DoctorRepository
from app.services.doctor import DoctorService
from app.repository.template import TemplateRepository
from app.services.template import TemplateService
from app.repository.study import StudyRepository
from app.services.study import StudyService

def get_patient_repository(db: Session = Depends(get_db)) -> PatientRepository:
    return PatientRepository(db)

def get_patient_service(patient_repository: PatientRepository = Depends(get_patient_repository)) -> PatientService:
    return PatientService(patient_repository)

def get_employee_repository(db: Session = Depends(get_db)) -> EmployeeRepository:
    return EmployeeRepository(db)

def get_employee_service(employee_repository: EmployeeRepository = Depends(get_employee_repository)) -> EmployeeService:
    return EmployeeService(employee_repository)

def get_authentication_service(employee_repository: EmployeeRepository = Depends(get_employee_repository)) -> AuthenticationService:
    return AuthenticationService(employee_repository)

def get_doctor_repository(db: Session = Depends(get_db)) -> DoctorRepository:
    return DoctorRepository(db)

def get_doctor_service(doctor_repository: DoctorRepository = Depends(get_doctor_repository)) -> DoctorService:
    return DoctorService(doctor_repository)

def get_template_repository(db: Session = Depends(get_db)) -> TemplateRepository:
    return TemplateRepository(db)

def get_template_service(template_repository: TemplateRepository = Depends(get_template_repository)) -> TemplateService:
    return TemplateService(template_repository)

def get_study_repository(db: Session = Depends(get_db)) -> StudyRepository:
    return StudyRepository(db)

def get_study_service(study_repository: StudyRepository = Depends(get_study_repository)) -> StudyService:
    return StudyService(study_repository)