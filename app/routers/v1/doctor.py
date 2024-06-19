from fastapi import APIRouter, Depends, HTTPException
from app.models import database
from app.schemas import doctor as doctor_schema
from app.services.doctor import DoctorService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_doctor_service

# Create a new APIRouter instance
router = APIRouter(
    tags=["Doctors"],
    prefix="/doctors",
)

# Define a route for the employee list
@router.get("/")
async def read_doctors(limit: int = 10, skip: int = 0, sort: str = None, doctor_service: DoctorService = Depends(get_doctor_service) ) -> List[doctor_schema.DoctorShow]:
    doctors = doctor_service.get_all()
    return doctors

# Define a route for creating a new employee
@router.post("/")
async def create_doctors(request: doctor_schema.DoctorCreate, doctor_service: DoctorService = Depends(get_doctor_service)) -> doctor_schema.DoctorShow:
    doctor = doctor_service.create(request.dict())
    return doctor

# Define a route for getting a single employee
@router.get("/{doctor_id}")
async def read_doctor(doctor_id: int, doctor_service: DoctorService = Depends(get_doctor_service)) -> doctor_schema.DoctorShow:
    doctor = doctor_service.show(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")
    return doctor

# Define a route for updating an employee
@router.put("/{doctor_id}")
async def update_doctor(doctor_id: int, request: doctor_schema.DoctorUpdate, doctor_service: DoctorService = Depends(get_doctor_service)) -> doctor_schema.DoctorShow:
    doctor = doctor_service.update(doctor_id, request.dict())
    return doctor

# Define a route for deleting an employee
@router.delete("/{doctor_id}")
async def delete_doctor(doctor_id: int, doctor_service: DoctorService = Depends(get_doctor_service)) -> bool:
    deleted = doctor_service.destroy(doctor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")
    return deleted