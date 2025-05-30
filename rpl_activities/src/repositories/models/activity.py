from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_activities.src.repositories.models.activity_category import (
        ActivityCategory,
    )
    from rpl_activities.src.repositories.models.rpl_file import RPLFile
    from rpl_activities.src.repositories.models.activity_submission import (
        ActivitySubmission,
    )
    from rpl_activities.src.repositories.models.io_test import IOTest
    from rpl_activities.src.repositories.models.unit_test_suite import UnitTestSuite

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, AutoDateTime, IntPK, Str, LargeStr, TextStr


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[IntPK]
    course_id: Mapped[BigInt]
    category_id: Mapped[BigInt] = mapped_column(ForeignKey("activity_categories.id"))
    name: Mapped[LargeStr]
    description: Mapped[Optional[TextStr]]
    language: Mapped[Str]
    is_io_tested: Mapped[bool]
    active: Mapped[bool]
    deleted: Mapped[bool]
    starting_rplfile_id: Mapped[BigInt] = mapped_column(ForeignKey("rpl_files.id"))
    points: Mapped[int]
    compilation_flags: Mapped[LargeStr] = mapped_column(insert_default="")
    date_created: Mapped[AutoDateTime]
    last_updated: Mapped[AutoDateTime]

    category: Mapped["ActivityCategory"] = relationship(back_populates="activities")
    starting_rplfile: Mapped["RPLFile"] = relationship(back_populates="activity")
    submissions: Mapped[List["ActivitySubmission"]] = relationship(
        back_populates="activity", lazy="raise"
    )
    io_tests: Mapped[List["IOTest"]] = relationship(back_populates="activity")
    unit_test_suite: Mapped[Optional["UnitTestSuite"]] = relationship(
        back_populates="activity"
    )
