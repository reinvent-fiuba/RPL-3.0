from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.test_run import TestRun

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, IntPK, BigInt, Str, TextStr, DateTime


class UnitTestRun(Base):
    __tablename__ = "unit_test_runs"

    id: Mapped[IntPK]
    test_run_id: Mapped[BigInt] = mapped_column(ForeignKey("test_runs.id"))
    name: Mapped[Str]
    passed: Mapped[bool]
    error_messages: Mapped[Optional[TextStr]]
    date_created: Mapped[DateTime]

    test_run: Mapped["TestRun"] = relationship(back_populates="unit_test_run")
