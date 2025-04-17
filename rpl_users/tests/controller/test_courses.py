from datetime import datetime, timedelta
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


from rpl_users.src.deps.database import get_db_session
from rpl_users.src.main import app
from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.models.base_model import Base
from rpl_users.src.repositories.models.course_user import CourseUser
from rpl_users.src.repositories.models.role import Role

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
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
    hasher = PasswordHash((BcryptHasher(rounds=10),))
    admin_user = User(
        id=1,
        name="some-name",
        surname="some-surname",
        student_id="some-student-id",
        username="username",
        email="admin@mail.com",
        password=hasher.hash("supersecret"),
        university="some-university",
        degree="some-hard-degree",
        email_validated=True,
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
        password=hasher.hash("supersecret"), 
        university="other-university",
        degree="other-hard-degree",
        email_validated=True,
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
        subject_id="some-university-id",
        description="some-description",
        active=True,
        semester="2019-2c",
        semester_start_date=datetime.now() - timedelta(days=60),
        semester_end_date=datetime.now() + timedelta(days=60),
        date_created=datetime.now(),
        last_updated=datetime.now(),
        img_uri="/some/uri",
        deleted=False,
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
        "username_or_email": "admin@mail.com",
        "password": "supersecret"
    }
    response = client.post("/api/v3/auth/login", json=login_data)
    assert response.status_code == 200
    result = response.json()
    assert result["access_token"] is not None
    assert result["token_type"] == "Bearer"
    return f"{result['token_type']} {result['access_token']}"

@pytest.fixture(name="admin_role")
def admin_role_fixture(session: Session):
    admin_role = Role(
        id=1,
        name="admin",
        permissions=json.dumps(["create_course", "delete_course", "update_course"]),
    )
    session.add(admin_role)
    session.commit()
    return admin_role


def test_get_all_courses(client: TestClient, course: Course, auth_token: str):
    login_data = {
        "username_or_email": "admin@mail.com",
        "password": "supersecret"
    }
    client.post("/api/v3/auth/login", json=login_data)
    response = client.get("/api/v3/courses", headers={"Authorization": auth_token})
    
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 1

def test_create_course_with_admin_user_success(client: TestClient, auth_token: str, admin_role: Role):
    login_data = {
        "username_or_email": "admin@mail.com",
        "password": "supersecret"
    }
    client.post("/api/v3/auth/login", json=login_data)
    response = client.get("/api/v3/courses", headers={"Authorization": auth_token})

    course_json = {
        "name": "new_course",
        "university": "fiuba",
        "subject_id": "12345",
        "description": "some-description",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-10-01",
        "semester_end_date": "2019-12-01",
        "img_uri": "/some/uri",
        "course_admin_id": "1"
    }

    response = client.post("/api/v3/courses", json=course_json, headers={"Authorization": auth_token})
    
    course = response.json()
    assert response.status_code == 201

    assert course["id"] is not None
    assert course["name"] == course_json["name"]
    assert course["university"] == course_json["university"]
    assert course["subject_id"] == course_json["subject_id"]
    assert course["description"] == course_json["description"]
    assert course["active"] == course_json["active"]
    assert course["semester"] == course_json["semester"]
    assert course["semester_start_date"] == course_json["semester_start_date"] + 'T00:00:00'
    assert course["semester_end_date"] == course_json["semester_end_date"] + 'T00:00:00'
    assert course["img_uri"] == course_json["img_uri"]
    
