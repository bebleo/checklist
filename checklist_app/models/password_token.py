import logging
from datetime import datetime, timedelta

from enum import Enum
from secrets import token_urlsafe

from checklist_app.db import get_db

logger = logging.getLogger(__name__)

class TokenExpiredError(Exception):
    def __init__(self, *args):
        super(*args)

class TokenInvalidError(Exception):
    def __init__(self, *args):
        super(*args)

class TokenPurpose(Enum):
    PASSWORD_RESET = "password_reset"

    def __repr__(self):
        # Return the string as the representation
        # mimicing "Magic classes".
        return self.value

def save_token(user_id, token=None, purpose=TokenPurpose.PASSWORD_RESET,
    expiry=datetime.utcnow()+timedelta(hours=24)):
    """Saves a token to the database and returns it. If no token is supplied then the
    token is generated using secrets.token_urlsafe().

    Parameters:
    -----------
    * user_id: The identifier for the user.
    * token: The token value to be verified. If None then generated for you.
    * expiry: The expiry for the token.

    Returns:
    --------
    The token on succesful insert to the database.
    """
    if token is None:
        token = token_urlsafe()

    db = get_db()
    db.execute(
        'INSERT INTO password_tokens (user_id, token, token_type, expires) VALUES (?, ?, ?, ?)',
        (user_id, token, f'{purpose}', expiry)
    )
    db.commit()

    return token

def _get_token(token):
    """Retrive a password token from the database."""
    _token = get_db().execute("SELECT * FROM password_tokens WHERE token = ?", (token,)).fetchone()

    return _token

def validate_token(token, user_id=None, purpose=TokenPurpose.PASSWORD_RESET, enforce_expiry=True):
    """Validate a provided token.

    Parameters:
    -----------
    * token: The token value.
    * user_id: The user for the token. If None then the check isn't performed
    * purpose: A TokenPurpose by default PASSWORD_RESET
    * enforce_expiry: If True enforce the token expiry. (Default is True)

    Raises:
    -------
    * TokenExpiredError if the token has expired.
    * TokenInvalidError if the token is invalid for some reason.

    Returns:
    --------
    True if the token is valid, False otherwise.
    """
    _password_token = _get_token(token)

    if _password_token is None:
        return False

    if _password_token['expires'] < datetime.utcnow() and enforce_expiry:
        raise TokenExpiredError()

    if user_id and \
    _password_token['user_id'] != user_id:
        raise TokenInvalidError()

    if _password_token['token_type'] != f'{purpose}':
        raise TokenInvalidError()

    return True
