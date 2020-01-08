# -------------------------------------------
# DB related functions for the application
#
# James Warne
# December 8, 2019
# -------------------------------------------

import os
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    """Gets the database and adds it to g."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """Removes the database from the globals and closes it."""
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """Initializes the database."""
    db = get_db()

    with current_app.open_resource('schemas/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized database.')

def init_app(app):
    """Register the close_db function for teardown."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
