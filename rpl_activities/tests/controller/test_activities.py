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



def test_get_acitvity
