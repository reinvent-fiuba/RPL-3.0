from .base import BaseRepository

from .models.course import Course
from .models.user import User
import sqlalchemy as sa

from ..dtos.course_dtos import CourseResponseDTO, CourseCreationDTO

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
                semester_start_date= course.semester_start_date,
                semester_end_date=course.semester_end_date,
                img_uri=course.img_uri,
                enrolled=False,
                accepted=False,
            )
            for course in courses
        }
    
    def create_course(self, course_data: CourseCreationDTO, current_user: User) -> Course:
        if current_user.is_admin != True:
            raise ValueError("Only admins can create courses")
        
        # Create the new course
        course = Course(
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

        self.db_session.add(course)
        self.db_session.commit()
        self.db_session.refresh(course)
        return course
            
    
