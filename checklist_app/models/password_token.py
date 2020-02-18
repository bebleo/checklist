from datetime import datetime, timedelta
from enum import Enum
from secrets import token_urlsafe

from checklist_app import db

__all__ = (
    "PasswordToken",
    "TokenExpiredError",
    "TokenInvalidError",
    "TokenPurpose",
    "save_token",
    "validate_token",
)


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


class PasswordToken(db.Model):
    default_expiry = datetime.utcnow() + timedelta(hours=24)
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    purpose = db.Column(db.String, nullable=False,
                        default=TokenPurpose.PASSWORD_RESET.value)
    expires = db.Column(db.DateTime, default=default_expiry)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)

    user = db.relationship('User',
                           backref=db.backref('tokens', lazy=True))


def save_token(user_id, token=None, purpose=TokenPurpose.PASSWORD_RESET,
               expiry=datetime.utcnow()+timedelta(hours=24)):
    """Saves a token to the database and returns it. If no token is
    supplied then the token is generated using secrets.token_urlsafe().

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

    pt = PasswordToken(token=token, expires=expiry, user_id=user_id)
    db.session.add(pt)
    db.session.commit()

    return token


def _get_token(token):
    """Retrive a password token from the database."""
    _token = PasswordToken.query.filter_by(token=token).first()
    return _token


def validate_token(token, user_id=None, purpose=TokenPurpose.PASSWORD_RESET,
                   enforce_expiry=True):
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

    if _password_token.expires < datetime.utcnow() and enforce_expiry:
        raise TokenExpiredError()

    if user_id and _password_token.user_id != user_id:
        raise TokenInvalidError()

    # if _password_token.purpose != purpose.value:
    #     raise TokenInvalidError()

    return True
