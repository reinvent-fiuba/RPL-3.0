import logging
import pytest
from fastapi.testclient import TestClient


def test_health_ping(users_api_client: TestClient):
    response = users_api_client.get("/api/v3/health")
    assert response.status_code == 200
    assert response.text == '"pong"'
