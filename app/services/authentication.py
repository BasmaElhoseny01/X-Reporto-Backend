from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.employee import EmployeeRepository
from app.models.employee import Employee
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.schemas.authentication import TokenData
import bcrypt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class AuthenticationService:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo
    
    def create_access_token(self,data: dict) -> dict:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": encoded_jwt, "token_type": "bearer"}

    def verify_token(self,token: str, credentials_exception: HTTPException):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        return token_data
    def check_password_strength(self, password: str) -> bool:
        if len(password) < 8:
            return True, "Password must be at least 8 characters long"
        
        # check the password has at least one uppercase letter and one lowercase letter and one digit and one special character
        if not any(char.isupper() for char in password):
            return True, "Password must have at least one uppercase letter"
        if not any(char.islower() for char in password):
            return True, "Password must have at least one lowercase letter"
        if not any(char.isdigit() for char in password):
            return True, "Password must have at least one digit"
        if not any(char in "!@#$%^&*()-_=+{}[]|;:,.<>?/~" for char in password):
            return True, "Password must have at least one special character"
        
        return False, "Password is strong"
    
    def encrypt_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())