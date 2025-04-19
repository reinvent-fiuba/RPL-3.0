from .base import BaseRepository

from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.course_user import CourseUser

from fastapi import HTTPException, status

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from ..dtos.course_dtos import CourseCreationDTO, CourseUptateDTO


class CoursesRepository(BaseRepository):

    # ====================== MANAGING ====================== #

    def save_new_course(self, course_data: CourseCreationDTO) -> Course:
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course already exists with this name, university, and semester",
            )

    def update_course(self, course_id: str, course_data: CourseUptateDTO) -> Course:
        try:
            updated_course = (
                self.db_session.execute(sa.select(Course).where(Course.id == course_id))
                .scalars()
                .one_or_none()
            )
            if not updated_course:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course not found",
                )
            updated_course.name = course_data.name
            updated_course.university = course_data.university
            updated_course.subject_id = course_data.subject_id
            updated_course.description = course_data.description
            updated_course.active = course_data.active
            updated_course.semester = course_data.semester
            updated_course.semester_start_date = course_data.semester_start_date
            updated_course.semester_end_date = course_data.semester_end_date
            updated_course.img_uri = course_data.img_uri
            self.db_session.commit()
            self.db_session.refresh(updated_course)
            return updated_course
        except IntegrityError:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course already exists with this name, university, and semester",
            )

    # ====================== QUERYING ====================== #

    def get_all_courses(self) -> list[Course]:
        return self.db_session.execute(sa.select(Course)).scalars().all()

    def get_by_id(self, course_id: str) -> Course:
        return (
            self.db_session.execute(sa.select(Course).where(Course.id == course_id))
            .scalars()
            .one_or_none()
        )
