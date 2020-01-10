import pytest
from datetime import datetime, timedelta

from checklist_app.db import get_db
from checklist_app.models.password_token import (TokenExpiredError,
                                                 TokenInvalidError,
                                                 save_token,
                                                 validate_token)


def test_valid(app):
    with app.app_context():
        db = get_db()
        token = save_token(1)
        count = db.execute("SELECT COUNT(*) FROM password_tokens").fetchone()
        assert count[0] == 1
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
