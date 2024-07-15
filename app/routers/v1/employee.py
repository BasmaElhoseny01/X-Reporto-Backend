from fastapi import APIRouter, Depends, HTTPException, Security
from app.models import database
from app.schemas import employee as employee_schema, authentication as auth_schema, error as error_schema
from app.schemas import study as study_schema
from app.models.enums import OccupationEnum, StatusEnum
from app.services.employee import EmployeeService
from app.services.study import StudyService
from app.services.authentication import AuthenticationService
from typing import List, Union
from sqlalchemy.orm import Session
from app.middleware.authentication import get_current_user, security
from app.dependencies import get_employee_service,get_study_service, get_authentication_service

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
    """
    Retrieve the currently authenticated user's employee details.

    Args:
    - user (auth_schema.TokenData): The current authenticated user.
    - employee_Service (EmployeeService): The employee service dependency.

    Returns:
    - employee_schema.EmployeeShow: The details of the authenticated employee.

    Raises:
    - HTTPException: If authentication fails.
    """
    employee = employee_Service.show(user.id)
    return employee

# Define a route for the employee list
@router.get("/", dependencies=[Security(security)],
            response_model= List[employee_schema.EmployeeShow],
            responses={400: {"model": error_schema.Error},
                       200: {"description": "Employees retrieved successfully"},
                       401: {"model": error_schema.Error}})
async def read_employees(type: OccupationEnum = None ,limit: int = 10, skip: int = 0, sort: str = None,user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service) ) -> List[employee_schema.EmployeeShow]:
    """
    Retrieve a list of employees with optional filters.

    Args:
    - type (OccupationEnum): The occupation type to filter employees.
    - limit (int): The number of employees to retrieve.
    - skip (int): The number of employees to skip.
    - sort (str): The field to sort by.
    - user (auth_schema.TokenData): The current authenticated user.
    - employee_Service (EmployeeService): The employee service dependency.

    Returns:
    - List[employee_schema.EmployeeShow]: A list of employees.

    Raises:
    - HTTPException: If authentication fails or if the request is invalid.
    """
    employees = employee_Service.get_all(type, limit, skip, sort)
    return employees

# Define a route for creating a new employee
@router.post("/", dependencies=[Security(security)], 
             response_model= Union[employee_schema.Employee, error_schema.Error],
             responses={400: {"model": error_schema.Error},
                        201: {"description": "Employee created successfully"},
                        401: {"model": error_schema.Error}})
async def create_employees(request: employee_schema.EmployeeCreate,user: auth_schema.TokenData  = Depends(get_current_user), authentication_service: AuthenticationService = Depends(get_authentication_service) ,employee_Service: EmployeeService = Depends(get_employee_service)) -> employee_schema.Employee:
    """
    Create a new employee.

    Args:
    - request (employee_schema.EmployeeCreate): The employee creation request.
    - user (auth_schema.TokenData): The current authenticated user.
    - authentication_service (AuthenticationService): The authentication service dependency.
    - employee_Service (EmployeeService): The employee service dependency.

    Returns:
    - employee_schema.Employee: The created employee.

    Raises:
    - HTTPException: If the user is not authorized, if the password is weak, or if the username already exists.
    """
    if user.role != "admin" and user.role != "manager":
        print(user.role)
        raise HTTPException(status_code=401, detail="You are not authorized to create an employee")
    
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
    request.employee_id = user.id

    # add employee
    employee = employee_Service.create(request.dict())
    return employee

# Define a route for getting a single employee
@router.get("/{employee_id}", dependencies=[Security(security)], response_model= Union[employee_schema.EmployeeShow, error_schema.Error]
            , responses={404: {"model": error_schema.Error},
                         200: {"description": "Employee retrieved successfully"},
                         401: {"model": error_schema.Error}})
async def read_employee(employee_id: int,user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service)) -> employee_schema.EmployeeShow:
    """
    Retrieve a single employee by their ID.

    Args:
    - employee_id (int): The ID of the employee to retrieve.
    - user (auth_schema.TokenData): The current authenticated user.
    - employee_Service (EmployeeService): The employee service dependency.

    Returns:
    - employee_schema.EmployeeShow: The details of the requested employee.

    Raises:
    - HTTPException: If the employee is not found.
    """
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
    """
    Update an existing employee by their ID.

    Args:
    - employee_id (int): The ID of the employee to update.
    - request (employee_schema.EmployeeUpdate): The employee update request.
    - user (auth_schema.TokenData): The current authenticated user.
    - employee_Service (EmployeeService): The employee service dependency.

    Returns:
    - employee_schema.EmployeeShow: The updated employee details.

    Raises:
    - HTTPException: If the employee is not found.
    """
    employee = employee_Service.update(employee_id, request.dict())
    return employee

# Define a route for deleting an employee
@router.delete("/{employee_id}", dependencies=[Security(security)]
               , response_model= Union[bool, error_schema.Error]
               , responses={404: {"model": error_schema.Error},
                            204: {"description": "Employee deleted successfully"},
                            401: {"model": error_schema.Error}})
async def delete_employee(employee_id: int,user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service)) -> bool:
    """
    Delete an employee by their ID.

    Args:
    - employee_id (int): The ID of the employee to delete.
    - user (auth_schema.TokenData): The current authenticated user.
    - employee_Service (EmployeeService): The employee service dependency.

    Returns:
    - bool: True if the employee was deleted, False otherwise.

    Raises:
    - HTTPException: If the user is not authorized or if the employee is not found.
    """
    if user.role != "admin":
        raise HTTPException(status_code=401, detail="You are not authorized to delete an employee")
    deleted = employee_Service.destroy(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")
    return deleted


# Define a route for getting the employee's studies assigned to them
@router.get("/{employee_id}/studies", dependencies=[Security(security)], response_model= List[study_schema.StudyShow]
            , responses={404: {"model": error_schema.Error},
                         200: {"description": "Studies retrieved successfully"},
                         401: {"model": error_schema.Error}})
async def read_employee_studies(employee_id: int,status: StatusEnum = None, limit: int = 10, skip: int = 0, sort: str = None, user: auth_schema.TokenData  = Depends(get_current_user), employee_Service: EmployeeService = Depends(get_employee_service), study_service: StudyService = Depends(get_study_service)) -> List[study_schema.StudyShow]:
    """
    Retrieve the studies assigned to a specific doctor by their employee ID.

    Args:
    - employee_id (int): The ID of the doctor whose studies are to be retrieved.
    - status (StatusEnum): The status of the studies to filter by.
    - limit (int): The number of studies to retrieve.
    - skip (int): The number of studies to skip.
    - sort (str): The field to sort by.
    - user (auth_schema.TokenData): The current authenticated user.
    - employee_Service (EmployeeService): The employee service dependency.
    - study_Service (StudyService): The study service dependency.

    Returns:
    - List[study_schema.StudyShow]: A list of studies assigned to the doctor.

    Raises:
    - HTTPException: If the doctor is not found or if the employee is not a doctor.
    """
    employee = employee_Service.show(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Doctor with id {employee_id} not found")
    if employee.type != "doctor":
        raise HTTPException(status_code=400, detail="Employee is not a doctor")
    return study_service.get_assigned_studies(employee.id, status, limit, skip, sort)