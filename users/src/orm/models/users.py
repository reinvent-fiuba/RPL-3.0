from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import validates
import re
from config.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, required=True)
    surname = Column(String)
    student_id = Column(String)
    username = Column(String, unique=True, required=True)
    email = Column(String, unique=True, required=True)
    password = Column(String, required=True)
    email_validated = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    university = Column(String)
    degree = Column(String)
    img_uri = Column(String)
    date_created = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True))

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
