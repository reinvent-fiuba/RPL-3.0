from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import sessionmaker, Session

from rpl_activities.src.repositories.models.rpl_file import RPLFile


def test_get_file_with_stored_file_return_crrectly(
    activities_api_client: TestClient,
    activities_api_dbsession: Session,
):

    data = open("rpl_activities/tests/resources/la_submission.tar.xz", "rb").read()
    example_file = RPLFile(
        id=1,
        file_name="la_submission.tar.xz",
        file_type="application/x-tar",
        data=data,
    )
    # Simulate saving the file to the database
    activities_api_dbsession.add(example_file)
    activities_api_dbsession.commit()
    activities_api_dbsession.refresh(example_file)

    response = activities_api_client.get(
        f"/api/v3/files/{example_file.id}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.content == example_file.data
    assert response.headers["Content-Type"] == example_file.file_type


def test_get_file_with_non_existent_file_return_404(
    activities_api_client: TestClient,
):
    # Attempt to retrieve a non-existent file
    response = activities_api_client.get(
        "/api/v3/files/99999",  # Assuming this ID does not exist
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
