from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.course import Course
    from rpl_users.src.repositories.models.role import Role
    from rpl_users.src.repositories.models.user import User

from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, AutoDateTime, IntPK, Str


class CourseUser(Base):
    __tablename__ = "course_users"

    __table_args__ = (
        ForeignKeyConstraint(
            ["course_name", "course_university", "course_semester"],
            ["courses.name", "courses.university", "courses.semester"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[IntPK]

    course_name: Mapped[Str] = mapped_column()
    course_university: Mapped[Str] = mapped_column()
    course_semester: Mapped[Str] = mapped_column()
    user_id: Mapped[BigInt] = mapped_column(ForeignKey("users.id"))
    role_id: Mapped[BigInt] = mapped_column(ForeignKey("roles.id"))
    accepted: Mapped[bool]
    date_created: Mapped[AutoDateTime]
    last_updated: Mapped[AutoDateTime]

    course: Mapped["Course"] = relationship(back_populates="course_users")
    role: Mapped["Role"] = relationship(back_populates="course_users")
    user: Mapped["User"] = relationship(back_populates="course_users")
