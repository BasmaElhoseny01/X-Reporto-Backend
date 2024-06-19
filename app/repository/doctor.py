from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.doctor import Doctor
from typing import List, Optional


class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Doctor]:
        doctors = self.db.query(Doctor).all()
        return doctors
    
    def create(self,doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor
    
    def destroy(self,id:int) -> bool:
        doctor = self.db.query(Doctor).filter(Doctor.id == id)
        if not doctor.first():
            return False

        doctor.delete(synchronize_session=False)
        self.db.commit()
        return True
    
    def update(self,doctor:Doctor) -> Doctor:
        self.db.commit()
        self.db.refresh(doctor)
        return doctor
    
    
    def show(self,id:int) ->  Optional[Doctor]:
        doctor = self.db.query(Doctor).filter(Doctor.id == id).first()
        if not doctor:
            return None
        return doctor
    def get_by_username(self,username:str) -> Optional[Doctor]:
        doctor = self.db.query(Doctor).filter(Doctor.username == username).first()
        if not doctor:
            return None
        return doctor
