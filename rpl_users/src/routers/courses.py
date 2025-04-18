from typing import Optional
from fastapi import APIRouter, status
from rpl_users.src.deps.auth import CurrentUserDependency
from rpl_users.src.deps.email import EmailHandlerDependency
from rpl_users.src.deps.database import DBSessionDependency
from rpl_users.src.dtos.course_dtos import (
    CourseCreationResponseDTO,
    CurrentCourseUserDTO,
    ExternalCourseUserRequestDTO,
    CourseCreationDTO,
)
from rpl_users.src.dtos.role_dtos import RoleResponseDTO
from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from rpl_users.src.services.courses import CoursesService


router = APIRouter(prefix="/api/v3", tags=["Courses"])


# ==============================================================================


@router.post(
    "/courses",
    response_model=CourseCreationResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_course(
    course_data: CourseCreationDTO,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).create_course(course_data, current_user)


# ==============================================================================


@router.get("/auth/roles", response_model=list[RoleResponseDTO])
def get_roles(
    db: DBSessionDependency,
):
    return CoursesService(db).get_roles()


@router.get("/auth/universities", response_model=list[UniversityResponseDTO])
def get_universities(
    db: DBSessionDependency,
):
    return CoursesService(db).get_universities()


# ==============================================================================


@router.post("/courses/{course_id}/enroll", response_model=RoleResponseDTO)
def enroll_user_in_course(
    course_id: str,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    print(f"Enrolling user {current_user.id} in course {course_id}")
    return CoursesService(db).enroll_user_in_course(course_id, current_user)


# ==============================================================================


@router.post("/auth/externalCourseUserAuth", response_model=CurrentCourseUserDTO)
def course_user_auth_from_activities_api(
    requested_access_info: ExternalCourseUserRequestDTO,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).get_course_user_for_ext_service(
        requested_access_info, current_user
    )
