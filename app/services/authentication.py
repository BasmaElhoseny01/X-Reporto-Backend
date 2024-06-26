from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repository.employee import EmployeeRepository
from app.models.employee import Employee
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.schemas.authentication import TokenData
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import configs
import bcrypt


security = HTTPBearer()

class AuthenticationService:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo
    
    def create_access_token(self,data: dict) -> dict:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, configs.SECRET_KEY, algorithm=configs.ALGORITHM)
        return {"access_token": encoded_jwt, "token_type": "bearer"}

    def verify_token(self,token: str, credentials_exception: HTTPException):
        try:
            payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
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
        try:
            return bcrypt.checkpw(password.encode(), hashed_password.encode())
        except:
            return False

    @staticmethod
    def decrypt_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
            print("payload", payload)
            username = payload.get("username",None)
            if username is None:
                raise  HTTPException(status_code=401, detail=f"Unauthorized user not found")
            token_data = TokenData(username=username)
        except JWTError:
            print("error")
            raise HTTPException(status_code=401, detail=f"Unauthorized token invalid")
        return token_data

    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
        token = credentials.credentials
        return AuthenticationService.decrypt_token(token)
