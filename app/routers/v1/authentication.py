from fastapi import APIRouter, Depends, HTTPException
from app.models import database
from app.schemas import employee as employee_schema,  authentication as authentication_schema
from app.services.employee import EmployeeService
from app.services.authentication import AuthenticationService 
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_employee_service, get_authentication_service

# Create a new APIRouter instance
router = APIRouter(
    tags=["Authentication"],
)

# Define a route for the patient list
@router.post("/signup")
async def signup(request: authentication_schema.SignUp,authentication_service: AuthenticationService = Depends(get_authentication_service) ,employee_Service: EmployeeService = Depends(get_employee_service)) -> authentication_schema.Token:
    
    # check if the password is weak
    weak_password, strength = authentication_service.check_password_strength(request.password)

    if weak_password:
        raise HTTPException(status_code=400, detail= strength)
    
    # check if the user already exists
    existing_employee = employee_Service.get_by_username(request.username)

    if existing_employee:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # encrypt password
    request.password = authentication_service.encrypt_password(request.password)
    
    # add employee
    employee = employee_Service.create(request.dict())

    # create token
    token = authentication_service.create_access_token(
        data= {
                "username": request.username,
                "role": request.role,
                "id": employee.id,
                "type": "employee"
            }
        )
    # return token from schema
    return token

# Define a route for creating a new patient
@router.post("/login")
async def login(request: authentication_schema.Login,authentication_service: AuthenticationService = Depends(get_authentication_service), employee_Service: EmployeeService = Depends(get_employee_service)) -> authentication_schema.Token:
    # check if the user exists
    employee = employee_Service.get_by_username(request.username)

    if not employee:
        raise HTTPException(status_code=400, detail="Invalid username")
    
    # check if the password is correct
    if not authentication_service.verify_password(request.password, employee.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    # create token
    token = authentication_service.create_access_token(
        data= {
                "username": request.username,
                "role": employee.role,
                "id": employee.id,
                "type": "employee"
            }
        )
    
    # return token from schema
    return token
