from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import validates
import re
from config.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String)
    student_id = Column(String)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email_validated = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    university = Column(String)
    degree = Column(String)
    img_uri = Column(String)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)

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
