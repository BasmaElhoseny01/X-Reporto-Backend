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
    """
    Retrieve a list of patients with optional pagination and sorting.

    Args:
        limit (int): Limit the number of patients returned (default is 10).
        skip (int): Number of patients to skip (default is 0).
        sort (str): Sort the patients by a specific field.
        user (auth_schema.TokenData): Current authenticated user.
        patient_service (PatientService): Dependency for patient operations.

    Returns:
        List[patient_schema.Patient]: A list of patients.
    """
    patients = patient_service.get_all()
    return patients

# Define a route for creating a new patient
@router.post("/", dependencies=[Security(security)])
async def create_patient(request: patient_schema.PatientCreate, user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    """
    Create a new patient.

    Args:
        request (patient_schema.PatientCreate): Patient creation request body.
        user (auth_schema.TokenData): Current authenticated user.
        patient_service (PatientService): Dependency for patient operations.

    Returns:
        patient_schema.Patient: The created patient.
    
    Raises:
        HTTPException: If user is not authorized to create a patient.
    """
    if user.type != "employee":
        raise HTTPException(status_code=403, detail="You are not allowed to create a patient")
    
    request.employee_id = user.id
    patient = patient_service.create(request.dict())
    return patient

# Define a route for retrieving a patient by ID
@router.get("/{id}", dependencies=[Security(security)])
async def read_patient(id: int,user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    """
    Retrieve a patient by ID.

    Args:
        id (int): Patient ID.
        user (auth_schema.TokenData): Current authenticated user.
        patient_service (PatientService): Dependency for patient operations.

    Returns:
        patient_schema.Patient: The retrieved patient.

    Raises:
        HTTPException: If patient not found.
    """
    patient = patient_service.show(id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with id {id} not found")
    return patient

# Define a route for updating a patient by ID
@router.put("/{id}", dependencies=[Security(security)] )
async def update_patient(id: int, request: patient_schema.PatientCreate,user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service)) -> patient_schema.Patient:
    """
    Update a patient by ID.

    Args:
        id (int): Patient ID.
        request (patient_schema.PatientCreate): Patient update request body.
        user (auth_schema.TokenData): Current authenticated user.
        patient_service (PatientService): Dependency for patient operations.

    Returns:
        patient_schema.Patient: The updated patient.

    Raises:
        HTTPException: If user is not authorized or patient not found.
    """
    if user.type != "employee":
        raise HTTPException(status_code=403, detail="You are not allowed to update a patient")

    patient = patient_service.update(id, request.dict())
    return patient

# Define a route for deleting a patient by ID
@router.delete("/{id}", dependencies=[Security(security)])
async def delete_patient(id: int,user: auth_schema.TokenData  = Depends(get_current_user), patient_service: PatientService = Depends(get_patient_service)) -> bool:
    """
    Delete a patient by ID.

    Args:
        id (int): Patient ID.
        user (auth_schema.TokenData): Current authenticated user.
        patient_service (PatientService): Dependency for patient operations.

    Returns:
        bool: True if the patient was successfully deleted.

    Raises:
        HTTPException: If user is not authorized or patient not found.
    """
    if user.type != "employee":
        raise HTTPException(status_code=403, detail="You are not allowed to delete a patient")
    result = patient_service.destroy(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Patient with id {id} not found")
    return result


# get studies of a patient, with limit, skip and sort 
@router.get("/{patient_id}/studies", dependencies=[Security(security)])
async def read_patient_studies(patient_id: int,status: StatusEnum = None, limit: int = 10, skip: int = 0, sort: str = None, user: auth_schema.TokenData  = Depends(get_current_user),patient_service: PatientService = Depends(get_patient_service), study_Service: StudyService = Depends(get_study_service)) -> List[study_schema.Study]:
    """
    Retrieve studies assigned to a patient.

    Args:
        patient_id (int): Patient ID.
        status (StatusEnum): Optional status filter for studies.
        limit (int): Limit the number of studies returned (default is 10).
        skip (int): Number of studies to skip (default is 0).
        sort (str): Sort the studies by a specific field.
        user (auth_schema.TokenData): Current authenticated user.
        patient_service (PatientService): Dependency for patient operations.
        study_Service (StudyService): Dependency for study operations.

    Returns:
        List[study_schema.Study]: A list of studies assigned to the patient.

    Raises:
        HTTPException: If patient not found.
    """
    # check if patient exists
    patient = patient_service.show(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with id {id} not found")
    
    studies = study_Service.get_patient_studies(patient_id,status, limit, skip, sort)
    return studies
