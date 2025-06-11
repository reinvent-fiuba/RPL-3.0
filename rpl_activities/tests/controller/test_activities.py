from datetime import timedelta
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
import logging

from rpl_activities.src.repositories.models import aux_models
from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.activity_submission import ActivitySubmission
from rpl_activities.src.repositories.models.activity_category import ActivityCategory

from rpl_activities.src.repositories.models.io_test import IOTest
from rpl_activities.src.repositories.models.rpl_file import RPLFile
from rpl_activities.src.repositories.models.unit_test_suite import UnitTestSuite
from rpl_activities.src.services.rpl_files import ExtractedFilesDict
from rpl_activities.tests.conftest import ExamplesOfStartingFilesRawData


def test_get_activities_as_student_returns_only_active_activities(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_inactive_activity: Activity,
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities", headers=regular_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()[0]

    assert len(response.json()) == 1
    assert response_activity["name"] == example_activity.name
    assert response_activity["description"] == example_activity.description
    assert (
        response_activity["language"]
        == aux_models.LanguageWithVersion(example_activity.language).without_version()
    )
    assert response_activity["is_io_tested"] == example_activity.is_io_tested
    assert response_activity["points"] == example_activity.points


def test_get_activities_as_teacher_returns_all_activities(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_inactive_activity: Activity,
    admin_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities", headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


def test_get_activities_empty(activities_api_client: TestClient, admin_auth_headers):
    response = activities_api_client.get("/api/v3/courses/1/activities", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


def test_get_activities_with_submission(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_submission: ActivitySubmission,
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities", headers=regular_auth_headers
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
        f"/api/v3/courses/{example_activity.course_id}/activities", headers=regular_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()[0]

    assert response_activity["submission_status"] == example_failed_submission.status
    assert response_activity["submission_status"] == aux_models.SubmissionStatus.FAILURE
    assert response_activity["last_submission_date"] == (
        example_submission.date_created - timedelta(hours=3)
    ).strftime("%Y-%m-%dT%H:%M:%S")


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
    assert (
        response_activity["language"]
        == aux_models.LanguageWithVersion(example_activity.language).without_version()
    )
    assert response_activity["active"] == example_activity.active
    assert response_activity["activity_io_tests"] == []
    assert response_activity["starting_rplfile_id"] == example_activity.starting_rplfile_id
    assert response_activity["date_created"] == (example_activity.date_created - timedelta(hours=3)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert response_activity["last_updated"] == (example_activity.last_updated - timedelta(hours=3)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )


def test_get_nonexistent_activity_not_found(
    activities_api_client: TestClient, example_activity: Activity, regular_auth_headers
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities/99999", headers=regular_auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_activity_with_io_tests(
    activities_api_client: TestClient,
    example_io_tests: list[IOTest],
    example_activity_with_io_tests: Activity,
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()
    assert len(response_activity["activity_io_tests"]) == 2
    assert response_activity["activity_io_tests"][0]["name"] == example_io_tests[0].name
    assert response_activity["activity_io_tests"][0]["test_in"] == example_io_tests[0].test_in
    assert response_activity["activity_io_tests"][0]["test_out"] == example_io_tests[0].test_out
    assert response_activity["activity_io_tests"][1]["name"] == example_io_tests[1].name
    assert response_activity["activity_io_tests"][1]["test_in"] == example_io_tests[1].test_in
    assert response_activity["activity_io_tests"][1]["test_out"] == example_io_tests[1].test_out


# ==============================================================================


def test_delete_activity_as_teacher_success(
    activities_api_client: TestClient, example_activity: Activity, admin_auth_headers
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
    activities_api_client: TestClient, example_activity: Activity, regular_auth_headers
):
    response = activities_api_client.delete(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_nonexistent_activity_not_found(
    activities_api_client: TestClient, example_activity: Activity, admin_auth_headers
):
    response = activities_api_client.delete(
        f"/api/v3/courses/{example_activity.course_id}/activities/99999", headers=admin_auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ==============================================================================


def test_create_activity_as_teacher_success(
    activities_api_client: TestClient,
    example_category: ActivityCategory,
    examples_of_starting_files_raw_data: ExamplesOfStartingFilesRawData,
    admin_auth_headers,
):
    form_data = {
        "name": "test",
        "points": 2,
        "language": "python",
        "category_id": example_category.id,
        "description": "enunciado",
    }

    response = activities_api_client.post(
        f"/api/v3/courses/{example_category.course_id}/activities",
        headers=admin_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["course_id"] == example_category.course_id
    assert response_data["category_id"] == example_category.id
    assert response_data["name"] == form_data["name"]
    assert response_data["description"] == form_data["description"]
    assert response_data["language"] == form_data["language"]
    assert response_data["is_io_tested"] is False
    assert response_data["active"] is True
    assert response_data["deleted"] is False
    assert response_data["points"] == int(form_data["points"])
    assert response_data["starting_rplfile_id"] is not None

    form_data = {
        "name": "test2",
        "points": 3,
        "language": "c",
        "category_id": example_category.id,
        "description": "enunciado2",
    }

    response = activities_api_client.post(
        f"/api/v3/courses/{example_category.course_id}/activities",
        headers=admin_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["c"],
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["course_id"] == example_category.course_id
    assert response_data["category_id"] == example_category.id
    assert response_data["name"] == form_data["name"]
    assert response_data["description"] == form_data["description"]
    assert response_data["language"] == form_data["language"]
    assert response_data["is_io_tested"] is False
    assert response_data["active"] is True
    assert response_data["deleted"] is False
    assert response_data["points"] == int(form_data["points"])
    assert response_data["starting_rplfile_id"] is not None


def test_create_activity_as_student_forbidden(
    activities_api_client: TestClient,
    example_category: ActivityCategory,
    examples_of_starting_files_raw_data: ExamplesOfStartingFilesRawData,
    regular_auth_headers,
):
    form_data = {
        "name": "test",
        "points": 2,
        "language": "python",
        "category_id": example_category.id,
        "description": "enunciado",
    }

    response = activities_api_client.post(
        f"/api/v3/courses/{example_category.course_id}/activities",
        headers=regular_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_activity_with_nonexistent_category_not_found(
    activities_api_client: TestClient,
    example_category: ActivityCategory,
    examples_of_starting_files_raw_data: ExamplesOfStartingFilesRawData,
    admin_auth_headers,
):
    form_data = {
        "name": "test",
        "points": 2,
        "language": "python",
        "category_id": 99999,
        "description": "enunciado",
    }

    response = activities_api_client.post(
        f"/api/v3/courses/{example_category.course_id}/activities",
        headers=admin_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_activity_with_missing_required_fields(
    activities_api_client: TestClient,
    example_category: ActivityCategory,
    examples_of_starting_files_raw_data: ExamplesOfStartingFilesRawData,
    admin_auth_headers,
):
    # Missing name
    form_data = {
        "points": 2,
        "language": "python",
        "category_id": example_category.id,
        "description": "enunciado",
    }
    response = activities_api_client.post(
        f"/api/v3/courses/{example_category.course_id}/activities",
        headers=admin_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"

    # Missing points
    form_data = {
        "name": "test",
        "language": "python",
        "category_id": example_category.id,
        "description": "enunciado",
    }
    response = activities_api_client.post(
        f"/api/v3/courses/{example_category.course_id}/activities",
        headers=admin_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"

    # Missing language
    form_data = {"name": "test", "points": 2, "category_id": example_category.id, "description": "enunciado"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_category.course_id}/activities",
        headers=admin_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"

    # Missing category_id
    form_data = {"name": "test", "points": 2, "language": "python", "description": "enunciado"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_category.course_id}/activities",
        headers=admin_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == "Field required"


def test_create_activity_in_wrong_existing_course_forbidden(
    activities_api_client: TestClient,
    example_category: ActivityCategory,
    examples_of_starting_files_raw_data: ExamplesOfStartingFilesRawData,
    example_category_from_another_course: ActivityCategory,
    admin_auth_headers,
):
    # Context: Since the course with regular user as teacher (course admin) is not the same as the one where the superadmin user is the teacher (course admin), the creation of the activity should be forbidden for said superadmin.
    form_data = {
        "name": "test",
        "points": 2,
        "language": "python",
        "category_id": example_category_from_another_course.id,
        "description": "enunciado",
    }
    response = activities_api_client.post(
        "/api/v3/courses/2/activities",
        headers=admin_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ==============================================================================


def test_update_activity_as_teacher_success(
    activities_api_client: TestClient,
    example_category: ActivityCategory,
    example_activity: Activity,
    example_inactive_activity: Activity,
    examples_of_starting_files_raw_data: ExamplesOfStartingFilesRawData,
    admin_auth_headers,
):
    form_data_1 = {
        "category_id": example_category.id,
        "name": "updated test",
        "description": "enunciado",
        "language": "python",
        "compilation_flags": "updated test",
        "active": "true",
        "points": 10,
    }

    response = activities_api_client.patch(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}",
        headers=admin_auth_headers,
        data=form_data_1,
        files=examples_of_starting_files_raw_data["python"],
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["course_id"] == example_category.course_id
    assert response_data["category_id"] == example_category.id
    assert response_data["name"] == form_data_1["name"]
    assert response_data["description"] == form_data_1["description"]
    assert response_data["language"] == form_data_1["language"]
    assert response_data["is_io_tested"] is False
    assert response_data["active"] is True
    assert response_data["deleted"] is False
    assert response_data["points"] == int(form_data_1["points"])
    assert response_data["starting_rplfile_id"] is not None
    aux_response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/extractedRPLFile/{response_data['starting_rplfile_id']}",
        headers=admin_auth_headers,
    )
    assert aux_response.status_code == status.HTTP_200_OK
    aux_response_data: ExtractedFilesDict = aux_response.json()
    assert aux_response_data.get("main.c") is None
    assert aux_response_data.get("tiempo.c") is None
    assert aux_response_data.get("tiempo.h") is None
    assert aux_response_data.get("main.py") is not None
    assert aux_response_data.get("assignment_main.py") is not None

    # Change only some fields
    form_data_2 = {"category_id": example_inactive_activity.category_id, "active": "true"}
    response = activities_api_client.patch(
        f"/api/v3/courses/{example_inactive_activity.course_id}/activities/{example_inactive_activity.id}",
        headers=admin_auth_headers,
        data=form_data_2,
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["category_id"] == example_inactive_activity.category_id
    assert response_data["name"] == example_inactive_activity.name
    assert response_data["description"] == example_inactive_activity.description
    assert (
        response_data["language"]
        == aux_models.LanguageWithVersion(example_inactive_activity.language).without_version()
    )
    assert response_data["is_io_tested"] is False
    assert response_data["active"] is True
    assert response_data["deleted"] is False
    assert response_data["points"] == example_inactive_activity.points
    assert response_data["starting_rplfile_id"] is not None


def test_update_activity_as_student_forbidden(
    activities_api_client: TestClient,
    example_activity: Activity,
    examples_of_starting_files_raw_data: ExamplesOfStartingFilesRawData,
    regular_auth_headers,
):
    form_data = {
        "category_id": example_activity.category_id,
        "name": "updated test",
        "description": "enunciado",
        "language": "python",
        "compilation_flags": "updated test",
        "active": "true",
        "points": 10,
    }

    response = activities_api_client.patch(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}",
        headers=regular_auth_headers,
        data=form_data,
        files=examples_of_starting_files_raw_data["python"],
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ==============================================================================


def test_create_io_test_for_activity_as_student_forbidden(
    activities_api_client: TestClient,
    example_io_tests: list[IOTest],
    example_activity_with_io_tests: Activity,
    regular_auth_headers,
):
    data = {"name": "test", "test_in": "test_in", "test_out": "test_out"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}/iotests",
        headers=regular_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_io_test_for_activity_as_student_forbidden(
    activities_api_client: TestClient,
    example_io_tests: list[IOTest],
    example_activity_with_io_tests: Activity,
    regular_auth_headers,
):
    data = {"name": "test", "test_in": "changed in", "test_out": "changed out"}
    response = activities_api_client.put(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}/iotests/{example_io_tests[0].id}",
        headers=regular_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_io_test_for_activity_as_student_forbidden(
    activities_api_client: TestClient,
    example_io_tests: list[IOTest],
    example_activity_with_io_tests: Activity,
    regular_auth_headers,
):
    response = activities_api_client.delete(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}/iotests/{example_io_tests[0].id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_io_test_for_activity_that_had_iotests_previously(
    activities_api_client: TestClient,
    example_io_tests: list[IOTest],
    example_activity_with_io_tests: Activity,
    admin_auth_headers,
):
    data = {"name": "test", "test_in": "test_in", "test_out": "test_out"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}/iotests",
        headers=admin_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["test_in"] == data["test_in"]
    assert response_data["test_out"] == data["test_out"]

    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()
    assert len(response_activity["activity_io_tests"]) == 3


def test_create_io_test_for_activity_that_had_unittests_previously(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_unit_test_suite: UnitTestSuite,
    admin_auth_headers,
):
    data = {"name": "test", "test_in": "test_in", "test_out": "test_out"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}/iotests",
        headers=admin_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["test_in"] == data["test_in"]
    assert response_data["test_out"] == data["test_out"]

    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()
    # It's mantained but the activity mode is changed and it has the new io test
    assert len(response_activity["activity_unit_tests_content"]) > 0
    assert response_activity["is_io_tested"] is True
    assert len(response_activity["activity_io_tests"]) == 1


def test_update_io_test_for_activity(
    activities_api_client: TestClient,
    example_io_tests: list[IOTest],
    example_activity_with_io_tests: Activity,
    admin_auth_headers,
):
    data = {"name": "test", "test_in": "changed in", "test_out": "changed out"}
    response = activities_api_client.put(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}/iotests/{example_io_tests[0].id}",
        headers=admin_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["test_in"] == data["test_in"]
    assert response_data["test_out"] == data["test_out"]

    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()
    assert len(response_activity["activity_io_tests"]) == 2


def test_delete_io_test_for_activity(
    activities_api_client: TestClient,
    example_io_tests: list[IOTest],
    example_activity_with_io_tests: Activity,
    admin_auth_headers,
):
    response = activities_api_client.delete(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}/iotests/{example_io_tests[0].id}",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()
    assert len(response_activity["activity_io_tests"]) == 1


# ==============================================================================


def test_create_unit_tests_for_activity_as_student_forbidden(
    activities_api_client: TestClient, example_activity: Activity, regular_auth_headers
):
    data = {"unit_tests_code": "print('Unit tests nuevos')"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}/unittests",
        headers=regular_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_unit_tests_for_activity_as_student_forbidden(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_unit_test_suite: UnitTestSuite,
    regular_auth_headers,
):
    data = {"unit_tests_code": "print('Unit tests que reemplazan a los anteriores')"}
    response = activities_api_client.put(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}/unittests",
        headers=regular_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_unit_tests_for_activity(
    activities_api_client: TestClient, example_activity: Activity, admin_auth_headers
):
    data = {"unit_tests_code": "print('Unit tests nuevos')"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}/unittests",
        headers=admin_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_activity = response.json()
    assert response_activity["activity_unit_tests_content"] == data["unit_tests_code"]


def test_create_unit_tests_for_activity_that_already_had_them_returns_conflict(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_unit_test_suite: UnitTestSuite,
    admin_auth_headers,
):
    data = {"unit_tests_code": "print('Unit tests nuevos')"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}/unittests",
        headers=admin_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_unit_tests_for_activity_that_had_iotests_previously(
    activities_api_client: TestClient,
    example_io_tests: list[IOTest],
    example_activity_with_io_tests: Activity,
    admin_auth_headers,
):
    data = {"unit_tests_code": "print('Unit tests nuevos')"}
    response = activities_api_client.post(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/activities/{example_activity_with_io_tests.id}/unittests",
        headers=admin_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_activity = response.json()
    # It's mantained but the activity mode is changed and it has the new unit tests
    assert len(response_activity["activity_io_tests"]) == 2
    assert response_activity["is_io_tested"] is False
    assert response_activity["activity_unit_tests_content"] == data["unit_tests_code"]


def test_update_unit_tests_for_activity(
    activities_api_client: TestClient,
    example_activity: Activity,
    example_unit_test_suite: UnitTestSuite,
    admin_auth_headers,
):
    data = {"unit_tests_code": "print('Unit tests que reemplazan a los anteriores')"}
    response = activities_api_client.put(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}/unittests",
        headers=admin_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK
    response_activity = response.json()
    assert response_activity["activity_unit_tests_content"] == data["unit_tests_code"]


def test_update_unit_tests_for_activity_that_didnt_have_any_returns_not_found(
    activities_api_client: TestClient, example_activity: Activity, admin_auth_headers
):
    data = {"unit_tests_code": "print('Unit tests que reemplazan a los anteriores (que no existen)')"}
    response = activities_api_client.put(
        f"/api/v3/courses/{example_activity.course_id}/activities/{example_activity.id}/unittests",
        headers=admin_auth_headers,
        json=data,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
