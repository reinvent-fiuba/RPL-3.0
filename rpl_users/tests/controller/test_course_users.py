from fastapi.testclient import TestClient
from fastapi import status

from rpl_users.src.repositories.models.role import Role

# ====================== USER ENROLLMENT ====================== #


def test_enroll_regular_user_into_course(
    users_api_client: TestClient, regular_auth_headers, base_roles, course_with_superadmin_as_admin_user
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] is not None
    assert result["name"] == "student"
    assert result["permissions"] == base_roles["student"].permissions.split(",")
    assert result["date_created"] is not None
    assert result["last_updated"] is not None


def test_cannot_enroll_an_user_twice(
    users_api_client: TestClient, regular_auth_headers, course_with_superadmin_as_admin_user
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "User is already enrolled in the course" in result["detail"]


def test_cannot_enroll_an_user_to_non_existing_course(users_api_client: TestClient, admin_auth_headers):
    non_existing_course_id = 99999999

    response = users_api_client.post(
        f"/api/v3/courses/{non_existing_course_id}/enroll", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]


# ====================== USER UNENROLLMENT ====================== #


def test_unenroll_course_user_from_course(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    response = users_api_client.post(f"/api/v3/courses/{course_id}/unenroll", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = users_api_client.get(f"/api/v3/courses/{course_id}/users", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1

    admin_user = next((r for r in result if r["user_id"] == example_users["admin"].id))
    assert admin_user["user_id"] == example_users["admin"].id
    assert admin_user["course_id"] == course_id
    assert admin_user["course_user_id"] is not None
    assert admin_user["name"] == example_users["admin"].name
    assert admin_user["surname"] == example_users["admin"].surname
    assert admin_user["student_id"] == example_users["admin"].student_id
    assert admin_user["username"] == example_users["admin"].username
    assert admin_user["email"] == example_users["admin"].email
    assert admin_user["email_validated"] == example_users["admin"].email_validated
    assert admin_user["university"] == example_users["admin"].university
    assert admin_user["degree"] == example_users["admin"].degree
    assert admin_user["role"] == base_roles["course_admin"].name
    assert admin_user["accepted"] is True
    assert admin_user["date_created"] is not None
    assert admin_user["last_updated"] is not None


def test_cannot_unenroll_course_user_from_course_that_has_not_been_enrolled_yet(
    users_api_client: TestClient, regular_auth_headers, course_with_superadmin_as_admin_user
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/unenroll", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "Couser user not found or does not have required permissions" in result["detail"]


def test_cannot_unenroll_course_user_from_non_existing_course(
    users_api_client: TestClient, admin_auth_headers
):
    non_existing_course_id = 99999999

    response = users_api_client.post(
        f"/api/v3/courses/{non_existing_course_id}/unenroll", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]


# ====================== GET PERMISSIONS ====================== #


def test_get_course_user_permissions_of_user_with_admin_role(
    users_api_client: TestClient,
    admin_auth_headers,
    base_roles: dict[str, Role],
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    response = users_api_client.get(f"/api/v3/courses/{course_id}/permissions", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result == base_roles["course_admin"].get_permissions() + ["superadmin"]


def test_get_course_user_permissions_of_user_with_student_role(
    users_api_client: TestClient,
    regular_auth_headers,
    base_roles: dict[str, Role],
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    response = users_api_client.get(f"/api/v3/courses/{course_id}/permissions", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result == base_roles["student"].get_permissions()


def test_cannot_get_course_user_permissions_using_non_existing_course(
    users_api_client: TestClient, admin_auth_headers
):
    non_existing_course_id = 99999999

    response = users_api_client.get(
        f"/api/v3/courses/{non_existing_course_id}/permissions", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]


def test_cannot_get_course_user_permissions_using_user_that_has_not_been_enrolled_yet(
    users_api_client: TestClient, regular_auth_headers, course_with_superadmin_as_admin_user
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    response = users_api_client.get(f"/api/v3/courses/{course_id}/permissions", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "Couser user not found or does not have required permissions" in result["detail"]


# ====================== GET COURSE USERS ====================== #


def test_get_all_course_users_from_course_when_only_admin_user(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    response = users_api_client.get(f"/api/v3/courses/{course_id}/users", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1

    admin_user = next((r for r in result if r["user_id"] == example_users["admin"].id))
    assert admin_user["user_id"] == example_users["admin"].id
    assert admin_user["course_id"] == course_id
    assert admin_user["course_user_id"] is not None
    assert admin_user["name"] == example_users["admin"].name
    assert admin_user["surname"] == example_users["admin"].surname
    assert admin_user["student_id"] == example_users["admin"].student_id
    assert admin_user["username"] == example_users["admin"].username
    assert admin_user["email"] == example_users["admin"].email
    assert admin_user["email_validated"] == example_users["admin"].email_validated
    assert admin_user["university"] == example_users["admin"].university
    assert admin_user["degree"] == example_users["admin"].degree
    assert admin_user["role"] == base_roles["course_admin"].name
    assert admin_user["accepted"] is True
    assert admin_user["date_created"] is not None
    assert admin_user["last_updated"] is not None


def test_get_all_course_users_from_course_when_multiple_users(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    response = users_api_client.get(f"/api/v3/courses/{course_id}/users", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 2

    admin_user = next((r for r in result if r["user_id"] == example_users["admin"].id))
    assert admin_user["user_id"] == example_users["admin"].id
    assert admin_user["course_id"] == course_id
    assert admin_user["course_user_id"] is not None
    assert admin_user["name"] == example_users["admin"].name
    assert admin_user["surname"] == example_users["admin"].surname
    assert admin_user["student_id"] == example_users["admin"].student_id
    assert admin_user["username"] == example_users["admin"].username
    assert admin_user["email"] == example_users["admin"].email
    assert admin_user["email_validated"] == example_users["admin"].email_validated
    assert admin_user["university"] == example_users["admin"].university
    assert admin_user["degree"] == example_users["admin"].degree
    assert admin_user["role"] == base_roles["course_admin"].name
    assert admin_user["accepted"] is True
    assert admin_user["date_created"] is not None
    assert admin_user["last_updated"] is not None

    student_user = next((r for r in result if r["user_id"] == example_users["regular"].id))
    assert student_user["user_id"] == example_users["regular"].id
    assert student_user["course_id"] == course_id
    assert student_user["course_user_id"] is not None
    assert student_user["name"] == example_users["regular"].name
    assert student_user["surname"] == example_users["regular"].surname
    assert student_user["student_id"] == example_users["regular"].student_id
    assert student_user["username"] == example_users["regular"].username
    assert student_user["email"] == example_users["regular"].email
    assert student_user["email_validated"] == example_users["regular"].email_validated
    assert student_user["university"] == example_users["regular"].university
    assert student_user["degree"] == example_users["regular"].degree
    assert student_user["role"] == base_roles["student"].name
    assert student_user["accepted"] is False
    assert student_user["date_created"] is not None
    assert student_user["last_updated"] is not None


def test_get_all_student_course_users_from_course_when_multiple_users(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    response = users_api_client.get(
        f"/api/v3/courses/{course_id}/users",
        headers=admin_auth_headers,
        params={"role_name": base_roles["student"].name},
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1

    student_user = next((r for r in result if r["user_id"] == example_users["regular"].id))
    assert student_user["user_id"] == example_users["regular"].id
    assert student_user["course_id"] == course_id
    assert student_user["course_user_id"] is not None
    assert student_user["name"] == example_users["regular"].name
    assert student_user["surname"] == example_users["regular"].surname
    assert student_user["student_id"] == example_users["regular"].student_id
    assert student_user["username"] == example_users["regular"].username
    assert student_user["email"] == example_users["regular"].email
    assert student_user["email_validated"] == example_users["regular"].email_validated
    assert student_user["university"] == example_users["regular"].university
    assert student_user["degree"] == example_users["regular"].degree
    assert student_user["role"] == base_roles["student"].name
    assert student_user["accepted"] is False
    assert student_user["date_created"] is not None
    assert student_user["last_updated"] is not None


def test_get_course_user_with_student_id_from_course_when_multiple_users(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    response = users_api_client.get(
        f"/api/v3/courses/{course_id}/users",
        headers=admin_auth_headers,
        params={"student_id": example_users["regular"].student_id},
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1

    student_user = next((r for r in result if r["user_id"] == example_users["regular"].id))
    assert student_user["user_id"] == example_users["regular"].id
    assert student_user["course_id"] == course_id
    assert student_user["course_user_id"] is not None
    assert student_user["name"] == example_users["regular"].name
    assert student_user["surname"] == example_users["regular"].surname
    assert student_user["student_id"] == example_users["regular"].student_id
    assert student_user["username"] == example_users["regular"].username
    assert student_user["email"] == example_users["regular"].email
    assert student_user["email_validated"] == example_users["regular"].email_validated
    assert student_user["university"] == example_users["regular"].university
    assert student_user["degree"] == example_users["regular"].degree
    assert student_user["role"] == base_roles["student"].name
    assert student_user["accepted"] is False
    assert student_user["date_created"] is not None
    assert student_user["last_updated"] is not None


def test_cannot_get_all_course_users_from_non_existing_course(
    users_api_client: TestClient, admin_auth_headers
):
    non_existing_course_id = 99999999

    response = users_api_client.get(
        f"/api/v3/courses/{non_existing_course_id}/users", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]


def test_cannot_get_all_course_users_from_course_using_user_that_has_not_been_enrolled_yet(
    users_api_client: TestClient, regular_auth_headers, course_with_superadmin_as_admin_user
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    response = users_api_client.get(f"/api/v3/courses/{course_id}/users", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "Couser user not found or does not have required permissions" in result["detail"]


def test_get_all_course_users_from_course_when_multiple_users_after_updating(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    course_user_data = {"accepted": True, "role": base_roles["student"].name}

    users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{example_users["regular"].id}",
        json=course_user_data,
        headers=admin_auth_headers,
    )

    response = users_api_client.get(f"/api/v3/courses/{course_id}/users", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 2

    admin_user = next((r for r in result if r["user_id"] == example_users["admin"].id))
    assert admin_user["user_id"] == example_users["admin"].id
    assert admin_user["course_id"] == course_id
    assert admin_user["course_user_id"] is not None
    assert admin_user["name"] == example_users["admin"].name
    assert admin_user["surname"] == example_users["admin"].surname
    assert admin_user["student_id"] == example_users["admin"].student_id
    assert admin_user["username"] == example_users["admin"].username
    assert admin_user["email"] == example_users["admin"].email
    assert admin_user["email_validated"] == example_users["admin"].email_validated
    assert admin_user["university"] == example_users["admin"].university
    assert admin_user["degree"] == example_users["admin"].degree
    assert admin_user["role"] == base_roles["course_admin"].name
    assert admin_user["accepted"] is True
    assert admin_user["date_created"] is not None
    assert admin_user["last_updated"] is not None

    student_user = next((r for r in result if r["user_id"] == example_users["regular"].id))
    assert student_user["user_id"] == example_users["regular"].id
    assert student_user["course_id"] == course_id
    assert student_user["course_user_id"] is not None
    assert student_user["name"] == example_users["regular"].name
    assert student_user["surname"] == example_users["regular"].surname
    assert student_user["student_id"] == example_users["regular"].student_id
    assert student_user["username"] == example_users["regular"].username
    assert student_user["email"] == example_users["regular"].email
    assert student_user["email_validated"] == example_users["regular"].email_validated
    assert student_user["university"] == example_users["regular"].university
    assert student_user["degree"] == example_users["regular"].degree
    assert student_user["role"] == base_roles["student"].name
    assert student_user["accepted"] is True
    assert student_user["date_created"] is not None
    assert student_user["last_updated"] is not None


# ====================== UPDATE COURSE USERS ====================== #


def test_update_course_user_using_super_admin_user(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    base_roles,
    course_with_regular_user_as_admin_user,
):
    course_id = course_with_regular_user_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=admin_auth_headers)

    course_user_data = {"accepted": True, "role": base_roles["course_admin"].name}

    response = users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}",
        json=course_user_data,
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["user_id"] == example_users["admin"].id
    assert result["course_id"] == course_id
    assert result["course_user_id"] is not None
    assert result["name"] == example_users["admin"].name
    assert result["surname"] == example_users["admin"].surname
    assert result["student_id"] == example_users["admin"].student_id
    assert result["username"] == example_users["admin"].username
    assert result["email"] == example_users["admin"].email
    assert result["email_validated"] == example_users["admin"].email_validated
    assert result["university"] == example_users["admin"].university
    assert result["degree"] == example_users["admin"].degree
    assert result["role"] == base_roles["course_admin"].name
    assert result["accepted"] is True
    assert result["date_created"] is not None
    assert result["last_updated"] is not None


def test_update_course_user_using_admin_user(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_regular_user_as_admin_user,
):
    course_id = course_with_regular_user_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=admin_auth_headers)

    course_user_data = {"accepted": True, "role": base_roles["course_admin"].name}

    response = users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}",
        json=course_user_data,
        headers=regular_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["user_id"] == example_users["admin"].id
    assert result["course_id"] == course_id
    assert result["course_user_id"] is not None
    assert result["name"] == example_users["admin"].name
    assert result["surname"] == example_users["admin"].surname
    assert result["student_id"] == example_users["admin"].student_id
    assert result["username"] == example_users["admin"].username
    assert result["email"] == example_users["admin"].email
    assert result["email_validated"] == example_users["admin"].email_validated
    assert result["university"] == example_users["admin"].university
    assert result["degree"] == example_users["admin"].degree
    assert result["role"] == base_roles["course_admin"].name
    assert result["accepted"] is True
    assert result["date_created"] is not None
    assert result["last_updated"] is not None


def test_accept_user_should_send_course_acceptance_email(
    users_api_client: TestClient,
    email_handler,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_regular_user_as_admin_user,
):
    course_id = course_with_regular_user_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=admin_auth_headers)

    course_user_data = {"accepted": True, "role": base_roles["course_admin"].name}

    response = users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}",
        json=course_user_data,
        headers=regular_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(email_handler.emails_sent()) == 1
    email_sent = email_handler.emails_sent()[0]
    assert email_sent["type"] == "course_acceptance"
    assert email_sent["to_address"] == example_users["admin"].email
    assert email_sent["user_data"].id == example_users["admin"].id
    assert email_sent["course_data"].id == course_id


def test_not_accept_user_should_not_send_course_acceptance_email(
    users_api_client: TestClient,
    email_handler,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_regular_user_as_admin_user,
):
    course_id = course_with_regular_user_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=admin_auth_headers)

    course_user_data = {"accepted": False, "role": base_roles["course_admin"].name}

    response = users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}",
        json=course_user_data,
        headers=regular_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(email_handler.emails_sent()) == 0

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["user_id"] == example_users["admin"].id
    assert result["course_id"] == course_id
    assert result["course_user_id"] is not None
    assert result["name"] == example_users["admin"].name
    assert result["surname"] == example_users["admin"].surname
    assert result["student_id"] == example_users["admin"].student_id
    assert result["username"] == example_users["admin"].username
    assert result["email"] == example_users["admin"].email
    assert result["email_validated"] == example_users["admin"].email_validated
    assert result["university"] == example_users["admin"].university
    assert result["degree"] == example_users["admin"].degree
    assert result["role"] == base_roles["course_admin"].name
    assert result["accepted"] is False
    assert result["date_created"] is not None
    assert result["last_updated"] is not None


def test_cannot_update_user_that_has_not_been_enrolled_yet(
    users_api_client: TestClient,
    email_handler,
    example_users,
    admin_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    course_user_data = {"accepted": True, "role": base_roles["course_admin"].name}

    response = users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{example_users["regular"].id}",
        json=course_user_data,
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "Couser user not found or does not have required permissions" in result["detail"]

    assert len(email_handler.emails_sent()) == 0


def test_cannot_update_course_user_using_student_user(
    users_api_client: TestClient,
    email_handler,
    example_users,
    regular_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    course_user_data = {"accepted": True, "role": base_roles["course_admin"].name}

    response = users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}",
        json=course_user_data,
        headers=regular_auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "Couser user not found or does not have required permissions" in result["detail"]

    assert len(email_handler.emails_sent()) == 0


def test_cannot_update_course_user_to_non_existing_role(
    users_api_client: TestClient,
    email_handler,
    example_users,
    admin_auth_headers,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    course_user_data = {"accepted": True, "role": "non existing role"}

    response = users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}",
        json=course_user_data,
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Role not found" in result["detail"]

    assert len(email_handler.emails_sent()) == 0


def test_cannot_update_course_user_of_non_existing_course(
    users_api_client: TestClient, email_handler, example_users, admin_auth_headers, base_roles
):
    non_existing_course_id = 99999999

    course_user_data = {"accepted": True, "role": base_roles["course_admin"].name}

    response = users_api_client.patch(
        f"/api/v3/courses/{non_existing_course_id}/users/{example_users["admin"].id}",
        json=course_user_data,
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]

    assert len(email_handler.emails_sent()) == 0


def test_cannot_update_course_user_of_non_existing_user(
    users_api_client: TestClient,
    email_handler,
    admin_auth_headers,
    base_roles,
    course_with_superadmin_as_admin_user,
):
    course_id = course_with_superadmin_as_admin_user["course"].id
    non_existing_user_id = 99999999

    course_user_data = {"accepted": True, "role": base_roles["course_admin"].name}

    response = users_api_client.patch(
        f"/api/v3/courses/{course_id}/users/{non_existing_user_id}",
        json=course_user_data,
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "User not found" in result["detail"]

    assert len(email_handler.emails_sent()) == 0


# ====================== DELETE COURSE USER ====================== #


def test_delete_course_user_from_course_using_super_admin_user(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_regular_user_as_admin_user,
):
    course_id = course_with_regular_user_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=admin_auth_headers)

    response = users_api_client.delete(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = users_api_client.get(f"/api/v3/courses/{course_id}/users", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1

    admin_user = next((r for r in result if r["user_id"] == example_users["regular"].id))
    assert admin_user["user_id"] == example_users["regular"].id
    assert admin_user["course_id"] == course_id
    assert admin_user["course_user_id"] is not None
    assert admin_user["name"] == example_users["regular"].name
    assert admin_user["surname"] == example_users["regular"].surname
    assert admin_user["student_id"] == example_users["regular"].student_id
    assert admin_user["username"] == example_users["regular"].username
    assert admin_user["email"] == example_users["regular"].email
    assert admin_user["email_validated"] == example_users["regular"].email_validated
    assert admin_user["university"] == example_users["regular"].university
    assert admin_user["degree"] == example_users["regular"].degree
    assert admin_user["role"] == base_roles["course_admin"].name
    assert admin_user["accepted"] is True
    assert admin_user["date_created"] is not None
    assert admin_user["last_updated"] is not None


def test_delete_course_user_from_course_using_admin_user(
    users_api_client: TestClient,
    example_users,
    admin_auth_headers,
    regular_auth_headers,
    base_roles,
    course_with_regular_user_as_admin_user,
):
    course_id = course_with_regular_user_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=admin_auth_headers)

    response = users_api_client.delete(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}", headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = users_api_client.get(f"/api/v3/courses/{course_id}/users", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1

    admin_user = next((r for r in result if r["user_id"] == example_users["regular"].id))
    assert admin_user["user_id"] == example_users["regular"].id
    assert admin_user["course_id"] == course_id
    assert admin_user["course_user_id"] is not None
    assert admin_user["name"] == example_users["regular"].name
    assert admin_user["surname"] == example_users["regular"].surname
    assert admin_user["student_id"] == example_users["regular"].student_id
    assert admin_user["username"] == example_users["regular"].username
    assert admin_user["email"] == example_users["regular"].email
    assert admin_user["email_validated"] == example_users["regular"].email_validated
    assert admin_user["university"] == example_users["regular"].university
    assert admin_user["degree"] == example_users["regular"].degree
    assert admin_user["role"] == base_roles["course_admin"].name
    assert admin_user["accepted"] is True
    assert admin_user["date_created"] is not None
    assert admin_user["last_updated"] is not None


def test_cannot_delete_course_user_from_course_that_has_not_been_enrolled_yet(
    users_api_client: TestClient, example_users, regular_auth_headers, course_with_regular_user_as_admin_user
):
    course_id = course_with_regular_user_as_admin_user["course"].id

    response = users_api_client.delete(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}", headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "Couser user not found or does not have required permissions" in result["detail"]


def test_cannot_delete_course_user_using_student_user(
    users_api_client: TestClient, example_users, regular_auth_headers, course_with_superadmin_as_admin_user
):
    course_id = course_with_superadmin_as_admin_user["course"].id

    response = users_api_client.post(f"/api/v3/courses/{course_id}/enroll", headers=regular_auth_headers)

    response = users_api_client.delete(
        f"/api/v3/courses/{course_id}/users/{example_users["admin"].id}", headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "Couser user not found or does not have required permissions" in result["detail"]


def test_cannot_delete_course_user_from_non_existing_course(
    users_api_client: TestClient, example_users, admin_auth_headers
):
    non_existing_course_id = 99999999

    response = users_api_client.delete(
        f"/api/v3/courses/{non_existing_course_id}/users/{example_users["admin"].id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "Course not found" in result["detail"]


def test_cannot_delete_course_user_of_non_existing_user(
    users_api_client: TestClient, admin_auth_headers, course_with_superadmin_as_admin_user
):
    course_id = course_with_superadmin_as_admin_user["course"].id
    non_existing_user_id = 99999999

    response = users_api_client.delete(
        f"/api/v3/courses/{course_id}/users/{non_existing_user_id}", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "User not found" in result["detail"]


# ====================== QUERYING COURSES OF COURSE USER ====================== #


def test_get_courses_of_user_when_user_has_not_been_enrolled_yet(
    users_api_client: TestClient, example_users, admin_auth_headers
):
    response = users_api_client.get(
        f"/api/v3/users/{example_users["admin"].id}/courses", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 0


def test_get_courses_of_user_when_user_is_enrolled_on_one_course(
    users_api_client: TestClient, admin_auth_headers, course_with_superadmin_as_admin_user
):
    course = course_with_superadmin_as_admin_user["course"]
    admin_user = course_with_superadmin_as_admin_user["admin_course_user"]

    response = users_api_client.get(f"/api/v3/users/{admin_user.id}/courses", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] == course.id
    assert result[0]["name"] == course.name
    assert result[0]["university"] == course.university
    assert result[0]["active"] == course.active
    assert result[0]["semester"] == course.semester
    assert result[0]["semester_start_date"] == course.semester_start_date.date().isoformat()
    assert result[0]["semester_end_date"] == course.semester_end_date.date().isoformat()


def test_get_courses_of_user_when_user_is_enrolled_on_multiple_courses(
    users_api_client: TestClient, admin_auth_headers, course_with_superadmin_as_admin_user
):
    course_1 = course_with_superadmin_as_admin_user["course"]
    admin_user = course_with_superadmin_as_admin_user["admin_course_user"]

    course_data = {
        "name": "Algo2Mendez",
        "university": "UCA",
        "subject_id": "3001",
        "active": False,
        "semester": "2019-2c",
        "semester_start_date": "2019-07-01T00:00:00",
        "semester_end_date": "2019-12-01T00:00:00",
        "course_user_admin_user_id": admin_user.id,
    }
    course_2_response = users_api_client.post(
        "/api/v3/courses", json=course_data, headers=admin_auth_headers
    ).json()

    response = users_api_client.get(f"/api/v3/users/{admin_user.id}/courses", headers=admin_auth_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 2

    result_course_1 = next((r for r in result if r["id"] == course_1.id))
    assert result_course_1["id"] == course_1.id
    assert result_course_1["name"] == course_1.name
    assert result_course_1["university"] == course_1.university
    assert result_course_1["active"] == course_1.active
    assert result_course_1["semester"] == course_1.semester
    assert result_course_1["semester_start_date"] == course_1.semester_start_date.date().isoformat()
    assert result_course_1["semester_end_date"] == course_1.semester_end_date.date().isoformat()

    result_course_2 = next((r for r in result if r["id"] == course_2_response["id"]))
    assert result_course_2["id"] == course_2_response["id"]
    assert result_course_2["name"] == course_2_response["name"]
    assert result_course_2["university"] == course_2_response["university"]
    assert result_course_2["active"] == course_2_response["active"]
    assert result_course_2["semester"] == course_2_response["semester"]
    assert result_course_2["semester_start_date"] == course_2_response["semester_start_date"]
    assert result_course_2["semester_end_date"] == course_2_response["semester_end_date"]


def test_cannot_get_courses_of_non_existing_user(users_api_client: TestClient, admin_auth_headers):
    non_existing_user_id = 99999999

    response = users_api_client.get(
        f"/api/v3/users/{non_existing_user_id}/courses", headers=admin_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = response.json()
    assert "User not found" in result["detail"]


def test_cannot_get_courses_of_another_user(
    users_api_client: TestClient, regular_auth_headers, course_with_superadmin_as_admin_user
):
    admin_user = course_with_superadmin_as_admin_user["admin_course_user"]

    response = users_api_client.get(f"/api/v3/users/{admin_user.id}/courses", headers=regular_auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN

    result = response.json()
    assert "User can only view its own courses" in result["detail"]
