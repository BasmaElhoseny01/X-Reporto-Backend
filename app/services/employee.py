from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.employee import EmployeeRepository
from app.models.employee import Employee
from app.models.enums import OccupationEnum
from typing import List, Optional



class EmployeeService:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo
    
    def get_all(self,type: OccupationEnum ) -> List[Employee]:
        return self.employee_repo.get_all(type)
    
    def create(self,employee: dict) -> Employee:
        # create a new patient
        employee = Employee(**employee)
        return self.employee_repo.create(employee)
    
    def destroy(self,id:int) -> bool:
        return self.employee_repo.destroy(id)
    
    def update(self,id:int,employee_data:dict) -> Employee:
        employee = self.employee_repo.show(id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Employee with id {id} not found")
        
        for key, value in employee_data.items():
            setattr(employee,key,value)
            
        self.employee_repo.update(employee)
        return employee
    
    def show(self,id:int) -> Optional[Employee]:
        return self.employee_repo.show(id)
    def get_by_username(self,username:str) -> Optional[Employee]:
        return self.employee_repo.get_by_username(username)