# Tests relating to the admin contoller
# Copyright 2020, James Warne
#
# 2020-01-02: Added tests for disabling a user.

import pytest

from checklist_app.models import AccountStatus, User, get_user

login_test_paths = ['/admin/users', '/admin/users/1', '/admin/users/new']
test_add_user_data = [
    (
        {
            "username": "user@bebleo.url",
            "given_name": "User",
            "family_name": "Bebleo",
            "password": "password",
            "confirm": "password",
            "is_admin": ""
        },
        b'Success',
        5,
        False
    ),
    (
        {
            "username": "admin@bebleo.url",
            "given_name": "User",
            "family_name": "Bebleo",
            "password": "password",
            "confirm": "password",
            "is_admin": ""
        },
        b'Username already exists',
        1,
        True
    ),
    (
        {
            "username": "success@bebleo.url",
            "given_name": "Admin",
            "family_name": "Bebleo",
            "password": "password",
            "confirm": "password",
            "is_admin": "checked"
        },
        b'Success',
        5,
        True
    )
]


def test_get_user(app):
    with app.app_context():
        user = get_user(username='test@bebleo.url')
        assert user.id == 2

        user = get_user(id=2)
        assert user.email == 'test@bebleo.url'

        with pytest.raises(ValueError) as e:
            user = get_user()
            assert 'No username or id' in str(e.value)


def test_list_users(client, auth):
    auth.login(username="admin@bebleo.url", password="admin")
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b'<h2>Users</h2>' in response.data


def test_get_edit_user(client, auth):
    auth.login(username="admin@bebleo.url", password="admin")
    response = client.get('/admin/users/1')
    assert response.status_code == 200
    assert b'admin@bebleo.url' in response.data

    response = client.get('/admin/users/5')
    assert response.status_code == 404


def test_edit_user(app, client, auth):
    # Test that the username needs to be there
    with app.app_context():
        auth.login(username="admin@bebleo.url", password="admin")
        data = {
            "username": "",
            "given_name": "",
            "family_name": ""
        }
        response = client.post('/admin/users/3', data=data)
        assert b'Username must not be blank.' in response.data
        user = User.query.filter_by(id=3).first()
        assert user.email != ""

    # Test that a user cannot remove their own admin flag
    with app.app_context():
        data = {
            "username": "admin@bebleo.url",
            "given_name": "Admin",
            "family_name": "Administrator"
        }
        auth.login(username="admin@bebleo.url", password="admin")
        response = client.post('/admin/users/1', data=data)
        assert b'Cannot remove admin rights from your own' in response.data
        user = User.query.filter_by(id=1).first()
        assert user.is_admin

    # Test a succesful edit
    with app.app_context():
        data = {
            "username": "modified@bebleo.url",
            "given_name": "Modified",
            "family_name": "Bebleo-User",
            "is_admin": "checked"
        }
        auth.login(username="admin@bebleo.url", password="admin")
        response = client.post('/admin/users/3', data=data)
        assert b'Success' in response.data
        user = User.query.filter_by(id=3).first()
        assert user.email == "modified@bebleo.url"
        assert user.full_name == "Modified Bebleo-User"
        assert user.is_admin


def test_get_add_user(client, auth):
    auth.login(username="admin@bebleo.url", password="admin")
    response = client.get('/admin/users/new')
    assert b'Add User' in response.data


@pytest.mark.parametrize("info, expected, id, is_admin", test_add_user_data)
def test_add_user(app, client, auth, info, expected, id, is_admin):
    auth.login(username="admin@bebleo.url", password="admin")
    response = client.post('/admin/users/new', data=info)
    assert expected in response.data

    with app.app_context():
        user = User.query.filter_by(email=info["username"]).first()
        assert user.id == id
        assert user.is_admin == is_admin


def test_add_user_mismatched_passwords(client, auth):
    info = {
        "username": "mismatched@bebleo.url",
        "given_name": "Mismatched",
        "family_name": "Bebleo",
        "password": "password",
        "confirm": "not_password",
        "is_admin": ""
    }
    expected = b'Password and confirmation must match'

    auth.login(username="admin@bebleo.url", password="admin")
    response = client.post('/admin/users/new', data=info)
    assert expected in response.data


def test_disable_user_on_edit_success(app, client, auth):
    """Disable a user."""
    # A user needs to be disabled so the administrator logs in and sets
    # the account disabled flag. The database record is then updated and
    # the success message returned to the administrator.
    info = {
        "username": "username@bebleo.url",
        "given_name": "User",
        "family_name": "Name",
        "account_flag": 1
    }

    with app.app_context():
        auth.login(username='admin@bebleo.url', password='admin')
        response = client.post('/admin/users/2', data=info)
        assert b'Success' in response.data

        record = User.query.get(2)
        assert record.account_status == AccountStatus.DEACTIVATED


def test_disable_user_on_edit_not_allowed(app, client, auth):
    # We don't want it to be the case that users can accidentally disable
    # their own accounts because they would then be unable to correct. Check
    # that if a user edits their own profile and set the account disabled
    # flag that they will get an error message.
    info = {
        "username": "username@bebleo.url",
        "given_name": "User",
        "family_name": "Name",
        "is_admin": True,
        "account_flag": 1
    }

    with app.app_context():
        auth.login(username="admin@bebleo.url", password="admin")
        response = client.post('/admin/users/1', data=info)
        assert b'Cannot deactivate' in response.data

        user = User.query.get(1)
        assert not user.deactivated
        assert user.account_status == AccountStatus.ACTIVE


@pytest.mark.parametrize("path", login_test_paths)
def test_login_required(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


@pytest.mark.parametrize("path", login_test_paths)
def test_admin_required(client, auth, path):
    auth.login()
    response = client.get(path, follow_redirects=True)
    assert response.status_code == 401
