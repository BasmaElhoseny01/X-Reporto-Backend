from fastapi import APIRouter, Depends, HTTPException, Security, File, UploadFile, BackgroundTasks
from app.models import database
from app.models.enums import StatusEnum, ResultTypeEnum
from app.schemas import study as study_schema, authentication as auth_schema, result as result_schema
from app.schemas import patient_study as patient_study_schema
from app.services.study import StudyService
from app.services.ai import AIService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_study_service, get_ai_service, get_result_repository
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
    study = study_Service.show(study_id,False)
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

# define a route for gettinng count of new studies
@router.get("/new/count", dependencies=[Security(security)])
async def get_new_studies_count(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.countStudy:
    return study_Service.get_new_studies_count()

# define a route for getting count of incomplete studies
@router.get("/incomplete/count", dependencies=[Security(security)])
async def get_incomplete_studies_count(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.countStudy:
    return study_Service.get_incomplete_studies_count()

# define a route for getting count of my pending studies
@router.get("/pending/count", dependencies=[Security(security)])
async def get_pending_studies_count(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.countStudy:
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to view pending studies")
    return study_Service.get_pending_studies_count(user.id)

# define a route for getting count of my completed studies
@router.get("/completed/count", dependencies=[Security(security)])
async def get_completed_studies_count(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) ->study_schema.countStudy:
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to view completed studies")
    return study_Service.get_completed_studies_count(user.id)


# Results endpoints
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


@router.post("/{study_id}/run_llm")
async def run_llm(study_id: int,
                  user: auth_schema.TokenData = Depends(get_current_user),
                  study_Service: StudyService = Depends(get_study_service),
                  ai_service: AIService = Depends(get_ai_service),
                  background: BackgroundTasks = BackgroundTasks()) -> result_schema.ResultShow:
    
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to run LLM model")
    
    # check if the study exists
    study = study_Service.study_repo.show(study_id)

    if not study:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    
    if study.doctor_id != user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to run LLM model for this study")
    
    if study.xray_path is None:
        raise HTTPException(status_code=400, detail="X-ray image is required to run LLM model")
    
    print("running LLM model")
    # get results for the study and check if the LLM model has already been run
    # result = ai_service.get_result_by_study_type(study_id, ResultTypeEnum.llm)
    result = None

    if result:
        raise HTTPException(status_code=400, detail="LLM model has already been run for this study")
    
    result = {
            "study_id": study_id,
            "xray_path": study.xray_path,
            "type": ResultTypeEnum.llm,
            "result_name": "GPT-2 generated report"
        }

    result = ai_service.create(result)

    # Add the task to the background tasks queue
    background.add_task(ai_service.run_llm, result.id, study.xray_path)
    
    # Return a response indicating the task is running
    return result