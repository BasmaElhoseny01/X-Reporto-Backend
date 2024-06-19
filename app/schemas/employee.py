from pydantic import BaseModel
from typing import Optional
import datetime
from app.models.enums import GenderEnum, RoleEnum

class EmployeeBase(BaseModel):
    employee_name: Optional[str] = None
    role:  Optional[str] = RoleEnum.user
    age: Optional[int] = None
    birth_date: Optional[str] = None
    created_at: Optional[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gender: Optional[str] = GenderEnum.male
    phone_number: Optional[str] = None
    email: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    password: str
    username: str


class EmployeeUpdate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    username: str
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True

class EmployeeShow(EmployeeBase):
    id: int
    username: str
    class Config:
        # allow population of ORM model
        orm_mode = True
        allow_population_by_field_name = True
