import pytest

from checklist_app.models import get_user, PasswordToken


def test_get_send_password_change(client):
    response = client.get('/auth/forgotpassword')
    assert b'Send Password Reset' in response.data


@pytest.mark.parametrize(
    "username, expected, msgcount",
    [
        ("false@bebleo.url", b"No user found", 0),
        ("admin@bebleo.url", b"Password Sent", 1)
    ]
)
def test_post_send_password_change(client, outbox, username, expected,
                                   msgcount):
    response = client.post('/auth/forgotpassword', data={"username": username})
    assert expected in response.data
    assert len(outbox) == msgcount


def test_forgot_password(app, outbox, client):
    with app.app_context():
        username = 'test@bebleo.url'
        client.post('/auth/forgotpassword', data={"username": username})

        user = get_user(username)
        print(user.__dict__)
        reset_token = PasswordToken.query.filter_by(user=user).first()
        print(reset_token.__dict__)
        response = client.get(f'/auth/forgotpassword/{reset_token.token}')
        assert b'Set New Password' in response.data
        assert len(outbox) > 0
        assert reset_token.token in outbox[0].body

    response = client.post(
        f'/auth/forgotpassword/{reset_token.token}',
        data={
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
            b'You should be redirected automatically to target'
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
                "username": "admin@bebleo.url",
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
        ("admin@bebleo.url", "admin", 302),
        ("admin@bebleo.url", "false-password", 200)
    ]
)
def test_post_login(client, username, password, expected):
    response = client.post('/auth/login',
                           data={"username": username, "password": password})
    assert response.status_code == expected


def test_post_login_diabled_user(client):
    """If a disabled user attempts to login direct them to the
    account disabled page."""
    response = client.post('/auth/login',
                           data={"username": "disabled@bebleo.url",
                                 "password": "disabled"})
    assert response.status_code == 302
    assert '/auth/disabled' in response.headers['Location']


def test_post_login_bad_user(client):
    response = client.post('/auth/login',
                           data={"username": "not_real@bebleo.url",
                                 "password": ""})
    assert b'Login incorrect, please try again.' in response.data


def test_logout(client):
    response = client.get('/auth/logout')
    assert response.status_code == 302
