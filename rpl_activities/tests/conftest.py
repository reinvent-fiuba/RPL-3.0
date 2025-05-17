from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import logging
from fastapi import HTTPException, Request, status
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from rpl_activities.src.deps.auth import (
    AuthDependency,
    CurrentCourseUser,
    CurrentMainUser,
    __basic_path_param_checks,
    get_current_course_user,
    get_current_main_user,
)
from rpl_activities.src.deps.database import get_db_session
from rpl_activities.src.dtos.auth_dtos import (
    ExternalCurrentMainUserDTO,
)
from rpl_activities.src.main import app
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.activity_submission import (
    ActivitySubmission,
)
from rpl_activities.src.repositories.models.base_model import Base
from rpl_activities.src.repositories.models import aux_models, models_metadata
from rpl_activities.src.config import env
from rpl_activities.src.repositories.models.activity_category import ActivityCategory

from rpl_activities.src.repositories.models.io_test import IOTest
from rpl_activities.src.repositories.models.rpl_file import RPLFile
from rpl_activities.src.repositories.models.unit_test import UnitTest
from rpl_users.src.dtos.course_dtos import CourseUserResponseDTO
from rpl_users.tests.conftest import (
    users_api_dbsession_fixture,
    users_api_http_client_fixture,
    email_handler_fixture,
    example_users_fixture,
    regular_auth_headers_fixture,
    admin_auth_headers_fixture,
    course_with_superadmin_as_admin_user_fixture,
    course_with_teacher_as_admin_user_and_student_user_fixture,
    course_with_regular_user_as_admin_user_fixture,
    base_roles_fixture,
)


@pytest.fixture(name="activities_api_dbsession", scope="function")
def activities_api_dbsession_fixture():
    engine = create_engine(
        env.DB_URL,
        # connect_args={"check_same_thread": False}, # Use if sqlite is active
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    logging.debug("[tests:conftest] DB tables: %s", Base.metadata.tables.keys())
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as session:
        yield session
    Base.metadata.drop_all(engine)
    logging.debug("[tests:conftest] DB tables dropped")


@pytest.fixture(name="activities_api_client", scope="function")
def activities_api_http_client_fixture(
    activities_api_dbsession,
    users_api_client: TestClient,
    course_with_teacher_as_admin_user_and_student_user,
):
    app.dependency_overrides[get_db_session] = lambda: activities_api_dbsession

    def override_get_current_main_user(auth_header: AuthDependency, request: Request):
        res = users_api_client.get(
            "/api/v3/auth/externalUserMainAuth",
            headers={
                "Authorization": f"{auth_header.scheme} {auth_header.credentials}"
            },
        )
        if res.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=res.status_code,
                detail=f"Failed to authenticate current user: {res.text}",
            )
        user_data = ExternalCurrentMainUserDTO(**res.json())
        return CurrentMainUser(user_data)

    def override_get_current_course_user(auth_header: AuthDependency, request: Request):
        course_id = __basic_path_param_checks(request.path_params.get("course_id"))
        res = users_api_client.get(
            "/api/v3/auth/externalCourseUserAuth",
            headers={
                "Authorization": f"{auth_header.scheme} {auth_header.credentials}"
            },
            params={"course_id": course_id},
        )
        if res.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=res.status_code,
                detail=f"Failed to authenticate current course user: {res.text}",
            )
        user_data = CourseUserResponseDTO(**res.json())
        return CurrentCourseUser(user_data)

    app.dependency_overrides[get_current_main_user] = override_get_current_main_user
    app.dependency_overrides[get_current_course_user] = override_get_current_course_user

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ==========================================================================


