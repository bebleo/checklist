import pytest

from checklist_app.models.user import AccountStatus, get_user, User

def test_get_user(app):
    with app.app_context():
        user = get_user(username='test@bebleo.url')
        assert user is not None
        
        user = get_user('test@bebleo.url')
        assert user is not None

        user = get_user(id=1)
        assert user is not None

        user = get_user(username='not_a_valid_user')
        assert user is None

        with pytest.raises(ValueError) as e:
            user = get_user()
            assert 'No username or id' in str(e.value)

def test_initialize_new_user():
    user = User()
    assert user is not None

def test_account_status():
    deactivated = AccountStatus.ACTIVE
    assert deactivated == 0
    assert not deactivated

    status = AccountStatus(1)
    assert status == AccountStatus.DEACTIVATED
    assert 1 == AccountStatus.DEACTIVATED
