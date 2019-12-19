# ------------------------------------------------------------------
# Factory for the checklist application closely following the 
# tutorial for Flask from the Pallets project site
#
# James Warne
# December 7, 2019
# ------------------------------------------------------------------

import os

from flask import Flask
from flask_mail import Mail

from . import admin, auth, db, home, checklist

def create_app(test_config=None):
    """Creates the flask app and initilizes the instance folder
        as necessary."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='<unsafe_secret_k3y/>',
        DATABASE=os.path.join(app.instance_path, 'checklist.sqlite3'),
    )

    # Load altenative mappings as necessary
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Create the Instance directory if not already there.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Wireup the database and mail.
    db.init_app(app)

    # Register BluePrints
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(checklist.bp)
    app.register_blueprint(admin.bp)

    return app
