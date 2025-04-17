from .base import BaseRepository

from .models.course_user import CourseUser
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
