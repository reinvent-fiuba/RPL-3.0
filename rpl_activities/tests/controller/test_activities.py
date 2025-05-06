from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
import logging

from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.activity_submission import (
    ActivitySubmission,
)
from rpl_activities.src.repositories.models.activity_category import ActivityCategory

from rpl_activities.src.repositories.models.io_test import IOTest
from rpl_activities.src.repositories.models.rpl_file import RPLFile


def test_get_activities_as_student_returns_only_active_activities(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_inactive_activity: Activity,
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()[0]

    assert len(response.json()) == 1
    assert response_activity["name"] == example_activity.name
    assert response_activity["description"] == example_activity.description
    assert response_activity["language"] == example_activity.language
    assert response_activity["is_io_tested"] == example_activity.is_io_tested
    assert response_activity["points"] == example_activity.points


def test_get_activities_as_teacher_returns_all_activities(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_inactive_activity: Activity,
    admin_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


def test_get_activities_empty(
    activities_api_client: TestClient,
    admin_auth_headers,
):
    response = activities_api_client.get(
        "/api/v3/courses/1/activities",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


def test_get_activities_with_submission(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_submission: ActivitySubmission,
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()[0]
    assert response_activity["submission_status"] == example_submission.status
    assert response_activity["last_submission_date"] is not None


def test_get_activities_with_multiple_submissions_returns_them_with_their_best_submission_status_to_date(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_submission: ActivitySubmission,
    example_failed_submission: ActivitySubmission,
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()[0]

    assert response_activity["submission_status"] == example_submission.status
    assert response_activity["submission_status"] == aux_models.SubmissionStatus.PENDING
    assert (
        response_activity["last_submission_date"]
        == example_failed_submission.date_created
    )


# ==============================================================================


def test_get_activity(
    activities_api_client: TestClient,
    example_category: ActivityCategory,
    example_activity: Activity,
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()
    assert response_activity["name"] == example_activity.name
    assert response_activity["description"] == example_activity.description
    assert response_activity["category_name"] == example_category.name
    assert response_activity["category_description"] == example_category.description
    assert response_activity["language"] == example_activity.language
    assert response_activity["active"] == example_activity.active
    assert response_activity["activity_iotests"] == []
    assert response_activity["rplfile_id"] == example_activity.starting_rplfile_id
    assert response_activity["date_created"] == example_activity.date_created
    assert response_activity["last_updated"] == example_activity.last_updated


def test_get_nonexistent_activity_not_found(
    activities_api_client: TestClient,
    example_activity: Activity,
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities/99999",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_activity_with_io_tests(
    activities_api_client: TestClient,
    example_activity_with_io_tests: Activity,
    example_io_tests: list[IOTest],
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()
    assert len(response_activity["activity_iotests"]) == 2
    assert response_activity["activity_iotests"][0]["name"] == example_io_tests[0].name
    assert response_activity["activity_iotests"][0]["in"] == example_io_tests[0].test_in
    assert (
        response_activity["activity_iotests"][0]["out"] == example_io_tests[0].test_out
    )
    assert response_activity["activity_iotests"][1]["name"] == example_io_tests[1].name
    assert response_activity["activity_iotests"][1]["in"] == example_io_tests[1].test_in
    assert (
        response_activity["activity_iotests"][1]["out"] == example_io_tests[1].test_out
    )


# ==============================================================================


def test_delete_activity_as_teacher_success(
    activities_api_client: TestClient,
    example_activity: Activity,
    admin_auth_headers,
):
    old_activity_id = example_activity.id
    response = activities_api_client.delete(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities/{old_activity_id}",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_activity_as_student_forbidden(
    activities_api_client: TestClient,
    example_activity: Activity,
    regular_auth_headers,
):
    response = activities_api_client.delete(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_nonexistent_activity_not_found(
    activities_api_client: TestClient,
    example_activity: Activity,
    admin_auth_headers,
):
    response = activities_api_client.delete(
        f"/api/v3/courses/{example_activity.course_id}/activities/99999",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ==============================================================================


def test_create_activity_as_teacher_success(
    activities_api_client: TestClient,
    example_category: ActivityCategory,
    # TODO: check what the frontend sends
    example_starting_rplfile_raw_data: list[tuple[str, bytes]],
    admin_auth_headers,
):
    pass
