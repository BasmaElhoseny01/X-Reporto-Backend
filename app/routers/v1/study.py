from fastapi import APIRouter, Depends, HTTPException, Security, File, UploadFile
from app.models import database
from app.models.enums import StatusEnum
from app.schemas import study as study_schema, authentication as auth_schema, result as result_schema
from app.schemas import patient_study as patient_study_schema
from app.services.study import StudyService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_study_service
from app.middleware.authentication import get_current_user, security

# Create a new APIRouter instance
router = APIRouter(
    tags=["Studies"],
    prefix="/studies",
)

# Define a route for the employee list
@router.get("/", dependencies=[Security(security)])
async def read_studies(user: auth_schema.TokenData  = Depends(get_current_user),status: StatusEnum = StatusEnum.new, limit: int = 10, skip: int = 0, sort: str = None, study_Service: StudyService = Depends(get_study_service) ) -> List[study_schema.StudyShow]:
    studies = study_Service.get_all(status, limit, skip, sort)
    return studies


# Define a route for creating a new employee
@router.post("/", dependencies=[Security(security)])
async def create_studies(request: study_schema.StudyCreate, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.StudyShow:
    study = study_Service.create(request.dict())
    return study


# define a route for getting assigned studies
@router.get("/assigned", dependencies=[Security(security)])
async def get_assigned_studies(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> List[study_schema.StudyShow]:
    return study_Service.get_assigned_studies(user.id)

# Define a route for getting a single employee
@router.get("/{study_id}", dependencies=[Security(security)])
async def read_study(study_id: int,user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> patient_study_schema.PatientStudy:
    study = study_Service.show(study_id)
    if not study:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    return study

# Define a route for updating an employee
@router.put("/{study_id}", dependencies=[Security(security)])
async def update_study(study_id: int, request: study_schema.StudyUpdate, user: auth_schema.TokenData = Depends(get_current_user),study_Service: StudyService = Depends(get_study_service)) -> study_schema.StudyShow:
    study = study_Service.update(study_id, request.dict())
    return study

# Define a route for deleting an employee
@router.delete("/{study_id}", dependencies=[Security(security)])
async def delete_study(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    deleted = study_Service.destroy(study_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    return deleted

@router.post("/{study_id}/upload_image", dependencies=[Security(security)])
async def upload_image(study_id: int, file: UploadFile = File(...), user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.StudyShow:
    study = study_Service.show(study_id)
    if not study:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    return study_Service.upload_image(study, file)

@router.post("/{study_id}/archive", dependencies=[Security(security)])
async def archive_study(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    # check if user is doctor and is assigned to the study
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to archive a study")

    return study_Service.archive(study_id, user.id)

@router.post("/{study_id}/unarchive", dependencies=[Security(security)])
async def unarchive_study(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    # check if user is doctor and is assigned to the study
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to unarchive a study")

    return study_Service.unarchive(study_id, user.id)

@router.post("/{study_id}/assign", dependencies=[Security(security)]) 
async def assign_doctor(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    # check if user is doctor and is assigned to the study
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to assign a doctor to a study")
    
    # make
    return study_Service.assign_doctor(study_id, user.id)

@router.post("/{study_id}/unassign", dependencies=[Security(security)])
async def unassign_doctor(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    # check if user is doctor and is assigned to the study
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to unassign a doctor from a study")
    return study_Service.unassign_doctor(study_id, user.id)

@router.get("/{study_id}/results", dependencies=[Security(security)])
async def get_results(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> List[result_schema.ResultShow]:
    return study_Service.get_results(study_id)

@router.post("/{study_id}/results", dependencies=[Security(security)])
async def create_result(study_id: int, request: result_schema.ResultCreate, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> result_schema.ResultShow:
    return study_Service.create_result(study_id, request.dict())

@router.get("/{study_id}/results/{result_id}", dependencies=[Security(security)])
async def get_result(study_id: int, result_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> result_schema.ResultShow:
    return study_Service.get_result(study_id, result_id)

@router.put("/{study_id}/results/{result_id}", dependencies=[Security(security)])
async def update_result(study_id: int, result_id: int, request: result_schema.ResultUpdate, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> result_schema.ResultShow:
    return study_Service.update_result(study_id, result_id, request.dict())

@router.delete("/{study_id}/results/{result_id}", dependencies=[Security(security)])
async def delete_result(study_id: int, result_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    return study_Service.delete_result(study_id, result_id)

# Define a route for getting studies of certain status attribute in study
