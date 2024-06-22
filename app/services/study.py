from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.study import StudyRepository
from app.models.study import Study
from typing import List, Optional
import datetime
import os



class StudyService:
    def __init__(self, study_repo: StudyRepository):
        self.study_repo = study_repo
    
    def get_all(self) -> List[Study]:
        return self.study_repo.get_all()
    
    def create(self,study: dict) -> Study:
        # create a new study
        study = Study(**study)
        return self.study_repo.create(study)
    
    def destroy(self,id:int) -> bool:
        return self.study_repo.destroy(id)
    
    def update(self,id:int,study_data:dict) -> Study:
        study = self.study_repo.show(id)
        if not study:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Study with id {id} not found")
        
        for key, value in study_data.items():
            setattr(study,key,value)
            
        self.study_repo.update(study)
        return study
    
    def show(self,id:int) -> Optional[Study]:
        return self.study_repo.show(id)
    
    def upload_image(self,study: Study,file) -> Study:
        # check if file is an image or dicom file
        if not file.content_type.startswith("image"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid file type. Only images are allowed")
        
        # save the image to the file system and update the study xray_path
        xray_path = f"static/studies/{study.id}/xray.jpg"

        # create the file path and nested directories
        os.makedirs(os.path.dirname(xray_path), exist_ok=True)
        with open(xray_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        study.xray_path = xray_path
        study.xray_type = "image"
        study.last_edited_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        study.last_view_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.study_repo.update(study)
        return study

    def archive(self,id:int, doctor_id:int) -> bool:
        success, message = self.study_repo.archive(id, doctor_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)
        return True
    
    def unarchive(self,id:int, doctor_id:int) -> bool:
        success, message = self.study_repo.unarchive(id, doctor_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)
        return True