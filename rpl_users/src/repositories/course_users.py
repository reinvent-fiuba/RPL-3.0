from .base import BaseRepository

from .models.course_user import CourseUser
from .models.course import Course
import sqlalchemy as sa


class CourseUsersRepository(BaseRepository):
    def get_by_course_id_and_user_id(self, course_id: int, user_id: int) -> CourseUser:
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

    def create_course_user(
        self, course_id: int, user_id: int, role_id: int, accepted: bool
    ) -> CourseUser:
        course_user = CourseUser(
            course_id=course_id,
            user_id=user_id,
            role_id=role_id,  # Assuming role_id 1 is for students
            accepted=accepted,
        )
        self.db_session.add(course_user)
        self.db_session.commit()
        self.db_session.refresh(course_user)
        return course_user


#             )
