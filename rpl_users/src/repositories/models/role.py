from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.course_user import CourseUser

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, DateTime, IntPK, LargeStr, SmallStr


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[IntPK]
    name: Mapped[SmallStr]
    permissions: Mapped[LargeStr]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    course_users: Mapped[List["CourseUser"]] = relationship(back_populates="role")
