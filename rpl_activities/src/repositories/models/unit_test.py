from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.activity import Activity
    from rpl_users.src.repositories.models.rpl_file import RPLFile

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, DateTime, IntPK


class UnitTest(Base):
    __tablename__ = "unit_tests"

    id: Mapped[IntPK]
    activity_id: Mapped[BigInt] = mapped_column(ForeignKey("activities.id"))
    test_file_id: Mapped[BigInt] = mapped_column(ForeignKey("rpl_files.id"))
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]

    activity: Mapped["Activity"] = relationship(back_populates="unit_tests")
    test_file: Mapped["RPLFile"] = relationship(back_populates="unit_tests")
