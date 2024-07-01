# utils/auth.py
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.schemas.authentication import TokenData
from app.dependencies import get_employee_repository 
from app.repository.employee import EmployeeRepository
from app.core.config import configs

security = HTTPBearer()

def decrypt_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
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
    user.type = employee.type
    if user.role != employee.role:
        raise HTTPException(status_code=401, detail="Unauthorized, user role does not match")

    if employee is None:
        raise HTTPException(status_code=401, detail="Employee not found")
    return user

