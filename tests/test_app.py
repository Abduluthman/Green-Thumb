import io
import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image
import pytest

from app import ROOT, create_app
from conftest import csrf_token, login


def image_file(mode="RGB"):
    stream = io.BytesIO()
    Image.new(mode, (32, 32)).save(stream, format="PNG")
    stream.seek(0)
    return stream


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/Home.html",
        "/Welcome.html",
        "/Upload.html",
        "/Camera.html",
        "/WasteDictionary.html",
        "/Search-Template.html",
        "/Feedback.html",
        "/login",
    ],
)
def test_public_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert b"Green Thumb" in response.data
    assert b"csrf-token" in response.data
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_homepage_uses_current_interface(client):
    page = client.get("/").get_data(as_text=True)
    assert "Not sure where an item belongs?" in page
    assert "Know your waste" not in page


@pytest.mark.parametrize(
    "path", ["/app.py", "/feedback.json", "/model.h5", "/base.html", "/dictionary.jso", "/README.md"]
)
def test_private_and_unknown_files_are_not_served(client, path):
    assert client.get(path).status_code == 404


def test_dictionary_served_as_json(client):
    response = client.get("/dictionary.json")
    assert response.is_json
    catalog = response.json
    assert catalog["schemaVersion"] == 2
    assert catalog["defaultJurisdiction"]["code"] == "NG-FC"
    entries = catalog["items"]
    assert len(entries) == 136
    assert len({entry["name"].lower() for entry in entries}) == len(entries)
    for entry in entries:
        assert set(entry) >= {
            "id",
            "name",
            "aliases",
            "streams",
            "riskLevel",
            "handlingFlags",
            "description",
            "guidance",
        }
        assert entry["riskLevel"] in catalog["riskLevels"]
        assert set(entry["streams"]) <= set(catalog["streams"])
        assert set(entry["guidance"]["routes"]) <= set(catalog["routeLabels"])
        assert set(entry["guidance"]["sourceIds"]) <= set(catalog["sources"])


def test_all_prediction_categories_exist_in_dictionary(client):
    from classifier import LABELS

    assert set(LABELS) <= {entry["name"] for entry in client.get("/dictionary.json").json["items"]}


def test_dictionary_risk_distribution(client):
    entries = client.get("/dictionary.json").json["items"]
    assert sum(entry["riskLevel"] == "special-handling" for entry in entries) == 22
    assert sum(entry["guidance"]["status"] == "source-linked" for entry in entries) == 41


def test_dictionary_stream_normalisation_does_not_confuse_negative_prefixes(client):
    entries = {entry["name"]: entry for entry in client.get("/dictionary.json").get_json()["items"]}

    assert "organic" not in entries["Ash"]["streams"]
    assert "recyclable" not in entries["Trash"]["streams"]


def test_source_linked_entries_have_dates_and_sources(client):
    entries = client.get("/dictionary.json").json["items"]
    linked = [entry for entry in entries if entry["guidance"]["status"] == "source-linked"]
    assert linked
    for entry in linked:
        assert entry["guidance"]["reviewedAt"]
        assert entry["guidance"]["sourceIds"]


@pytest.mark.parametrize("path", ["/home", "/AdminHome.html", "/AdminFeedback.html"])
def test_admin_pages_require_login(client, path):
    assert client.get(path).status_code == 302
    assert client.get(path).location == "/login"


def test_feedback_requires_login(client):
    assert client.get("/get_feedback").status_code == 401


def test_login_and_logout(client):
    assert login(client).status_code == 302
    assert client.get("/home").status_code == 200
    assert client.get("/AdminFeedback.html").status_code == 200
    assert client.get("/get_feedback").status_code == 200
    assert client.post("/logout", data={"csrf_token": csrf_token(client)}).status_code == 302
    assert client.get("/get_feedback").status_code == 401


def test_bad_password(client):
    response = client.post(
        "/login", data={"csrf_token": csrf_token(client), "username": "admin", "password": "password"}
    )
    assert response.status_code == 401
    assert client.get("/get_feedback").status_code == 401


def test_unicode_username_is_rejected_without_server_error(client):
    response = client.post(
        "/login", data={"csrf_token": csrf_token(client), "username": "異なる", "password": "test-password"}
    )
    assert response.status_code == 401


