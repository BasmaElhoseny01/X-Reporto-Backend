from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.employee import EmployeeRepository
from app.models.employee import Employee
from app.models.enums import OccupationEnum
from typing import List, Optional



class EmployeeService:
    """
    Service layer for managing Employee operations, handling business logic
    and interacting with the Employee repository.

    Attributes:
        employee_repo (EmployeeRepository): Repository for employee operations.
    """
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo
    
    def get_all(self,type: OccupationEnum, limit: int, skip: int, sort: str) -> List[Employee]:
        """
        Retrieve all employees based on occupation type and pagination.

        Args:
            type (OccupationEnum): The occupation type to filter employees.
            limit (int): The maximum number of employees to retrieve.
            skip (int): The number of employees to skip for pagination.
            sort (str): The sorting order for the employees.

        Returns:
            List[Employee]: A list of all employees matching the criteria.
        """
        return self.employee_repo.get_all(type, limit, skip, sort)
    
    def create(self,employee: dict) -> Employee:
        """
        Create a new employee and persist it to the database.

        Args:
            employee (dict): The employee data to create.

        Returns:
            Employee: The created employee object.
        """
        # create a new patient
        employee = Employee(**employee)
        return self.employee_repo.create(employee)
    
    def destroy(self,id:int) -> bool:
        """
        Delete an employee by its ID.

        Args:
            id (int): The ID of the employee to delete.

        Returns:
            bool: True if the deletion was successful, otherwise False.
        """
        return self.employee_repo.destroy(id)
    
    def update(self,id:int,employee_data:dict) -> Employee:
        """
        Update an existing employee.

        Args:
            id (int): The ID of the employee to update.
            employee_data (dict): The data to update the employee with.

        Returns:
            Employee: The updated employee object.

        Raises:
            HTTPException: If the employee is not found.
        """
        employee = self.employee_repo.show(id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Employee with id {id} not found")
        
        for key, value in employee_data.items():
            setattr(employee,key,value)
            
        self.employee_repo.update(employee)
        return employee
    
    def show(self,id:int) -> Optional[Employee]:
        """
        Retrieve a single employee by its ID.

        Args:
            id (int): The ID of the employee to retrieve.

        Returns:
            Optional[Employee]: The retrieved employee object, or None if not found.
        """
        return self.employee_repo.show(id)
    def get_by_username(self,username:str) -> Optional[Employee]:
        """
        Retrieve an employee by their username.

        Args:
            username (str): The username of the employee to retrieve.

        Returns:
            Optional[Employee]: The retrieved employee object, or None if not found.
        """
        return self.employee_repo.get_by_username(username)