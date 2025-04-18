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


class CourseCreationResponseDTO(BaseModel):
    id: int
    name: str
    university: str
    subject_id: Optional[str] = None
    description: Optional[str] = None
    active: bool
    semester: str
    semester_start_date: datetime.datetime
    semester_end_date: datetime.datetime
    img_uri: Optional[str] = None
    # enrolled: bool = False
    # accepted: bool = False


class CourseCreationDTO(BaseModel):
    name: str
    university: str
    subject_id: str
    description: Optional[str] = None
    active: bool
    semester: str
    semester_start_date: datetime.datetime
    semester_end_date: datetime.datetime
    img_uri: Optional[str] = None
    course_user_admin_user_id: int