def test_oversized_password_is_rejected(client):
    response = client.post(
        "/login", data={"csrf_token": csrf_token(client), "username": "admin", "password": "x" * 201}
    )
    assert response.status_code == 401


def test_admin_disabled_without_configuration(app):
    app.config["ADMIN_PASSWORD_HASH"] = ""
    with app.test_client() as client:
        assert login(client).status_code == 503


@pytest.mark.parametrize("path", ["/submit_feedback", "/classify/upload", "/classify/realtime", "/login", "/logout"])
def test_csrf_required(client, path):
    assert client.post(path).status_code == 400


def test_invalid_csrf(client):
    csrf_token(client)
    assert (
        client.post(
            "/submit_feedback", headers={"X-CSRFToken": "invalid"}, json={"issue": "Test", "description": "Test"}
        ).status_code
        == 400
    )


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"issue": 1, "description": "x"},
        {"issue": " ", "description": "x"},
        {"issue": "x", "description": "x" * 2001},
    ],
)
def test_invalid_feedback(client, payload):
    response = client.post("/submit_feedback", json=payload, headers={"X-CSRFToken": csrf_token(client)})
    assert response.status_code == 400


def test_feedback_round_trip_keeps_text(client):
    payload = {"issue": "General feedback", "description": "<img src=x onerror=alert(1)>"}
    response = client.post("/submit_feedback", json=payload, headers={"X-CSRFToken": csrf_token(client)})
    assert response.status_code == 201
    login(client)
    saved = client.get("/get_feedback").json
    assert saved[0]["description"] == payload["description"]
    assert saved[0]["timestamp"].endswith("Z")


def test_concurrent_feedback_is_not_lost(app):
    def submit(index):
        with app.test_client() as client:
            return client.post(
                "/submit_feedback",
                json={"issue": "Test", "description": str(index)},
                headers={"X-CSRFToken": csrf_token(client)},
            ).status_code

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(submit, range(8))) == [201] * 8
    with app.test_client() as client:
        login(client)
        assert len(client.get("/get_feedback").json) == 8


@pytest.mark.parametrize("endpoint", ["/classify/upload", "/classify/realtime"])
def test_missing_and_invalid_upload(client, endpoint):
    token = csrf_token(client)
    assert client.post(endpoint, headers={"X-CSRFToken": token}).status_code == 400
    response = client.post(
        endpoint, headers={"X-CSRFToken": token}, data={"file": (io.BytesIO(b"not an image"), "test.png")}
    )
    assert response.status_code == 400


def test_missing_model_is_graceful(client):
    response = client.post(
        "/classify/upload", headers={"X-CSRFToken": csrf_token(client)}, data={"file": (image_file(), "test.png")}
    )
    assert response.status_code == 503
    assert client.get("/dictionary.json").status_code == 200


def test_upload_size_limit(client, app):
    app.config["MAX_CONTENT_LENGTH"] = 1024
    response = client.post(
        "/classify/upload",
        headers={"X-CSRFToken": csrf_token(client)},
        data={"file": (io.BytesIO(b"x" * 2048), "test.png")},
    )
    assert response.status_code == 413
    assert response.is_json


def test_successful_prediction_contract(client, app):
    class Model:
        def predict(self, image, verbose=0):
            assert image.shape == (1, 128, 128, 3)
            return np.array([[0.01, 0.01, 0.01, 0.01, 0.01, 0.94, 0.01]])

    app.extensions["classifier"]._model = Model()
    response = client.post(
        "/classify/upload", headers={"X-CSRFToken": csrf_token(client)}, data={"file": (image_file("RGBA"), "test.png")}
    )
    assert response.json == {"class": "Plastic", "confidence": 0.94}


def test_rate_limit_login(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "DATABASE": str(tmp_path / "rate.sqlite3"),
            "ADMIN_PASSWORD_HASH": "",
            "RATELIMIT_ENABLED": True,
        }
    )
    with app.test_client() as client:
        token = csrf_token(client)
        statuses = [client.post("/login", data={"csrf_token": token}).status_code for _ in range(6)]
        assert statuses == [503] * 5 + [429]


def test_dictionary_file_is_valid():
    catalog = json.loads((ROOT / "dictionary.json").read_text(encoding="utf-8"))
    assert catalog["schemaVersion"] == 2
    assert isinstance(catalog["items"], list)
