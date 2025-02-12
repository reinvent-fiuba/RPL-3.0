from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

# WARNING: FOR REFERENCE ONLY. The actual models are modified, simplified, and optimized to be more readable and database-agnostic.


class Base(DeclarativeBase):
    pass


class Courses(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    university: Mapped[Optional[str]] = mapped_column(String(255))
    university_course_id: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    active: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    deleted: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    semester: Mapped[Optional[str]] = mapped_column(String(255))
    semester_start_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    semester_END_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    img_uri: Mapped[Optional[str]] = mapped_column(String(255))
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    course_users: Mapped[List["CourseUsers"]] = relationship(
        "CourseUsers", back_populates="course"
    )


class Permissions(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(50))
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(50))
    permissions: Mapped[Optional[str]] = mapped_column(String(1000))
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    course_users: Mapped[List["CourseUsers"]] = relationship(
        "CourseUsers", back_populates="role"
    )


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("email", "email", unique=True),
        Index("username", "username", unique=True),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    email_validated: Mapped[int] = mapped_column(TINYINT(1))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    surname: Mapped[Optional[str]] = mapped_column(String(255))
    student_id: Mapped[Optional[str]] = mapped_column(String(255))
    is_admin: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    degree: Mapped[Optional[str]] = mapped_column(String(255))
    university: Mapped[Optional[str]] = mapped_column(String(255))
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    img_uri: Mapped[Optional[str]] = mapped_column(String(255))

    course_users: Mapped[List["CourseUsers"]] = relationship(
        "CourseUsers", back_populates="user"
    )
    validation_token: Mapped[List["ValidationToken"]] = relationship(
        "ValidationToken", back_populates="user"
    )


class CourseUsers(Base):
    __tablename__ = "course_users"
    __table_args__ = (
        ForeignKeyConstraint(["course_id"], ["courses.id"], name="course_users_ibfk_1"),
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="course_users_ibfk_2"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="course_users_ibfk_3"),
        Index("course_id", "course_id"),
        Index("role_id", "role_id"),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    course_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    role_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    accepted: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    course: Mapped["Courses"] = relationship("Courses", back_populates="course_users")
    role: Mapped["Roles"] = relationship("Roles", back_populates="course_users")
    user: Mapped["Users"] = relationship("Users", back_populates="course_users")


class ValidationToken(Base):
    __tablename__ = "validation_token"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], name="validation_token_ibfk_1"),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    token: Mapped[Optional[str]] = mapped_column(String(255))
    expiry_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    user: Mapped["Users"] = relationship("Users", back_populates="validation_token")
