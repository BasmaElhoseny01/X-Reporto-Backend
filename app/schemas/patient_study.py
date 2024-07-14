from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import StatusEnum
from app.schemas.patient import Patient

class PatientStudy(BaseModel):
    study_name: Optional[str] = None
    status:  Optional[str] = StatusEnum.new
    notes: Optional[str] = None
    last_view_at: Optional[datetime] = datetime.utcnow()
    last_edited_at: Optional[datetime] = datetime.utcnow()
    updated_at: Optional[datetime] = datetime.utcnow()
    created_at: Optional[datetime] = datetime.utcnow()
    xray_path: Optional[str] = None
    resized_xray_path: Optional[str] = None
    xray_type: Optional[str] = None
    severity: Optional[float] = 0
    is_archived: Optional[bool] =False
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    employee_id: Optional[int] = None
    patient: Optional[Patient] = None
    id: int
    
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True
