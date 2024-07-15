from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.activity import ActivityRepository
from app.models.activity import Activity
from app.models.enums import ActivityEnum
from typing import List, Optional



class ActivityService:
    """
    Service layer for managing activities related to doctors.

    Attributes:
        activity_repo (ActivityRepository): Repository for activity operations.
    """
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo
    
    def get_all(self, doctor_id: int,activity_type: ActivityEnum, limit: int, skip: int , sort: str) -> List[Activity]:
        """
        Retrieve a list of activities for a specific doctor.

        Args:
            doctor_id (int): The ID of the doctor to retrieve activities for.
            activity_type (ActivityEnum): The type of activity to filter by.
            limit (int): The maximum number of activities to return.
            skip (int): The number of activities to skip for pagination.
            sort (str): The sorting criteria for the activities.

        Returns:
            List[Activity]: A list of activities matching the criteria.
        """
        return self.activity_repo.get_all(doctor_id,activity_type, limit, skip, sort)
    
    def create(self,activity: dict) -> Activity:
        """
        Create a new activity.

        Args:
            activity (dict): The activity data to create.

        Returns:
            Activity: The created activity object.
        """
        # create a new patient
        activity = Activity(**activity)
        return self.activity_repo.create(activity)
    
    def destroy(self,id:int) -> bool:
        """
        Delete an activity by its ID.

        Args:
            id (int): The ID of the activity to delete.

        Returns:
            bool: True if the activity was successfully deleted, otherwise False.
        """
        return self.activity_repo.destroy(id)
    
    def update(self,id:int,activity_data:dict) -> Activity:
        """
        Update an existing activity.

        Args:
            id (int): The ID of the activity to update.
            activity_data (dict): The new data for the activity.

        Returns:
            Activity: The updated activity object.

        Raises:
            HTTPException: If the activity with the specified ID does not exist.
        """
        activity = self.activity_repo.show(id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Activity with id {id} not found")
        # update the patient
        for key, value in activity_data.items():
            setattr(activity,key,value)
            
        self.activity_repo.update(activity)
        return activity
    
    def show(self,id:int) -> Optional[Activity]:
        """
        Retrieve a specific activity by its ID.

        Args:
            id (int): The ID of the activity to retrieve.

        Returns:
            Optional[Activity]: The activity object if found, otherwise None.
        """
        return self.activity_repo.show(id)