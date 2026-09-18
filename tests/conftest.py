import re

import pytest
from werkzeug.security import generate_password_hash

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-key-not-for-deployment",
            "DATABASE": str(tmp_path / "feedback.sqlite3"),
            "MODEL_PATH": str(tmp_path / "missing.h5"),
            "ADMIN_PASSWORD_HASH": generate_password_hash("test-password"),
            "RATELIMIT_ENABLED": False,
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()


def csrf_token(client, path="/"):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)


def login(client):
    return client.post(
        "/login",
        data={
            "csrf_token": csrf_token(client, "/login"),
            "username": "admin",
            "password": "test-password",
        },
    )
