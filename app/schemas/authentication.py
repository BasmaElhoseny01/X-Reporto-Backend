from pydantic import BaseModel
from typing import Optional
from app.models.enums import GenderEnum, RoleEnum

class SignUp(BaseModel):
    username: str
    password: str
    role:  Optional[str] = RoleEnum.user
    email: str

class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    id: Optional[int] = None
    type: Optional[str] = None


