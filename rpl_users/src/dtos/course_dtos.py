from pydantic import BaseModel, Field, EmailStr
from typing import Optional

from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.course_user import CourseUser

import datetime

# ====================== REQUESTS ====================== #


class CourseCreationRequestDTO(BaseModel):
    id: Optional[int] = None
    name: str
    university: str
    subject_id: str
    description: Optional[str] = None
    semester: str
    semester_start_date: datetime.date
    semester_end_date: datetime.date
    img_uri: Optional[str] = None
    course_admin_user_id: int


class CourseUptateRequestDTO(BaseModel):
    name: str
    university: str
    subject_id: str
    description: Optional[str] = None
    active: Optional[bool] = True
    semester: str
    semester_start_date: datetime.date
    semester_end_date: datetime.date
    img_uri: Optional[str] = None


class CourseUserUptateRequestDTO(BaseModel):
    accepted: Optional[bool] = None
    role: Optional[str] = None


# ====================== RESPONSES ====================== #


class CourseUserScoreResponseDTO(BaseModel):
    name: str
    surname: str
    img_uri: str
    total_score: int
    successful_activities_count: int


class CourseResponseDTO(BaseModel):
    id: int
    name: str
    university: str
    subject_id: Optional[str] = None
    description: Optional[str] = None
    active: bool
    semester: str
    semester_start_date: datetime.date
    semester_end_date: datetime.date
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
            semester_start_date=course.semester_start_date.date(),
            semester_end_date=course.semester_end_date.date(),
            img_uri=course.img_uri,
        )


class CourseWithUserInformationResponseDTO(BaseModel):
    id: int
    name: str
    university: str
    subject_id: Optional[str] = None
    description: Optional[str] = None
    active: bool
    semester: str
    semester_start_date: datetime.date
    semester_end_date: datetime.date
    img_uri: Optional[str] = None
    # user info
    enrolled: bool
    accepted: bool

    @classmethod
    def from_course_and_user_info(
        cls, course: "Course", enrolled: "bool", accepted: "bool"
    ) -> "CourseWithUserInformationResponseDTO":
        return cls(
            id=course.id,
            name=course.name,
            university=course.university,
            subject_id=course.subject_id,
            description=course.description,
            active=course.active,
            semester=course.semester,
            semester_start_date=course.semester_start_date.date(),
            semester_end_date=course.semester_end_date.date(),
            img_uri=course.img_uri,
            enrolled=enrolled,
            accepted=accepted,
        )


class CourseUserResponseDTO(BaseModel):
    id: int
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

    @classmethod
    def from_course_user(cls, course_user: "CourseUser") -> "CourseUserResponseDTO":
        return cls(
            id=course_user.user.id,
            course_id=course_user.course.id,
            course_user_id=course_user.id,
            name=course_user.user.name,
            surname=course_user.user.surname,
            student_id=course_user.user.student_id,
            username=course_user.user.username,
            email=course_user.user.email,
            email_validated=course_user.user.email_validated,
            university=course_user.user.university,
            degree=course_user.user.degree,
            role=course_user.role.name,
            permissions=course_user.get_permissions(),
            accepted=course_user.accepted,
            date_created=(course_user.date_created - datetime.timedelta(hours=3)),
            last_updated=(course_user.last_updated - datetime.timedelta(hours=3)),
        )
