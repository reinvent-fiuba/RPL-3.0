from contextlib import contextmanager
from datetime import datetime, timezone
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
    ExternalCurrentCourseUserDTO,
    ExternalCurrentMainUserDTO,
)
from rpl_activities.src.main import app
from rpl_activities.src.repositories.models.base_model import Base
from rpl_activities.src.repositories.models import models_metadata
from rpl_activities.src.config import env
from rpl_activities.src.repositories.models.activity_category import ActivityCategory

from rpl_users.tests.conftest import (
    users_api_dbsession_fixture,
    users_api_http_client_fixture,
    email_handler_fixture,
    example_users_fixture,
    regular_auth_headers_fixture,
    admin_auth_headers_fixture,
    example_course_fixture,
    example_teacher_course_user_fixture,
    example_student_course_user_fixture,
    insert_base_roles_fixture,
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
    example_teacher_course_user,
    example_student_course_user,
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
        user_data = ExternalCurrentCourseUserDTO(**res.json())
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
