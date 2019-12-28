# -----------------------------------------------------
# Admin controller for the checklist solution
#
# James Warne
# December 13, 2019
# -----------------------------------------------------

from flask import (abort, Blueprint, current_app, flash, g, redirect, render_template,
                   request, url_for)
from werkzeug.security import generate_password_hash

from checklist_app.auth import admin_required, login_required
from checklist_app.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

def checked(field):
    """
    Returns True/False based on whether a checkbox has been
    found and checked on the form.

    Limited in that the way to determine is if the checkbox has been
    returned in the form data. If the name doesn't match, therefore,
    this method will always return False not an error.
    """
    if request.form.get(field):
        return True

    return False

def user_by_username(username=None, id=None):
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

@bp.route('/users')
@admin_required
def list_users():
    """
    List all of the users in the application
    
    Returns
    -------
    Returns the rendered view that lists all of the users
    in the application.
    """
    db = get_db()
    users = db.execute('SELECT * FROM users').fetchall()

    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_user(id: int):
    """Edit the user with the id."""
    user = user_by_username(id=id)
    saved = False

    if not user:
        # ID doesn't exist in the database so return 404-Page Not Found.
        abort(404)

    # If the user isn't an admin check that the user id matches the logged in user.
    # If not then abort the request with a 401-Unauthorized error
    if not g.user['is_admin']:
        current_app.logger.debug(f"user with id {g.user['id']} is editing user with id {user['id']}.")
        if user['id'] != g.user['id']:
            abort(401)

    if request.method == 'POST':
        username = request.form['username'].strip()
        given_name = request.form['given_name'].strip()
        family_name = request.form['family_name'].strip()
        is_admin = checked('is_admin')

        db = get_db()
        error = None

        if not username:
            error = 'Username must not be blank.'
        elif g.user['id'] == id:
            # Make it impossible to remove oneself as an admin.
            # This ensures that there is always at least on admin.
            if user['is_admin'] and not is_admin:
                error = 'Cannot remove admin rights from own account.' 

        if error:
            flash(error)
        else:
            db.execute(
                """UPDATE users SET 
                      email = ?,
                      given_name = ?, 
                      family_name = ?, 
                      is_admin = ? 
                   WHERE 
                      id = ?
                """, 
                (username, given_name, family_name, is_admin, id)
            )
            user = user_by_username(id=id)
            db.commit()
            saved = True

    return render_template('admin/edit_user.html', user=user, success=saved)

@bp.route('/users/new', methods=('GET', 'POST'))
@admin_required
def add_user():
    """Add a user to the solution."""
    user = None
    saved = False
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        given_name = request.form['given_name'].strip()
        family_name = request.form['family_name'].strip()
        password = request.form['password'].strip()
        confirm = request.form['confirmed'].strip()
        is_admin = checked('is_admin')

        error = None
        user_check = user_by_username(username=username)

        if user_check:
            # Username already in use.
            error = f"Username already exists. <a href=\"{url_for('admin.edit_user', id=user_check['id'])}\">Edit</a>"
        elif password != confirm:
            error = "Password and confirmation must match"

        if error:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """INSERT INTO users (email, given_name, family_name, password, is_admin) VALUES (?, ?, ?, ?, ?);""",
                (username, given_name, family_name, generate_password_hash(password), is_admin, )
            )
            db.commit()
        
            saved = True
  
    return render_template('admin/add_user.html', user=user, success=saved)
