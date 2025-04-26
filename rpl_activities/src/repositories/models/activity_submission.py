from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_activities.src.repositories.models.activity import Activity
    from rpl_activities.src.repositories.models.rpl_file import RPLFile
    from rpl_activities.src.repositories.models.result import Result
    from rpl_activities.src.repositories.models.test_run import TestRun

from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, AutoDateTime, IntPK, Str


class ActivitySubmission(Base):
    __tablename__ = "activity_submissions"

    id: Mapped[IntPK]
    is_final_solution: Mapped[bool]
    activity_id: Mapped[BigInt] = mapped_column(ForeignKey("activities.id"))
    user_id: Mapped[BigInt]
    response_rplfile_id: Mapped[BigInt] = mapped_column(ForeignKey("rpl_files.id"))
    status: Mapped[Str]
    date_created: Mapped[AutoDateTime]
    last_updated: Mapped[AutoDateTime]

    activity: Mapped["Activity"] = relationship(back_populates="activity_submissions")
    response_rplfile: Mapped["RPLFile"] = relationship(
        back_populates="activity_submission"
    )
    result: Mapped["Result"] = relationship(back_populates="activity_submission")
    test_run: Mapped["TestRun"] = relationship(back_populates="activity_submission")
