import json
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import sessionmaker, Session
import logging

from rpl_activities.src.repositories.models.rpl_file import RPLFile


def test_get_raw_rplfile_success(
    activities_api_client: TestClient,
    example_rplfiles: list[RPLFile],
):
    response = activities_api_client.get(
        f"/api/v3/RPLFile/{example_rplfiles[0].id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.content == example_rplfiles[0].data
    assert response.headers["Content-Type"] == example_rplfiles[0].file_type


def test_get_nonexistent_raw_rplfile(
    activities_api_client: TestClient,
):
    response = activities_api_client.get(
        "/api/v3/RPLFile/99999",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_extracted_rplfile_returns_all_inner_files(
    activities_api_client: TestClient,
    example_rplfiles: list[RPLFile],
):
    response = activities_api_client.get(
        f"/api/v3/extractedRPLFile/{example_rplfiles[0].id}",
    )
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_200_OK
    assert "assignment_main.py" in content
    assert "main.c" in content


def test_get_extracted_rplfile_for_student_only_returns_not_hidden_inner_files(
    activities_api_client: TestClient,
    example_rplfiles: list[RPLFile],
):
    response = activities_api_client.get(
        f"/api/v3/extractedRPLFileForStudent/{example_rplfiles[0].id}",
    )
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_200_OK
    assert "assignment_main.py" in content
    assert "main.c" not in content  # This is hidden


def test_get_multiple_extracted_rplfiles_returns_all_inner_files_from_all_of_them(
    activities_api_client: TestClient,
    example_rplfiles: list[RPLFile],
):
    response = activities_api_client.get(
        f"/api/v3/extractedRPLFiles/{example_rplfiles[0].id},{example_rplfiles[1].id}",
    )
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_200_OK
    assert "assignment_main.py" in content[0]
    assert "main.c" in content[0]
    assert "assignment_main.py" in content[1]
    assert "main.c" in content[1]


def test_get_multiple_extracted_rplfiles_for_student_returns_only_not_hidden_inner_files_from_all_of_them(
    activities_api_client: TestClient,
    example_rplfiles: list[RPLFile],
):
    response = activities_api_client.get(
        f"/api/v3/extractedRPLFilesForStudent/{example_rplfiles[0].id},{example_rplfiles[1].id}",
    )
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_200_OK
    assert "assignment_main.py" in content[0]
    assert "main.c" not in content[0]  # This is hidden
    assert "assignment_main.py" in content[1]
    assert "main.c" not in content[1]  # This is hidden
