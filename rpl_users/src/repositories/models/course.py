from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.course_user import CourseUser

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

import datetime

from .base_model import Base, AutoDateTime, IntPK, Str


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[IntPK]

    name: Mapped[Str]
    university: Mapped[Str]
    subject_id: Mapped[Optional[Str]]
    description: Mapped[Optional[Str]]
    active: Mapped[bool] = mapped_column(default=True)
    deleted: Mapped[bool] = mapped_column(default=False)
    semester: Mapped[Str]
    semester_start_date: Mapped[datetime.datetime]
    semester_end_date: Mapped[datetime.datetime]
    img_uri: Mapped[Optional[Str]]
    date_created: Mapped[AutoDateTime]
    last_updated: Mapped[AutoDateTime]

    course_users: Mapped[List["CourseUser"]] = relationship(back_populates="course")
