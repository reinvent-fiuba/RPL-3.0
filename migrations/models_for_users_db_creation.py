from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Course(Base):
    __tablename__ = "courses"
    id = Column(BIGINT, primary_key=True)
    name = Column(String(255))
    university = Column(String(255))
    university_course_id = Column(String(255))
    description = Column(String(255))
    active = Column(Boolean)
    deleted = Column(Boolean)
    semester = Column(String(255))
    semester_start_date = Column(DateTime)
    semester_END_date = Column(DateTime)
    img_uri = Column(String(255))
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class User(Base):
    __tablename__ = "users"
    id = Column(BIGINT, primary_key=True)
    name = Column(String(255))
    surname = Column(String(255))
    student_id = Column(String(255))
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email_validated = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False)
    degree = Column(String(255))
    university = Column(String(255))
    date_created = Column(DateTime)
    last_updated = Column(DateTime)
    img_uri = Column(String(255))


class Role(Base):
    __tablename__ = "roles"
    id = Column(BIGINT, primary_key=True)
    name = Column(String(50))
    permissions = Column(String(1000))
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class CourseUser(Base):
    __tablename__ = "course_users"
    id = Column(BIGINT, primary_key=True)
    course_id = Column(BIGINT, ForeignKey("courses.id"))
    user_id = Column(BIGINT, ForeignKey("users.id"))
    role_id = Column(BIGINT, ForeignKey("roles.id"))
    accepted = Column(Boolean)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(BIGINT, primary_key=True)
    name = Column(String(50))
    date_created = Column(DateTime)


class ValidationToken(Base):
    __tablename__ = "validation_token"
    id = Column(BIGINT, primary_key=True)
    user_id = Column(BIGINT, ForeignKey("users.id"))
    token = Column(String(255))
    expiry_date = Column(DateTime)