@pytest.fixture(name="example_category")
def example_category_fixture(
    activities_api_dbsession: Session,
):
    category = ActivityCategory(
        id=1,
        course_id=1,
        name="Example Category",
        description="This is an example category",
        active=True,
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(category)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(category)
    yield category


@pytest.fixture(name="example_inactive_category")
def example_inactive_category_fixture(
    activities_api_dbsession: Session,
):
    category = ActivityCategory(
        id=2,
        course_id=1,
        name="Inactive Category",
        description="This is an example inactive category",
        active=False,
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(category)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(category)
    yield category


@pytest.fixture(name="example_category_from_another_course")
def example_category_from_another_course_fixture(
    course_with_regular_user_as_admin_user,
    activities_api_dbsession: Session,
):
    category = ActivityCategory(
        id=3,
        course_id=course_with_regular_user_as_admin_user["course"].id,
        name="Example Category",
        description="This is an example category",
        active=True,
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(category)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(category)
    yield category
    


# ==========================================================================


@pytest.fixture(name="example_basic_rplfiles")
def example_basic_rplfiles_fixture(activities_api_dbsession: Session):
    with open("rpl_activities/tests/resources/basic_rplfile.tar.gz", "rb") as f:
        rplfile_data = f.read()
    example_rplfile = RPLFile(
        id=1,
        file_name="basic_rplfile.tar.gz",
        file_type="application/gzip",
        data=rplfile_data,
    )
    activities_api_dbsession.add(example_rplfile)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(example_rplfile)

    with open("rpl_activities/tests/resources/basic_rplfile_copy.tar.gz", "rb") as f:
        rplfile_data = f.read()
    example_rplfile_2 = RPLFile(
        id=2,
        file_name="basic_rplfile_copy.tar.gz",
        file_type="application/gzip",
        data=rplfile_data,
    )
    activities_api_dbsession.add(example_rplfile_2)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(example_rplfile_2)

    example_rplfile_3 = RPLFile(
        id=3,
        file_name="basic_rplfile_with_text.txt",
        file_type="text",
        data=b"print('This is a file with many unit tests')",
    )
    activities_api_dbsession.add(example_rplfile_3)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(example_rplfile_3)

    yield [example_rplfile, example_rplfile_2, example_rplfile_3]


@pytest.fixture(name="example_starting_rplfile")
def example_starting_rplfile_fixture(activities_api_dbsession: Session):
    with open(
        "rpl_activities/tests/resources/activity_1_starting_files/activity_1_starting_files.tar.gz",
        "rb",
    ) as f:
        rplfile_data = f.read()
    example_rplfile = RPLFile(
        id=4,
        file_name="activity_1_starting_files.tar.gz",
        file_type="application/gzip",
        data=rplfile_data,
    )
    activities_api_dbsession.add(example_rplfile)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(example_rplfile)
    yield example_rplfile


type StartingFileRawRequestData = tuple[str, tuple[str, bytes, str]]
type ExamplesOfStartingFilesRawData = dict[list[StartingFileRawRequestData]]
@pytest.fixture(name="examples_of_starting_files_raw_data")
def examples_of_starting_files_raw_data_fixture():
    py_files = [
        ("startingFile", ("main.py", b'print("test")', "application/octet-stream")),
        ("startingFile", ("assignment_main.py", b"# file assignment_main.py\ndef test():\n    pass\n", "application/octet-stream")),
        ("startingFile", ("files_metadata", b'{"assignment_main.py":{"display":"read_write"}}', "application/octet-stream")),
    ]
    c_files = [
        ("startingFile", ("main.c", open("rpl_activities/tests/resources/activity_1_starting_files/main.c", "rb").read(), "application/octet-stream")),
        ("startingFile", ("tiempo.c", open("rpl_activities/tests/resources/activity_1_starting_files/tiempo.c", "rb").read(), "application/octet-stream")),
        ("startingFile", ("tiempo.h", open("rpl_activities/tests/resources/activity_1_starting_files/tiempo.h", "rb").read(), "application/octet-stream")),
        ("startingFile", ("files_metadata", open("rpl_activities/tests/resources/activity_1_starting_files/files_metadata", "rb").read(), "application/octet-stream")),
    ]
    return {
        "python": py_files,
        "c": c_files,
    }


@pytest.fixture(name="example_submission_rplfile")
def example_submission_rplfile_fixture(activities_api_dbsession: Session):
    with open(
        "rpl_activities/tests/resources/activity_1_submission/activity_1_submission.tar.gz",
        "rb",
    ) as f:
        rplfile_data = f.read()
    example_rplfile = RPLFile(
        id=5,
        file_name="activity_1_submission.tar.gz",
        file_type="application/gzip",
        data=rplfile_data,
    )
    activities_api_dbsession.add(example_rplfile)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(example_rplfile)
    yield example_rplfile


# ==========================================================================


@pytest.fixture(name="example_activity")
def example_activity_fixture(
    activities_api_dbsession: Session,
    example_category: ActivityCategory,
    example_starting_rplfile: RPLFile,
):
    activity = Activity(
        id=1,
        course_id=1,
        category_id=example_category.id,
        name="Example Activity",
        description="This is an example activity",
        language=aux_models.LanguageWithVersion.C,
        is_io_tested=False,
        active=True,
        deleted=False,
        starting_rplfile_id=example_starting_rplfile.id,
        points=10,
        compilation_flags="",
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(activity)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(activity)
    yield activity


@pytest.fixture(name="example_inactive_activity")
def example_inactive_activity_fixture(
    activities_api_dbsession: Session,
    example_inactive_category: ActivityCategory,
    example_starting_rplfile: RPLFile,
):
    activity = Activity(
        id=2,
        course_id=1,
        category_id=example_inactive_category.id,
        name="Inactive Activity",
        description="This is an example inactive activity",
        language=aux_models.LanguageWithVersion.C,
        is_io_tested=False,
        active=False,
        deleted=False,
        starting_rplfile_id=example_starting_rplfile.id,
        points=10,
        compilation_flags="",
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(activity)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(activity)
    yield activity


@pytest.fixture(name="example_submission")
def example_submission_fixture(
    activities_api_dbsession: Session,
    example_activity: Activity,
    example_submission_rplfile: RPLFile,
):
    submission = ActivitySubmission(
        id=1,
        is_final_solution=False,
        activity_id=example_activity.id,
        user_id=2,
        response_rplfile_id=example_submission_rplfile.id,
        status=aux_models.SubmissionStatus.PENDING,
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(submission)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(submission)
    yield submission


@pytest.fixture(name="example_failed_submission")
def example_failed_submission_fixture(
    activities_api_dbsession: Session,
    example_activity: Activity,
    example_submission_rplfile: RPLFile,
):
    submission = ActivitySubmission(
        id=2,
        is_final_solution=False,
        activity_id=example_activity.id,
        user_id=2,
        response_rplfile_id=example_submission_rplfile.id,
        status=aux_models.SubmissionStatus.FAILURE,
        date_created=datetime.now(timezone.utc) - timedelta(days=1),
        last_updated=datetime.now(timezone.utc) - timedelta(days=1),
    )
    activities_api_dbsession.add(submission)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(submission)
    yield submission


# ==============================================================================


@pytest.fixture(name="example_activity_with_io_tests")
def example_activity_with_io_tests_fixture(
    activities_api_dbsession: Session,
    example_category: ActivityCategory,
    example_basic_rplfiles: list[RPLFile],
):
    activity = Activity(
        id=3,
        course_id=1,
        category_id=example_category.id,
        name="Example Activity with IO Tests",
        description="This is an example activity with IO tests",
        language=aux_models.LanguageWithVersion.C,
        is_io_tested=True,
        active=True,
        deleted=False,
        starting_rplfile_id=example_basic_rplfiles[0].id,
        points=10,
        compilation_flags="",
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(activity)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(activity)
    yield activity


@pytest.fixture(name="example_io_tests")
def example_io_tests_fixture(
    activities_api_dbsession: Session,
    example_activity_with_io_tests: Activity,
):
    io_test1 = IOTest(
        id=1,
        activity_id=example_activity_with_io_tests.id,
        name="IOTest 1",
        test_in="input1",
        test_out="output1",
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    io_test2 = IOTest(
        id=2,
        activity_id=example_activity_with_io_tests.id,
        name="IOTest 2",
        test_in="input2",
        test_out="output2",
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(io_test1)
    activities_api_dbsession.add(io_test2)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(io_test1)
    activities_api_dbsession.refresh(io_test2)
    yield [io_test1, io_test2]


# ==============================================================================


@pytest.fixture(name="example_unit_test")
def example_unit_test_fixture(
    activities_api_dbsession: Session,
    example_activity: Activity,
    example_basic_rplfiles: list[RPLFile],
):
    unit_test = UnitTest(
        id=1,
        activity_id=example_activity.id,
        test_rplfile_id=example_basic_rplfiles[2].id,
        date_created=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
    )
    activities_api_dbsession.add(unit_test)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(unit_test)
    yield unit_test


# ==============================================================================
