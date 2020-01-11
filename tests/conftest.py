# Configuration tests for the application
# Copyright 2019, Licensed under MIT

import os
import tempfile

import pytest

from checklist_app import create_app
from checklist_app.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    """Define a new instance for the tests."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "DATABASE": db_path,
                      "WTF_CSRF_ENABLED": False})

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Returns a client for the tests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Returns a runner for the tests."""
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test@bebleo.url", password="test"):
        """Login to the app."""
        return self._client.post('/auth/login',
                                 data={"username": username,
                                       "password": password})

    def logout(self):
        """Logout from the application."""
        return self._client.post('/auth/logout')


@pytest.fixture
def auth(client):
    print("auth called")
    return AuthActions(client)
