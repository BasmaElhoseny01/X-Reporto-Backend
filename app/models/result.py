from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.enums import  ResultTypeEnum
import datetime


class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    result_name = Column(String)
    type = Column(Enum(ResultTypeEnum), default=ResultTypeEnum.custom)
    created_at = Column(DateTime, default = datetime.datetime.utcnow)
    confidence = Column(ARRAY(Float), default = None)
    labels = Column(ARRAY(Integer), default = None)
    xray_path = Column(String)
    report_path = Column(String)
    heatmap_path = Column(String)
    region_path = Column(String)
    region_sentence_path = Column(String)
    last_view_at = Column(DateTime, default = datetime.datetime.utcnow)
    last_edited_at = Column(DateTime, default = datetime.datetime.utcnow)
    is_ready = Column(Boolean, default=False)
    study_id = Column(Integer, ForeignKey("studies.id"), nullable=False)

    study = relationship("Study", back_populates="results")



    