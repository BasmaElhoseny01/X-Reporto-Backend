# app/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.repository.patient import PatientRepository
from app.services.patient import PatientService
from app.repository.employee import EmployeeRepository
from app.services.employee import EmployeeService
from app.services.authentication import AuthenticationService
from app.repository.activity import ActivityRepository
from app.services.activity import ActivityService
from app.repository.template import TemplateRepository
from app.services.template import TemplateService
from app.repository.study import StudyRepository
from app.services.study import StudyService
from app.repository.activity import ActivityRepository
from app.repository.result import ResultRepository
from app.services.ai import AIService


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

def get_template_repository(db: Session = Depends(get_db)) -> TemplateRepository:
    return TemplateRepository(db)

def get_template_service(template_repository: TemplateRepository = Depends(get_template_repository)) -> TemplateService:
    return TemplateService(template_repository)

def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db,)

def get_activity_service(activity_repository: ActivityRepository = Depends(get_activity_repository)) -> ActivityService:
    return ActivityService(activity_repository)

def get_study_repository(db: Session = Depends(get_db)) -> StudyRepository:
    return StudyRepository(db)

def get_study_service(study_repository: StudyRepository = Depends(get_study_repository), activity_repository: ActivityRepository= Depends(get_activity_repository)) -> StudyService:
    return StudyService(study_repository,activity_repository)

def get_result_repository(db: Session = Depends(get_db)) -> ResultRepository:
    return ResultRepository(db)

def get_ai_service(study_repository: StudyRepository = Depends(get_study_repository), result_repository: ResultRepository = Depends(get_result_repository), activity_repository: ActivityRepository= Depends(get_activity_repository)) -> AIService:
    return AIService(study_repository,result_repository,activity_repository)