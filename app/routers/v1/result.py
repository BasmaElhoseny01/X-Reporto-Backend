from fastapi import APIRouter, Depends, HTTPException, Security, File, UploadFile, BackgroundTasks
from app.models import database
from app.models.enums import StatusEnum, ResultTypeEnum
from app.schemas import study as study_schema, authentication as auth_schema, result as result_schema
from app.schemas import patient_study as patient_study_schema
from app.services.study import StudyService
from app.services.ai import AIService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_study_service, get_ai_service
from app.middleware.authentication import get_current_user, security
from fastapi.responses import FileResponse, StreamingResponse

# Create a new APIRouter instance
router = APIRouter(
    tags=["Results"],
    prefix="/results",
)

# Results endpoints
@router.get("/", dependencies=[Security(security)])
async def get_results( user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service),type: ResultTypeEnum = None, limit: int = 10, skip: int = 0, sort: str = None) -> List[result_schema.ResultShow]:
    return ai_service.get_all(type, limit, skip, sort)

@router.post("/", dependencies=[Security(security)])
async def create_result(request: result_schema.ResultCreate, user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service)) -> result_schema.ResultShow:
    return ai_service.create(request.dict())

# get file with file_path
@router.get("/download_file", dependencies=[Security(security)])
async def download_file(file_path: str, user: auth_schema.TokenData = Depends(get_current_user)) -> FileResponse:
    print("file_path", file_path)
    return FileResponse(file_path)

@router.get("/{result_id}", dependencies=[Security(security)])
async def get_result(result_id: int, user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service)) -> result_schema.ResultShow:
    return ai_service.show(result_id)

@router.put("/{result_id}", dependencies=[Security(security)])
async def update_result(result_id: int, request: result_schema.ResultUpdate, user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service)) -> result_schema.ResultShow:
    return ai_service.update(result_id,request.dict())

@router.delete("/{result_id}", dependencies=[Security(security)])
async def delete_result( result_id: int, user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service)) -> bool:
    return ai_service.destroy(result_id)

@router.post("/{result_id}/upload_report", dependencies=[Security(security)])
async def upload_report(result_id: int, report: UploadFile = File(...), user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service)) -> result_schema.ResultShow:
    # check if the result exists
    result = ai_service.show(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return ai_service.upload_report(result, report)

@router.post("/{result_id}/get_heatmap/{label}", dependencies=[Security(security)])
async def get_heatmap(result_id: int, label: int, user: auth_schema.TokenData = Depends(get_current_user), ai_service: AIService = Depends(get_ai_service)) -> FileResponse:
    heatmap = ai_service.get_heatmap(result_id, label) # 224,224,3
    return heatmap
    