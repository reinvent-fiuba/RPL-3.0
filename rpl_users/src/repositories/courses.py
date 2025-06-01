from datetime import datetime, timezone
from .base import BaseRepository

from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.course_user import CourseUser

from fastapi import HTTPException, status

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from ..dtos.course_dtos import CourseCreationDTO, CourseUptateDTO


class CoursesRepository(BaseRepository):

    # ====================== PRIVATE - EXCEPTIONS  ====================== #

    def _raise_http_conflict_exception(self):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course already exists with this name, university and semester",
        )

    # ====================== MANAGING ====================== #

    def save_new_course(self, course_data: CourseCreationDTO) -> Course:
        old_course = self.get_course_with_name_university_semester_and_subject_id(
            course_data.name,
            course_data.university,
            course_data.semester,
            course_data.subject_id,
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
            active=course_data.active,
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

    def update_course(self, course_id: str, course_data: CourseUptateDTO) -> Course:
        try:
            updated_course = self.get_course_with_id(course_id)
            updated_course.name = course_data.name
            updated_course.university = course_data.university
            updated_course.subject_id = course_data.subject_id
            updated_course.description = course_data.description
            updated_course.active = course_data.active
            updated_course.semester = course_data.semester
            updated_course.semester_start_date = course_data.semester_start_date
            updated_course.semester_end_date = course_data.semester_end_date
            updated_course.img_uri = course_data.img_uri
            updated_course.last_updated = datetime.now(timezone.utc)
            self.db_session.commit()
            self.db_session.refresh(updated_course)
            return updated_course
        except IntegrityError:
            self.db_session.rollback()
            self._raise_http_conflict_exception()

    def delete_course(self, course_id: str) -> Course:
        course = self.get_course_with_id(course_id)
        self.db_session.delete(course)
        self.db_session.refresh(course)

    # ====================== QUERYING ====================== #

    def get_all_courses(self) -> list[Course]:
        return self.db_session.execute(sa.select(Course)).scalars().all()

    def get_course_with_id(self, course_id: str) -> Course:
        return (
            self.db_session.execute(sa.select(Course).where(Course.id == course_id))
            .scalars()
            .one_or_none()
        )

    def get_course_with_name_university_semester_and_subject_id(
        self,
        name: str,
        university: str,
        semester: str,
        subject_id: str,
    ) -> Course:
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

    def get_all_courses_from_user(self, user_id: str) -> list[Course]:
        return (
            self.db_session.execute(
                sa.select(Course)
                .join(CourseUser, CourseUser.course_id == Course.id)
                .where(CourseUser.user_id == user_id)
            )
            .scalars()
            .all()
        )
