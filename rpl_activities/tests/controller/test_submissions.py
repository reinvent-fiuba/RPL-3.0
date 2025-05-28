from datetime import datetime
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
from rpl_activities.src.repositories.models.unit_test import UnitTest
from rpl_activities.src.services.rpl_files import ExtractedFilesDict
from rpl_activities.tests.conftest import ExamplesOfStartingFilesRawData, ExamplesOfSubmissionRawData


def test_get_submission(
    activities_api_client: TestClient,
    example_unit_test: UnitTest,
    example_submission: ActivitySubmission,
    admin_auth_headers: dict[str, str],
):
    response = activities_api_client.get(
        f"/api/v3/submissions/{example_submission.id}",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == example_submission.id
    assert response_data["submission_rplfile_name"] == example_submission.response_rplfile.file_name
    assert response_data["submission_rplfile_type"] == example_submission.response_rplfile.file_type
    assert response_data["submission_rplfile_id"] == example_submission.response_rplfile_id
    assert response_data["acitivity_starting_rplfile_name"] == example_submission.activity.starting_rplfile.file_name
    assert response_data["activity_starting_rplfile_type"] == example_submission.activity.starting_rplfile.file_type
    assert response_data["activity_starting_rplfile_id"] == example_submission.activity.starting_rplfile_id
    assert response_data["activity_language"] == example_submission.activity.language # With version! (intended)
    assert response_data["is_io_tested"] == example_submission.activity.is_io_tested
    assert response_data["compilation_flags"] == example_submission.activity.compilation_flags
    assert response_data["activity_unit_tests_content"] == example_submission.activity.unit_test.test_rplfile.data
    assert len(response_data["activity_io_tests_input"]) == len(example_submission.activity.io_tests)


def test_get_non_existent_submission_not_found(
    activities_api_client: TestClient,
    example_unit_test: UnitTest,
    example_submission: ActivitySubmission,
    admin_auth_headers: dict[str, str],
):
    response = activities_api_client.get(
        "/api/v3/submissions/99999",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ==============================================================================


def test_create_submission(
    activities_api_client: TestClient,
    example_unit_test: UnitTest,
    example_activity: Activity,
    example_submission_raw_data: ExamplesOfSubmissionRawData,
    admin_auth_headers: dict[str, str],
):
    response = activities_api_client.post(
        f"/api/v3/{example_activity.course_id}/activities/{example_activity.id}/submissions",
        files=example_submission_raw_data,
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    # the name contains date, course_id, activity_id and user_id; finishing with a SUBM suffix
    assert f"__{example_activity.course_id}__{example_activity.id}__" in response_data["submission_rplfile_name"] 
    assert response_data["submission_rplfile_type"] == aux_models.RPLFileType.GZIP
    assert response_data["activity_starting_rplfile_name"] == example_activity.starting_rplfile.file_name
    assert response_data["activity_starting_rplfile_type"] == example_activity.starting_rplfile.file_type
    assert response_data["activity_starting_rplfile_id"] == example_activity.starting_rplfile_id
    assert response_data["activity_language"] == example_activity.language  # With version! (intended)
    assert response_data["is_io_tested"] == example_activity.is_io_tested
    assert response_data["compilation_flags"] == example_activity.compilation_flags
    assert response_data["activity_unit_tests_content"] == example_activity.unit_test.test_rplfile.data
    assert len(response_data["activity_io_tests_input"]) == len(example_activity.io_tests)

    # the submission's stored rplfile should contain both the ones from the student's solution (tiempo.c, tiempo.h) and the activities' starting files. Thus, it should also have overwritten any submission files that were marked as either "read" or "hidden" within the starting files that the teacher created.
    submission_rplfile = activities_api_client.get(
        f"/api/v3/extractedRPLFile/{response_data['submission_rplfile_id']}",
        headers=admin_auth_headers,
    )
    activity_rplfile = activities_api_client.get(
        f"/api/v3/extractedRPLFile/{example_activity.starting_rplfile_id}",
        headers=admin_auth_headers,
    )
    assert submission_rplfile.status_code == status.HTTP_200_OK
    subm_rplfile_data = submission_rplfile.json()
    act_rplfile_data = activity_rplfile.json()
    assert subm_rplfile_data.keys() == {"main.c", "tiempo.c", "tiempo.h"}
    assert "INTEGRATION_TEST_FAILED" not in subm_rplfile_data["tiempo.h"]
    assert subm_rplfile_data["tiempo.h"] == act_rplfile_data["tiempo.h"]
    assert subm_rplfile_data["main.c"] == act_rplfile_data["main.c"]

