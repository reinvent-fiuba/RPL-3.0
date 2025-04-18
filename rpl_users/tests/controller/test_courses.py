import logging
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.models.course_user import CourseUser
from rpl_users.src.repositories.models.role import Role


def test_get_all_courses(
    client: TestClient, admin_auth_headers, example_course: Course
):
    response = client.get("/api/v3/courses", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    courses = response.json()
    # assert len(courses) == 1


def test_create_course_with_admin_user_success(client: TestClient, admin_auth_headers):
    course_json = {
        "name": "new_course",
        "university": "fiuba",
        "subject_id": "12345",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-08-01T00:00:00",
        "semester_end_date": "2019-08-01T00:00:00",
        "course_user_admin_user_id": "1",
    }

    response = client.post(
        "/api/v3/courses", json=course_json, headers=admin_auth_headers
    )
    logging.warning("Response: %s", response.json())

    course = response.json()
    assert response.status_code == status.HTTP_201_CREATED

    assert course["id"] is not None
    assert course["name"] == course_json["name"]
    assert course["university"] == course_json["university"]
    assert course["subject_id"] == course_json["subject_id"]
    assert course["active"] == course_json["active"]
    assert course["semester"] == course_json["semester"]
