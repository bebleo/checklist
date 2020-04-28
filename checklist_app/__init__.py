# ------------------------------------------------------------------
# Factory for the checklist application closely following the
# tutorial for Flask from the Pallets project site
#
# James Warne
# December 7, 2019
# ------------------------------------------------------------------

import logging
import os

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

csrf = CSRFProtect()
db = SQLAlchemy()
mail = Mail()
log = logging.getLogger(__name__)
talisman = Talisman()

_content_security_policy = {
    'default-src': '\'self\'',
    'script-src': [
        '\'self\'',
        'ajax.googleapis.com'
    ],
}


def create_app(test_config=None):
    """Creates the flask app and initilizes the instance folder
    as necessary.
    """
    app = Flask(__name__, instance_relative_config=True)

    db_path = os.path.join(app.instance_path, 'checklist.sqlite3')

    app.config.from_mapping(
        SECRET_KEY='<unsafe_secret_k3y/>',
        DATABASE=db_path,
        MAIL_SERVER='localhost',
        MAIL_USERNAME='',
        MAIL_PASSWORD='',
        MAIL_PORT=25,
        MAIL_USE_SSL=False,
        MAIL_USE_TLS=False,
        MAIL_SENDER='',
        MAIL_SUPPRESS_SEND=True,
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Load altenative mappings as necessary
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True, )
    else:
        app.config.from_mapping(test_config)

    # Create the Instance directory if not already there.
    os.makedirs(app.instance_path, exist_ok=True)

    talisman.init_app(app, content_security_policy=_content_security_policy,
                      content_security_policy_nonce_in=['script-src'])
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    log = app.logger

    # Register BluePrints
    from checklist_app import admin, auth, checklist, home
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(checklist.bp)
    app.register_blueprint(admin.bp)

    # Add the click commands
    app.cli.add_command(init_db_command)

    return app


def init_db():
    from checklist_app.models import User
    db.drop_all()
    db.create_all()
    db.session.add(
        User(email="admin@bebleo.url", is_admin=True,
             password=generate_password_hash("admin"))
    )
    db.session.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized database.')
