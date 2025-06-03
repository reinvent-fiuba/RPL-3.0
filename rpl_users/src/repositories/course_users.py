from datetime import datetime, timezone
from .base import BaseRepository

from .models.course_user import CourseUser
from .models.course import Course

from fastapi import HTTPException, status

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError


class CourseUsersRepository(BaseRepository):

    # ====================== MANAGING ====================== #

    def save_new_course_user(
        self, course_id: int, user_id: int, role_id: int, accepted: bool = False
    ) -> CourseUser:
        new_course_user = CourseUser(course_id=course_id, user_id=user_id, role_id=role_id, accepted=accepted)
        try:
            self.db_session.add(new_course_user)
            self.db_session.commit()
            self.db_session.refresh(new_course_user)
            return new_course_user
        except IntegrityError:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User is already enrolled in the course"
            )

    def update_course_user(self, course_id: int, user_id: int, role_id: int, accepted: bool):
        course_user = self.get_course_user(course_id=course_id, user_id=user_id)
        course_user.role_id = role_id
        course_user.accepted = accepted
        course_user.last_updated = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(course_user)
        return course_user

    def delete_course_user(self, course_id: int, user_id: int):
        course_user = self.get_course_user(course_id=course_id, user_id=user_id)
        self.db_session.delete(course_user)
        self.db_session.commit()

    # ====================== QUERYING ====================== #

    def get_course_user(self, course_id: int, user_id: int) -> CourseUser:
        return (
            self.db_session.execute(
                sa.select(CourseUser).where(CourseUser.course_id == course_id, CourseUser.user_id == user_id)
            )
            .scalars()
            .one_or_none()
        )

    def get_course_users(self, course_id: int) -> list[CourseUser]:
        return (
            self.db_session.execute(sa.select(CourseUser).where(CourseUser.course_id == course_id))
            .scalars()
            .all()
        )
