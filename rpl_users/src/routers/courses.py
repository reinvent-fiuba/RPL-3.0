from typing import Optional
from fastapi import APIRouter, status
from rpl_users.src.deps.auth import CurrentUserDependency
from rpl_users.src.deps.email import EmailHandlerDependency
from rpl_users.src.deps.database import DBSessionDependency
from rpl_users.src.dtos.course_dtos import (
    CurrentCourseUserDTO,
    ExternalCourseUserRequestDTO,
)
from rpl_users.src.dtos.role_dtos import RoleResponseDTO
from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from rpl_users.src.services.courses import CoursesService


router = APIRouter(prefix="/api/v3", tags=["Courses"])


# ==============================================================================


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


@router.get("/auth/externalCourseUserAuth", response_model=CurrentCourseUserDTO)
def course_user_auth_from_activities_api(
    requested_access_info: ExternalCourseUserRequestDTO,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).get_course_user_for_ext_service(
        requested_access_info, current_user
    )
