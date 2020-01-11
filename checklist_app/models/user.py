# Classes and functions relating to users
# Copyright 2019. Licensed under MIT

from enum import IntEnum

from flask import current_app

from checklist_app.db import get_db

__all__ = (
    "AccountStatus",
    "User",
    "get_user",
)


class AccountStatus(IntEnum):
    """Account Statuses."""
    ACTIVE = 0
    DEACTIVATED = 1
    VERIFICATION_REQUIRED = 2
    PASSWORD_RESET_REQUIRED = 3


class User(object):
    """User object here as a stub for future development."""
    def __init__(self):
        pass


def get_user(username=None, id=None):
    """
    Get the user identified by the id or the username.
    Return None if the user does not exist.
    """
    db = get_db()

    if id:
        variable = "id"
        values = (id, )
    elif username:
        variable = 'email'
        values = (username, )
    else:
        current_app.logger.error('No argument supplied to fetch user from db.')
        raise ValueError("No username or id supplied to get user.")

    user = db.execute(
        f'SELECT * FROM users WHERE {variable} = ?',
        values
    ).fetchone()

    return user
