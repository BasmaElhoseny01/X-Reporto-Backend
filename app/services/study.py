from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.study import StudyRepository
from app.repository.activity import ActivityRepository
from app.models.study import Study
from app.models.activity import Activity
from app.models.enums import StatusEnum, ActivityEnum
from typing import List, Optional
from datetime import datetime
import albumentations as A
import cv2
import os



class StudyService:
    def __init__(self, study_repo: StudyRepository, activity_repo: ActivityRepository):
        self.study_repo = study_repo
        self.activity_repo = activity_repo
    
    def get_all(self,status: StatusEnum, limit: int, skip: int , sort: str) -> List[Study]:
        return self.study_repo.get_all(status, limit, skip, sort)
    
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
        
        
        # update the last edited time
        study.last_edited_at = datetime.utcnow()

        for key, value in study_data.items():
            setattr(study,key,value)
            
        self.study_repo.update(study)

        # create a new activity
        # check if status was updated
        if "status" in study_data:
            # check if the status was updated to completed
            if study_data["status"] == StatusEnum.completed:
                activity = {
                    "employee_id": study.doctor_id,
                    "study_id": id,
                    "activity_type": ActivityEnum.submit
                }
            else:
                activity = {
                    "employee_id": study.doctor_id,
                    "study_id": id,
                    "activity_type": ActivityEnum.edit
                }
        else:
            activity = {
                "employee_id": study.doctor_id,
                "study_id": id,
                "activity_type": ActivityEnum.edit
            }

        activity = Activity(**activity)
        
        self.activity_repo.create(activity)
        return study
    
    def show(self,id:int, is_doctor: bool = True) -> Optional[Study]:
        study = self.study_repo.show(id)
        if not study:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Study with id {id} not found")
        
        # update the last view time
        study.last_view_at =  datetime.utcnow()
        self.study_repo.update(study)

        if study.doctor_id and is_doctor:
            # create a new activity
            activity = {
                "employee_id": study.doctor_id,
                "study_id": id,
                "activity_type": ActivityEnum.view
            }

            activity = Activity(**activity)
            
            self.activity_repo.create(activity)
        return study
    
    def get_patient_studies(self,patient_id:int, status: StatusEnum, limit: int, skip: int, sort: str) -> List[Study]:
        return self.study_repo.get_patient_studies(patient_id,status, limit, skip, sort)
    
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
        study.last_edited_at =  datetime.utcnow()
        study.last_view_at =  datetime.utcnow()
        self.study_repo.update(study)
        return study
    
    def resize_image(self, img_path: str):
        # read image
        img = cv2.imread(img_path)

        transform =  A.Compose(
                        [
                            A.LongestMaxSize(max_size=512, interpolation=cv2.INTER_AREA),
                            A.PadIfNeeded(min_height=512, min_width=512,border_mode= cv2.BORDER_CONSTANT,value=0),

                        ])
        
        # apply transformation
        img = transform(image=img)["image"]

        # save resized image in new path
        new_path = img_path.replace("xray.jpg", "resized_xray.jpg")

        cv2.imwrite(new_path, img)

        return new_path

    def archive(self,id:int, doctor_id:int) -> bool:
        success, message = self.study_repo.archive(id, doctor_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)
        
        # create a new activity
        activity = {
            "employee_id": doctor_id,
            "study_id": id,
            "activity_type": ActivityEnum.archive
        }

        activity = Activity(**activity)
        
        self.activity_repo.create(activity)
        return True
    
    def unarchive(self,id:int, doctor_id:int) -> bool:
        success, message = self.study_repo.unarchive(id, doctor_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)
        
        # create a new activity
        activity = {
            "employee_id": doctor_id,
            "study_id": id,
            "activity_type": ActivityEnum.unarchive
        }

        activity = Activity(**activity)
        
        self.activity_repo.create(activity)
        return True
    
    def assign_doctor(self,study_id:int, doctor_id:int) -> bool:
        success, message = self.study_repo.assign_doctor(study_id, doctor_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)
        
        # create a new activity
        activity = {
            "employee_id": doctor_id,
            "study_id": study_id,
            "activity_type": ActivityEnum.assign
        }


        activity = Activity(**activity)
        self.activity_repo.create(activity)

        return True
    
    def unassign_doctor(self,study_id:int, doctor_id:int) -> bool:
        success, message = self.study_repo.unassign_doctor(study_id, doctor_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=message)
        
        # create a new activity
        activity = {
            "employee_id": doctor_id,
            "study_id": study_id,
            "activity_type": ActivityEnum.unassign
        }

        activity = Activity(**activity)
        
        self.activity_repo.create(activity)

        return True
    
    def get_assigned_studies(self,employee_id: int, status: StatusEnum, limit: int, skip: int, sort: str) -> List[Study]:
        return self.study_repo.get_assigned_studies(employee_id, status, limit, skip, sort)
    
    def get_new_studies_count(self) -> dict:
        count = self.study_repo.get_new_studies_count()
        return {"count":count}
    
    def get_incomplete_studies_count(self) -> dict:
        count = self.study_repo.get_incomplete_studies_count()
        return {"count":count}
    
    def get_pending_studies_count(self,doctor_id:int) -> dict:
        count = self.study_repo.get_pending_studies_count(doctor_id)
        return {"count":count}
    
    def get_completed_studies_count(self,doctor_id:int) -> dict:
        count = self.study_repo.get_completed_studies_count(doctor_id)
        return {"count":count}
