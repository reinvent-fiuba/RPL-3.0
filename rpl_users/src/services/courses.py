import logging
from pkgutil import get_data
from fastapi import HTTPException, status
from rpl_users.src.dtos.course_dtos import (
    CurrentCourseUserResponseDTO,
    CourseCreationDTO,
    CourseUptateDTO,
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
        self.users_repo = UsersRepository(db_session)
        self.roles_repo = RolesRepository(db_session)
        self.courses_repo = CoursesRepository(db_session)
        self.course_users_repo = CourseUsersRepository(db_session)
        self.universities_repo = UniversitiesRepository(db_session)

    # ====================== PRIVATE - PERMISSIONS ====================== #

    def _has_course_user_permission(
        self, course_user: CourseUser, permission: str
    ) -> bool:
        if course_user.user.is_admin:
            # super admin has all permissions
            return True
        else:
            return permission in course_user.role.permissions.split(",")

    # ====================== MANAGING - COURSES ====================== #

    def create_course(
        self, course_data: CourseCreationDTO, current_user: User
    ) -> CourseResponseDTO:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only admins can create courses",
            )

        user_admin = self.users_repo.get_by_id(course_data.course_user_admin_user_id)
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

        return CourseResponseDTO.from_course(new_course)

    def update_course(
        self, course_id: str, course_data: CourseUptateDTO, current_user: User
    ) -> CourseResponseDTO:

        course_user = self.course_users_repo.get_course_user(course_id, current_user.id)
        if not course_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course user not found",
            )

        if not self._has_course_user_permission(course_user, "course_edit"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not have permission to edit the course",
            )

        updated_course = self.courses_repo.update_course(course_id, course_data)

        return CourseResponseDTO.from_course(updated_course)

    # ====================== QUERYING - COURSES ====================== #

    def get_all_courses_including_their_relationship_with_user(
        self, current_user: User
    ) -> list[CourseUserResponseDTO]:
        courses_with_user_info = []
        for course in self.courses_repo.get_all_courses():
            course_user = self.course_users_repo.get_course_user(
                course.id,
                current_user.id,
            )
            if course_user:
                courses_with_user_info.append(
                    CourseUserResponseDTO.from_course_and_user_info(
                        course, True, course_user.accepted
                    )
                )
            else:
                courses_with_user_info.append(
                    CourseUserResponseDTO.from_course_and_user_info(
                        course, False, False
                    )
                )
        return courses_with_user_info

    def get_course_details(
        self, course_id: str, current_user: User
    ) -> CourseResponseDTO:
        course = self.courses_repo.get_course_with_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found"
            )

        course_user = self.course_users_repo.get_course_user(course_id, current_user.id)
        if (not course_user) or (
            not self._has_course_user_permission(course_user, "course_view")
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to view course details",
            )

        return CourseResponseDTO.from_course(course)

    # ====================== MANAGING - COURSE USERS ====================== #

    def enroll_student_in_course(
        self, course_id: str, current_user: User
    ) -> RoleResponseDTO:
        course = self.courses_repo.get_course_with_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found"
            )

        new_course_user = self.course_users_repo.save_new_course_user(
            course_id=course_id,
            user_id=current_user.id,
            role_id=self._get_role_named("student").id,
            accepted=False,
        )

        return RoleResponseDTO.from_course_user(new_course_user)

    # ====================== QUERYING - COURSE USERS ====================== #

    def get_course_user_for_ext_service(
        self, course_id, current_user: User
    ) -> CurrentCourseUserResponseDTO:
        course_user = self.course_users_repo.get_course_user(course_id, current_user.id)
        if not course_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course user not found"
            )

        current_perms = course_user.role.permissions.split(",")
        current_perms = [perm.strip() for perm in current_perms]
        if course_user.role.name == "admin":
            current_perms.append("superadmin")
        return CurrentCourseUserResponseDTO(
            id=course_user.id,
            course_id=course_user.course_id,
            username=current_user.username,
            email=current_user.email,
            name=current_user.name,
            surname=current_user.surname,
            student_id=current_user.student_id,
            permissions=current_perms,
        )

    # ====================== PRIVATE - QUERYING - ROLES ====================== #

    def _get_role_named(self, role_name: str) -> list[RoleResponseDTO]:
        return self.roles_repo.get_role_named(role_name)

    # ====================== QUERYING - ROLES ====================== #

    def get_all_roles(self) -> list[RoleResponseDTO]:
        return [
            RoleResponseDTO.from_role(role) for role in self.roles_repo.get_all_roles()
        ]

    # ====================== QUERYING - UNIVERSITIES ====================== #

    def get_all_universities(self) -> list[UniversityResponseDTO]:
        return [
            UniversityResponseDTO.from_university(university)
            for university in self.universities_repo.get_all_universities()
        ]
