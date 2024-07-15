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
    """
    Service layer for managing authentication and authorization.

    Attributes:
        employee_repo (EmployeeRepository): Repository for employee operations.
    """
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo
    
    def create_access_token(self,data: dict) -> dict:
        """
        Create an access token for authentication.

        Args:
            data (dict): The data to encode in the token, typically including the username.

        Returns:
            dict: A dictionary containing the access token and its type.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, configs.SECRET_KEY, algorithm=configs.ALGORITHM)
        return {"access_token": encoded_jwt, "token_type": "bearer"}

    def verify_token(self,token: str, credentials_exception: HTTPException):
        """
        Verify the provided JWT token.

        Args:
            token (str): The JWT token to verify.
            credentials_exception (HTTPException): The exception to raise if verification fails.

        Returns:
            TokenData: The decoded token data containing the username.

        Raises:
            HTTPException: If the token is invalid or expired.
        """
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
        """
        Check the strength of a password.

        Args:
            password (str): The password to check.

        Returns:
            tuple: A tuple containing a boolean indicating if the password is strong and a message.
        """
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
        """
        Encrypt a password using bcrypt.

        Args:
            password (str): The password to encrypt.

        Returns:
            str: The hashed password.
        """
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hashed password.

        Args:
            password (str): The plaintext password.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the passwords match, otherwise False.
        """
        try:
            return bcrypt.checkpw(password.encode(), hashed_password.encode())
        except:
            return False

    @staticmethod
    def decrypt_token(token: str) -> dict:
        """
        Decrypt a JWT token to extract its payload.

        Args:
            token (str): The JWT token to decrypt.

        Returns:
            dict: The extracted token data.

        Raises:
            HTTPException: If the token is invalid or the user is not found.
        """
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
        """
        Retrieve the current user based on the provided credentials.

        Args:
            credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials containing the token.

        Returns:
            TokenData: The token data of the current user.
        """
        token = credentials.credentials
        return AuthenticationService.decrypt_token(token)
