import pytest

from checklist_app.admin import user_by_username
from checklist_app.db import get_db

test_add_user_data = [
    (
        {
            "username": "user@bebleo.url",
            "given_name": "User",
            "family_name": "Bebleo",
            "password": "password",
            "confirmed": "password",
            "is_admin": ""
        },
        b'Success',
        4,
        False
    ),
    (
        {
            "username": "admin@admin.ad",
            "given_name": "User",
            "family_name": "Bebleo",
            "password": "password",
            "confirmed": "password",
            "is_admin": ""
        },
        b'Username already exists',
        1,
        True
    ),
    (
        {
            "username": "admin@bebleo.url",
            "given_name": "Admin",
            "family_name": "Bebleo",
            "password": "password",
            "confirmed": "password",
            "is_admin": "checked"
        },
        b'Success',
        4,
        True
    )
]

def test_user_by_username(app):
    with app.app_context():
        user = user_by_username(username='test@bebleo.url')
        assert user['id'] == 2

        user = user_by_username(id=2)
        assert user['email'] == 'test@bebleo.url'

        with pytest.raises(ValueError) as e:
            user = user_by_username()
            assert 'No username or id' in str(e.value)

def test_list_users(client, auth):
    auth.login(username="admin@admin.ad", password="admin")
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b'<h2>Users</h2>' in response.data

def test_get_edit_user(client, auth):
    auth.login(username="admin@admin.ad", password="admin")
    response = client.get('/admin/users/1')
    assert response.status_code == 200
    assert b'admin@admin.ad' in response.data

    response = client.get('/admin/users/4')
    assert response.status_code == 404

def test_edit_user(app, client, auth):
    # Test that the username needs to be there
    with app.app_context():
        auth.login(username="admin@admin.ad", password="admin")
        db = get_db()
        data = {
            "username": "",
            "given_name": "",
            "family_name": ""
        }
        response = client.post('/admin/users/3', data=data)
        assert b'Username must not be blank.' in response.data
        user = db.execute("SELECT * FROM users WHERE id = ?", (3,)).fetchone()
        assert user['email'] is not ""

    # Test that a user cannot remove their own admin flag
    with app.app_context():
        db = get_db()
        data = {
            "username": "admin@admin.ad",
            "given_name": "Admin",
            "family_name": "Administrator"
        }
        auth.login(username="admin@admin.ad", password="admin")
        response = client.post('/admin/users/1', data=data)
        assert b'Cannot remove admin rights from own account' in response.data
        user = db.execute("SELECT * FROM users WHERE id = ?", (1,)).fetchone()
        assert user['is_admin']

    # Test a succesful edit
    with app.app_context():
        db = get_db()
        data = {
            "username": "modified@bebleo.url",
            "given_name": "Modified",
            "family_name": "Bebleo-User",
            "is_admin": "checked"
        }
        auth.login(username="admin@admin.ad", password="admin")
        response = client.post('/admin/users/3', data=data)
        assert b'Success' in response.data
        user = db.execute("SELECT * FROM users WHERE id = ?", (3,)).fetchone()
        assert user['email'] == "modified@bebleo.url"
        assert user['given_name'] == "Modified"
        assert user['family_name'] == "Bebleo-User"
        assert user['is_admin']

def test_get_add_user(client, auth):
    auth.login(username="admin@admin.ad", password="admin")
    response = client.get('/admin/users/new')
    assert b'Add User' in response.data

@pytest.mark.parametrize("info, expected, id, is_admin", test_add_user_data)
def test_add_user(app, client, auth, info, expected, id, is_admin):
    auth.login(username = "admin@admin.ad", password = "admin")
    response = client.post('/admin/users/new', data = info)
    assert expected in response.data

    with app.app_context():
        db = get_db()
        print(f"Username being added is {info['username']}")

        added_user = db.execute(
            'SELECT * FROM users WHERE email = ?;',
            (info['username'],)
        ).fetchone()

        assert added_user['id'] == id
        assert added_user['is_admin'] == is_admin

def test_add_user_mismatched_passwords(client, auth):
    info = {
        "username": "mismatched@bebleo.url",
        "given_name": "Mismatched",
        "family_name": "Bebleo",
        "password": "password",
        "confirmed": "not_password",
        "is_admin": ""
    }
    expected = b'Password and confirmation must match'

    auth.login(username="admin@admin.ad", password="admin")
    response = client.post('/admin/users/new', data=info)
    assert expected in response.data

@pytest.mark.parametrize("path", ['/admin/users', '/admin/users/1', '/admin/users/new'])
def test_login_required(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

@pytest.mark.parametrize("path", ['/admin/users', '/admin/users/1', '/admin/users/new'])
def test_admin_required(client, auth, path):
    auth.login()
    response = client.get(path, follow_redirects=True)
    assert response.status_code == 401
