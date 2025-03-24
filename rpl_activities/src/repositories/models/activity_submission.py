from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.models.activity import Activity
    from src.repositories.models.rpl_file import RPLFile
    from src.repositories.models.result import Result
    from src.repositories.models.test_run import TestRun

from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, DateTime, IntPK, Str


class ActivitySubmission(Base):
    __tablename__ = "activity_submissions"

    id: Mapped[IntPK]
    is_final_solution: Mapped[bool]
    activity_id: Mapped[BigInt] = mapped_column(ForeignKey("activities.id"))
    user_id: Mapped[BigInt]
    response_files_id: Mapped[BigInt] = mapped_column(ForeignKey("rpl_files.id"))
    status: Mapped[Str]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    activity: Mapped["Activity"] = relationship(back_populates="activity_submissions")
    response_files: Mapped["RPLFile"] = relationship(
        back_populates="activity_submissions"
    )
    results: Mapped[List["Result"]] = relationship(back_populates="activity_submission")
    test_run: Mapped[List["TestRun"]] = relationship(
        back_populates="activity_submission"
    )
