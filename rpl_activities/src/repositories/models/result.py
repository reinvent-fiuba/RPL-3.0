from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.models.activity_submission import ActivitySubmission

from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from base_model import Base, BigInt, IntPK, Str, DateTime


class Result(Base):
    __tablename__ = "results"

    id: Mapped[IntPK]
    activity_submission_id: Mapped[BigInt] = mapped_column(
        ForeignKey("activity_submissions.id")
    )
    score: Mapped[Str]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    activity_submission: Mapped["ActivitySubmission"] = relationship(
        back_populates="results"
    )
