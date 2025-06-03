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
        def __init__(self):
            self._emails_sent = []

        def send_validation_email(self, to_address):
            self._emails_sent.append({"type": "validation", "to_address": to_address})
            return "fake_token"

        def send_password_reset_email(self, to_address):
            self._emails_sent.append({"type": "password_reset", "to_address": to_address})
            return "fake_token"

        def send_course_acceptance_email(self, to_address, user_data, course_data):
            self._emails_sent.append(
                {
                    "type": "course_acceptance",
                    "to_address": to_address,
                    "user_data": user_data,
                    "course_data": course_data,
                }
            )

        def emails_sent(self):
            return self._emails_sent

    return TestEmailHandler()


@pytest.fixture(name="users_api_client", scope="function")
def users_api_http_client_fixture(users_api_dbsession, email_handler):
    app.dependency_overrides[get_db_session] = lambda: users_api_dbsession
    app.dependency_overrides[get_email_handler] = lambda: email_handler

    users_api_client = TestClient(app)
    yield users_api_client
    app.dependency_overrides.clear()


# ====================== USERS ====================== #


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


@pytest.fixture(name="admin_auth_headers", scope="function")
def admin_auth_headers_fixture(
    users_api_client: TestClient, example_users: dict[str, User]
) -> dict[str, str]:
    response = users_api_client.post(
        "/api/v3/auth/login", json={"username_or_email": "adminUsername", "password": "secret"}
    )
    response_data = response.json()
    if response.status_code != status.HTTP_200_OK:
        pytest.fail(f"Failed to get [admin auth headers]: {response.status_code} - {response_data}")
    return {"Authorization": f"{response_data['token_type']} {response_data['access_token']}"}


@pytest.fixture(name="regular_auth_headers", scope="function")
def regular_auth_headers_fixture(
    users_api_client: TestClient, example_users: dict[str, User]
) -> dict[str, str]:
    response = users_api_client.post(
        "/api/v3/auth/login", json={"username_or_email": "regularUsername", "password": "secret"}
    )
    response_data = response.json()
    if response.status_code != status.HTTP_200_OK:
        pytest.fail(f"Failed to get [regular auth headers]: {response.status_code} - {response_data}")
    return {"Authorization": f"{response_data['token_type']} {response_data['access_token']}"}


# ====================== COURSE ROLES ====================== #


@pytest.fixture(name="base_roles", scope="function", autouse=True)
def base_roles_fixture(users_api_dbsession: Session):
    course_admin_role = Role(
        id=1,
        name="course_admin",
        permissions="course_delete,course_view,course_edit,activity_view,activity_manage,activity_submit,user_view,user_manage",
    )
    users_api_dbsession.add(course_admin_role)
    users_api_dbsession.commit()

    student_role = Role(
        id=2, name="student", permissions="course_view,activity_view,activity_submit,user_view"
    )
    users_api_dbsession.add(student_role)
    users_api_dbsession.commit()

    users_api_dbsession.refresh(course_admin_role)
    users_api_dbsession.refresh(student_role)
    yield {"course_admin": course_admin_role, "student": student_role}


# ====================== COURSES ====================== #


@pytest.fixture(name="course_with_superadmin_as_admin_user", scope="function")
def course_with_superadmin_as_admin_user_fixture(
    users_api_dbsession: Session, example_users: dict[str, User], base_roles: dict[str, Role]
):
    course = Course(
        name="Algo1Mendez",
        university="FIUBA",
        subject_id="8001",
        description="some-description",
        semester="2019-1c",
        semester_start_date="2019-03-01T00:00:00",
        semester_end_date="2019-07-01T00:00:00",
    )
    users_api_dbsession.add(course)
    users_api_dbsession.commit()

    admin_course_user = CourseUser(
        course_id=course.id,
        user_id=example_users["admin"].id,
        role_id=base_roles["course_admin"].id,
        accepted=True,
    )
    users_api_dbsession.add(admin_course_user)
    users_api_dbsession.commit()

    users_api_dbsession.refresh(course)
    users_api_dbsession.refresh(admin_course_user)
    yield {"course": course, "admin_course_user": admin_course_user}


@pytest.fixture(name="course_with_regular_user_as_admin_user", scope="function")
def course_with_regular_user_as_admin_user_fixture(
    users_api_dbsession: Session, example_users: dict[str, User], base_roles: dict[str, Role]
):
    course = Course(
        name="Algo1Mendez",
        university="FIUBA",
        subject_id="8001",
        description="some-description",
        semester="2019-1c",
        semester_start_date="2019-03-01T00:00:00",
        semester_end_date="2019-07-01T00:00:00",
    )
    users_api_dbsession.add(course)
    users_api_dbsession.commit()

    admin_course_user = CourseUser(
        course_id=course.id,
        user_id=example_users["regular"].id,
        role_id=base_roles["course_admin"].id,
        accepted=True,
    )
    users_api_dbsession.add(admin_course_user)
    users_api_dbsession.commit()

    users_api_dbsession.refresh(course)
    users_api_dbsession.refresh(admin_course_user)
    yield {"course": course, "admin_course_user": admin_course_user}


@pytest.fixture(name="course_with_teacher_as_admin_user_and_student_user", scope="function")
def course_with_teacher_as_admin_user_and_student_user_fixture(
    users_api_dbsession: Session,
    example_users: dict[str, User],
    base_roles: dict[str, Role],
    course_with_superadmin_as_admin_user,
):
    course = course_with_superadmin_as_admin_user["course"]

    student_user = CourseUser(
        course_id=course.id,
        user_id=example_users["regular"].id,
        role_id=base_roles["student"].id,
        accepted=True,
    )
    users_api_dbsession.add(student_user)
    users_api_dbsession.commit()
    users_api_dbsession.refresh(student_user)

    yield {
        "course": course,
        "teacher_user": course_with_superadmin_as_admin_user["admin_course_user"],
        "student_user": student_user,
    }
