import logging
from fastapi.testclient import TestClient
from fastapi import status

# def test_get_categories(activities_api_client: TestClient, example_category: Category):
#     response = activities_api_client.get(
#         f"/api/v3/courses/{example_category.course_id}/categories",
#         headers=regular_auth_headers,
#     )
#     assert response.status_code == status.HTTP_200_OK
#     response_category = response.json()[0]
#     assert response_category["id"] == example_category.id
#     assert response_category["name"] == example_category.name
#     assert response_category["description"] == example_category.description
#     assert response_category["course_id"] == example_category.course_id


# def test_get_categories_empty(activities_api_client: TestClient):
#     response = activities_api_client.get(
#         "/api/v3/courses/1/categories", headers=regular_auth_headers
#     )
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == []


# def test_get_category(activities_api_client: TestClient, example_category: Category):
#     response = activities_api_client.get(
#         f"/api/v3/courses/{example_category.course_id}/categories/{example_category.id}",
#         headers=regular_auth_headers,
#     )
#     assert response.status_code == status.HTTP_200_OK
#     response_category = response.json()
#     assert response_category["id"] == example_category.id
#     assert response_category["name"] == example_category.name
#     assert response_category["description"] == example_category.description
#     assert response_category["course_id"] == example_category.course_id


# def test_get_category_not_found(activities_api_client: TestClient):
#     response = activities_api_client.get(
#         "/api/v3/courses/1/categories/1", headers=regular_auth_headers
#     )
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     response_error = response.json()
#     assert (
#         response_error["detail"]
#         == "The Category with ID 1 does not exist in the Course 1"
#     )


def test_create_category(activities_api_client: TestClient, admin_auth_headers):
    course_id = 1
    category_data = {
        "name": "New Category",
        "description": "Some new description",
        "active": True,
        "date_created": "2023-10-01T00:00:00Z",
        "last_updated": "2023-10-01T00:00:00Z",
    }
    response = activities_api_client.post(
        f"/api/v3/courses/{course_id}/categories",
        headers=admin_auth_headers,
        json=category_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_category = response.json()
    assert response_category["name"] == category_data["name"]
    assert response_category["description"] == category_data["description"]
    assert "date_created" in response_category
    assert "last_updated" in response_category


# def test_create_category_invalid_data(activities_api_client: TestClient):
#     category_data = {"description": "Some new description", "active": True}
#     response = activities_api_client.post(
#         "/api/v3/courses/1/categories",
#         headers=regular_auth_headers,
#         json=category_data,
#     )
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     assert "name" in response.json()["detail"][0]["loc"]


# def test_create_category_unauthorized(activities_api_client: TestClient):
#     category_data = {
#         "name": "New Category",
#         "description": "Some new description",
#         "active": True,
#     }
#     response = activities_api_client.post(
#         "/api/v3/courses/1/categories", json=category_data
#     )
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED


# def test_create_category_forbidden(activities_api_client: TestClient):
#     category_data = {
#         "name": "New Category",
#         "description": "Some new description",
#         "active": True,
#     }
#     response = activities_api_client.post(
#         "/api/v3/courses/1/categories",
#         headers={"Authorization": "forbidden_token"},
#         json=category_data,
#     )
#     assert response.status_code == status.HTTP_403_FORBIDDEN
#     assert response.json()["detail"] == "Forbidden"


# def test_update_category(activities_api_client: TestClient, example_category: Category):
#     update_data = {
#         "name": "Updated Category",
#         "description": "Updated description",
#         "active": False
#     }
#     response = activities_api_client.put(
#         f"/api/v3/courses/{example_category.course_id}/categories/{example_category.id}",
#         headers=regular_auth_headers,
#         json=update_data
#     )
#     assert response.status_code == status.HTTP_200_OK
#     response_category = response.json()
#     assert response_category["id"] == example_category.id
#     assert response_category["name"] == update_data["name"]
#     assert response_category["description"] == update_data["description"]
#     assert response_category["active"] == update_data["active"]
#     assert response_category["course_id"] == example_category.course_id


# def test_update_category_not_found(activities_api_client: TestClient):
#     update_data = {
#         "name": "Updated Category",
#         "description": "Updated description",
#         "active": False
#     }
#     response = activities_api_client.put(
#         "/api/v3/courses/1/categories/999",
#         headers=regular_auth_headers,
#         json=update_data
#     )
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     response_error = response.json()
#     assert (
#         response_error["detail"]
#         == "The Category with ID 999 does not exist in the Course 1"
#     )


# def test_delete_category(activities_api_client: TestClient, example_category: Category):
#     response = activities_api_client.delete(
#         f"/api/v3/courses/{example_category.course_id}/categories/{example_category.id}",
#         headers=regular_auth_headers,
#     )
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {"message": "Category deleted successfully"}

#     response = activities_api_client.get(
#         f"/api/v3/courses/{example_category.course_id}/categories/{example_category.id}",
#         headers=regular_auth_headers,
#     )
#     assert response.status_code == status.HTTP_404_NOT_FOUND
