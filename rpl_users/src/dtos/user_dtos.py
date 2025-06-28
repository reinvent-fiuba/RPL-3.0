from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreationDTO(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=5)
    name: str
    surname: str
    student_id: str
    degree: str
    university: str


class UserCreationResponseDTO(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str
    surname: str
    student_id: str
    degree: str
    university: str
    img_uri: Optional[str] = None


class UserLoginDTO(BaseModel):
    username_or_email: str
    password: str


class UserLoginResponseDTO(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class UserProfileResponseDTO(BaseModel):
    id: int
    username: str
    name: str
    surname: str
    email: EmailStr
    is_admin: bool
    student_id: str
    degree: str
    university: str
    img_uri: Optional[str] = None


class UserProfileUpdateDTO(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    student_id: Optional[str] = None
    degree: Optional[str] = None
    university: Optional[str] = None
    img_uri: Optional[str] = None


class UserEmailValidationDTO(BaseModel):
    token: str


class ResendEmailValidationDTO(BaseModel):
    username_or_email: str


class UserForgotPasswordDTO(BaseModel):
    email: EmailStr


class UserPasswordResetDTO(BaseModel):
    token: str
    new_password: str = Field(min_length=5)


class FindUsersResponseDTO(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str
    surname: str
    student_id: str
    degree: str
    university: str


class CurrentMainUserResponseDTO(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str
    surname: str
    student_id: str
    degree: str
    university: str
    is_admin: bool
