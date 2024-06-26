from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.activity import ActivityRepository
from app.models.activity import Activity
from typing import List, Optional



class ActivityService:
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo
    
    def get_all(self) -> List[Activity]:
        return self.activity_repo.get_all()
    
    def create(self,activity: dict) -> Activity:
        # create a new patient
        activity = Activity(**activity)
        return self.activity_repo.create(activity)
    
    def destroy(self,id:int) -> bool:
        return self.activity_repo.destroy(id)
    
    def update(self,id:int,activity_data:dict) -> Activity:
        activity = self.activity_repo.show(id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Activity with id {id} not found")
        # update the patient
        for key, value in activity_data.items():
            setattr(activity,key,value)
            
        self.activity_repo.update(activity)
        return activity
    
    def show(self,id:int) -> Optional[Activity]:
        return self.activity_repo.show(id)