import pytest
from fastapi.testclient import TestClient
from fastapi import status

from rpl_users.src.repositories.models.user import User

# =============================================================================


def test_create_user_success(client: TestClient):
    new_user_data = {
        "username": "asd1234",
        "email": "asd@asd.com",
        "password": "12345",
        "name": "Asd",
        "surname": "AsdAsd",
        "student_id": "107378",
        "degree": "Ing. Informatica",
        "university": "FIUBA",
    }

    response = client.post("/api/v3/auth/signup", json=new_user_data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["id"] is not None
    assert result["username"] == new_user_data["username"]
    assert result["email"] == new_user_data["email"]
    assert result["name"] == new_user_data["name"]
    assert result["surname"] == new_user_data["surname"]
    assert result["student_id"] == new_user_data["student_id"]
    assert result["degree"] == new_user_data["degree"]
    assert result["university"] == new_user_data["university"]


@pytest.mark.parametrize(
    "test_name,missing_field",
    [
        ("missing_username", "username"),
        ("missing_email", "email"),
        ("missing_password", "password"),
    ],
)
def test_create_user_missing_fields(client: TestClient, test_name, missing_field):
    new_user_data = {
        "username": "asd1234",
        "email": "asd@asd.com",
        "password": "12345",
        "name": "Asd",
        "surname": "AsdAsd",
        "student_id": "107378",
        "degree": "Ing. Informatica",
        "university": "FIUBA",
    }

    del new_user_data[missing_field]

    response = client.post("/api/v3/auth/signup", json=new_user_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    result = response.json()
    assert "missing" in result["detail"][0]["type"]


@pytest.mark.parametrize(
    "test_name,username,email,password",
    [
        ("username_too_short", "a", "asd@asdd.com", "1234"),
        ("invalid_email", "asdoxx", "Asdgmail.com", "1234"),
        ("null_password", "asdoxxx", "asd@asdddd.com", ""),
    ],
)
def test_create_user_validation_errors(
    client: TestClient, test_name, username, email, password
):
    new_user_data = {
        "username": username,
        "email": email,
        "password": password,
        "name": "Asd",
        "surname": "AsdAsd",
        "student_id": "107378",
        "degree": "Ing. Informatica",
        "university": "FIUBA",
    }

    response = client.post("/api/v3/auth/signup", json=new_user_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    result = response.json()
    assert "too_short" or "value_error" in result["detail"][0]["type"]


def test_login_wrong_credentials(client: TestClient, example_users: dict[str, User]):
    login_data = {"username_or_email": "regularUsername", "password": "1"}

    response = client.post("/api/v3/auth/login", json=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    result = response.json()
    assert "Invalid credentials" in result["detail"]


@pytest.mark.parametrize("username_or_email", ["regularUsername", "regular@mail.com"])
def test_login_success(
    client: TestClient, example_users: dict[str, User], username_or_email
):
    login_data = {"username_or_email": username_or_email, "password": "secret"}

    response = client.post("/api/v3/auth/login", json=login_data)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["access_token"] is not None
    assert result["token_type"] == "Bearer"


def test_get_profile(
    client: TestClient, example_users: dict[str, User], regular_auth_headers
):
    response = client.get("/api/v3/auth/profile", headers=regular_auth_headers)

    assert response.status_code == 200

    result = response.json()
    assert result["username"] == example_users["regular"].username
    assert result["name"] == example_users["regular"].name
    assert result["student_id"] == example_users["regular"].student_id


@pytest.mark.parametrize(
    "fields_to_update",
    [
        {},
        {"name": "other-name"},
        {"university": "other-university"},
        {"name": "other-name", "university": "other-university"},
    ],
)
def test_update_profile(
    client: TestClient,
    example_users: dict[str, User],
    regular_auth_headers,
    fields_to_update,
):
    response = client.patch(
        "/api/v3/auth/profile", json=fields_to_update, headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()

    for key, expected_value in fields_to_update.items():
        assert result[key] == expected_value

    assert result["username"] == example_users["regular"].username


def test_update_immutable_fields(
    client: TestClient,
    example_users: dict[str, User],
    regular_auth_headers,
):
    immutable_fields = {"username": "regularUsername"}
    response = client.patch(
        "/api/v3/auth/profile", json=immutable_fields, headers=regular_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    result = response.json()

    for key in immutable_fields:
        assert result[key] == getattr(example_users["regular"], key)
