from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import datetime


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

class CourseResponseDTO(BaseModel):
    id: int
    name: str
    university: str
    subject_id: Optional[str]
    description: Optional[str]
    active: bool
    semester: str
    semester_start_date: datetime.datetime
    semester_end_date: datetime.datetime
    img_uri: Optional[str]
    enrolled: bool = False
    accepted: bool = False
