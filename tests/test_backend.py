import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def restore_activities():
    original_state = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_state))


@pytest.fixture()
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup?email=student@example.com"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up student@example.com for Chess Club"
    assert "student@example.com" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    client.post("/activities/Chess%20Club/signup?email=student@example.com")

    response = client.post(
        "/activities/Chess%20Club/signup?email=student@example.com"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post("/activities/Missing%20Club/signup?email=student@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_participant(client):
    client.post("/activities/Chess%20Club/signup?email=student@example.com")

    response = client.delete(
        "/activities/Chess%20Club/participants/student@example.com"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered student@example.com from Chess Club"
    assert "student@example.com" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/participants/student@example.com"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
