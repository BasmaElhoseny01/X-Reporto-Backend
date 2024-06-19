from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.enums import GenderEnum, RoleEnum
import datetime


class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String)
    doctor_name = Column(String) 
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    age = Column(Integer)
    birth_date = Column(String)
    created_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    gender = Column(Enum(GenderEnum), default=GenderEnum.male)
    phone_number = Column(String)
    email = Column(String)
    is_deleted = Column(Boolean, default=False)

    studies = relationship("Study", back_populates="doctor")
    templates = relationship("Template", back_populates="doctor")