from sqlalchemy.orm import validates
import re

from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rpl_users.src.repositories.models.course_user import CourseUser
    from rpl_users.src.repositories.models.validation_token import ValidationToken

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, DateTime, IntPK, Str


class User(Base):
    __tablename__ = "users"

    id: Mapped[IntPK]
    username: Mapped[Str] = mapped_column(unique=True)
    email: Mapped[Str] = mapped_column(unique=True)
    password: Mapped[Str]
    email_validated: Mapped[bool]
    name: Mapped[Str]
    surname: Mapped[Str]
    student_id: Mapped[Str]
    is_admin: Mapped[bool]
    degree: Mapped[Str]
    university: Mapped[Str]
    date_created: Mapped[DateTime]
    last_updated: Mapped[DateTime]
    img_uri: Mapped[Optional[Str]]

    course_users: Mapped[List["CourseUser"]] = relationship(back_populates="user")
    validation_token: Mapped[List["ValidationToken"]] = relationship(
        back_populates="user"
    )

    @validates("username")
    def validate_username(self, key, username):
        if not re.match(r"^[a-zA-Z0-9_-]{3,}$", username):
            raise ValueError("Invalid username")
        return username

    @validates("email")
    def validate_email(self, key, email):
        if not re.match(r"^[a-zA-Z0-9_!#$%&’*+/=?`{|}~^.-]+@[a-zA-Z0-9.-]+$", email):
            raise ValueError("Invalid email")
        return email
