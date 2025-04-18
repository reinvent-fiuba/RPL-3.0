import logging
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from rpl_activities.src.config.database import get_db_session
from rpl_activities.src.main import app
from rpl_activities.src.repositories.models.base_model import Base
from rpl_activities.src.repositories.models import models_metadata
from rpl_activities.src.config import env

from rpl_users.tests.conftest import (
    users_api_dbsession_fixture,
    users_api_http_client_fixture,
    email_handler_fixture,
    example_users_fixture,
    regular_auth_headers_fixture,
    admin_auth_headers_fixture,
)

# @pytest.fixture(name="session", scope="module")
# def session_fixture():
#     engine = create_engine(
#         env.DB_URL,
#         # connect_args={"check_same_thread": False}, # Use if sqlite is active
#         poolclass=StaticPool,
#     )
#     Base.metadata.create_all(engine)
#     logging.debug("[tests:conftest] DB tables: %s", Base.metadata.tables.keys())
#     TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     with TestingSessionLocal() as session:
#         yield session
#     Base.metadata.drop_all(engine)
#     logging.debug("[tests:conftest] DB tables dropped")


# @pytest.fixture(name="client", scope="module")
# def client_fixture(session):
#     def override_get_db():
#         return session

#     app.dependency_overrides[get_db_session] = override_get_db

#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()
