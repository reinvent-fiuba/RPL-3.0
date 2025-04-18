import logging
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.models.course_user import CourseUser
from rpl_users.src.repositories.models.role import Role


@pytest.fixture(scope="function", autouse=True)
def cleanup_trash_data(users_api_dbsession: Session):
    yield
    users_api_dbsession.query(Course).delete()
    users_api_dbsession.commit()


def test_create_course_with_admin_user_without_optional_fields(
    users_api_client: TestClient, admin_auth_headers, example_users
):
    course_data = {
        "name": "new course",
        "university": "fiuba",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]


def test_create_course_with_admin_user_with_all_fields(
    users_api_client: TestClient, admin_auth_headers, example_users
):
    course_data = {
        "name": "new course",
        "university": "fiuba",
        "subject_id": "8001",
        "description": "course description",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "img_uri": "https://example.com/image.png",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["description"] == course_data["description"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]
    assert result["img_uri"] == course_data["img_uri"]


def test_cannot_create_course_with_regular_user(
    users_api_client: TestClient, regular_auth_headers, example_users
):
    course_data = {
        "name": "new course",
        "university": "fiuba",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    result = response.json()
    assert "Only admins can create courses" in result["detail"]


def test_cannot_create_course_with_admin_user_using_non_existing_user_as_admin(
    users_api_client: TestClient, admin_auth_headers, example_users
):
    non_existing_user_id = example_users["admin"].id + 12345
    course_data = {
        "name": "new course",
        "university": "fiuba",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": non_existing_user_id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "User not found" in result["detail"]


def test_create_course_with_admin_user_using_admin_user_as_admin(
    users_api_client: TestClient, admin_auth_headers, example_users
):
    course_data = {
        "name": "new course",
        "university": "fiuba",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]


def test_create_course_with_admin_user_using_regular_user_as_admin(
    users_api_client: TestClient, admin_auth_headers, example_users
):
    course_data = {
        "name": "new course",
        "university": "fiuba",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["regular"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]


def test_cannot_create_the_same_course_twice(
    users_api_client: TestClient, admin_auth_headers, example_users
):
    course_data = {
        "name": "new course",
        "university": "fiuba",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["regular"].id,
    }

    users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    result = response.json()
    assert (
        "Course already exists with this name, university, and semester"
        in result["detail"]
    )
