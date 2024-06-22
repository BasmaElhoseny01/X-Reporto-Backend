from pydantic import BaseModel
from typing import Optional
import datetime
from app.models.enums import StatusEnum

class StudyBase(BaseModel):
    study_name: Optional[str] = None
    status:  Optional[str] = StatusEnum.new
    notes: Optional[str] = None
    last_view_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_edited_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    created_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    xray_path: Optional[str] = None
    xray_type: Optional[str] = None
    severity: Optional[int] = 0
    archived: Optional[bool] =False
    patient_id: int
    doctor_id: Optional[int] = None
    employee_id: Optional[int] = None


class StudyCreate(StudyBase):
    pass

class StudyUpdate(StudyBase):
    pass

class Study(StudyBase):
    id: int
    
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True

class StudyShow(Study):
    pass