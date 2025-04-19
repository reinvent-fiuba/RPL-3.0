from .base import BaseRepository

from .models.course_user import CourseUser
from .models.course import Course

from fastapi import HTTPException, status

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError


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
        try:
            self.db_session.add(new_course_user)
            self.db_session.commit()
            self.db_session.refresh(new_course_user)
            return new_course_user
        except IntegrityError:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already registered in the course",
            )

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
