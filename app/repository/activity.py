from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.activity import Activity
from typing import List, Optional


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Activity]:
        # get all studies non deleted or archived
        activities = self.db.query(Activity).all()
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