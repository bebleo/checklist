from datetime import datetime, timedelta

import pytest

from checklist_app.models import (PasswordToken, TokenExpiredError,
                                  TokenInvalidError, save_token,
                                  validate_token)


def test_valid(app):
    with app.app_context():
        token = save_token(1)
        tokens = PasswordToken.query.all()
        assert len(tokens) == 1
        assert validate_token(token)


def test_invalid(app):
    with app.app_context():
        yesterday = datetime.utcnow() - timedelta(days=1)
        token = save_token(1, expiry=yesterday)
        with pytest.raises(TokenExpiredError, match=""):
            validate_token(token)

        token = save_token(1)
        with pytest.raises(TokenInvalidError, match=""):
            validate_token(token, user_id=2)
