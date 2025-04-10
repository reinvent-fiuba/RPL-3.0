import logging
import pytest
from fastapi.testclient import TestClient


def test_health_ping(client: TestClient):
    response = client.get("/api/v3/health")
    assert response.status_code == 200
    assert response.text == '"pong"'
