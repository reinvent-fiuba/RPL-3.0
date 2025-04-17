from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class CurrentCourseUserDTO(BaseModel):
    id: int
    course_id: int
    username: str
    email: EmailStr
    name: str
    surname: str
    student_id: str


class ExternalCourseUserRequestDTO(BaseModel):
    course_id: int
    required_permission: str
