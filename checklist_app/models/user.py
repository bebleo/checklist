# Classes and functions relating to users
# Copyright 2019. Licensed under MIT

from datetime import datetime
from enum import IntEnum

from flask import current_app

from checklist_app import db

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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    given_name = db.Column(db.String)
    family_name = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
    deactivated = db.Column(db.Integer, default=AccountStatus.ACTIVE.value)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    """User object here as a stub for future development."""
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @property
    def full_name(self):
        return f"{self.given_name} {self.family_name}"

    @property
    def account_status(self):
        return AccountStatus(self.deactivated)

    @account_status.setter
    def account_status(self, value):
        self.deactivated = value.value


def get_user(username=None, id=None):
    """
    Get the user identified by the id or the username.
    Return None if the user does not exist.
    """
    if id:
        user = User.query.filter_by(id=id).first()
    elif username:
        user = User.query.filter_by(email=username).first()
    else:
        current_app.logger.error('No argument supplied to fetch user from db.')
        raise ValueError("No username or id supplied to get user.")

    return user
