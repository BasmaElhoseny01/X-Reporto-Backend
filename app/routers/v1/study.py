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
from fastapi.responses import FileResponse, StreamingResponse

# Create a new APIRouter instance
router = APIRouter(
    tags=["Studies"],
    prefix="/studies",
)

# Define a route for the employee list
@router.get("/", dependencies=[Security(security)])
async def read_studies(user: auth_schema.TokenData  = Depends(get_current_user),status: StatusEnum = StatusEnum.new, limit: int = 10, skip: int = 0, sort: str = None, study_Service: StudyService = Depends(get_study_service) ) -> List[study_schema.StudyShow]:
    """
    Retrieve a list of studies based on status, limit, skip, and sort parameters.

    Args:
    - user (auth_schema.TokenData): The current authenticated user.
    - status (StatusEnum): The status of the studies to retrieve (default is new).
    - limit (int): The maximum number of studies to return (default is 10).
    - skip (int): The number of studies to skip (default is 0).
    - sort (str): The sorting parameter.

    Returns:
    - List[study_schema.StudyShow]: A list of studies.
    """
    studies = study_Service.get_all(status, limit, skip, sort)
    return studies


# Define a route for creating a new employee
@router.post("/", dependencies=[Security(security)])
async def create_studies(request: study_schema.StudyCreate, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.StudyShow:
    """
    Create a new study.

    Args:
    - request (study_schema.StudyCreate): The request body containing study details.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - study_schema.StudyShow: The created study.
    """    
    study = study_Service.create(request.dict())
    return study


# define a route for getting assigned studies
@router.get("/assigned", dependencies=[Security(security)])
async def get_assigned_studies(user: auth_schema.TokenData = Depends(get_current_user),status: StatusEnum = None, limit: int = 10, skip: int = 0, sort: str = None, study_Service: StudyService = Depends(get_study_service)) -> List[study_schema.StudyShow]:
    """
    Retrieve a list of assigned studies.

    Args:
    - user (auth_schema.TokenData): The current authenticated user.
    - status (StatusEnum): The status of the studies to retrieve.
    - limit (int): The maximum number of studies to return (default is 10).
    - skip (int): The number of studies to skip (default is 0).
    - sort (str): The sorting parameter.

    Returns:
    - List[study_schema.StudyShow]: A list of assigned studies.
    """
    return study_Service.get_assigned_studies(user.id, status, limit, skip, sort)

@router.post("/run_backgroud", dependencies=[Security(security)])
async def run_background(user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service) , background: BackgroundTasks = BackgroundTasks()) -> dict:
    """
    Run a background task to calculate severities.

    Args:
    - user (auth_schema.TokenData): The current authenticated user.
    - ai_service (AIService): The AI service dependency.
    - background (BackgroundTasks): The background tasks dependency.

    Returns:
    - dict: A response indicating the task is running.
    """
    background.add_task(ai_service.calculate_severities)
    # return a response indicating the task is running
    return {"detail": "Task is running in the background"}

