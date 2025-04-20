from typing import List

from sqlalchemy.orm import Mapped

from .base_model import Base, IntPK, LargeStr, Str

PERMISSION_DELIMITER = ","


class University(Base):
    __tablename__ = "universities"

    id: Mapped[IntPK]
    name: Mapped[Str]
    degrees: Mapped[LargeStr]

    def get_degrees(self) -> List[str]:
        """Get the degrees as a list of strings."""
        return [degree.strip() for degree in self.degrees.split(PERMISSION_DELIMITER)]
