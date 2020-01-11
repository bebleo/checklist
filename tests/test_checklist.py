# Tests for the checklist module in checklist_app
# December 2019, see LICENSE for licensing details.

import pytest

from checklist_app.db import get_db

login_required = {
    "get": ['', '/', '/create', '/edit/1', '/1/check/1', '/1/add'],
    "post": ['/create', '/edit/1', '/1/add']
}


def test_get_checklists(client, auth):
    auth.login()
    response = client.get('/checklist')
    assert response.status_code == 200
    assert b'Checklists' in response.data


def test_add_checklist(app, client, auth):
    auth.login()
    checklist = {
        "list_title": "List no. 3",
        "list_description": "This is a list being added as a test"
    }
    with app.app_context():
        response = client.post('/checklist/create', data=checklist)
        assert response.status_code == 302
        assert '/checklist/3' in response.headers['Location']

        db = get_db()
        list_ = db.execute('SELECT * FROM checklists WHERE title = ?',
                           (checklist['list_title'],)).fetchone()
        assert list_ is not None


def test_edit_checklist(app, client, auth):
    with app.app_context():
        db = get_db()
        auth.login()
        list_ = {
            "list_title": "Edited List",
            "list_description": "Edited description."
        }

        response = client.post('/checklist/edit/1', data=list_)
        assert response.status_code == 302
        assert '/checklist/1' in response.headers['Location']

        checklist = db.execute("""SELECT * FROM checklists
                                  WHERE id = 1;""").fetchone()
        assert checklist['title'] == list_['list_title']
        assert checklist['description'] == list_['list_description']


def test_mark_item_done(app, client, auth):
    with app.app_context():
        auth.login()
        response = client.get('/checklist/1/check/1')
        assert response.status_code == 302
        assert '/checklist/1' in response.headers['Location']

        db = get_db()
        item = db.execute("""SELECT * FROM checklist_items
                             WHERE id = 1""").fetchone()
        assert item['done']


def test_unmark_item_done(app, client, auth):
    with app.app_context():
        auth.login()
        response = client.get('/checklist/2/check/4')
        assert response.status_code == 302
        assert '/checklist/2' in response.headers['Location']

        db = get_db()
        item = db.execute("""SELECT * FROM checklist_items
                             WHERE id = 4""").fetchone()
        assert not item['done']


def test_delete_checklist(app, client, auth):
    with app.app_context():
        db = get_db()
        auth.login()

        # Get the form and make sure the message displays
        response = client.get('/checklist/delete/1', follow_redirects=True)
        assert b'Delete' in response.data

        # Simulate clicking the button and check that the form is deleted
        data = {
            "confirm_delete": "1"
        }
        response = client.post('/checklist/delete/1', data=data)
        # redirects to the listing
        assert response.status_code == 302
        assert '/checklist' in response.headers['Location']
        # check that the changes have been made
        _list = db.execute("SELECT * FROM checklists WHERE id = 1").fetchone()
        assert _list['is_deleted']
        history = db.execute("""SELECT * FROM checklist_history
                                WHERE checklist_id = 1
                                ORDER BY id DESC LIMIT 1""").fetchone()
        assert 'deleted' in history['change_description']


@pytest.mark.parametrize("path", login_required['get'])
def test_get_login_required(client, path):
    response = client.get('/checklist' + path)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


@pytest.mark.parametrize("path", login_required['post'])
def test_post_login_required(client, path):
    response = client.post('/checklist' + path)
    assert response.status_code == 302
    assert 'auth/login' in response.headers['Location']
