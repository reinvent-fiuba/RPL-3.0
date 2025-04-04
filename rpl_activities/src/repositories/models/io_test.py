from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.activity import Activity

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, DateTime, IntPK, LargeStr, TextStr


class IOTest(Base):
    __tablename__ = "io_tests"

    id: Mapped[IntPK]
    activity_id: Mapped[BigInt] = mapped_column(ForeignKey("activities.id"))
    name: Mapped[LargeStr]
    test_in: Mapped[TextStr]
    test_out: Mapped[TextStr]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    activity: Mapped["Activity"] = relationship(back_populates="io_tests")
