from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class CurrentCourseUserResponseDTO(BaseModel):
    id: int
    course_id: int
    username: str
    email: EmailStr
    name: str
    surname: str
    student_id: str
    permissions: list[str]
