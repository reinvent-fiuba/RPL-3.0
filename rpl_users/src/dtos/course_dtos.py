from pydantic import BaseModel, Field, EmailStr
from typing import Optional

from rpl_users.src.repositories.models.course import Course

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


# ====================== REQUESTS ====================== #


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


class CourseUptateDTO(BaseModel):
    name: str
    university: str
    subject_id: str
    description: Optional[str] = None
    active: bool
    semester: str
    semester_start_date: datetime.datetime
    semester_end_date: datetime.datetime
    img_uri: Optional[str] = None


# ====================== RESPONSES ====================== #


class CourseResponseDTO(BaseModel):
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

    @classmethod
    def from_course(cls, course: "Course") -> "CourseResponseDTO":
        return cls(
            id=course.id,
            name=course.name,
            university=course.university,
            subject_id=course.subject_id,
            description=course.description,
            active=course.active,
            semester=course.semester,
            semester_start_date=course.semester_start_date,
            semester_end_date=course.semester_end_date,
            img_uri=course.img_uri,
        )


class CourseUserResponseDTO(BaseModel):
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
    # user info
    enrolled: bool
    accepted: bool

    @classmethod
    def from_course_and_user_info(
        cls,
        course: "Course",
        enrolled: "bool",
        accepted: "bool",
    ) -> "CourseResponseDTO":
        return cls(
            id=course.id,
            name=course.name,
            university=course.university,
            subject_id=course.subject_id,
            description=course.description,
            active=course.active,
            semester=course.semester,
            semester_start_date=course.semester_start_date,
            semester_end_date=course.semester_end_date,
            img_uri=course.img_uri,
            enrolled=enrolled,
            accepted=accepted,
        )
