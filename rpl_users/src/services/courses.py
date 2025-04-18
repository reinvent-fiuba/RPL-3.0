from pkgutil import get_data
from fastapi import HTTPException, status
from rpl_users.src.dtos.course_dtos import (
    CourseCreationDTO,
    CurrentCourseUserDTO,
    ExternalCourseUserRequestDTO,
)
from rpl_users.src.dtos.role_dtos import RoleResponseDTO
from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from rpl_users.src.dtos.course_dtos import CourseCreationResponseDTO
from rpl_users.src.repositories.course_users import CourseUsersRepository
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.role import Role
from rpl_users.src.repositories.roles import RolesRepository
from rpl_users.src.repositories.users import UsersRepository
from rpl_users.src.repositories.universities import UniversitiesRepository
from rpl_users.src.repositories.courses import CoursesRepository
from sqlalchemy.orm import Session


class CoursesService:
    def __init__(self, db_session: Session):
        self.users_repo = UsersRepository(db_session)
        self.course_users_repo = CourseUsersRepository(db_session)
        self.roles_repo = RolesRepository(db_session)
        self.universities_repo = UniversitiesRepository(db_session)
        self.courses_repo = CoursesRepository(db_session)

    # =============================================================================

    def create_course(
        self, course_data: CourseCreationDTO, current_user: User
    ) -> CourseCreationResponseDTO:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only admins can create courses",
            )

        course_user_admin = self.users_repo.get_by_id(
            course_data.course_user_admin_user_id
        )
        if course_user_admin is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        new_course = self.courses_repo.save_new_course(course_data)

        return CourseCreationResponseDTO(
            id=new_course.id,
            name=new_course.name,
            university=new_course.university,
            subject_id=new_course.subject_id,
            description=new_course.description,
            active=new_course.active,
            semester=new_course.semester,
            semester_start_date=new_course.semester_start_date,
            semester_end_date=new_course.semester_end_date,
            img_uri=new_course.img_uri,
        )

    # =============================================================================

    def get_roles(self) -> list[RoleResponseDTO]:
        return self.roles_repo.get_all()

    def get_universities(self) -> list[UniversityResponseDTO]:
        return self.universities_repo.get_all()

    # =============================================================================

    def enroll_user_in_course(
        self, course_id: str, current_user: User
    ) -> RoleResponseDTO:
        course_user = self.course_users_repo.get_by_course_id_and_user_id(
            course_id, current_user.id
        )
        if course_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already enrolled in the course",
            )

        course = self.courses_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )

        role = self.roles_repo.get_by_name("student")
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        new_course_user = self.course_users_repo.create_course_user(
            course_id=course.id,
            user_id=current_user.id,
            role_id=role.id,
        )

        return RoleResponseDTO(
            id=new_course_user.role.id,
            name=new_course_user.role.name,
            permissions=new_course_user.role.get_permissions(),
        )

    # =============================================================================

    def get_course_user_for_ext_service(
        self, requested_access_info: ExternalCourseUserRequestDTO, current_user: User
    ) -> CurrentCourseUserDTO:
        course_user = self.course_users_repo.get_by_course_id_and_user_id(
            requested_access_info.course_id, current_user.id
        )
        if not course_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course user not found"
            )
        if (
            requested_access_info.required_permission
            not in course_user.role.permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have the required permission",
            )

        return CurrentCourseUserDTO(
            id=course_user.id,
            course_id=course_user.course_id,
            username=current_user.username,
            email=current_user.email,
            name=current_user.name,
            surname=current_user.surname,
            student_id=current_user.student_id,
        )
