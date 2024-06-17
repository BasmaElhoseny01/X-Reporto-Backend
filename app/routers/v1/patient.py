from fastapi import APIRouter, Depends, HTTPException
from app.models import database
from app.schemas import patient as patient_schema
from app.services.patient import PatientService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_patient_service

# Create a new APIRouter instance
router = APIRouter(
    tags=["Patients"],
    prefix="/patients",
)

# Define a route for the patient list
@router.get("/")
async def read_patients(limit: int = 10, skip: int = 0, sort: str = None, patient_Service: PatientService = Depends(get_patient_service) ) -> List[patient_schema.Patient]:
    patients = patient_Service.get_all()
    return patients

# Define a route for creating a new patient
@router.post("/")
async def create_patient(request: patient_schema.PatientCreate, patient_Service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    patient = patient_Service.create(request.dict())
    return patient

# Define a route for retrieving a patient by ID


