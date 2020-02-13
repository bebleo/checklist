from datetime import datetime, timedelta
from secrets import token_urlsafe

import pytest

from checklist_app.models import (PasswordToken, TokenExpiredError,
                                  TokenInvalidError, TokenPurpose, save_token,
                                  validate_token)


def test_valid(app):
    with app.app_context():
        token = save_token(1)
        tokens = PasswordToken.query.all()
        assert len(tokens) == 1
        assert validate_token(token)


def test_valid_withvalue(app):
    with app.app_context():
        token = save_token(1, token_urlsafe())
        tokens = PasswordToken.query.all()
        assert len(tokens) == 1
        assert validate_token(token)

        password_token = PasswordToken.query.get(1)
        assert password_token.purpose == TokenPurpose.PASSWORD_RESET.__repr__()


def test_invalid(app):
    with app.app_context():
        yesterday = datetime.utcnow() - timedelta(days=1)
        token = save_token(1, expiry=yesterday)
        with pytest.raises(TokenExpiredError, match=""):
            validate_token(token)

        token = save_token(1)
        with pytest.raises(TokenInvalidError, match=""):
            validate_token(token, user_id=2)

        assert not validate_token(None)
