from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.course_user import CourseUser

from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base_model import Base, AutoDateTime, IntPK, LargeStr, SmallStr

PERMISSION_DELIMITER = ","


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[IntPK]
    name: Mapped[SmallStr] = mapped_column(unique=True)
    permissions: Mapped[LargeStr]
    date_created: Mapped[AutoDateTime]
    last_updated: Mapped[AutoDateTime]

    course_users: Mapped[List["CourseUser"]] = relationship(
        back_populates="role", lazy="raise"
    )

    def get_permissions(self) -> List[str]:
        """Get the permissions as a list of strings."""
        return [
            permission.strip()
            for permission in self.permissions.split(PERMISSION_DELIMITER)
        ]
