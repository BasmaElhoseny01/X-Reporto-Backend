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
    """
    Service layer for managing Study operations, handling business logic
    and interacting with repositories.

    Attributes:
        study_repo (StudyRepository): Repository for study operations.
        activity_repo (ActivityRepository): Repository for activity operations.
    """
    def __init__(self, study_repo: StudyRepository, activity_repo: ActivityRepository):
        self.study_repo = study_repo
        self.activity_repo = activity_repo
    
    def get_all(self,status: StatusEnum, limit: int, skip: int , sort: str) -> List[Study]:
        """
        Retrieve all studies with specified filters.

        Args:
            status (StatusEnum): The status of studies to retrieve.
            limit (int): Maximum number of studies to return.
            skip (int): Number of studies to skip for pagination.
            sort (str): Sorting criteria for the studies.

        Returns:
            List[Study]: A list of studies matching the criteria.
        """
        return self.study_repo.get_all(status, limit, skip, sort)
    
    def create(self,study: dict) -> Study:
        """
        Create a new study and persist it to the database.

        Args:
            study (dict): The study data to create.

        Returns:
            Study: The created study object.
        """
        # create a new study
        study = Study(**study)
        return self.study_repo.create(study)
    
    def destroy(self,id:int) -> bool:
        """
        Delete a study by its ID.

        Args:
            id (int): The ID of the study to delete.

        Returns:
            bool: True if the deletion was successful, otherwise False.
        """
        return self.study_repo.destroy(id)
    
    def update(self,id:int,study_data:dict, user_id: int) -> Study:
        """
        Update an existing study.

        Args:
            id (int): The ID of the study to update.
            study_data (dict): The data to update the study with.
            user_id (int): The ID of the user performing the update.

        Returns:
            Study: The updated study object.

        Raises:
            HTTPException: If the study is not found or the user is not authorized.
        """
        study = self.study_repo.show(id)
        if not study:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Study with id {id} not found")
        
        
        if study.doctor_id != user_id or study.employee_id != user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not authorized to edit this study")
        
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
        """
        Retrieve a single study by its ID.

        Args:
            id (int): The ID of the study to retrieve.
            is_doctor (bool): Flag to indicate if the requester is a doctor.

        Returns:
            Optional[Study]: The retrieved study object.

        Raises:
            HTTPException: If the study is not found.
        """
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
        """
        Retrieve studies for a specific patient.

        Args:
            patient_id (int): The ID of the patient.
            status (StatusEnum): The status of studies to retrieve.
            limit (int): Maximum number of studies to return.
            skip (int): Number of studies to skip for pagination.
            sort (str): Sorting criteria for the studies.

        Returns:
            List[Study]: A list of studies associated with the patient.
        """
        return self.study_repo.get_patient_studies(patient_id,status, limit, skip, sort)
    
    def upload_image(self,study: Study,file) -> Study:
        """
        Upload an image file for a study and save it to the filesystem.

        Args:
            study (Study): The study to upload the image for.
            file: The uploaded file containing the image.

        Returns:
            Study: The updated study object with the image path.

        Raises:
            HTTPException: If the file type is invalid.
        """
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
    
    def resize_image(self, study: Study):
        """
        Resize the X-ray image associated with a study.

        Args:
            study (Study): The study containing the X-ray image.

        Returns:
            str: The path of the resized image.

        Raises:
            HTTPException: If the image processing fails.
        """
        # read image
        img = cv2.imread(study.xray_path)

        transform =  A.Compose(
                        [
                            A.LongestMaxSize(max_size=512, interpolation=cv2.INTER_AREA),
                            A.PadIfNeeded(min_height=512, min_width=512,border_mode= cv2.BORDER_CONSTANT,value=0),

                        ])
        
        # apply transformation
        img = transform(image=img)["image"]

        # save resized image in new path
        new_path = study.xray_path.replace("xray.jpg", "resized_xray.jpg")

        cv2.imwrite(new_path, img)

        study.resized_xray_path = new_path

        self.study_repo.update(study)

        return new_path

    def archive(self,id:int, doctor_id:int) -> bool:
        """
        Archive a study by its ID.

        Args:
            id (int): The ID of the study to archive.
            doctor_id (int): The ID of the doctor performing the archiving.

        Returns:
            bool: True if the archiving was successful.

        Raises:
            HTTPException: If archiving fails.
        """
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
        """
        Unarchive a study by its ID.

        Args:
            id (int): The ID of the study to unarchive.
            doctor_id (int): The ID of the doctor performing the unarchiving.

        Returns:
            bool: True if the unarchiving was successful.

        Raises:
            HTTPException: If unarchiving fails.
        """
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
        """
        Assign a doctor to a study.

        Args:
            study_id (int): The ID of the study to assign.
            doctor_id (int): The ID of the doctor to assign.

        Returns:
            bool: True if the assignment was successful.

        Raises:
            HTTPException: If assignment fails.
        """
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
        """
        Unassign a doctor from a study.

        Args:
            study_id (int): The ID of the study to unassign.
            doctor_id (int): The ID of the doctor to unassign.

        Returns:
            bool: True if the unassignment was successful.

        Raises:
            HTTPException: If unassignment fails.
        """
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
        """
        Retrieve studies assigned to a specific employee.

        Args:
            employee_id (int): The ID of the employee.
            status (StatusEnum): The status of studies to retrieve.
            limit (int): Maximum number of studies to return.
            skip (int): Number of studies to skip for pagination.
            sort (str): Sorting criteria for the studies.

        Returns:
            List[Study]: A list of studies assigned to the employee.
        """
        return self.study_repo.get_assigned_studies(employee_id, status, limit, skip, sort)
    
    def get_new_studies_count(self) -> dict:
        """
        Get the count of new studies.

        Returns:
            dict: A dictionary containing the count of new studies.
        """
        count = self.study_repo.get_new_studies_count()
        return {"count":count}
    
    def get_incomplete_studies_count(self) -> dict:
        """
        Get the count of incomplete studies.

        Returns:
            dict: A dictionary containing the count of incomplete studies.
        """
        count = self.study_repo.get_incomplete_studies_count()
        return {"count":count}
    
    def get_pending_studies_count(self,doctor_id:int) -> dict:
        """
        Get the count of pending studies for a specific doctor.

        Args:
            doctor_id (int): The ID of the doctor.

        Returns:
            dict: A dictionary containing the count of pending studies.
        """
        count = self.study_repo.get_pending_studies_count(doctor_id)
        return {"count":count}
    
    def get_completed_studies_count(self,doctor_id:int) -> dict:
        """
        Get the count of completed studies for a specific doctor.

        Args:
            doctor_id (int): The ID of the doctor.

        Returns:
            dict: A dictionary containing the count of completed studies.
        """
        count = self.study_repo.get_completed_studies_count(doctor_id)
        return {"count":count}
