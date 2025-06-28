import json
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
import logging

from rpl_activities.src.repositories.models.activity import Activity
from rpl_activities.src.repositories.models.rpl_file import RPLFile


def test_get_raw_rplfile_success(activities_api_client: TestClient, example_basic_rplfiles: list[RPLFile]):
    response = activities_api_client.get(
        f"/api/v3/RPLFile/{example_basic_rplfiles[0].id}", headers={"Authorization": "Bearer test"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.content == example_basic_rplfiles[0].data
    assert response.headers["Content-Type"] == example_basic_rplfiles[0].file_type


def test_get_nonexistent_raw_rplfile(activities_api_client: TestClient):
    response = activities_api_client.get("/api/v3/RPLFile/99999", headers={"Authorization": "Bearer test"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_extracted_rplfile_for_teacher_returns_all_inner_files(
    activities_api_client: TestClient,
    example_activity_with_io_tests: Activity,
    example_basic_rplfiles: list[RPLFile],
    admin_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/extractedRPLFile/{example_basic_rplfiles[0].id}",
        headers=admin_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = json.loads(response.content)
    assert "assignment_main.py" in content
    assert "main.c" in content


def test_get_extracted_rplfile_for_teacher_logged_as_student_returns_forbidden(
    activities_api_client: TestClient,
    example_activity_with_io_tests: Activity,
    example_basic_rplfiles: list[RPLFile],
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/extractedRPLFile/{example_basic_rplfiles[0].id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_extracted_rplfile_for_student_only_returns_not_hidden_inner_files(
    activities_api_client: TestClient,
    example_activity_with_io_tests: Activity,
    example_basic_rplfiles: list[RPLFile],
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/extractedRPLFileForStudent/{example_basic_rplfiles[0].id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = json.loads(response.content)
    assert "assignment_main.py" in content
    assert "main.c" not in content  # This is hidden


def test_get_multiple_extracted_rplfiles_for_student_returns_only_not_hidden_inner_files_from_all_of_them(
    activities_api_client: TestClient,
    example_activity_with_io_tests: Activity,
    example_basic_rplfiles: list[RPLFile],
    regular_auth_headers,
):
    response = activities_api_client.get(
        f"/api/v3/courses/{example_activity_with_io_tests.course_id}/extractedRPLFilesForStudent/{example_basic_rplfiles[0].id},{example_basic_rplfiles[1].id}",
        headers=regular_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    content = json.loads(response.content)
    assert "assignment_main.py" in content[0]
    assert "main.c" not in content[0]  # This is hidden
    assert "assignment_main.py" in content[1]
    assert "main.c" not in content[1]  # This is hidden
