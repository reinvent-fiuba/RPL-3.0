from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

# WARNING: FOR REFERENCE ONLY. The actual models are modified, simplified, and optimized to be more readable and database-agnostic.


class Base(DeclarativeBase):
    pass


class ActivityCategories(Base):
    __tablename__ = "activity_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    course_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    active: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    activities: Mapped[List["Activities"]] = relationship(
        "Activities", back_populates="activity_category"
    )


class RplFiles(Base):
    __tablename__ = "rpl_files"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_type: Mapped[Optional[str]] = mapped_column(String(255))
    data: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    activities: Mapped[List["Activities"]] = relationship(
        "Activities", back_populates="starting_files"
    )
    activity_submissions: Mapped[List["ActivitySubmissions"]] = relationship(
        "ActivitySubmissions", back_populates="response_files"
    )
    unit_tests: Mapped[List["UnitTests"]] = relationship(
        "UnitTests", back_populates="test_file"
    )


class Activities(Base):
    __tablename__ = "activities"
    __table_args__ = (
        ForeignKeyConstraint(
            ["activity_category_id"],
            ["activity_categories.id"],
            name="activities_ibfk_1",
        ),
        ForeignKeyConstraint(
            ["starting_files_id"], ["rpl_files.id"], name="activities_ibfk_2"
        ),
        Index("activity_category_id", "activity_category_id"),
        Index("starting_files_id", "starting_files_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    compilation_flags: Mapped[str] = mapped_column(String(500))
    course_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    activity_category_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[Optional[str]] = mapped_column(String(255))
    is_io_tested: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    active: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    deleted: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    starting_files_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    points: Mapped[Optional[int]] = mapped_column(Integer)
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    activity_category: Mapped["ActivityCategories"] = relationship(
        "ActivityCategories", back_populates="activities"
    )
    starting_files: Mapped["RplFiles"] = relationship(
        "RplFiles", back_populates="activities"
    )
    activity_submissions: Mapped[List["ActivitySubmissions"]] = relationship(
        "ActivitySubmissions", back_populates="activity"
    )
    io_tests: Mapped[List["IoTests"]] = relationship(
        "IoTests", back_populates="activity"
    )
    unit_tests: Mapped[List["UnitTests"]] = relationship(
        "UnitTests", back_populates="activity"
    )


class ActivitySubmissions(Base):
    __tablename__ = "activity_submissions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["activity_id"], ["activities.id"], name="activity_submissions_ibfk_1"
        ),
        ForeignKeyConstraint(
            ["response_files_id"], ["rpl_files.id"], name="activity_submissions_ibfk_2"
        ),
        Index("activity_id", "activity_id"),
        Index("response_files_id", "response_files_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_final_solution: Mapped[int] = mapped_column(TINYINT(1))
    activity_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    response_files_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    status: Mapped[Optional[str]] = mapped_column(String(255))
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    activity: Mapped["Activities"] = relationship(
        "Activities", back_populates="activity_submissions"
    )
    response_files: Mapped["RplFiles"] = relationship(
        "RplFiles", back_populates="activity_submissions"
    )
    results: Mapped[List["Results"]] = relationship(
        "Results", back_populates="activity_submission"
    )
    test_run: Mapped[List["TestRun"]] = relationship(
        "TestRun", back_populates="activity_submission"
    )


class IoTests(Base):
    __tablename__ = "io_tests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["activity_id"], ["activities.id"], name="io_tests_ibfk_1"
        ),
        Index("activity_id", "activity_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    activity_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(String(500))
    test_in: Mapped[Optional[str]] = mapped_column(Text)
    test_out: Mapped[Optional[str]] = mapped_column(Text)
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    activity: Mapped["Activities"] = relationship(
        "Activities", back_populates="io_tests"
    )


class UnitTests(Base):
    __tablename__ = "unit_tests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["activity_id"], ["activities.id"], name="unit_tests_ibfk_1"
        ),
        ForeignKeyConstraint(
            ["test_file_id"], ["rpl_files.id"], name="unit_tests_ibfk_2"
        ),
        Index("activity_id", "activity_id"),
        Index("test_file_id", "test_file_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    activity_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    test_file_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    activity: Mapped["Activities"] = relationship(
        "Activities", back_populates="unit_tests"
    )
    test_file: Mapped["RplFiles"] = relationship(
        "RplFiles", back_populates="unit_tests"
    )


class Results(Base):
    __tablename__ = "results"
    __table_args__ = (
        ForeignKeyConstraint(
            ["activity_submission_id"],
            ["activity_submissions.id"],
            name="results_ibfk_1",
        ),
        Index("activity_submission_id", "activity_submission_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    activity_submission_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    score: Mapped[Optional[str]] = mapped_column(String(255))
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    activity_submission: Mapped["ActivitySubmissions"] = relationship(
        "ActivitySubmissions", back_populates="results"
    )


class TestRun(Base):
    __tablename__ = "test_run"
    __table_args__ = (
        ForeignKeyConstraint(
            ["activity_submission_id"],
            ["activity_submissions.id"],
            name="test_run_ibfk_1",
        ),
        Index("activity_submission_id", "activity_submission_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    activity_submission_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    success: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    exit_message: Mapped[Optional[str]] = mapped_column(String(255))
    stderr: Mapped[Optional[str]] = mapped_column(Text)
    stdout: Mapped[Optional[str]] = mapped_column(Text)
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    activity_submission: Mapped["ActivitySubmissions"] = relationship(
        "ActivitySubmissions", back_populates="test_run"
    )
    io_test_run: Mapped[List["IoTestRun"]] = relationship(
        "IoTestRun", back_populates="test_run"
    )
    unit_test_run: Mapped[List["UnitTestRun"]] = relationship(
        "UnitTestRun", back_populates="test_run"
    )


class IoTestRun(Base):
    __tablename__ = "io_test_run"
    __table_args__ = (
        ForeignKeyConstraint(
            ["test_run_id"], ["test_run.id"], name="io_test_run_ibfk_1"
        ),
        Index("test_run_id", "test_run_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    test_run_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    test_name: Mapped[Optional[str]] = mapped_column(String(500))
    test_in: Mapped[Optional[str]] = mapped_column(Text)
    expected_output: Mapped[Optional[str]] = mapped_column(Text)
    run_output: Mapped[Optional[str]] = mapped_column(Text)
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="io_test_run")


class UnitTestRun(Base):
    __tablename__ = "unit_test_run"
    __table_args__ = (
        ForeignKeyConstraint(
            ["test_run_id"], ["test_run.id"], name="unit_test_run_ibfk_1"
        ),
        Index("test_run_id", "test_run_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    test_run_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    passed: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    error_messages: Mapped[Optional[str]] = mapped_column(Text)
    date_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    test_run: Mapped["TestRun"] = relationship(
        "TestRun", back_populates="unit_test_run"
    )
