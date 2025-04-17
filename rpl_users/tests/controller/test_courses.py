from datetime import datetime, timedelta
import json

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from src.deps.database import get_db_session
from src.main import app
from src.repositories.models.course import Course
from src.repositories.models.user import User, Role
from src.repositories.models.course_user import CourseUser


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    app.dependency_overrides[get_db_session] = lambda: session

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()



@pytest.fixture(name="users")
def users_fixture(session: Session):
    # Create an admin user
    admin_user = User(
        id=1,
        name="some-name",
        surname="some-surname",
        student_id="some-student-id",
        username="username",
        email="some@mail.com",
        password="supersecret",  # In a real test, this would be hashed
        university="some-university",
        degree="some-hard-degree",
        is_validated=True,
        is_admin=True
    )
    
    # Create a regular user
    regular_user = User(
        id=2,
        name="other-name",
        surname="other-surname",
        student_id="other-student-id",
        username="otheruser",
        email="other@mail.com",
        password="supersecret",  # In a real test, this would be hashed
        university="other-university",
        degree="other-hard-degree",
        is_validated=True,
        is_admin=False
    )
    
    session.add(admin_user)
    session.add(regular_user)
    session.commit()
    return {"admin": admin_user, "regular": regular_user}


@pytest.fixture(name="course")
def course_fixture(session: Session):
    course = Course(
        id=1,
        name="some-course",
        university="fiuba",
        university_course_id="some-university-id",
        description="some-description",
        active=True,
        semester="2019-2c",
        date_created=datetime.now(),
        last_updated=datetime.now(),
        image_uri="/some/uri"
    )
    session.add(course)
    session.commit()
    return course

@pytest.fixture(name="course_user")
def course_user_fixture(session: Session, course: Course, users: dict, roles: dict):
    course_user = CourseUser(
        id=1,
        course_id=course.id,
        user_id=users["admin"].id,
        role_id=roles["admin"].id,
        is_accepted=True,
        date_created=datetime.now(),
        last_updated=datetime.now()
    )
    session.add(course_user)
    session.commit()
    return course_user

@pytest.fixture(name="auth_token")
def auth_token_fixture(client: TestClient, users: dict):
    login_data = {
        "username_or_email": users["admin"].username,
        "password": "supersecret"
    }
    response = client.post("/api/v3/auth/login", json=login_data)
    assert response.status_code == 200
    result = response.json()
    assert result["access_token"] is not None
    assert result["token_type"] == "Bearer"
    return f"{result['token_type']} {result['access_token']}"


def test_get_all_courses(client: TestClient, course: Course, auth_token: str):
    response = client.get(
        "/api/v2/courses",
        headers={"Authorization": auth_token}
    )
    
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 1







