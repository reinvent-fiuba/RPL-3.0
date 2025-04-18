from fastapi import HTTPException, status
from rpl_users.src.dtos.course_dtos import (
    CourseCreationDTO,
    CurrentCourseUserDTO,
    ExternalCourseUserRequestDTO,
)
from rpl_users.src.dtos.role_dtos import RoleResponseDTO
from rpl_users.src.dtos.university_dtos import UniversityResponseDTO
from rpl_users.src.dtos.course_dtos import CourseResponseDTO
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

    def get_courses_for_user(self, current_user: User) -> list[CourseResponseDTO]:
        course_users = self.course_users_repo.get_course_users_by_user_id(
            current_user.id
        )
        # courses = self.courses_repo.get_all_courses_dict()
        # for courses_user in course_users:
        #     enrolled_course_id = courses.get(courses_user.course_id)
        #     courses[enrolled_course_id].enrolled = True
        #     courses[enrolled_course_id].accepted = courses_user.accepted
        # return courses.values()
        return []

    def create_course(
        self, course_data: CourseCreationDTO, current_user: User
    ) -> CourseResponseDTO:
        # if current_user.is_admin is not True:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Only admins can create courses",
        #     )

        # admin_role = self.roles_repo.get_by_name("course_admin")

        # course_exists = (
        #     self.course_users_repo.exists_course_by_name_subject_id_semester_and_admin(
        #         name=course_data.name,
        #         subject_id=course_data.subject_id,
        #         semester=course_data.semester,
        #         admin_id=current_user.id,
        #     )
        # )

        # if course_exists:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Course already exists",
        #     )

        # course = self.courses_repo.create_course(
        #     course_data=course_data,
        #     current_user=current_user,
        # )
        # if not course:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Course creation failed",
        #     )
        # # Assign the admin role to the course
        # course_user = self.course_users_repo.create_course_user(
        #     course_id=course.id,
        #     user_id=current_user.id,
        #     role_id=admin_role.id,
        #     accepted=True,
        # )
        # if not course_user:
        #     # TODO: remove course if course_user creation fails
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Course user creation failed",
        #     )

        # return CourseResponseDTO(
        #     id=course.id,
        #     name=course.name,
        #     university=course.university,
        #     subject_id=course.subject_id,
        #     description=course.description,
        #     active=course.active,
        #     semester=course.semester,
        #     semester_start_date=course.semester_start_date,
        #     semester_end_date=course.semester_end_date,
        #     img_uri=course.img_uri,
        #     enrolled=True,
        #     accepted=True,
        # )

    # =============================================================================

    def get_roles(self) -> list[RoleResponseDTO]:
        return self.roles_repo.get_all()

    def get_universities(self) -> list[UniversityResponseDTO]:
        return self.universities_repo.get_all()

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
