import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Keep tests isolated because the API stores data in memory."""
    original_state = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_state)


client = TestClient(app_module.app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_adds_student_to_activity():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    before_count = len(app_module.activities[activity_name]["participants"])
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    after_count = len(app_module.activities[activity_name]["participants"])

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert after_count == before_count + 1
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"