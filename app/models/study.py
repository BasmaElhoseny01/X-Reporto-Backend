from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.database import Base
from app.models.enums import StatusEnum
import datetime


class Study(Base):
    __tablename__ = "studies"
    
    id = Column(Integer, primary_key=True, index=True)
    study_name = Column(String, index=True)
    notes = Column(String)
    status = Column(Enum(StatusEnum), default=StatusEnum.new)
    created_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    severity = Column(Integer)
    xray_path = Column(String)
    xray_type = Column(String) # This should be an Enum
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    last_view_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_edited_at = Column(String, default = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # last_edited_by = Column(Integer, ForeignKey("doctors.id"))
    # last_viewed_by = Column(Integer, ForeignKey("doctors.id"))

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    
    patient = relationship("Patient", back_populates="studies")
    doctor = relationship("Doctor", back_populates="studies")
    employee = relationship("Employee", back_populates="studies")
    results = relationship("Result", back_populates="study")
    # doctor_last_edited = relationship("Doctor", foreign_keys=[last_edited_by])
    # doctor_last_viewed = relationship("Doctor", foreign_keys=[last_viewed_by])

    