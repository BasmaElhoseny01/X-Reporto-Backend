from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import ActivityEnum

class ActivityBase(BaseModel):
    activity_type: Optional[str] = ActivityEnum.view
    created_at: Optional[datetime] = datetime.utcnow()
    study_id: Optional[int] = None
    employee_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True

class ActivityShow(ActivityBase):
    id: int
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True
