from fastapi import APIRouter, Depends, HTTPException
from app.models import database
from app.schemas import employee as employee_schema
from app.services.employee import EmployeeService
from typing import List
from sqlalchemy.orm import Session
from app.dependencies import get_employee_service

# Create a new APIRouter instance
router = APIRouter(
    tags=["Employees"],
    prefix="/employees",
)

# Define a route for the employee list
@router.get("/")
async def read_employees(limit: int = 10, skip: int = 0, sort: str = None, employee_Service: EmployeeService = Depends(get_employee_service) ) -> List[employee_schema.EmployeeShow]:
    employees = employee_Service.get_all()
    return employees

# Define a route for creating a new employee
@router.post("/")
async def create_employees(request: employee_schema.EmployeeCreate, employee_Service: EmployeeService = Depends(get_employee_service)) -> employee_schema.Employee:
    employee = employee_Service.create(request.dict())
    return employee

# Define a route for getting a single employee
@router.get("/{employee_id}")
async def read_employee(employee_id: int, employee_Service: EmployeeService = Depends(get_employee_service)) -> employee_schema.EmployeeShow:
    employee = employee_Service.show(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")
    return employee

# Define a route for updating an employee
@router.put("/{employee_id}")
async def update_employee(employee_id: int, request: employee_schema.EmployeeUpdate, employee_Service: EmployeeService = Depends(get_employee_service)) -> employee_schema.EmployeeShow:
    employee = employee_Service.update(employee_id, request.dict())
    return employee

# Define a route for deleting an employee
@router.delete("/{employee_id}")
async def delete_employee(employee_id: int, employee_Service: EmployeeService = Depends(get_employee_service)) -> bool:
    deleted = employee_Service.destroy(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")
    return deleted

