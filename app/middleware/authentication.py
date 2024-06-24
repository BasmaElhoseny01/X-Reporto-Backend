# utils/auth.py
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.schemas.authentication import TokenData
from app.dependencies import get_employee_repository 
from app.repository.employee import EmployeeRepository

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def decrypt_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("payload", payload)
        username = payload.get("username",None)
        if username is None:
            raise  HTTPException(status_code=401, detail=f"Unauthorized, user not found")
        token_data = TokenData(**payload)
    except JWTError:
        print("error")
        raise HTTPException(status_code=401, detail=f"Unauthorized, token invalid")
    return token_data

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), employee_repo: EmployeeRepository = Depends(get_employee_repository)):
    token = credentials.credentials
    user =  decrypt_token(token)

    employee = employee_repo.show(user.id)
    user.role = employee.role
    if employee is None:
        raise HTTPException(status_code=401, detail="Employee not found")
    return user

