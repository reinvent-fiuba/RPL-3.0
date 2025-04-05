from sqlalchemy.orm import Mapped

from .base_model import Base, AutoDateTime, IntPK, SmallStr


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[IntPK]
    name: Mapped[SmallStr]
    date_created: Mapped[AutoDateTime]
