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
from rpl_users.src.config import env


@pytest.fixture(name="users_api_dbsession", scope="module")
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


@pytest.fixture(name="email_handler", scope="package")
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

    users_api_dbsession.delete(admin_user)
    users_api_dbsession.delete(regular_user)
    users_api_dbsession.commit()


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
