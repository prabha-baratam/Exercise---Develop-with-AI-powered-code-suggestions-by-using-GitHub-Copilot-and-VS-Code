from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)

    with TestClient(app) as test_client:
        yield test_client

    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_static_index_is_served(client):
    response = client.get("/static/index.html")

    assert response.status_code == 200
    assert "Mergington High School" in response.text


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    activity_name = "Basketball Team"
    email = "student@example.com"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_not_found(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_without_email_returns_unprocessable_entity(client):
    response = client.post("/activities/Basketball Team/signup")

    assert response.status_code == 422


def test_unregister_removes_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_unknown_activity_returns_not_found(client):
    response = client.delete(
        "/activities/Unknown Club/unregister",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_participant_returns_not_found(client):
    response = client.delete(
        "/activities/Basketball Team/unregister",
        params={"email": "missing@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"


def test_unregister_without_email_returns_unprocessable_entity(client):
    response = client.delete("/activities/Basketball Team/unregister")

    assert response.status_code == 422
