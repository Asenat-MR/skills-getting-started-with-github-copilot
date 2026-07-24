from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def test_unregister_participant():
    activity = app_module.activities["Chess Club"]
    original_participants = activity["participants"][:]

    try:
        response = client.delete(
            "/activities/Chess%20Club/participants/michael@mergington.edu"
        )

        assert response.status_code == 200
        assert response.json()["message"] == (
            "Unregistered michael@mergington.edu from Chess Club"
        )
        assert "michael@mergington.edu" not in activity["participants"]
    finally:
        activity["participants"] = original_participants
