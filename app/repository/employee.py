from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.employee import Employee
from app.models.enums import OccupationEnum
from typing import List, Optional


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self,type: OccupationEnum, limit: int, skip: int, sort: str) -> List[Employee]:
        query = self.db.query(Employee)
        if type:
            query = query.filter(Employee.type == type)
        if sort:
            sort_key = sort.lstrip("-")
            if sort.startswith("-"):
                query = query.order_by(getattr(Employee,sort_key).desc())
            else:
                query = query.order_by(getattr(Employee,sort_key))
        if limit:
            query = query.limit(limit)
        if skip:
            query = query.offset(skip)
        employees = query.all()
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
