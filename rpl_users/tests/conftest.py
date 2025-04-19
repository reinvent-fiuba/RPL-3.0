from datetime import datetime, timedelta
import logging
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from rpl_users.src.deps.database import get_db_session
from rpl_users.src.deps.email import get_email_handler
from rpl_users.src.main import app

from rpl_users.src.repositories.models.base_model import Base
from rpl_users.src.repositories.models import models_metadata  # NEEDED
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.course_user import CourseUser
from rpl_users.src.repositories.models.role import Role
from rpl_users.src.config import env


@pytest.fixture(name="users_api_dbsession", scope="function")
def users_api_dbsession_fixture():
    engine = create_engine(
        env.DB_URL,
        # connect_args={"check_same_thread": False}, # Use if sqlite is active
        echo=False,
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    logging.debug("[tests:conftest] DB tables: %s", Base.metadata.tables.keys())
    TestingSessionLocal = sessionmaker(autoflush=False, bind=engine)
    with TestingSessionLocal() as users_api_dbsession:
        yield users_api_dbsession
    Base.metadata.drop_all(engine)
    logging.debug("[tests:conftest] DB tables dropped")


@pytest.fixture(name="email_handler", scope="function")
def email_handler_fixture():
    class TestEmailHandler:
        def send_validation_email(self, user):
            return "fake_token"

        def send_password_reset_email(self, user):
            return "fake_token"

        def send_course_acceptance_email(self, user):
            pass

    return TestEmailHandler()


@pytest.fixture(name="users_api_client", scope="function")
def users_api_http_client_fixture(users_api_dbsession, email_handler):
    app.dependency_overrides[get_db_session] = lambda: users_api_dbsession
    app.dependency_overrides[get_email_handler] = lambda: email_handler

    users_api_client = TestClient(app)
    yield users_api_client
    app.dependency_overrides.clear()


# ==========================================================================


@pytest.fixture(name="example_users", scope="function")
def example_users_fixture(users_api_dbsession: Session):
    admin_user = User(
        name="adminName",
        surname="adminSurname",
        student_id="50000",
        username="adminUsername",
        email="admin@mail.com",
        password="$2a$10$cQQj.LWxHGB/gaoZwH2ilOAgJabst84IMgJ363F.lmLNjh0D43ZhG",  # hashed "secret"
        university="FIUBA",
        degree="Ing. Informatica",
        email_validated=True,
        is_admin=True,
    )
    users_api_dbsession.add(admin_user)
    users_api_dbsession.commit()

    regular_user = User(
        name="regularName",
        surname="regularSurname",
        student_id="50001",
        username="regularUsername",
        email="regular@mail.com",
        password="$2a$10$cQQj.LWxHGB/gaoZwH2ilOAgJabst84IMgJ363F.lmLNjh0D43ZhG",
        university="FIUBA",
        degree="Ing. Informatica",
        email_validated=True,
        is_admin=False,
    )
    users_api_dbsession.add(regular_user)
    users_api_dbsession.commit()

    users_api_dbsession.refresh(admin_user)
    users_api_dbsession.refresh(regular_user)
    yield {"admin": admin_user, "regular": regular_user}


@pytest.fixture(name="regular_auth_headers", scope="function")
def regular_auth_headers_fixture(
    users_api_client: TestClient, example_users
) -> dict[str, str]:
    response = users_api_client.post(
        "/api/v3/auth/login",
        json={"username_or_email": "regularUsername", "password": "secret"},
    )
    response_data = response.json()
    if response.status_code != status.HTTP_200_OK:
        pytest.fail(
            f"Failed to get [regular auth headers]: {response.status_code} - {response_data}"
        )
    return {
        "Authorization": f"{response_data['token_type']} {response_data['access_token']}"
    }


@pytest.fixture(name="admin_auth_headers", scope="function")
def admin_auth_headers_fixture(
    users_api_client: TestClient, example_users
) -> dict[str, str]:
    response = users_api_client.post(
        "/api/v3/auth/login",
        json={"username_or_email": "adminUsername", "password": "secret"},
    )
    response_data = response.json()
    if response.status_code != status.HTTP_200_OK:
        pytest.fail(
            f"Failed to get [admin auth headers]: {response.status_code} - {response_data}"
        )
    return {
        "Authorization": f"{response_data['token_type']} {response_data['access_token']}"
    }


# ==========================================================================


@pytest.fixture(name="example_course", scope="function")
def example_course_fixture(users_api_dbsession: Session):
    course = Course(
        id=1,
        name="some-course",
        university="FIUBA",
        subject_id="some-university-id",
        description="some-description",
        active=True,
        semester="2025-1c",
        semester_start_date=datetime.now() - timedelta(days=60),
        semester_end_date=datetime.now() + timedelta(days=60),
        date_created=datetime.now(),
        last_updated=datetime.now(),
        img_uri=None,
        deleted=False,
    )
    users_api_dbsession.add(course)
    users_api_dbsession.commit()
    users_api_dbsession.refresh(course)
    yield course


@pytest.fixture(name="example_course_user")
def course_user_fixture(
    users_api_dbsession: Session, course: Course, example_users: dict[str, User]
):
    course_user = CourseUser(
        id=1,
        course_id=course.id,
        user_id=example_users["admin"].id,
        role_id=1,
        is_accepted=True,
        date_created=datetime.now(),
        last_updated=datetime.now(),
    )
    users_api_dbsession.add(course_user)
    users_api_dbsession.commit()
    users_api_dbsession.refresh(course_user)
    yield course_user


@pytest.fixture(name="base_roles", autouse=True)
def insert_base_roles_fixture(users_api_dbsession: Session):
    course_admin_role = Role(
        id=1,
        name="course_admin",
        permissions="course_delete,course_view,course_edit,activity_view,activity_manage,activity_submit,user_view,user_manage",
    )
    users_api_dbsession.add(course_admin_role)
    users_api_dbsession.commit()

    student_role = Role(
        id=2,
        name="student",
        permissions="course_view,activity_view,activity_submit,user_view",
    )
    users_api_dbsession.add(student_role)
    users_api_dbsession.commit()

    users_api_dbsession.refresh(course_admin_role)
    users_api_dbsession.refresh(student_role)
    yield {"course_admin": course_admin_role, "student": student_role}
