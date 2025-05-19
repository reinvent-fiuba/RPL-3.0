from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_activities.src.repositories.models.activity import Activity

from sqlalchemy.orm import Mapped, relationship

from .base_model import Base, BigInt, AutoDateTime, IntPK, Str


class ActivityCategory(Base):
    __tablename__ = "activity_categories"

    id: Mapped[IntPK]
    course_id: Mapped[BigInt]
    name: Mapped[Str]
    description: Mapped[Optional[Str]]
    active: Mapped[bool]
    date_created: Mapped[AutoDateTime]
    last_updated: Mapped[AutoDateTime]

    activities: Mapped[List["Activity"]] = relationship(
        back_populates="category", lazy="raise"
    )
