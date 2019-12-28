import pytest

def test_index(client):
    response = client.get('/')
    assert b'Login' in response.data

def test_index_with_login(client, auth):
    auth.login()
    response = client.get('/')
    assert b'Logout' in response.data

def test_about(client):
    assert client.get('/about').status_code == 200

def test_contact(client):
    assert client.get('/contact').status_code == 200

def test_privacy(client):
    assert client.get('/privacy').status_code == 200

def test_favicon(client):
    assert client.get('/favicon.ico').status_code == 200

def test_page_not_found(client):
    assert client.get('/does_not_exist').status_code == 404
