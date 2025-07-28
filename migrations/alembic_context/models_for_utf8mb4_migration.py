from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy import Text, LargeBinary

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


# ==============================================================================


class Activity(Base):
    __tablename__ = "activities"
    id = Column(BIGINT, primary_key=True)
    course_id = Column(BIGINT, ForeignKey("courses.id"))
    activity_category_id = Column(BIGINT, ForeignKey("activity_categories.id"))
    name = Column(String(500))
    description = Column(Text)  # Changed from VARCHAR(20000) to TEXT
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
    course_id = Column(BIGINT, ForeignKey("courses.id"))
    name = Column(String(255))
    description = Column(String(255))
    active = Column(Boolean)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class ActivitySubmission(Base):
    __tablename__ = "activity_submissions"
    id = Column(BIGINT, primary_key=True)
    activity_id = Column(BIGINT, ForeignKey("activities.id"))
    user_id = Column(BIGINT, ForeignKey("users.id"))
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
    data = Column(LargeBinary)  # For BLOB storage
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class IOTest(Base):
    __tablename__ = "io_tests"
    id = Column(BIGINT, primary_key=True)
    activity_id = Column(BIGINT, ForeignKey("activities.id"))
    name = Column(String(500))
    test_in = Column(Text)  # Changed from VARCHAR(5000)
    test_out = Column(Text)  # Changed from VARCHAR(5000)
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
    stderr = Column(Text)  # Changed from VARCHAR(10000)
    stdout = Column(Text)  # Changed from VARCHAR(10000)
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


class IOTestRun(Base):
    __tablename__ = "io_test_run"
    id = Column(BIGINT, primary_key=True)
    test_run_id = Column(BIGINT, ForeignKey("test_run.id"))
    test_name = Column(String(500))
    test_in = Column(Text)  # Changed from VARCHAR(5000)
    expected_output = Column(Text)  # Changed from VARCHAR(5000)
    run_output = Column(Text)  # Changed from VARCHAR(5000)
    date_created = Column(DateTime)


class UnitTestRun(Base):
    __tablename__ = "unit_test_run"
    id = Column(BIGINT, primary_key=True)
    test_run_id = Column(BIGINT, ForeignKey("test_run.id"))
    name = Column(String(255))
    passed = Column(Boolean)
    error_messages = Column(Text)  # Changed from VARCHAR(5000)
    date_created = Column(DateTime)


class Result(Base):
    __tablename__ = "results"
    id = Column(BIGINT, primary_key=True)
    activity_submission_id = Column(BIGINT, ForeignKey("activity_submissions.id"))
    score = Column(String(255))
    date_created = Column(DateTime)
    last_updated = Column(DateTime)


# PREVIOUSLY CHECKED THAT THERE ARE ONLY INDEXES FOR THE ID COLUMNS (STRINGS ARE NOT INDEXED IN THE SOURCE DATABASE)
