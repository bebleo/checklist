# Configuration tests for the application
# Copyright 2019, Licensed under MIT

import pytest
from werkzeug.security import generate_password_hash

from checklist_app import create_app, db, init_db, mail, talisman
from checklist_app.models import AccountStatus, Checklist, User, get_user


@pytest.fixture
def app():
    """Define a new instance for the tests."""
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False,
                      "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    with app.app_context():
        init_db()
        db.session.add_all([
            User(email="test@bebleo.url",
                 password=generate_password_hash("test")),
            User(email="other@bebleo.url",
                 password=generate_password_hash("other")),
            User(email="disabled@bebleo.url",
                 account_status=AccountStatus.DEACTIVATED,
                 password=generate_password_hash("disabled"))
        ])
        db.session.commit()

        user = get_user(username="test@bebleo.url")
        checklist = Checklist(
            title="List",
            description="A list created for testing purposes",
            created_by=user
        )
        checklist.add_item("Item 1.1", user)
        checklist.add_item("Item 1.2", user)
        checklist.add_item("Item 1.3", user, done=True)
        db.session.add(checklist)

        empty_list = Checklist(
            title="Empty List",
            description="A list with no items",
            created_by=user
        )
        db.session.add(empty_list)

        db.session.commit()

        app.mail = mail

        talisman.force_https = False

    yield app


@pytest.fixture
def client(app):
    """Returns a client for the tests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Returns a runner for the tests."""
    return app.test_cli_runner()


@pytest.fixture
def outbox(app):
    with app.mail.record_messages() as _outbox:
        yield _outbox


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
    return AuthActions(client)
