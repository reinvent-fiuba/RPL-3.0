from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.models.activity_category import ActivityCategory
    from src.repositories.models.rpl_file import RplFile
    from src.repositories.models.activity_submission import ActivitySubmission
    from src.repositories.models.io_test import IoTest
    from src.repositories.models.unit_test import UnitTest

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from base_model import Base, BigInt, DateTime, IntPK, Str, LargeStr, TextStr


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[IntPK]
    course_id: Mapped[BigInt]
    activity_category_id: Mapped[BigInt] = mapped_column(
        ForeignKey("activity_categories.id")
    )
    name: Mapped[LargeStr]
    description: Mapped[Optional[TextStr]]
    language: Mapped[Str]
    is_io_tested: Mapped[bool]
    active: Mapped[bool]
    deleted: Mapped[bool]
    starting_files_id: Mapped[BigInt] = mapped_column(ForeignKey("rpl_files.id"))
    points: Mapped[int]
    compilation_flags: Mapped[LargeStr] = mapped_column(insert_default="")
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    activity_category: Mapped["ActivityCategory"] = relationship(
        back_populates="activities"
    )
    starting_files: Mapped["RplFile"] = relationship(back_populates="activities")
    activity_submissions: Mapped[List["ActivitySubmission"]] = relationship(
        back_populates="activity"
    )
    io_tests: Mapped[List["IoTest"]] = relationship(back_populates="activity")
    unit_tests: Mapped[List["UnitTest"]] = relationship(back_populates="activity")
