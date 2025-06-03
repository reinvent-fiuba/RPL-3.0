from typing import List, Optional
from fastapi import APIRouter, status
from rpl_activities.src.deps.auth import AuthDependency
from rpl_users.src.deps.auth import CurrentUserDependency
from rpl_users.src.deps.database import DBSessionDependency
from rpl_users.src.deps.email import EmailHandlerDependency
from rpl_users.src.dtos.course_dtos import (
    CourseCreationDTO,
    CourseUptateDTO,
    CourseUserUptateDTO,
    CourseResponseDTO,
    CourseWithUserInformationResponseDTO,
    CourseUserResponseDTO,
)
from rpl_users.src.dtos.role_dtos import RoleResponseDTO
from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from rpl_users.src.services.courses import CoursesService


router = APIRouter(prefix="/api/v3", tags=["Courses"])


# ====================== MANAGING - COURSES ====================== #


@router.post(
    "/courses",
    response_model=CourseResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_course(
    course_data: CourseCreationDTO,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
    auth_header: AuthDependency,
):
    return CoursesService(db).create_course(course_data, current_user, auth_header)


@router.put(
    "/courses/{course_id}",
    response_model=CourseResponseDTO,
)
def update_course(
    course_id: str,
    course_data: CourseUptateDTO,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).update_course(course_id, course_data, current_user)


# ====================== QUERYING - COURSES ====================== #


@router.get(
    "/courses",
    response_model=List[CourseWithUserInformationResponseDTO],
)
def get_all_courses_including_their_relationship_with_user(
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).get_all_courses_including_their_relationship_with_user(current_user)


@router.get(
    "/courses/{course_id}",
    response_model=CourseResponseDTO,
)
def get_course_details(
    course_id: str,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).get_course_details(course_id, current_user)


# ====================== MANAGING - COURSE USERS ====================== #


@router.post(
    "/courses/{course_id}/enroll",
    response_model=RoleResponseDTO,
)
def enroll_student_in_course(
    course_id: str,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).enroll_student_in_course(course_id, current_user)


@router.patch(
    "/courses/{course_id}/users/{user_id}",
    response_model=CourseUserResponseDTO,
)
def update_course_user(
    course_id: str,
    user_id: str,
    course_data: CourseUserUptateDTO,
    current_user: CurrentUserDependency,
    email_handler: EmailHandlerDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).update_course_user(course_id, user_id, course_data, current_user, email_handler)


@router.post(
    "/courses/{course_id}/unenroll",
    status_code=status.HTTP_204_NO_CONTENT,
)
def unenroll_course_user(
    course_id: str,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    CoursesService(db).unenroll_course_user(course_id, current_user)


@router.delete(
    "/courses/{course_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_course_user(
    course_id: str,
    user_id: str,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    CoursesService(db).delete_course_user(course_id, user_id, current_user)


# ====================== QUERYING - COURSE USERS ====================== #


@router.get(
    "/courses/{course_id}/permissions",
    response_model=List[str],
)
def get_user_permissions(
    course_id: str,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).get_user_permissions(course_id, current_user)


@router.get(
    "/courses/{course_id}/users",
    response_model=List[CourseUserResponseDTO],
)
def get_all_course_users_from_course(
    course_id: str,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
    role_name: Optional[str] = None,
    student_id: Optional[str] = None,
):
    return CoursesService(db).get_all_course_users_from_course(course_id, current_user, role_name, student_id)


@router.get(
    "/users/{user_id}/courses",
    response_model=List[CourseResponseDTO],
)
def get_all_courses_from_user(
    user_id: str,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).get_all_courses_from_user(user_id, current_user)


# ====================== QUERYING - ROLES ====================== #


@router.get(
    "/auth/roles",
    response_model=List[RoleResponseDTO],
)
def get_all_roles(
    db: DBSessionDependency,
):
    return CoursesService(db).get_all_roles()


# ====================== QUERYING - UNIVERSITIES ====================== #


@router.get(
    "/auth/universities",
    response_model=List[UniversityResponseDTO],
)
def get_all_universities(
    db: DBSessionDependency,
):
    return CoursesService(db).get_all_universities()


# ====================== QUERYING - EXTERNAL COURSE USER AUTH ====================== #


@router.get(
    "/auth/externalCourseUserAuth",
    response_model=CourseUserResponseDTO,
)
def course_user_auth_from_activities_api(
    course_id: int,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    return CoursesService(db).get_course_user_for_ext_service(course_id, current_user)