# Define a route for getting a single employee
@router.get("/{study_id}", dependencies=[Security(security)])
async def read_study(study_id: int,user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> patient_study_schema.PatientStudy:
    """
    Retrieve a single study by its ID.

    Args:
    - study_id (int): The ID of the study to retrieve.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - patient_study_schema.PatientStudy: The retrieved study.

    Raises:
    - HTTPException: If the study is not found.
    """
    study = study_Service.show(study_id)
    if not study:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    return study

# Define a route for updating an employee
@router.put("/{study_id}", dependencies=[Security(security)])
async def update_study(study_id: int, request: study_schema.StudyUpdate, user: auth_schema.TokenData = Depends(get_current_user),study_Service: StudyService = Depends(get_study_service)) -> study_schema.StudyShow:
    """
    Update a study by its ID.

    Args:
    - study_id (int): The ID of the study to update.
    - request (study_schema.StudyUpdate): The request body containing updated study details.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - study_schema.StudyShow: The updated study.
    """
    study = study_Service.update(study_id, request.dict(), user.id)
    return study

# Define a route for deleting an employee
@router.delete("/{study_id}", dependencies=[Security(security)])
async def delete_study(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    """
    Delete a study by its ID.

    Args:
    - study_id (int): The ID of the study to delete.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - bool: True if the study was deleted, False otherwise.

    Raises:
    - HTTPException: If the study is not found.
    """
    deleted = study_Service.destroy(study_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    return deleted

@router.post("/{study_id}/upload_image", dependencies=[Security(security)])
async def upload_image(study_id: int, file: UploadFile = File(...), user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.StudyShow:
    """
    Upload an image for a specific study.

    Args:
    - study_id (int): The ID of the study.
    - file (UploadFile): The image file to upload.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - study_schema.StudyShow: The updated study with the uploaded image.

    Raises:
    - HTTPException: If the study is not found.
    """
    study = study_Service.show(study_id,False)
    if not study:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    return study_Service.upload_image(study, file)

@router.get("/{study_id}/download_resized_image", dependencies=[Security(security)])
async def download_image(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> FileResponse:
    """
    Download a resized image for a specific study.

    Args:
    - study_id (int): The ID of the study.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - FileResponse: The resized image file response.

    Raises:
    - HTTPException: If the study is not found or the X-ray image is missing.
    """
    study = study_Service.show(study_id,False)
    if not study:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    if study.xray_path is None:
        raise HTTPException(status_code=400, detail="X-ray image is required to download resized image")
    resized_path = study_Service.resize_image(study)

    # add path of resized image to response headers
    return FileResponse(resized_path, headers={"resized_xray_path": resized_path})

@router.post("/{study_id}/archive", dependencies=[Security(security)])
async def archive_study(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    """
    Archive a study by its ID.

    Args:
    - study_id (int): The ID of the study to archive.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - bool: True if the study was archived, False otherwise.

    Raises:
    - HTTPException: If the study is not found.
    """
    # check if user is doctor and is assigned to the study
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to archive a study")

    return study_Service.archive(study_id, user.id)

@router.post("/{study_id}/unarchive", dependencies=[Security(security)])
async def unarchive_study(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    """
    Unarchive a study by its ID.

    Args:
    - study_id (int): The ID of the study to unarchive.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - bool: True if the study was unarchived, False otherwise.

    Raises:
    - HTTPException: If the user is not a doctor or if the study is not found.
    """
    # check if user is doctor and is assigned to the study
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to unarchive a study")

    return study_Service.unarchive(study_id, user.id)

@router.post("/{study_id}/assign", dependencies=[Security(security)]) 
async def assign_doctor(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    """
    Assign a doctor to a study by its ID.

    Args:
    - study_id (int): The ID of the study to assign a doctor.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - bool: True if the doctor was assigned, False otherwise.

    Raises:
    - HTTPException: If the user is not a doctor or if the study is not found.
    """
    # check if user is doctor and is assigned to the study
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to assign a doctor to a study")
    
    # make
    return study_Service.assign_doctor(study_id, user.id)

@router.post("/{study_id}/unassign", dependencies=[Security(security)])
async def unassign_doctor(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> bool:
    """
    Unassign a doctor from a study by its ID.

    Args:
    - study_id (int): The ID of the study to unassign a doctor.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - bool: True if the doctor was unassigned, False otherwise.

    Raises:
    - HTTPException: If the user is not a doctor or if the study is not found.
    """
    # check if user is doctor and is assigned to the study
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to unassign a doctor from a study")
    return study_Service.unassign_doctor(study_id, user.id)

# define a route for gettinng count of new studies
@router.get("/new/count", dependencies=[Security(security)])
async def get_new_studies_count(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.countStudy:
    """
    Retrieve the count of new studies.

    Args:
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - study_schema.countStudy: The count of new studies.
    """
    return study_Service.get_new_studies_count()

# define a route for getting count of incomplete studies
@router.get("/incomplete/count", dependencies=[Security(security)])
async def get_incomplete_studies_count(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.countStudy:
    """
    Retrieve the count of incomplete studies.

    Args:
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - study_schema.countStudy: The count of incomplete studies.
    """
    return study_Service.get_incomplete_studies_count()

# define a route for getting count of my pending studies
@router.get("/pending/count", dependencies=[Security(security)])
async def get_pending_studies_count(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) -> study_schema.countStudy:
    """
    Retrieve the count of pending studies assigned to the current doctor.

    Args:
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - study_schema.countStudy: The count of pending studies.

    Raises:
    - HTTPException: If the user is not a doctor.
    """
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to view pending studies")
    return study_Service.get_pending_studies_count(user.id)

# define a route for getting count of my completed studies
@router.get("/completed/count", dependencies=[Security(security)])
async def get_completed_studies_count(user: auth_schema.TokenData = Depends(get_current_user), study_Service: StudyService = Depends(get_study_service)) ->study_schema.countStudy:
    """
    Retrieve the count of completed studies assigned to the current doctor.

    Args:
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - study_schema.countStudy: The count of completed studies.

    Raises:
    - HTTPException: If the user is not a doctor.
    """
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to view completed studies")
    return study_Service.get_completed_studies_count(user.id)


@router.get("/{study_id}/results", dependencies=[Security(security)])
async def get_results(study_id: int, user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service)) -> List[result_schema.ResultShow]:
    """
    Retrieve the results of a specific study by its ID.

    Args:
    - study_id (int): The ID of the study.
    - user (auth_schema.TokenData): The current authenticated user.
    - ai_service (AIService): The AI service dependency.

    Returns:
    - List[result_schema.ResultShow]: The results of the study.
    """
    return ai_service.get_results(study_id)

@router.post("/{study_id}/run_llm")
async def run_llm(study_id: int,
                  user: auth_schema.TokenData = Depends(get_current_user),
                  study_Service: StudyService = Depends(get_study_service),
                  ai_service: AIService = Depends(get_ai_service),
                  background: BackgroundTasks = BackgroundTasks()) -> result_schema.ResultShow:
    
    """
    Run the LLM model for a specific study by its ID.

    Args:
    - study_id (int): The ID of the study.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.
    - ai_service (AIService): The AI service dependency.
    - background (BackgroundTasks): The background tasks dependency.

    Returns:
    - result_schema.ResultShow: The result of the LLM model run.

    Raises:
    - HTTPException: If the user is not a doctor, the study is not found, the user is not assigned to the study, or the X-ray image is missing.
    """
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
    result = ai_service.get_result_by_study_type(study_id, ResultTypeEnum.llm)
    # result = None

    if not result:
        
        # raise HTTPException(status_code=400, detail="LLM model has already been run for this study")
        result = {
                "study_id": study_id,
                "xray_path": study.xray_path,
                "type": ResultTypeEnum.llm,
                "result_name": "GPT-2 generated report"
            }

        result = ai_service.create(result)

    # Add the task to the background tasks queue
    background.add_task(ai_service.run_llm, result.id, study.xray_path)
    background.add_task(ai_service.denoise, result.id, study.xray_path)
    
    # Return a response indicating the task is running
    return result

@router.post("/{study_id}/run_heatmap")
async def run_heatmap(study_id: int,
                      user: auth_schema.TokenData = Depends(get_current_user),
                      study_Service: StudyService = Depends(get_study_service),
                      ai_service: AIService = Depends(get_ai_service),
                      background: BackgroundTasks = BackgroundTasks()) -> result_schema.ResultShow:
    """
    Run the heatmap model for a specific study by its ID.

    Args:
    - study_id (int): The ID of the study.
    - user (auth_schema.TokenData): The current authenticated user.
    - study_Service (StudyService): The study service dependency.
    - ai_service (AIService): The AI service dependency.
    - background (BackgroundTasks): The background tasks dependency.

    Returns:
    - result_schema.ResultShow: The result of the heatmap model run.

    Raises:
    - HTTPException: If the user is not a doctor, the study is not found, the user is not assigned to the study, or the X-ray image is missing.
    """
    if user.type != "doctor":
        raise HTTPException(status_code=403, detail="You are not allowed to run heatmap model")
    
    # check if the study exists
    study = study_Service.study_repo.show(study_id)

    if not study:
        raise HTTPException(status_code=404, detail=f"Study with id {study_id} not found")
    
    if study.doctor_id != user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to run heatmap model for this study")
    
    if study.xray_path is None:
        raise HTTPException(status_code=400, detail="X-ray image is required to run heatmap model")
    
    print("running heatmap model")
    # get results for the study and check if the heatmap model has already been run
    result = ai_service.get_result_by_study_type(study_id, ResultTypeEnum.template)
    # result = None

    if not result:
        # raise HTTPException(status_code=400, detail="Heatmap model has already been run for this study")
    
        result = {
                "study_id": study_id,
                "xray_path": study.xray_path,
                "type": ResultTypeEnum.template,
                "result_name": " Template based report with heatmaps"
            }
        
        result = ai_service.create(result)

    # Add the task to the background tasks queue
    background.add_task(ai_service.run_heatmap, result.id, study.xray_path)

    # Return a response indicating the task is running
    return result
