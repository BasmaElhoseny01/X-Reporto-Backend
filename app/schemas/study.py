from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import StatusEnum

class StudyBase(BaseModel):
    study_name: Optional[str] = None
    status:  Optional[str] = StatusEnum.new
    notes: Optional[str] = None
    last_view_at: Optional[datetime] = datetime.utcnow()
    last_edited_at: Optional[datetime] = datetime.utcnow()
    updated_at: Optional[datetime] = datetime.utcnow()
    created_at: Optional[datetime] = datetime.utcnow()
    xray_path: Optional[str] = None
    xray_type: Optional[str] = None
    severity: Optional[int] = 0
    patient_id: Optional[int] = None
    employee_id: int


class StudyCreate(StudyBase):
    patient_id: int
    pass

class StudyUpdate(StudyBase):
    pass

class Study(StudyBase):
    id: int
    doctor_id: Optional[int] = None
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True

class StudyShow(Study):
    pass

class countStudy(BaseModel):
    count: int
    pass