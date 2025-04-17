from sqlalchemy.orm import Mapped

from .base_model import Base, IntPK, LargeStr, Str


class University(Base):
    __tablename__ = "universities"

    id: Mapped[IntPK]
    name: Mapped[Str]
    degrees: Mapped[LargeStr]
