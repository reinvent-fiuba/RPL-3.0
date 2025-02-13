from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.models.course_user import CourseUser

from sqlalchemy.orm import Mapped, relationship
import datetime

from base_model import Base, DateTime, IntPK, Str


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[IntPK]
    name: Mapped[Str]
    university: Mapped[Str]
    university_course_id: Mapped[Optional[Str]]
    description: Mapped[Optional[Str]]
    active: Mapped[bool]
    deleted: Mapped[bool]
    semester: Mapped[Str]
    semester_start_date: Mapped[datetime.datetime]
    semester_END_date: Mapped[datetime.datetime]
    img_uri: Mapped[Optional[Str]]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    course_users: Mapped[List["CourseUser"]] = relationship(back_populates="course")
