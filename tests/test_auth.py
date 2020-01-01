import pytest

from checklist_app.db import get_db

def test_get_send_password_change(client):
    response = client.get('/auth/forgotpassword')
    assert b'Send Password Reset' in response.data

@pytest.mark.parametrize(
    "username, expected", 
    [
        ("false", b"No user found"), 
        ("admin@admin.ad", b"Password Sent")
    ]
)
def test_post_send_password_change(client, username, expected):
    response = client.post(
        '/auth/forgotpassword', 
        data = {"username": username}
    )
    assert expected in response.data

def test_forgot_password(app, client):
    with app.app_context():
        db = get_db()
        username = 'test@bebleo.url'

        client.post('/auth/forgotpassword', data={"username": username})
        user = db.execute(
            'SELECT * FROM users WHERE email = ?',
            (username,)
        ).fetchone()
        row = db.execute(
            'SELECT * FROM password_tokens WHERE user_id = ?',
            (user['id'],)
        ).fetchone()
        token = row['token']
        response = client.get(f'/auth/forgotpassword/{token}')
        assert b'Set New Password' in response.data

    response = client.post(
        f'/auth/forgotpassword/{token}',
        data = {
            "username": "test@bebleo.url",
            "password": "password",
            "confirm": "password"
        }
    )
    assert response.status_code == 302

@pytest.mark.parametrize(
    "registration_info, expected",
    [
        (
            {
                "username": "user1@example.url",
                "given_name": "User1",
                "family_name": "Bebleo",
                "password": "password",
                "confirm": "password"
            },
            b'You should be redirected automatically to target URL: <a href="/">/</a>.'
        ),
        (
            {
                "username": "",
                "given_name": "User1",
                "family_name": "Bebleo",
                "password": "password",
                "confirm": "password"
            },
            b'Username cannot be empty.'
        ),
        (
            {
                "username": "user1@example.url",
                "given_name": "User1",
                "family_name": "Bebleo",
                "password": "",
                "confirm": ""
            },
            b'Password cannot be empty.'
        ),
        (
            {
                "username": "user1@example.url",
                "given_name": "User1",
                "family_name": "Bebleo",
                "password": "password",
                "confirm": "not_password"
            },
            b'Password and confirmation must match.'
        ),
        (
            {
                "username": "admin@admin.ad",
                "given_name": "User1",
                "family_name": "Bebleo",
                "password": "password",
                "confirm": "password"
            },
            b'Username is already used.'
        )
    ]
)
def test_register(client, registration_info, expected):
    response = client.post('/auth/register', data=registration_info)
    assert expected in response.data

def test_register_already_logged_in(client, auth):
    auth.login()
    response = client.get('/auth/register')
    assert response.status_code == 401

def test_get_login(client):
    response = client.get('/auth/login')
    assert b'Register' in response.data

@pytest.mark.parametrize(
    "username, password, expected",
    [
        ("admin@admin.ad", "admin", 302),
        ("admin@admin.ad", "false-password", 200)
    ]
)
def test_post_login(client, username, password, expected):
    response = client.post('/auth/login', data={"username": username, "password": password})
    assert response.status_code == expected

def test_logout(client):
    response = client.get('/auth/logout')
    assert response.status_code == 302