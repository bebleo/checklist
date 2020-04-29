# Tests for the checklist module in checklist_app
# December 2019, see LICENSE for licensing details.

import pytest

from checklist_app.models import Checklist, ChecklistItem

login_required = {
    "get": ['', '/', '/create', '/edit/1', '/1/check/1', '/1/add'],
    "post": ['/create', '/edit/1', '/1/add']
}


def test_get_checklists(app, client, auth):
    with app.app_context():
        auth.login()
        response = client.get('/checklist')
        assert response.status_code == 200
        assert b'Checklists' in response.data
        assert b'Empty List' in response.data
        assert b'0%' in response.data


def test_add_checklist(app, client, auth):
    checklist = {
        "list_title": "List no. 3",
        "list_description": "This is a list being added as a test"
    }
    with app.app_context():
        auth.login()
        response = client.post('/checklist/create', data=checklist)
        assert response.status_code == 302
        assert '/checklist/3' in response.headers['Location']

        list_ = Checklist.query.filter_by(title=checklist['list_title']).all()
        assert list_ is not None


def test_edit_checklist(app, client, auth):
    with app.app_context():
        auth.login()
        list_ = {
            "list_title": "Edited List",
            "list_description": "Edited description."
        }

        response = client.post('/checklist/edit/1', data=list_)
        assert response.status_code == 302
        assert '/checklist/1' in response.headers['Location']

        checklist = Checklist.query.get(1)
        assert checklist.title == list_['list_title']
        assert checklist.description == list_['list_description']


def test_add_item(app, client, auth):
    with app.app_context():
        auth.login()
        text = {"item_text": "Added item"}
        response = client.post('/checklist/1/add', data=text, follow_redirects=True)
        assert b'Added item' in response.data

        text = {"item_text": ""}
        response = client.post('/checklist/1/add', data=text, follow_redirects=True)
        assert b'Text for item required' in response.data


def test_mark_item_done(app, client, auth):
    with app.app_context():
        auth.login()
        response = client.get('/checklist/1/check/1')
        assert response.status_code == 302
        assert '/checklist/1' in response.headers['Location']

        item = ChecklistItem.query.get(1)
        assert item.done


def test_unmark_item_done(app, client, auth):
    with app.app_context():
        auth.login()
        response = client.get('/checklist/1/check/3')
        assert response.status_code == 302
        assert '/checklist/1' in response.headers['Location']

        item = ChecklistItem.query.get(3)
        assert not item.done


def test_delete_item(app, client, auth):
    with app.app_context():
        auth.login()
        response = client.get('/checklist/1/delete/1')
        assert response.status_code == 302
        assert '/checklist/1' in response.headers['Location']

        checklist = Checklist.query.get(1)
        assert checklist.percent_complete == 0.5


def test_mark_all_items_done(app, client, auth):
    with app.app_context():
        auth.login()
        response = client.get('/checklist/1/check/all')
        assert response.status_code == 302
        assert '/checklist/1' in response.headers['Location']

        for item in Checklist.query.get(1).items:
            assert item.done


def test_delete_checklist(app, client, auth):
    with app.app_context():
        auth.login()

        # Get the form and make sure the message displays
        response = client.get('/checklist/delete/1', follow_redirects=True)
        assert b'Delete' in response.data

        # Simulate clicking the button and check that the form is deleted
        data = {"confirm_delete": "1"}
        response = client.post('/checklist/delete/1', data=data)
        # redirects to the listing
        assert response.status_code == 302
        assert '/checklist' in response.headers['Location']
        # check that the changes have been made
        _list = Checklist.query.get(1)
        assert _list.is_deleted


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
