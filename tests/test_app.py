from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_signup_and_unregister_activity():
    activity_name = "Basketball Team"
    email = "student@example.com"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200, response.text
    assert email in response.json()["message"]

    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200, response.text
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_missing_email_returns_404():
    response = client.delete("/activities/Basketball Team/unregister?email=missing@example.com")
    assert response.status_code == 404, response.text
