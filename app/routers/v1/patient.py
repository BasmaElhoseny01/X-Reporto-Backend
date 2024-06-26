from fastapi import APIRouter, Depends, HTTPException, Security
from app.models import database
from app.models.enums import StatusEnum
from app.schemas import patient as patient_schema, authentication as auth_schema, study as study_schema
from app.services.patient import PatientService
from app.services.study import StudyService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_patient_service, get_study_service
from app.middleware.authentication import get_current_user, security

# Create a new APIRouter instance
router = APIRouter(
    tags=["Patients"],
    prefix="/patients",
)

# Define a route for the patient list
@router.get("/", dependencies=[Security(security)])
async def read_patients(limit: int = 10, skip: int = 0, sort: str = None,user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service) ) -> List[patient_schema.Patient]:
    patients = patient_service.get_all()
    return patients

# Define a route for creating a new patient
@router.post("/", dependencies=[Security(security)])
async def create_patient(request: patient_schema.PatientCreate, user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    request["employee_id"] = user.id
    patient = patient_service.create(request.dict())
    return patient

# Define a route for retrieving a patient by ID
@router.get("/{id}", dependencies=[Security(security)])
async def read_patient(id: int,user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    patient = patient_service.show(id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with id {id} not found")
    return patient

# Define a route for updating a patient by ID
@router.put("/{id}", dependencies=[Security(security)] )
async def update_patient(id: int, request: patient_schema.PatientCreate,user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    patient = patient_service.update(id, request.dict())
    return patient

# Define a route for deleting a patient by ID
@router.delete("/{id}", dependencies=[Security(security)])
async def delete_patient(id: int,user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service)) -> bool:
    result = patient_service.destroy(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Patient with id {id} not found")
    return result


# get studies of a patient, with limit, skip and sort 
@router.get("/{patient_id}/studies", dependencies=[Security(security)])
async def read_patient_studies(patient_id: int,status: StatusEnum = None, limit: int = 10, skip: int = 0, sort: str = None, user: auth_schema.TokenData  = Depends(get_current_user),patient_service: PatientService = Depends(get_patient_service), study_Service: StudyService = Depends(get_study_service)) -> List[study_schema.Study]:
    # check if patient exists
    patient = patient_service.show(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with id {id} not found")
    
    studies = study_Service.get_patient_studies(patient_id,status, limit, skip, sort)
    return studies

    # patient = patient_service.show_with_studies(patient_id,status, limit, skip, sort)
    # # print patient as dict
    # # convert patient of model to dict
    # if not patient:
    #     raise HTTPException(status_code=404, detail=f"Patient with id {patient_id} not found")
    
    # return patient
