from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repositories.models.user import User

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, BigInt, DateTime, IntPK


class ValidationToken(Base):
    __tablename__ = "validation_tokens"

    id: Mapped[IntPK]
    user_id: Mapped[BigInt] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str]
    expiry_date: Mapped[DateTime]

    user: Mapped["User"] = relationship(back_populates="validation_token")
