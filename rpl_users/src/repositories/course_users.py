from .base import BaseRepository

from .models.course_user import CourseUser
from .models.course import Course
import sqlalchemy as sa


class CourseUsersRepository(BaseRepository):

    # ====================== MANAGING ====================== #

    def save_new_course_user(
        self,
        course_id: int,
        user_id: int,
        role_id: int,
        accepted: bool = False,
    ) -> CourseUser:
        new_course_user = CourseUser(
            course_id=course_id,
            user_id=user_id,
            role_id=role_id,
            accepted=accepted,
        )
        self.db_session.add(new_course_user)
        self.db_session.commit()
        self.db_session.refresh(new_course_user)
        return new_course_user

    # ====================== QUERYING ====================== #

    def get_course_user(self, course_id: int, user_id: int) -> CourseUser:
        return (
            self.db_session.execute(
                sa.select(CourseUser).where(
                    CourseUser.course_id == course_id,
                    CourseUser.user_id == user_id,
                )
            )
            .scalars()
            .one_or_none()
        )

    def get_course_users_by_user_id(self, user_id: int) -> list[CourseUser]:
        return (
            self.db_session.execute(
                sa.select(CourseUser).where(
                    CourseUser.user_id == user_id,
                )
            )
            .scalars()
            .all()
        )

    def exists_course_by_name_subject_id_semester_and_admin(
        self, name: str, subject_id: str, semester: str, admin_id: int
    ) -> bool:
        return (
            self.db_session.execute(
                sa.select(Course).where(
                    Course.name == name,
                    Course.subject_id == subject_id,
                    Course.semester == semester,
                    Course.course_users.any(CourseUser.user_id == admin_id),
                )
            )
            .scalars()
            .one_or_none()
            is not None
        )

    def enrroll_user_in_course(
        self, course_id: int, user_id: int, role_id: int
    ) -> CourseUser:
        # Check if the user is already enrolled in the course
        existing_course_user = self.get_course_user(course_id, user_id)
        if existing_course_user:
            raise ValueError("User is already registered in the course")

        course_user = CourseUser(
            course_id=course_id,
            user_id=user_id,
            role_id=role_id,
            accepted=False,
        )
        self.db_session.add(course_user)
        self.db_session.commit()
        self.db_session.refresh(course_user)
        return course_user
