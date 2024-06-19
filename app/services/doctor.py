from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.doctor import DoctorRepository
from app.models.doctor import Doctor
from typing import List, Optional



class DoctorService:
    def __init__(self, doctor_repo: DoctorRepository):
        self.doctor_repo = doctor_repo
    
    def get_all(self) -> List[Doctor]:
        return self.doctor_repo.get_all()
    
    def create(self,doctor: dict) -> Doctor:
        # create a new patient
        doctor = Doctor(**doctor)
        return self.doctor_repo.create(doctor)
    
    def destroy(self,id:int) -> bool:
        return self.doctor_repo.destroy(id)
    
    def update(self,id:int,doctor_data:dict) -> Doctor:
        doctor = self.doctor_repo.show(id)
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Doctor with id {id} not found")
        
        for key, value in doctor_data.items():
            setattr(doctor,key,value)
            
        self.doctor_repo.update(doctor)
        return doctor
    
    def show(self,id:int) -> Optional[Doctor]:
        return self.doctor_repo.show(id)
    def get_by_username(self,username:str) -> Optional[Doctor]:
        return self.doctor_repo.get_by_username(username)