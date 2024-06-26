from pydantic import BaseModel
from fastapi import Form
from typing import Optional, List
from datetime import datetime
from app.models.enums import GenderEnum
from app.schemas.study import Study

class PatientBase(BaseModel):
    patient_name: Optional[str] = None
    age: Optional[int] = None 
    email: Optional[str] = None
    birth_date: Optional[str] = None
    created_at: Optional[datetime] = datetime.utcnow()
    gender: Optional[str] = GenderEnum.male
    phone_number : Optional[str] = None
    employee_id: Optional[int] = None



class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    studies: Optional[List[Study]] = []
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True
