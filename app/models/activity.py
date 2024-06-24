from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.enums import ActivityEnum
import datetime


class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(Enum(ActivityEnum), default=ActivityEnum.view)
    created_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    study_id = Column(Integer, ForeignKey("studies.id"))
    study = relationship("Study", back_populates="activities")

    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", back_populates="activities")


    