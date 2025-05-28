import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class ExternalCurrentMainUserDTO(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str
    surname: str
    student_id: str
    degree: str
    university: str
    is_admin: bool
    img_uri: Optional[str] = None


class CourseUserResponseDTO(BaseModel):
    user_id: int
    course_id: int
    course_user_id: int
    name: str
    surname: str
    student_id: str
    username: str
    email: EmailStr
    email_validated: bool
    university: str
    degree: str
    role: str
    permissions: list[str]
    accepted: bool
    date_created: datetime.datetime
    last_updated: datetime.datetime
