from fastapi import APIRouter, Depends, HTTPException, Security
from app.models import database
from app.schemas import patient as patient_schema, authentication as auth_schema
from app.services.patient import PatientService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_patient_service
from app.middleware.authentication import get_current_user, security

# Create a new APIRouter instance
router = APIRouter(
    tags=["Patients"],
    prefix="/patients",
)

# Define a route for the patient list
@router.get("/", dependencies=[Security(security)])
async def read_patients(limit: int = 10, skip: int = 0, sort: str = None,user: auth_schema.TokenData  = Depends(get_current_user), patient_Service: PatientService = Depends(get_patient_service) ) -> List[patient_schema.Patient]:
    patients = patient_Service.get_all()
    return patients

# Define a route for creating a new patient
@router.post("/", dependencies=[Security(security)])
async def create_patient(request: patient_schema.PatientCreate, user: auth_schema.TokenData  = Depends(get_current_user), patient_Service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    request["employee_id"] = user.id
    patient = patient_Service.create(request.dict())
    return patient

# Define a route for retrieving a patient by ID
@router.get("/{id}", dependencies=[Security(security)])
async def read_patient(id: int,user: auth_schema.TokenData  = Depends(get_current_user), patient_Service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    patient = patient_Service.show(id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with id {id} not found")
    return patient

# Define a route for updating a patient by ID
@router.put("/{id}", dependencies=[Security(security)] )
async def update_patient(id: int, request: patient_schema.PatientCreate,user: auth_schema.TokenData  = Depends(get_current_user), patient_Service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    patient = patient_Service.update(id, request.dict())
    return patient

# Define a route for deleting a patient by ID
@router.delete("/{id}", dependencies=[Security(security)])
async def delete_patient(id: int,user: auth_schema.TokenData  = Depends(get_current_user), patient_Service: PatientService = Depends(get_patient_service)) -> bool:
    result = patient_Service.destroy(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Patient with id {id} not found")
    return result


