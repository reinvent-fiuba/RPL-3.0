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
    semester_start_date: str
    semester_end_date: str
    img_uri: Optional[str]
    date_created: datetime
    last_updated: datetime
    enrolled: bool = False
    accepted: bool = False
