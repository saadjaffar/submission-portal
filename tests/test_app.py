import pytest

from app import create_app

VALID = {
    "name": "Saad Jaffar",
    "reg_no": "FA23-BSE-056",
    "title": "Assignment 1",
    "url": "https://github.com/saadjaffar/assignment1",
}


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "submissions.json"))
    app.config["TESTING"] = True
    return app.test_client()


def test_valid_submission_is_saved_and_listed(client):
    resp = client.post("/", data=VALID, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Saad Jaffar" in resp.data
    assert b"Assignment 1" in resp.data


def test_missing_registration_number_is_rejected(client):
    resp = client.post("/", data={**VALID, "reg_no": ""})
    assert resp.status_code == 400
    assert b"Registration number is required" in resp.data
    assert b"Assignment 1" not in client.get("/").data


def test_invalid_url_is_rejected_and_not_saved(client):
    resp = client.post("/", data={**VALID, "url": "not-a-url"})
    assert resp.status_code == 400
    assert b"valid URL" in resp.data
    assert b"Assignment 1" not in client.get("/").data