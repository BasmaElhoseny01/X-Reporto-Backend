from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.activity import Activity
from app.models.enums import ActivityEnum
from typing import List, Optional


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self,doctor_id: int,activity_type: ActivityEnum, limit: int, skip: int , sort: str) -> List[Activity]:
        # get all studies non deleted or archived
        query = self.db.query(Activity).filter(Activity.employee_id == doctor_id)
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        if sort:
            query = query.order_by(sort)
        activities = query.offset(skip).limit(limit).all()
        return activities
    
    def create(self,activity: Activity) -> Activity:
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def destroy(self,id:int) -> bool:
        activity = self.db.query(Activity).filter(Activity.id == id)
        if not activity.first():
            return False

        activity.delete(synchronize_session=False)
        self.db.commit()
        return True
    
    def update(self,activity:Activity) -> Activity:
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    
    def show(self,id:int) ->  Optional[Activity]:
        activity = self.db.query(Activity).filter(Activity.id == id).first()
        if not activity:
            return None
        return activity