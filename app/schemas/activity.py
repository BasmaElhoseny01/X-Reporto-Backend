from pydantic import BaseModel
from typing import Optional
import datetime
from app.models.enums import ActivityEnum

class ActivityBase(BaseModel):
    activity_type: Optional[str] = ActivityEnum.view
    created_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
