from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime
from app.models.database import Base
from app.models.enums import StatusEnum
from sqlalchemy.orm import relationship
import datetime


class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String, index=True)
    template_path = Column(String)
    created_at = Column(DateTime, default = datetime.datetime.utcnow)
    used_count = Column(Integer, default=0)
    last_edited_at = Column(DateTime, default = datetime.datetime.utcnow)
    last_view_at = Column(DateTime, default = datetime.datetime.utcnow)

    doctor_id = Column(Integer, ForeignKey("employees.id"))
    doctor = relationship("Employee", back_populates="templates")




    