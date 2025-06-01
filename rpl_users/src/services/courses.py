from typing import List, Optional
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
import httpx
from rpl_users.src.config import env
from rpl_users.src.deps.email import EmailHandler
from rpl_users.src.dtos.course_dtos import (
    CourseCreationDTO,
    CourseUptateDTO,
    CourseUserUptateDTO,
    CourseWithUserInformationResponseDTO,
    CourseUserResponseDTO,
)
from rpl_users.src.dtos.role_dtos import RoleResponseDTO
from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from rpl_users.src.dtos.course_dtos import CourseResponseDTO
from rpl_users.src.repositories.course_users import CourseUsersRepository
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.course_user import CourseUser
from rpl_users.src.repositories.models.role import Role
from rpl_users.src.repositories.roles import RolesRepository
from rpl_users.src.repositories.users import UsersRepository
from rpl_users.src.repositories.universities import UniversitiesRepository
from rpl_users.src.repositories.courses import CoursesRepository
from sqlalchemy.orm import Session


class CoursesService:
    def __init__(self, db_session: Session):
        self.activitiesHttpApiClient = httpx.Client(
            base_url=f"{env.ACTIVITIES_API_URL}/api/v3",
        )

        self.users_repo = UsersRepository(db_session)
        self.roles_repo = RolesRepository(db_session)
        self.courses_repo = CoursesRepository(db_session)
        self.course_users_repo = CourseUsersRepository(db_session)
        self.universities_repo = UniversitiesRepository(db_session)

    # ====================== PRIVATE - PERMISSIONS ====================== #

    def _has_course_user_permissions(
        self, course_user: CourseUser, permissions: List[str]
    ) -> bool:
        if course_user.user.is_admin:
            # super admin has all permissions
            return True
        else:
            return all(
                permission in course_user.role.get_permissions()
                for permission in permissions
            )

    # ====================== PRIVATE - ASSERTIONS ====================== #

    def _assert_or_else_raise_http_exception(
        self, assertion: bool, status_code: int, detail: str = ""
    ) -> Course:
        if assertion is False:
            raise HTTPException(status_code, detail)

    def _assert_course_exists(self, course_id: str) -> Course:
        course = self.courses_repo.get_course_with_id(course_id)
        self._assert_or_else_raise_http_exception(
            course is not None,
            status.HTTP_400_BAD_REQUEST,
            "Course not found",
        )
        return course

    def _assert_user_exists(self, user_id: str) -> User:
        user = self.users_repo.get_user_with_id(user_id)
        self._assert_or_else_raise_http_exception(
            user is not None,
            status.HTTP_400_BAD_REQUEST,
            "User not found",
        )
        return user

    def _assert_role_exists(self, role_name: str) -> Role:
        role = self._get_role_named(role_name)
        self._assert_or_else_raise_http_exception(
            role is not None,
            status.HTTP_400_BAD_REQUEST,
            "Role not found",
        )
        return role

    def _assert_course_user_exists_and_has_permissions(
        self, course_id: str, user_id: str, permissions: List[str] = []
    ) -> CourseUser:
        course_user = self.course_users_repo.get_course_user(course_id, user_id)
        self._assert_or_else_raise_http_exception(
            (course_user is not None)
            and self._has_course_user_permissions(course_user, permissions),
            status.HTTP_403_FORBIDDEN,
            "Couser user not found or does not have required permissions",
        )
        return course_user

    # ====================== PRIVATE - MANAGING - COURSES ====================== #

    def _create_course_as_admin(self, course_data: CourseCreationDTO) -> Course:
        user_admin = self.users_repo.get_user_with_id(
            course_data.course_user_admin_user_id
        )
        if user_admin is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        new_course = self.courses_repo.save_new_course(course_data)
        self.course_users_repo.save_new_course_user(
            course_id=new_course.id,
            user_id=user_admin.id,
            role_id=self._get_role_named("course_admin").id,
            accepted=True,
        )

        return new_course

    def _clone_course(
        self,
        course_data: CourseCreationDTO,
        auth_header: HTTPBearer,
    ) -> Course:
        course = self._assert_course_exists(course_data.id)

        course_data.img_uri = course_data.img_uri or course.img_uri
        course_data.description = course_data.description or course.description

        new_course = self._create_course_as_admin(course_data)

        self.activitiesHttpApiClient.post(
            url=f"/courses/{course.id}/activityCategories/clone",
            params={"to_course_id": new_course.id},
            headers={
                "Authorization": f"{auth_header.scheme} {auth_header.credentials}"
            },
        )

        return new_course

    # ====================== MANAGING - COURSES ====================== #

    def create_course(
        self,
        course_data: CourseCreationDTO,
        current_user: User,
        auth_header: HTTPBearer,
    ) -> CourseResponseDTO:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create courses",
            )

        if course_data.id is None:
            new_course = self._create_course_as_admin(course_data)
        else:
            new_course = self._clone_course(course_data, auth_header)

        return CourseResponseDTO.from_course(new_course)

    def update_course(
        self, course_id: str, course_data: CourseUptateDTO, current_user: User
    ) -> CourseResponseDTO:
        self._assert_course_exists(course_id)
        self._assert_course_user_exists_and_has_permissions(
            course_id, current_user.id, ["course_edit"]
        )

        updated_course = self.courses_repo.update_course(course_id, course_data)

        return CourseResponseDTO.from_course(updated_course)

    # ====================== QUERYING - COURSES ====================== #

    def get_all_courses_including_their_relationship_with_user(
        self, current_user: User
    ) -> List[CourseWithUserInformationResponseDTO]:
        courses_with_user_info = []
        for course in self.courses_repo.get_all_courses():
            course_user = self.course_users_repo.get_course_user(
                course.id,
                current_user.id,
            )
            if course_user:
                courses_with_user_info.append(
                    CourseWithUserInformationResponseDTO.from_course_and_user_info(
                        course, True, course_user.accepted
                    )
                )
            else:
                courses_with_user_info.append(
                    CourseWithUserInformationResponseDTO.from_course_and_user_info(
                        course, False, False
                    )
                )
        return courses_with_user_info

    def get_course_details(
        self, course_id: str, current_user: User
    ) -> CourseResponseDTO:
        course = self._assert_course_exists(course_id)
        self._assert_course_user_exists_and_has_permissions(
            course_id, current_user.id, ["course_view"]
        )

        return CourseResponseDTO.from_course(course)

    # ====================== MANAGING - COURSE USERS ====================== #

    def enroll_student_in_course(
        self, course_id: str, current_user: User
    ) -> RoleResponseDTO:
        self._assert_course_exists(course_id)

        new_course_user = self.course_users_repo.save_new_course_user(
            course_id=course_id,
            user_id=current_user.id,
            role_id=self._get_role_named("student").id,
            accepted=False,
        )

        return RoleResponseDTO.from_course_user(new_course_user)

    def update_course_user(
        self,
        course_id: str,
        user_id: str,
        course_data: CourseUserUptateDTO,
        current_user: User,
        email_handler: EmailHandler,
    ) -> CourseUserResponseDTO:
        self._assert_user_exists(user_id)
        self._assert_course_exists(course_id)
        role = self._assert_role_exists(course_data.role)
        self._assert_course_user_exists_and_has_permissions(
            course_id, current_user.id, ["user_manage"]
        )
        course_user = self._assert_course_user_exists_and_has_permissions(
            course_id, user_id
        )

        self.course_users_repo.update_course_user(
            course_id,
            user_id,
            role.id,
            course_data.accepted,
        )

        if course_data.accepted:
            email_handler.send_course_acceptance_email(
                course_user.user.email,
                course_user.user,
                course_user.course,
            )

        return CourseUserResponseDTO.from_course_user(course_user)

    def unenroll_course_user(self, course_id: str, current_user: User):
        self._assert_course_exists(course_id)
        self._assert_course_user_exists_and_has_permissions(course_id, current_user.id)

        self.course_users_repo.delete_course_user(
            course_id=course_id,
            user_id=current_user.id,
        )

    def delete_course_user(self, course_id: str, user_id: str, current_user: User):
        self._assert_user_exists(user_id)
        self._assert_course_exists(course_id)
        self._assert_course_user_exists_and_has_permissions(
            course_id, current_user.id, ["user_manage"]
        )
        self._assert_course_user_exists_and_has_permissions(course_id, user_id)

        self.course_users_repo.delete_course_user(
            course_id=course_id,
            user_id=user_id,
        )

    # ====================== QUERYING - COURSE USERS ====================== #

    def get_user_permissions(self, course_id: str, current_user: User) -> List[str]:
        self._assert_course_exists(course_id)
        course_user = self._assert_course_user_exists_and_has_permissions(
            course_id, current_user.id, []
        )

        return course_user.get_permissions()

    def get_all_course_users_from_course(
        self,
        course_id: str,
        current_user: User,
        role_name: Optional[str],
        student_id: Optional[str],
    ) -> List[CourseUserResponseDTO]:
        self._assert_course_exists(course_id)
        self._assert_course_user_exists_and_has_permissions(
            course_id, current_user.id, ["user_view"]
        )

        course_users = self.course_users_repo.get_course_users(course_id)

        if role_name is not None:
            course_users = [
                course_user
                for course_user in course_users
                if course_user.role.name == role_name
            ]
        if student_id is not None:
            course_users = [
                course_user
                for course_user in course_users
                if course_user.user.student_id == student_id
            ]

        return [
            CourseUserResponseDTO.from_course_user(course_user)
            for course_user in course_users
        ]

    def get_all_courses_from_user(
        self, user_id: str, current_user: User
    ) -> List[CourseResponseDTO]:
        self._assert_user_exists(user_id)
        self._assert_or_else_raise_http_exception(
            user_id == str(current_user.id),
            status.HTTP_403_FORBIDDEN,
            "User can only view its own courses",
        )

        return [
            CourseResponseDTO.from_course(course)
            for course in self.courses_repo.get_all_courses_from_user(user_id)
        ]

    # ====================== PRIVATE - QUERYING - ROLES ====================== #

    def _get_role_named(self, role_name: str) -> Role:
        return self.roles_repo.get_role_named(role_name)

    # ====================== QUERYING - ROLES ====================== #

    def get_all_roles(self) -> List[RoleResponseDTO]:
        return [
            RoleResponseDTO.from_role(role) for role in self.roles_repo.get_all_roles()
        ]

    # ====================== QUERYING - UNIVERSITIES ====================== #

    def get_all_universities(self) -> List[UniversityResponseDTO]:
        return [
            UniversityResponseDTO.from_university(university)
            for university in self.universities_repo.get_all_universities()
        ]

    # ====================== QUERYING - EXTERNAL COURSE USER AUTH ====================== #

    def get_course_user_for_ext_service(
        self, course_id, current_user: User
    ) -> CourseUserResponseDTO:
        course_user = self._assert_course_user_exists_and_has_permissions(
            course_id,
            current_user.id,
        )

        return CourseUserResponseDTO.from_course_user(course_user)
