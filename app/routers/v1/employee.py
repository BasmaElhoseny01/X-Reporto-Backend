from fastapi import APIRouter, Depends, HTTPException, Security
from app.models import database
from app.schemas import employee as employee_schema, authentication as auth_schema, error as error_schema
from app.models.enums import OccupationEnum
from app.services.employee import EmployeeService
from typing import List, Union
from sqlalchemy.orm import Session
from app.middleware.authentication import get_current_user, security
from app.dependencies import get_employee_service

# Create a new APIRouter instance
router = APIRouter(
    tags=["Employees"],
    prefix="/employees",
)


# Define a route for me
@router.get("/me", dependencies=[Security(security)], response_model= employee_schema.EmployeeShow,
            responses={401: {"model": error_schema.Error},
                       200: {"description": "User retrieved successfully"}})
async def read_me(user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service) ) -> employee_schema.EmployeeShow:
    employee = employee_Service.show(user.id)
    return employee

# Define a route for the employee list
@router.get("/", dependencies=[Security(security)],
            response_model= List[employee_schema.EmployeeShow],
            responses={400: {"model": error_schema.Error},
                       200: {"description": "Employees retrieved successfully"},
                       401: {"model": error_schema.Error}})
async def read_employees(type: OccupationEnum = None ,limit: int = 10, skip: int = 0, sort: str = None,user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service) ) -> List[employee_schema.EmployeeShow]:
    employees = employee_Service.get_all(type, limit, skip, sort)
    return employees

# Define a route for creating a new employee
@router.post("/", dependencies=[Security(security)], 
             response_model= Union[employee_schema.Employee, error_schema.Error],
             responses={400: {"model": error_schema.Error},
                        201: {"description": "Employee created successfully"},
                        401: {"model": error_schema.Error}})
async def create_employees(request: employee_schema.EmployeeCreate,user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service)) -> employee_schema.Employee:
    employee = employee_Service.create(request.dict())
    return employee

# Define a route for getting a single employee
@router.get("/{employee_id}", dependencies=[Security(security)], response_model= Union[employee_schema.EmployeeShow, error_schema.Error]
            , responses={404: {"model": error_schema.Error},
                         200: {"description": "Employee retrieved successfully"},
                         401: {"model": error_schema.Error}})
async def read_employee(employee_id: int,user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service)) -> employee_schema.EmployeeShow:
    employee = employee_Service.show(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")
    return employee

# Define a route for updating an employee
@router.put("/{employee_id}", dependencies=[Security(security)]
            , response_model= Union[employee_schema.EmployeeShow, error_schema.Error]
            , responses={404: {"model": error_schema.Error},
                         200: {"description": "Employee updated successfully"},
                         401: {"model": error_schema.Error}})
async def update_employee(employee_id: int, request: employee_schema.EmployeeUpdate,user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service)) -> employee_schema.EmployeeShow:
    employee = employee_Service.update(employee_id, request.dict())
    return employee

# Define a route for deleting an employee
@router.delete("/{employee_id}", dependencies=[Security(security)]
               , response_model= Union[bool, error_schema.Error]
               , responses={404: {"model": error_schema.Error},
                            204: {"description": "Employee deleted successfully"},
                            401: {"model": error_schema.Error}})
async def delete_employee(employee_id: int,user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service)) -> bool:
    deleted = employee_Service.destroy(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")
    return deleted

