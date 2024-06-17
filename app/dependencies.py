# app/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.repository.patient import PatientRepository
from app.services.patient import PatientService

def get_patient_repository(db: Session = Depends(get_db)) -> PatientRepository:
    return PatientRepository(db)

def get_patient_service(patient_repository: PatientRepository = Depends(get_patient_repository)) -> PatientService:
    return PatientService(patient_repository)
