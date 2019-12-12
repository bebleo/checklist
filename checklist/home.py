from flask import (Blueprint, g, render_template)


bp = Blueprint('home', __name__)


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
    