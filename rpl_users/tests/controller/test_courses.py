import logging
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session

from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.user import User
from rpl_users.src.repositories.models.course_user import CourseUser
from rpl_users.src.repositories.models.role import Role

# ====================== CREATE COURSE ====================== #


def test_create_course_with_admin_user_without_optional_fields(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["id"] is not None
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]


def test_create_course_with_admin_user_with_all_fields(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "description": "course description",
        "active": True,
        "semester": "2019-1c",
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
    assert result["id"] is not None
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["description"] == course_data["description"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]
    assert result["img_uri"] == course_data["img_uri"]


def test_cannot_create_course_with_regular_user(
    users_api_client: TestClient,
    example_users,
    regular_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
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
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    non_existing_user_id = example_users["admin"].id + 12345
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
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
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["id"] is not None
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]


def test_create_course_with_admin_user_using_regular_user_as_admin(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["regular"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["id"] is not None
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]


def test_cannot_create_the_same_course_twice(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
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


# ====================== GET ALL COURSES ====================== #


def test_get_all_courses_when_no_courses_created(
    users_api_client: TestClient, admin_auth_headers
):
    response = users_api_client.get("/api/v3/courses", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 0


def test_get_all_courses_of_admin_course_user(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    response = users_api_client.get("/api/v3/courses", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] is not None
    assert result[0]["name"] == course_data["name"]
    assert result[0]["university"] == course_data["university"]
    assert result[0]["active"] == course_data["active"]
    assert result[0]["semester"] == course_data["semester"]
    assert result[0]["semester_start_date"] == course_data["semester_start_date"]
    assert result[0]["semester_end_date"] == course_data["semester_end_date"]
    assert result[0]["enrolled"] is True
    assert result[0]["accepted"] is True


def test_get_all_courses_of_user_that_has_not_been_enrolled_to_a_course(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )

    response = users_api_client.get("/api/v3/courses", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] is not None
    assert result[0]["name"] == course_data["name"]
    assert result[0]["university"] == course_data["university"]
    assert result[0]["active"] == course_data["active"]
    assert result[0]["semester"] == course_data["semester"]
    assert result[0]["semester_start_date"] == course_data["semester_start_date"]
    assert result[0]["semester_end_date"] == course_data["semester_end_date"]
    assert result[0]["enrolled"] is False
    assert result[0]["accepted"] is False


def test_get_all_courses_of_user_that_has_been_enrolled_to_a_course(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    response = users_api_client.post(
        f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers
    )

    response = users_api_client.get("/api/v3/courses", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] is not None
    assert result[0]["name"] == course_data["name"]
    assert result[0]["university"] == course_data["university"]
    assert result[0]["active"] == course_data["active"]
    assert result[0]["semester"] == course_data["semester"]
    assert result[0]["semester_start_date"] == course_data["semester_start_date"]
    assert result[0]["semester_end_date"] == course_data["semester_end_date"]
    assert result[0]["enrolled"] is True
    assert result[0]["accepted"] is False


# ====================== EDIT COURSE ====================== #


def test_update_course_with_super_admin_user_without_optional_fields(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    course_data = {
        "name": "Algo2Mendez",
        "university": "UCA",
        "subject_id": "3001",
        "active": False,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
    }

    response = users_api_client.put(
        f"/api/v3/courses/{course_id}", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == course_id
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]


def test_update_course_with_super_admin_user_with_all_fields(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "description": "course description",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "img_uri": "https://example.com/image.png",
    }

    response = users_api_client.put(
        f"/api/v3/courses/{course_id}", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == course_id
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["description"] == course_data["description"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]
    assert result["img_uri"] == course_data["img_uri"]


def test_cannot_update_course_with_user_that_has_not_been_enrolled(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    course_data = {
        "name": "Algo2Mendez",
        "university": "UCA",
        "subject_id": "3001",
        "active": False,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
    }

    response = users_api_client.put(
        f"/api/v3/courses/{course_id}", json=course_data, headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    result = response.json()
    assert "Course user not found" in result["detail"]


def test_cannot_update_course_with_user_that_doest_have_course_edit_permission(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    users_api_client.post(
        f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers
    )

    course_data = {
        "name": "Algo2Mendez",
        "university": "UCA",
        "subject_id": "3001",
        "active": False,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
    }

    response = users_api_client.put(
        f"/api/v3/courses/{course_id}", json=course_data, headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    result = response.json()
    assert (
        "Course already exists with this name, university, and semester"
        in result["detail"]
    )


def test_update_course_with_user_that_has_course_edit_permission(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["regular"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    course_data = {
        "name": "Algo2Mendez",
        "university": "UCA",
        "subject_id": "3001",
        "active": False,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
    }

    response = users_api_client.put(
        f"/api/v3/courses/{course_id}", json=course_data, headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == course_id
    assert result["name"] == course_data["name"]
    assert result["university"] == course_data["university"]
    assert result["active"] == course_data["active"]
    assert result["semester"] == course_data["semester"]
    assert result["semester_start_date"] == course_data["semester_start_date"]
    assert result["semester_end_date"] == course_data["semester_end_date"]


def test_get_updated_course_of_user(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    course_data = {
        "name": "Algo2Mendez",
        "university": "UCA",
        "subject_id": "3001",
        "active": False,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
    }

    users_api_client.put(
        f"/api/v3/courses/{course_id}", json=course_data, headers=admin_auth_headers
    )

    response = users_api_client.get("/api/v3/courses", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] is not None
    assert result[0]["name"] == course_data["name"]
    assert result[0]["university"] == course_data["university"]
    assert result[0]["active"] == course_data["active"]
    assert result[0]["semester"] == course_data["semester"]
    assert result[0]["semester_start_date"] == course_data["semester_start_date"]
    assert result[0]["semester_end_date"] == course_data["semester_end_date"]
    assert result[0]["enrolled"] is True
    assert result[0]["accepted"] is True


@pytest.mark.only
def test_cannot_update_course_to_an_existing_one(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    another_course_data = {
        "name": "Algo2Mendez",
        "university": "UCA",
        "subject_id": "3001",
        "active": False,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=another_course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    response = users_api_client.put(
        f"/api/v3/courses/{course_id}", json=course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    result = response.json()
    assert (
        "Course already exists with this name, university, and semester"
        in result["detail"]
    )


# ====================== USER ENROLLMENT ====================== #


def test_enroll_regular_user_into_course(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
):
    course_data = {
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-1c",
        "semester_start_date": "2019-03-01T00:00:00",
        "semester_end_date": "2019-07-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    course_id = result["id"]

    response = users_api_client.post(
        f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] is not None
    assert result["name"] == "student"
    assert result["permissions"] == base_roles["student"].permissions.split(",")
    assert result["date_created"] is not None
    assert result["last_updated"] is not None

# cannot enroll non existing user
# cannot enroll user that is already enrolled
# cannot enroll user to non existing course