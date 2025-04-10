from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.user import User

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, AutoDateTime, IntPK, Str


class ValidationToken(Base):
    __tablename__ = "validation_tokens"

    id: Mapped[IntPK]
    user_id: Mapped[BigInt] = mapped_column(ForeignKey("users.id"))
    token: Mapped[Str]
    expiration_date: Mapped[AutoDateTime]

    user: Mapped["User"] = relationship(back_populates="validation_tokens")
