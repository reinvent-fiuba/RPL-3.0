from .base import BaseRepository

from .models.course import Course
import sqlalchemy as sa

from ..dtos.course_dtos import CourseResponseDTO

class CoursesRepository(BaseRepository):
    def get_all_courses_dict(self) -> dict[int, CourseResponseDTO]:
        # Get all courses from the database
        courses = (
            self.db_session.execute(sa.select(Course))
            .scalars()
            .all()
        )
        return {
            course.id: CourseResponseDTO(
                id=course.id,
                name=course.name,
                university=course.university,
                subject_id=course.subject_id,
                description=course.description,
                active=course.active,
                semester=course.semester,
                semester_start_date=course.semester_start_date,
                semester_end_date=course.semester_end_date,
                img_uri=course.img_uri,
                date_created=course.date_created,
                last_updated=course.last_updated,
                enrolled=False,
                accepted=False,
            )
            for course in courses
        }
            
    
