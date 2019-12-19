import os

from flask import (Blueprint, current_app, g, render_template,
                   send_from_directory)

bp = Blueprint('home', __name__)

@bp.route('/favicon.ico')
def favicon():
    """Serves the favicon from the static folder without redirects.
    Taken largely from the Flask documentation."""
    path = os.path.join(current_app.root_path, 'static')
    filename = 'favicon.ico'
    return send_from_directory(path, filename)

@bp.route('/')
@bp.route('/index')
def index():
    """returns the home page"""
    return render_template('home/index.html')

@bp.route('/about')
def about():
    """About us page."""
    return render_template('home/about.html')

@bp.route('/contact')
def contact():
    """Contact us page."""
    return render_template('home/contact.html')
