from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_activities.src.repositories.models.activity import Activity
    from rpl_activities.src.repositories.models.activity_submission import (
        ActivitySubmission,
    )
    from rpl_activities.src.repositories.models.unit_test_suite import UnitTestSuite


from sqlalchemy.orm import Mapped, relationship


from .base_model import Base, AutoDateTime, IntPK, Str


class RPLFile(Base):
    __tablename__ = "rpl_files"

    id: Mapped[IntPK]
    file_name: Mapped[Str]
    file_type: Mapped[Str]
    data: Mapped[Optional[bytes]]
    date_created: Mapped[AutoDateTime]
    last_updated: Mapped[AutoDateTime]

    activity: Mapped[Optional["Activity"]] = relationship(
        back_populates="starting_rplfile"
    )
    submission: Mapped[Optional["ActivitySubmission"]] = relationship(
        back_populates="solution_rplfile"
    )
    unit_test_suite: Mapped[Optional["UnitTestSuite"]] = relationship(
        back_populates="test_rplfile"
    )
