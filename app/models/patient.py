from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from app.models.database import Base
from app.models.enums import GenderEnum
import datetime


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True) 
    age = Column(Integer)
    birth_date = Column(String)
    created_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    gender = Column(Enum(GenderEnum), default=GenderEnum.male)
    phone_number = Column(String)
    email = Column(String)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    is_deleted = Column(Boolean, default=False)
    assigned_doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=True)
    assigned_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    assigned_doctor = relationship("Doctor", back_populates="patients")
    employee = relationship("Employee", back_populates="patients")
    studies = relationship("Study", back_populates="patient")


