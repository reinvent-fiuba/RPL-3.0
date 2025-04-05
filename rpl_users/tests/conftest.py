import logging
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from rpl_users.src.config.database import get_db_session
from rpl_users.src.main import app
from rpl_users.src.repositories.models.base_model import Base
from rpl_users.src.repositories.models import models_metadata
from rpl_users.src.repositories.models.user import User

DB_URL = "sqlite:///:memory:"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    logging.getLogger().debug(">>> [DB Tables]: %s", Base.metadata.tables.keys())
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        return session

    app.dependency_overrides[get_db_session] = override_get_db

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ==========================================================================


@pytest.fixture(name="example_users")
def example_users_fixture(session: Session):
    admin_user = User(
        name="adminName",
        surname="adminSurname",
        student_id="50000",
        username="adminUsername",
        email="admin@mail.com",
        password="$2a$10$cQQj.LWxHGB/gaoZwH2ilOAgJabst84IMgJ363F.lmLNjh0D43ZhG",  # hashed "secret"
        university="UBA",
        degree="Ing. Informatica",
        email_validated=True,
        is_admin=True,
    )
    session.add(admin_user)
    session.commit()

    regular_user = User(
        name="regularName",
        surname="regularSurname",
        student_id="50001",
        username="regularUsername",
        email="regular@mail.com",
        password="$2a$10$cQQj.LWxHGB/gaoZwH2ilOAgJabst84IMgJ363F.lmLNjh0D43ZhG",
        university="UBA",
        degree="Ing. Informatica",
        email_validated=True,
        is_admin=False,
    )
    session.add(regular_user)
    session.commit()

    session.refresh(admin_user)
    session.refresh(regular_user)
    yield {"admin": admin_user, "regular": regular_user}

    session.delete(admin_user)
    session.delete(regular_user)
    session.commit()


@pytest.fixture(name="regular_auth_headers")
def regular_auth_headers_fixture(client: TestClient, example_users) -> dict[str, str]:
    response = client.post(
        "/api/v2/auth/login",
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


@pytest.fixture(name="admin_auth_headers")
def admin_auth_headers_fixture(client: TestClient, example_users) -> dict[str, str]:
    response = client.post(
        "/api/v2/auth/login",
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
