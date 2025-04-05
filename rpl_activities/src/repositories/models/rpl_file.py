from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_activities.src.repositories.models.activity import Activity
    from rpl_activities.src.repositories.models.activity_submission import (
        ActivitySubmission,
    )
    from rpl_activities.src.repositories.models.unit_test import UnitTest


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

    activities: Mapped[List["Activity"]] = relationship(back_populates="starting_files")
    activity_submissions: Mapped[List["ActivitySubmission"]] = relationship(
        back_populates="response_files"
    )
    unit_tests: Mapped[List["UnitTest"]] = relationship(back_populates="test_file")
