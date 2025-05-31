from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx

from rpl_activities.src.dtos.auth_dtos import (
    CourseUserResponseDTO,
)


# Dependencies =============================

auth_handler = HTTPBearer()
AuthDependency = Annotated[HTTPAuthorizationCredentials, Depends(auth_handler)]

# ==========================================


class CurrentCourseUser:
    def __init__(self, user_data: CourseUserResponseDTO):
        self.id = user_data.course_user_id
        self.user_id = user_data.user_id
        self.course_id = user_data.course_id
        self.username = user_data.username
        self.email = user_data.email
        self.name = user_data.name
        self.surname = user_data.surname
        self.student_id = user_data.student_id
        self.permissions = user_data.permissions

    def has_authority(self, authority: str) -> bool:
        return authority in self.permissions


def __basic_path_param_checks(course_id: str) -> int:
    # Note: done due to direct usage of raw request. The proper handling is also done at router level, this is just an extra precaution.
    if not course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID is required in the path parameters.",
        )
    try:
        course_id = int(course_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be an integer.",
        )
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be a positive integer.",
        )
    return course_id


async def get_current_course_user(
    auth_header: AuthDependency, request: Request
) -> CurrentCourseUser:
    users_api_client: httpx.AsyncClient = request.state.users_api_client
    course_id = __basic_path_param_checks(request.path_params.get("course_id"))

    res = await users_api_client.get(
        "/api/v3/auth/externalCourseUserAuth",
        headers={"Authorization": f"{auth_header.scheme} {auth_header.credentials}"},
        params={"course_id": course_id},
    )
    if res.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=res.status_code,
            detail=f"Failed to authenticate current course user: {res.text}",
        )
    user_data = CourseUserResponseDTO(**res.json())
    return CurrentCourseUser(user_data)


CurrentCourseUserDependency = Annotated[
    CurrentCourseUser,
    Depends(get_current_course_user),
]

# ==========================================

# class StudentCourseUser:
#     def __init__(self, user_data: CourseUserResponseDTO):
#         self.id = user_data.course_user_id
#         self.user_id = user_data.user_id
#         self.course_id = user_data.course_id
#         self.username = user_data.username
#         self.student_id = user_data.student_id
#         self.permissions = user_data.permissions

# async def get_student_course_user_for_current_user(
#     auth_header: AuthDependency, request: Request
# ) -> StudentCourseUser:
    