from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.employee import Employee
from typing import List, Optional


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Employee]:
        employees = self.db.query(Employee).all()
        return employees
    
    def create(self,employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee
    
    def destroy(self,id:int) -> bool:
        employee = self.db.query(Employee).filter(Employee.id == id)
        if not employee.first():
            return False

        employee.delete(synchronize_session=False)
        self.db.commit()
        return True
    
    def update(self,employee:Employee) -> Employee:
        self.db.commit()
        self.db.refresh(employee)
        return employee
    
    
    def show(self,id:int) ->  Optional[Employee]:
        employee = self.db.query(Employee).filter(Employee.id == id).first()
        if not employee:
            return None
        return employee
    def get_by_username(self,username:str) -> Optional[Employee]:
        employee = self.db.query(Employee).filter(Employee.username == username).first()
        if not employee:
            return None
        return employee
