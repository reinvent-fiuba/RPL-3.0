from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_activities.src.repositories.models.test_execution_log import TestsExecutionLog

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, AutoDateTime, IntPK, LargeStr, TextStr


class IOTestRun(Base):
    __tablename__ = "io_test_runs"

    id: Mapped[IntPK]
    tests_execution_log_id: Mapped[BigInt] = mapped_column(ForeignKey("tests_execution_logs.id"))
    test_name: Mapped[LargeStr]
    test_in: Mapped[Optional[TextStr]]
    expected_output: Mapped[TextStr]
    run_output: Mapped[TextStr]
    date_created: Mapped[AutoDateTime]

    tests_execution_log: Mapped["TestsExecutionLog"] = relationship(back_populates="io_test_runs")
