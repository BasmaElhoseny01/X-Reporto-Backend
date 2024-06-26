from sqlalchemy import Column, Integer, String, Enum, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.enums import GenderEnum, RoleEnum, OccupationEnum
import datetime


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    password = Column(String)
    employee_name = Column(String) 
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    type = Column(Enum(OccupationEnum), default=OccupationEnum.employee)
    age = Column(Integer)
    birth_date = Column(String)
    created_at = Column(DateTime, default = datetime.datetime.utcnow)
    gender = Column(Enum(GenderEnum), default=GenderEnum.male)
    phone_number = Column(String)
    email = Column(String)
    is_deleted = Column(Boolean, default=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)


    # created patients by employee
    patients = relationship("Patient", back_populates="employee", foreign_keys="Patient.employee_id")

    # created studies by employee
    studies = relationship("Study", back_populates="employee", foreign_keys="Study.employee_id" )

    # created employee by employee
    # employee = relationship("Employee", remote_side=[id])
    employee = relationship("Employee", remote_side=[id], back_populates="employees")  # Manager (self-referential)
    employees = relationship("Employee", back_populates="employee")  # Employees managed by this employee

    # assigned studies by employee "doctor"
    assigned_studies = relationship("Study", back_populates="doctor", foreign_keys="Study.doctor_id")

    # created templates by employee "doctor"
    templates = relationship("Template", back_populates="doctor", foreign_keys="Template.doctor_id")

    
    activities = relationship("Activity", back_populates="employee")

    


