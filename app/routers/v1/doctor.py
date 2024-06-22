from fastapi import APIRouter, Depends, HTTPException, Security
from app.models import database
from app.schemas import doctor as doctor_schema, authentication as auth_schema, error as error_schema
from app.services.doctor import DoctorService
from typing import List, Union
from sqlalchemy.orm import Session
from app.dependencies import get_doctor_service
from app.middleware.authentication import get_current_user, security

# Create a new APIRouter instance
router = APIRouter(
    tags=["Doctors"],
    prefix="/doctors",
)

# Define a route for the employee list
@router.get("/", dependencies=[Security(security)],
            response_model= List[doctor_schema.DoctorShow],
            responses={400: {"model": error_schema.Error},
                       200: {"description": "Doctors retrieved successfully"},
                       401: {"model": error_schema.Error}},
                       status_code=200)
async def read_doctors(limit: int = 10, skip: int = 0, sort: str = None, user: auth_schema.TokenData  = Depends(get_current_user), doctor_service: DoctorService = Depends(get_doctor_service) ) -> List[doctor_schema.DoctorShow]:
    doctors = doctor_service.get_all()
    return doctors

# Define a route for creating a new employee
@router.post("/", dependencies=[Security(security)],
             response_model= Union[doctor_schema.DoctorShow, error_schema.Error],
             responses={400: {"model": error_schema.Error},
                        201: {"model": doctor_schema.DoctorShow, "description": "Doctor created successfully"},
                        401: {"model": error_schema.Error}},
                        status_code=201)
async def create_doctors(request: doctor_schema.DoctorCreate,user: auth_schema.TokenData  = Depends(get_current_user), doctor_service: DoctorService = Depends(get_doctor_service)) -> doctor_schema.DoctorShow:
    # check if the user is an admin
    if user.role != "admin" and user.type != "employee":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")
    
    request.employee_id = user.id
    doctor = doctor_service.create(request.dict())
    return doctor

# Define a route for getting a single employee
@router.get("/{doctor_id}",dependencies=[Security(security)],
            response_model= Union[doctor_schema.DoctorShow, error_schema.Error]
            , responses={404: {"model": error_schema.Error},
                         200: {"description": "Doctor retrieved successfully"},
                         401: {"model": error_schema.Error}},
                         status_code=200)
async def read_doctor(doctor_id: int, user: auth_schema.TokenData  = Depends(get_current_user), doctor_service: DoctorService = Depends(get_doctor_service)) -> doctor_schema.DoctorShow:
    doctor = doctor_service.show(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")
    return doctor

# Define a route for updating an employee
@router.put("/{doctor_id}", dependencies=[Security(security)],
            response_model= Union[doctor_schema.DoctorShow, error_schema.Error]
            , responses={404: {"model": error_schema.Error},
                         200: {"description": "Doctor updated successfully"},
                         401: {"model": error_schema.Error}},
                         status_code=200)
async def update_doctor(doctor_id: int, request: doctor_schema.DoctorUpdate,user: auth_schema.TokenData  = Depends(get_current_user), doctor_service: DoctorService = Depends(get_doctor_service)) -> doctor_schema.DoctorShow:
    if user.role != "admin" and user.type != "employee":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

    doctor = doctor_service.update(doctor_id, request.dict())
    return doctor

# Define a route for deleting an employee
@router.delete("/{doctor_id}", dependencies=[Security(security)],
               response_model= Union[bool, error_schema.Error]
               , responses={404: {"model": error_schema.Error},
                            204: {"description": "Doctor deleted successfully"},
                            401: {"model": error_schema.Error}})
async def delete_doctor(doctor_id: int, user: auth_schema.TokenData  = Depends(get_current_user), doctor_service: DoctorService = Depends(get_doctor_service)) -> bool:
    if user.role != "admin" and user.type != "employee":
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

    deleted = doctor_service.destroy(doctor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")
    return deleted