from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.models.activity_submission import ActivitySubmission
    from src.repositories.models.io_test_run import IOTestRun
    from src.repositories.models.unit_test_run import UnitTestRun

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, DateTime, IntPK, Str, TextStr


class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[IntPK]
    activity_submission_id: Mapped[BigInt] = mapped_column(
        ForeignKey("activity_submissions.id")
    )
    success: Mapped[bool]
    exit_message: Mapped[Str]
    stderr: Mapped[Optional[TextStr]]
    stdout: Mapped[Optional[TextStr]]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    activity_submission: Mapped["ActivitySubmission"] = relationship(
        back_populates="test_run"
    )
    io_test_run: Mapped[List["IOTestRun"]] = relationship(back_populates="test_run")
    unit_test_run: Mapped[List["UnitTestRun"]] = relationship(back_populates="test_run")
