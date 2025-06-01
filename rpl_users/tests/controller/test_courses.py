from fastapi.testclient import TestClient
from fastapi import status
import httpx
from pytest_httpx import HTTPXMock

from rpl_users.src.config import env

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

    assert response.status_code == status.HTTP_403_FORBIDDEN

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

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert (
        "Course already exists with this name, university and semester"
        in result["detail"]
    )


# ====================== CLONE COURSE ====================== #


def test_clone_course_with_admin_user_with_all_fields(
    httpx_mock: HTTPXMock,
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
    course_id = result["id"]

    url = httpx.URL(
        url=f"{env.ACTIVITIES_API_URL}/api/v3/courses/{course_id}/activityCategories/clone",
        params={"to_course_id": course_id + 1},
    )
    httpx_mock.add_response(
        status_code=status.HTTP_201_CREATED,
        method="POST",
        url=url,
        match_headers=admin_auth_headers,
    )

    clone_course_data = {
        "id": course_id,
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=clone_course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["id"] is not None
    assert result["name"] == clone_course_data["name"]
    assert result["university"] == clone_course_data["university"]
    assert result["description"] == course_data["description"]
    assert result["active"] == clone_course_data["active"]
    assert result["semester"] == clone_course_data["semester"]
    assert result["semester_start_date"] == clone_course_data["semester_start_date"]
    assert result["semester_end_date"] == clone_course_data["semester_end_date"]
    assert result["img_uri"] == course_data["img_uri"]


def test_clone_non_existing_course(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
):
    non_existing_course_id = 99999999

    clone_course_data = {
        "id": non_existing_course_id,
        "name": "Algo1Mendez",
        "university": "FIUBA",
        "subject_id": "8001",
        "active": True,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
        "course_user_admin_user_id": example_users["admin"].id,
    }

    response = users_api_client.post(
        "/api/v3/courses", json=clone_course_data, headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]


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
    admin_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course = course_with_superadmin_as_admin_user["course"]

    response = users_api_client.get("/api/v3/courses", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] == course.id
    assert result[0]["name"] == course.name
    assert result[0]["university"] == course.university
    assert result[0]["active"] == course.active
    assert result[0]["semester"] == course.semester
    assert result[0]["semester_start_date"] == course.semester_start_date.isoformat()
    assert result[0]["semester_end_date"] == course.semester_end_date.isoformat()
    assert result[0]["enrolled"] is True
    assert result[0]["accepted"] is True


def test_get_all_courses_of_user_that_has_not_been_enrolled_to_a_course_yet(
    users_api_client: TestClient,
    regular_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course = course_with_superadmin_as_admin_user["course"]

    response = users_api_client.get("/api/v3/courses", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] == course.id
    assert result[0]["name"] == course.name
    assert result[0]["university"] == course.university
    assert result[0]["active"] == course.active
    assert result[0]["semester"] == course.semester
    assert result[0]["semester_start_date"] == course.semester_start_date.isoformat()
    assert result[0]["semester_end_date"] == course.semester_end_date.isoformat()
    assert result[0]["enrolled"] is False
    assert result[0]["accepted"] is False


def test_get_all_courses_of_user_that_has_been_enrolled_to_a_course(
    users_api_client: TestClient,
    regular_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course = course_with_superadmin_as_admin_user["course"]
    course_id = course.id

    response = users_api_client.post(
        f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers
    )

    response = users_api_client.get("/api/v3/courses", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] == course.id
    assert result[0]["name"] == course.name
    assert result[0]["university"] == course.university
    assert result[0]["active"] == course.active
    assert result[0]["semester"] == course.semester
    assert result[0]["semester_start_date"] == course.semester_start_date.isoformat()
    assert result[0]["semester_end_date"] == course.semester_end_date.isoformat()
    assert result[0]["enrolled"] is True
    assert result[0]["accepted"] is False


def test_get_all_courses_of_admin_course_user_when_multiple_courses(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    course_with_superadmin_as_admin_user,
):
    superadmin_course = course_with_superadmin_as_admin_user["course"]

    course_data = {
        "name": "Algo2Mendez",
        "university": "UCA",
        "subject_id": "3001",
        "active": False,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
        "course_user_admin_user_id": example_users["regular"].id,
    }
    regular_user_course_response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    ).json()

    response = users_api_client.get("/api/v3/courses", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 2

    result_superadmin_course = next(
        (r for r in result if r["id"] == superadmin_course.id)
    )
    assert result_superadmin_course["id"] == superadmin_course.id
    assert result_superadmin_course["name"] == superadmin_course.name
    assert result_superadmin_course["university"] == superadmin_course.university
    assert result_superadmin_course["active"] == superadmin_course.active
    assert result_superadmin_course["semester"] == superadmin_course.semester
    assert (
        result_superadmin_course["semester_start_date"]
        == superadmin_course.semester_start_date.isoformat()
    )
    assert (
        result_superadmin_course["semester_end_date"]
        == superadmin_course.semester_end_date.isoformat()
    )
    assert result_superadmin_course["enrolled"] is True
    assert result_superadmin_course["accepted"] is True

    result_regular_user_course = next(
        (r for r in result if r["id"] == regular_user_course_response["id"])
    )
    assert result_regular_user_course["id"] == regular_user_course_response["id"]
    assert result_regular_user_course["name"] == regular_user_course_response["name"]
    assert (
        result_regular_user_course["university"]
        == regular_user_course_response["university"]
    )
    assert (
        result_regular_user_course["active"] == regular_user_course_response["active"]
    )
    assert (
        result_regular_user_course["semester"]
        == regular_user_course_response["semester"]
    )
    assert (
        result_regular_user_course["semester_start_date"]
        == regular_user_course_response["semester_start_date"]
    )
    assert (
        result_regular_user_course["semester_end_date"]
        == regular_user_course_response["semester_end_date"]
    )
    assert result_regular_user_course["enrolled"] is False
    assert result_regular_user_course["accepted"] is False


# ====================== GET COURSE ====================== #


def test_get_course_details_using_super_admin_user(
    users_api_client: TestClient,
    admin_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course = course_with_superadmin_as_admin_user["course"]
    course_id = course.id

    response = users_api_client.get(
        f"/api/v3/courses/{course_id}", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == course.id
    assert result["name"] == course.name
    assert result["university"] == course.university
    assert result["active"] == course.active
    assert result["semester"] == course.semester
    assert result["semester_start_date"] == course.semester_start_date.isoformat()
    assert result["semester_end_date"] == course.semester_end_date.isoformat()


def test_get_course_details_using_user_with_admin_role_permissions(
    users_api_client: TestClient,
    regular_auth_headers,
    course_with_regular_user_as_admin_user,
):
    course = course_with_regular_user_as_admin_user["course"]
    course_id = course.id

    response = users_api_client.get(
        f"/api/v3/courses/{course_id}", headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == course.id
    assert result["name"] == course.name
    assert result["university"] == course.university
    assert result["active"] == course.active
    assert result["semester"] == course.semester
    assert result["semester_start_date"] == course.semester_start_date.isoformat()
    assert result["semester_end_date"] == course.semester_end_date.isoformat()


def test_get_course_details_using_user_with_student_role_permissions(
    users_api_client: TestClient,
    regular_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course = course_with_superadmin_as_admin_user["course"]
    course_id = course.id

    users_api_client.post(
        f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers
    )

    response = users_api_client.get(
        f"/api/v3/courses/{course_id}", headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == course.id
    assert result["name"] == course.name
    assert result["university"] == course.university
    assert result["active"] == course.active
    assert result["semester"] == course.semester
    assert result["semester_start_date"] == course.semester_start_date.isoformat()
    assert result["semester_end_date"] == course.semester_end_date.isoformat()


def test_cannot_get_course_details_from_non_existing_course(
    users_api_client: TestClient,
    admin_auth_headers,
):
    non_existing_course_id = 99999999

    response = users_api_client.get(
        f"/api/v3/courses/{non_existing_course_id}", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]


def test_cannot_get_course_details_using_user_that_has_not_been_enrolled_yet(
    users_api_client: TestClient,
    regular_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course = course_with_superadmin_as_admin_user["course"]
    course_id = course.id

    response = users_api_client.get(
        f"/api/v3/courses/{course_id}", headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert (
        "Couser user not found or does not have required permissions"
        in result["detail"]
    )


# ====================== UPDATE COURSE ====================== #


def test_update_course_with_super_admin_user_without_optional_fields(
    users_api_client: TestClient,
    admin_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

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
    admin_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

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
    regular_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

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

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert (
        "Couser user not found or does not have required permissions"
        in result["detail"]
    )


def test_cannot_update_course_using_user_with_student_role_permissions(
    users_api_client: TestClient,
    regular_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

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

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert (
        "Couser user not found or does not have required permissions"
        in result["detail"]
    )


def test_update_course_using_user_with_admin_role_permissions(
    users_api_client: TestClient,
    regular_auth_headers,
    course_with_regular_user_as_admin_user,
):
    course_id = course_with_regular_user_as_admin_user["course"].id

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
    admin_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

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
    assert result[0]["id"] == course_id
    assert result[0]["name"] == course_data["name"]
    assert result[0]["university"] == course_data["university"]
    assert result[0]["active"] == course_data["active"]
    assert result[0]["semester"] == course_data["semester"]
    assert result[0]["semester_start_date"] == course_data["semester_start_date"]
    assert result[0]["semester_end_date"] == course_data["semester_end_date"]
    assert result[0]["enrolled"] is True
    assert result[0]["accepted"] is True


def test_cannot_update_non_existing_course(
    users_api_client: TestClient,
    admin_auth_headers,
):
    non_existing_course_id = 99999999

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
        f"/api/v3/courses/{non_existing_course_id}",
        json=course_data,
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]
