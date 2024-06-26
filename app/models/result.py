from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.enums import StatusEnum, ResultTypeEnum
import datetime


class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    result_name = Column(String, index=True)
    type = Column(Enum(ResultTypeEnum), default=ResultTypeEnum.custom)
    created_at = Column(DateTime, default = datetime.datetime.utcnow)
    confidence = Column(String)
    xray_path = Column(String)
    report_path = Column(String)
    heatmap_path = Column(String)
    region_path = Column(String)
    last_view_at = Column(DateTime, default = datetime.datetime.utcnow)
    last_edited_at = Column(DateTime, default = datetime.datetime.utcnow)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=False)

    study = relationship("Study", back_populates="results")



    