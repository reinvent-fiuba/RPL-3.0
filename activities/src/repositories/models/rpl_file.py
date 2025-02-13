from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.models.activity import Activity
    from src.repositories.models.activity_submission import ActivitySubmission
    from src.repositories.models.unit_test import UnitTest


from sqlalchemy.orm import Mapped, relationship


from base_model import Base, DateTime, IntPK, Str


class RplFile(Base):
    __tablename__ = "rpl_files"

    id: Mapped[IntPK]
    file_name: Mapped[Str]
    file_type: Mapped[Str]
    data: Mapped[Optional[bytes]]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    activities: Mapped[List["Activity"]] = relationship(
        "Activity", back_populates="starting_files"
    )
    activity_submissions: Mapped[List["ActivitySubmission"]] = relationship(
        back_populates="response_files"
    )
    unit_tests: Mapped[List["UnitTest"]] = relationship(back_populates="test_file")
