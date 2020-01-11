# -----------------------------------------------------
# Admin controller for the checklist solution
#
# James Warne
# December 13, 2019
# -----------------------------------------------------

from flask import (Blueprint, abort, current_app, flash, g, render_template,
                   request, url_for)
from werkzeug.security import generate_password_hash

from checklist_app.auth import admin_required, login_required
from checklist_app.db import get_db
from checklist_app.forms.admin_forms import AddUserForm, EditUserForm
from checklist_app.models.user import get_user

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
    form = EditUserForm()
    user = get_user(id=id)
    saved = False

    if not user:
        # ID doesn't exist in the database so return 404-Page Not Found.
        abort(404)

    deactivated = user['deactivated'] if user['deactivated'] else 0

    # If the user isn't an admin check that user id matches the logged in user.
    # If not then abort the request with a 401-Unauthorized error
    if not g.user['is_admin']:
        if user['id'] != g.user['id']:
            abort(401)

    if form.validate_on_submit():
        username = form.username.data
        given_name = form.given_name.data
        family_name = form.family_name.data
        is_admin = form.is_admin.data
        if checked('account_flag'):
            account_flag = request.form.get('account_flag')
        else:
            account_flag = 0

        db = get_db()
        error = None
        if account_flag:
            deactivated = max(account_flag)
        else:
            deactivated = 0

        if not username:
            error = 'Username must not be blank.'
        elif g.user['id'] == id:
            # Make it impossible to remove oneself as an admin.
            # This ensures that there is always at least on admin.
            if user['is_admin'] and not is_admin:
                error = 'Cannot remove admin rights from your own account.'
            elif account_flag:
                error = "Cannot deactivate your own account."

        if error:
            flash(error)
        else:
            db.execute(
                """UPDATE users SET
                   email = ?, given_name = ?, family_name = ?,
                   is_admin = ?, deactivated = ?
                   WHERE id = ?;""",
                (username, given_name, family_name, is_admin, deactivated, id)
            )
            user = user_by_username(id=id)
            db.commit()
            saved = True

    return render_template('admin/edit_user.html', form=form, user=user,
                           deactivated=deactivated, success=saved)


def validate_password(password_field='password', confirmation_field='confirm'):
    return request.form[password_field] == request.form[confirmation_field]


@bp.route('/users/new', methods=('GET', 'POST'))
@admin_required
def add_user():
    """Add a user to the solution."""
    saved = False
    form = AddUserForm()

    if form.validate_on_submit():
        username = form.username.data
        given_name = form.given_name.data
        family_name = form.family_name.data
        password = form.password.data
        is_admin = form.is_admin.data

        user_check = get_user(username=username)

        if user_check:
            # Username already in use.
            error = (f"Username already exists. <a href=\"",
                     f"{url_for('admin.edit_user', id=user_check['id'])}",
                     f"\">Edit</a>")
            flash(error)
        else:
            db = get_db()
            db.execute(
                """INSERT INTO users
                   (email, given_name, family_name, password, is_admin)
                   VALUES (?, ?, ?, ?, ?);""",
                (username, given_name, family_name,
                 generate_password_hash(password), is_admin, )
            )
            db.commit()
            saved = True

    return render_template('admin/add_user.html', form=form, success=saved)
