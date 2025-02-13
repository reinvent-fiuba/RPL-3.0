from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy import Text, LargeBinary

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# WARNING: These models are not complete and are only meant to be used for the purpose of the migration script. Additionally, they use core SQLAlchemy features from 1.4, which are still in use but are not recommended anymore since they are considered legacy.


class Activity(Base):
    __tablename__ = "activities"
    id = Column(BIGINT, primary_key=True)
    course_id = Column(BIGINT, nullable=False)  # No FK (cross-service)
    activity_category_id = Column(BIGINT, ForeignKey("activity_categories.id"))
    name = Column(String(500))
    description = Column(Text)
    language = Column(String(255))
    is_io_tested = Column(Boolean)
    active = Column(Boolean)
    deleted = Column(Boolean)
    starting_files_id = Column(BIGINT, ForeignKey("rpl_files.id"))
    points = Column(Integer)
    compilation_flags = Column(String(500), nullable=False, default="")
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class ActivityCategory(Base):
    __tablename__ = "activity_categories"
    id = Column(BIGINT, primary_key=True)
    course_id = Column(BIGINT, nullable=False)  # No FK (cross-service)
    name = Column(String(255))
    description = Column(String(255))
    active = Column(Boolean)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class ActivitySubmission(Base):
    __tablename__ = "activity_submissions"
    id = Column(BIGINT, primary_key=True)
    activity_id = Column(BIGINT, ForeignKey("activities.id"))
    user_id = Column(BIGINT, nullable=False)  # No FK (cross-service)
    response_files_id = Column(BIGINT, ForeignKey("rpl_files.id"))
    status = Column(String(255))
    is_final_solution = Column(Boolean, nullable=False, default=False)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class RPLFile(Base):
    __tablename__ = "rpl_files"
    id = Column(BIGINT, primary_key=True)
    file_name = Column(String(255))
    file_type = Column(String(255))
    data = Column(LargeBinary)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class IOTest(Base):
    __tablename__ = "io_tests"
    id = Column(BIGINT, primary_key=True)
    activity_id = Column(BIGINT, ForeignKey("activities.id"))
    name = Column(String(500))
    test_in = Column(Text)
    test_out = Column(Text)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class UnitTest(Base):
    __tablename__ = "unit_tests"
    id = Column(BIGINT, primary_key=True)
    activity_id = Column(BIGINT, ForeignKey("activities.id"))
    test_file_id = Column(BIGINT, ForeignKey("rpl_files.id"))
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class TestRun(Base):
    __tablename__ = "test_run"
    id = Column(BIGINT, primary_key=True)
    activity_submission_id = Column(BIGINT, ForeignKey("activity_submissions.id"))
    success = Column(Boolean)
    exit_message = Column(String(255))
    stderr = Column(Text)
    stdout = Column(Text)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class IOTestRun(Base):
    __tablename__ = "io_test_run"
    id = Column(BIGINT, primary_key=True)
    test_run_id = Column(BIGINT, ForeignKey("test_run.id"))
    test_name = Column(String(500))
    test_in = Column(Text)
    expected_output = Column(Text)
    run_output = Column(Text)
    date_created = Column(DateTime)


class UnitTestRun(Base):
    __tablename__ = "unit_test_run"
    id = Column(BIGINT, primary_key=True)
    test_run_id = Column(BIGINT, ForeignKey("test_run.id"))
    name = Column(String(255))
    passed = Column(Boolean)
    error_messages = Column(Text)
    date_created = Column(DateTime)


class Result(Base):
    __tablename__ = "results"
    id = Column(BIGINT, primary_key=True)
    activity_submission_id = Column(BIGINT, ForeignKey("activity_submissions.id"))
    score = Column(String(255))
    date_created = Column(DateTime)
    last_updated = Column(DateTime)
