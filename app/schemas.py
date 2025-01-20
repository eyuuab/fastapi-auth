from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)

class UserCreate(UserBase):
    password: constr(min_length=8, max_length=50)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: Optional[constr(min_length=3, max_length=50)] = None
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: constr(min_length=8, max_length=50)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class PasswordReset(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: constr(min_length=8, max_length=50)