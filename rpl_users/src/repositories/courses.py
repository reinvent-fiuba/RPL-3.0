from datetime import datetime, timezone
from typing import Optional
from .base import BaseRepository

from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.course_user import CourseUser

from fastapi import HTTPException, status

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from ..dtos.course_dtos import CourseCreationRequestDTO, CourseUptateRequestDTO


class CoursesRepository(BaseRepository):

    # ====================== PRIVATE - EXCEPTIONS  ====================== #

    def _raise_http_conflict_exception(self):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course already exists with this name, university and semester",
        )

    # ====================== MANAGING ====================== #

    def save_new_course(self, course_data: CourseCreationRequestDTO) -> Course:
        old_course = self.get_course_with_name_university_semester_and_subject_id(
            course_data.name, course_data.university, course_data.semester, course_data.subject_id
        )
        if old_course:
            if old_course.deleted:
                old_course.deleted = False
                self.db_session.commit()
                self.db_session.refresh(old_course)
                return old_course
            else:
                self._raise_http_conflict_exception()

        new_course = Course(
            name=course_data.name,
            university=course_data.university,
            subject_id=course_data.subject_id,
            description=course_data.description,
            active=True,
            semester=course_data.semester,
            semester_start_date=course_data.semester_start_date,
            semester_end_date=course_data.semester_end_date,
            img_uri=course_data.img_uri,
        )

        try:
            self.db_session.add(new_course)
            self.db_session.commit()
            self.db_session.refresh(new_course)
            return new_course
        except IntegrityError:
            self.db_session.rollback()
            self._raise_http_conflict_exception()

    def update_course(self, course_id: int, new_data: CourseUptateRequestDTO) -> Course:
        try:
            course = self.get_course_with_id(course_id)
            course.name = new_data.name
            course.university = new_data.university
            course.subject_id = new_data.subject_id
            course.description = (
                new_data.description if new_data.description is not None else course.description
            )
            course.active = new_data.active if new_data.active is not None else course.active
            course.deleted = new_data.deleted if new_data.deleted is not None else course.deleted
            course.semester = new_data.semester
            course.semester_start_date = new_data.semester_start_date
            course.semester_end_date = new_data.semester_end_date
            course.img_uri = new_data.img_uri if new_data.img_uri is not None else course.img_uri

            course.last_updated = datetime.now(timezone.utc)
            self.db_session.commit()
            self.db_session.refresh(course)
            return course
        except IntegrityError:
            self.db_session.rollback()
            self._raise_http_conflict_exception()

    def delete_course(self, course_id: int):
        course = self.get_course_with_id(course_id)
        self.db_session.delete(course)
        self.db_session.commit()

    # ====================== QUERYING ====================== #

    def get_all_courses(self) -> list[Course]:
        return self.db_session.execute(sa.select(Course)).scalars().all()

    def get_course_with_id(self, course_id: int) -> Optional[Course]:
        return (
            self.db_session.execute(sa.select(Course).where(Course.id == course_id)).scalars().one_or_none()
        )

    def get_course_with_name_university_semester_and_subject_id(
        self, name: str, university: str, semester: str, subject_id: str
    ) -> Optional[Course]:
        return (
            self.db_session.execute(
                sa.select(Course).where(
                    Course.name == name,
                    Course.university == university,
                    Course.semester == semester,
                    Course.subject_id == subject_id,
                )
            )
            .scalars()
            .one_or_none()
        )

    def get_all_courses_from_user(self, user_id: int) -> list[Course]:
        return (
            self.db_session.execute(
                sa.select(Course)
                .join(CourseUser, CourseUser.course_id == Course.id)
                .where(CourseUser.user_id == user_id)
            )
            .scalars()
            .all()
        )
