from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.enums import ActivityEnum
import datetime


class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(Enum(ActivityEnum), default=ActivityEnum.view)
    created_at = Column(DateTime, default = datetime.datetime.utcnow)

    study_id = Column(Integer, ForeignKey("studies.id"))
    study = relationship("Study", back_populates="activities")

    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", back_populates="activities")


    