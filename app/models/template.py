from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean
from app.models.database import Base
from app.models.enums import StatusEnum
import datetime


class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String, index=True)
    template_path = Column(String)
    created_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    used_count = Column(Integer, default=0)

    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    doctor = relationship("Doctor", back_populates="templates")




    