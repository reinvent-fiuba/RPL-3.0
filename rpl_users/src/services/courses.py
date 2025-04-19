from fastapi import HTTPException, status
from rpl_users.src.dtos.course_dtos import (
    CurrentCourseUserResponseDTO,
)
from rpl_users.src.dtos.role_dtos import RoleResponseDTO
from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from rpl_users.src.repositories.course_users import CourseUsersRepository
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.roles import RolesRepository
from rpl_users.src.repositories.universities import UniversitiesRepository
from sqlalchemy.orm import Session


class CoursesService:
    def __init__(self, db_session: Session):
        # self.users_repo = UsersRepository(db_session)
        # self.courses_repo = CoursesRepository(db_session)
        self.course_users_repo = CourseUsersRepository(db_session)
        self.roles_repo = RolesRepository(db_session)
        self.universities_repo = UniversitiesRepository(db_session)

    # =============================================================================

    # def __

    # =============================================================================

    def get_roles(self) -> list[RoleResponseDTO]:
        return self.roles_repo.get_all()

    def get_universities(self) -> list[UniversityResponseDTO]:
        return self.universities_repo.get_all()

    # =============================================================================

    def get_course_user_for_ext_service(
        self, course_id, current_user: User
    ) -> CurrentCourseUserResponseDTO:
        course_user = self.course_users_repo.get_by_course_id_and_user_id(
            course_id, current_user.id
        )
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
