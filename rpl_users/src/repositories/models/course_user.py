from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.course import Course
    from rpl_users.src.repositories.models.role import Role
    from rpl_users.src.repositories.models.user import User

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, DateTime, IntPK


class CourseUser(Base):
    __tablename__ = "course_users"

    id: Mapped[IntPK]
    course_id: Mapped[BigInt] = mapped_column(ForeignKey("courses.id"))
    user_id: Mapped[BigInt] = mapped_column(ForeignKey("users.id"))
    role_id: Mapped[BigInt] = mapped_column(ForeignKey("roles.id"))
    accepted: Mapped[bool]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    course: Mapped["Course"] = relationship(back_populates="course_users")
    role: Mapped["Role"] = relationship(back_populates="course_users")
    user: Mapped["User"] = relationship(back_populates="course_users")
