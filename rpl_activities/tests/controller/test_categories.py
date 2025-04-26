import logging
from fastapi.testclient import TestClient
from fastapi import status

from rpl_activities.src.repositories.models.activity_category import ActivityCategory


def test_teacher_get_categories(
    activities_api_client: TestClient,
    admin_auth_headers,
    example_category: ActivityCategory,
    example_inactive_category: ActivityCategory,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_category.course_id}/activityCategories",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    response_category = response.json()[0]
    assert response_category["name"] == example_category.name
    assert response_category["description"] == example_category.description
    assert response_category["active"] == example_category.active
    assert "date_created" in response_category
    assert "last_updated" in response_category
    inactive_response_category = response.json()[1]
    assert inactive_response_category["name"] == example_inactive_category.name
    assert (
        inactive_response_category["description"]
        == example_inactive_category.description
    )
    assert inactive_response_category["active"] == example_inactive_category.active
    assert "date_created" in inactive_response_category
    assert "last_updated" in inactive_response_category


def test_student_get_categories(
    activities_api_client: TestClient,
    regular_auth_headers,
    example_category: ActivityCategory,
    example_inactive_category: ActivityCategory,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_category.course_id}/activityCategories",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    response_category = response.json()[0]
    assert response_category["name"] == example_category.name
    assert response_category["description"] == example_category.description
    assert response_category["active"] == example_category.active
    assert "date_created" in response_category
    assert "last_updated" in response_category


def test_get_categories_empty(activities_api_client: TestClient, admin_auth_headers):
    course_id = 1
    response = activities_api_client.get(
        f"/api/v3/courses/{course_id}/activityCategories",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_create_category_success(activities_api_client: TestClient, admin_auth_headers):
    course_id = 1
    category_data = {"name": "New Category", "description": "Some new description"}
    response = activities_api_client.post(
        f"/api/v3/courses/{course_id}/activityCategories",
        headers=admin_auth_headers,
        json=category_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_category = response.json()
    assert response_category["name"] == category_data["name"]
    assert response_category["description"] == category_data["description"]
    assert response_category["active"] is True
    assert "date_created" in response_category
    assert "last_updated" in response_category


def test_create_category_invalid_data(
    activities_api_client: TestClient, admin_auth_headers
):
    course_id = 1
    category_data = {"description": "Some new description", "active": True}
    response = activities_api_client.post(
        f"/api/v3/courses/{course_id}/activityCategories",
        headers=admin_auth_headers,
        json=category_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "name" in response.json()["detail"][0]["loc"]


def test_create_category_without_login(activities_api_client: TestClient):
    course_id = 1
    category_data = {"name": "New Category", "description": "Some new description"}
    response = activities_api_client.post(
        f"/api/v3/courses/{course_id}/activityCategories", json=category_data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_category_without_permission(
    activities_api_client: TestClient, regular_auth_headers
):
    course_id = 1
    category_data = {"name": "New Category", "description": "Some new description"}
    response = activities_api_client.post(
        f"/api/v3/courses/{course_id}/activityCategories",
        headers=regular_auth_headers,
        json=category_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        "User does not have permission to create a category"
        in response.json()["detail"]
    )


def test_update_category(
    activities_api_client: TestClient,
    admin_auth_headers,
    example_category: ActivityCategory,
):
    update_data = {
        "name": "Updated Category",
        "description": "Updated description",
        "active": False,
    }
    response = activities_api_client.patch(
        f"/api/v3/courses/{example_category.course_id}/activityCategories/{example_category.id}",
        headers=admin_auth_headers,
        json=update_data,
    )
    assert response.status_code == status.HTTP_200_OK
    response_category = response.json()
    assert response_category["name"] == update_data["name"]
    assert response_category["description"] == update_data["description"]
    assert response_category["active"] == example_category.active


def test_update_category_without_permission(
    activities_api_client: TestClient,
    regular_auth_headers,
    example_category: ActivityCategory,
):
    update_data = {
        "name": "Updated Category",
        "description": "Updated description",
        "active": False,
    }
    response = activities_api_client.patch(
        f"/api/v3/courses/{example_category.course_id}/activityCategories/{example_category.id}",
        headers=regular_auth_headers,
        json=update_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        "User does not have permission to update a category"
        in response.json()["detail"]
    )
