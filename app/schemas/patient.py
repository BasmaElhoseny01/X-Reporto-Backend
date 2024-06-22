from pydantic import BaseModel
from fastapi import Form
from typing import Optional
import datetime
from app.models.enums import GenderEnum

class PatientBase(BaseModel):
    patient_name: Optional[str] = None
    age: Optional[int] = None 
    email: Optional[str] = None
    birth_date: Optional[str] = None
    created_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gender: Optional[str] = GenderEnum.male
    phone_number : Optional[str] = None
    employee_id: Optional[int] = None
    assigned_doctor_id: Optional[int] = None


class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    
    class Config:
        # allow population of ORM model
        orm_mode = True
