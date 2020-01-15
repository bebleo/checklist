# -----------------------------------------------------
# Admin controller for the checklist solution
#
# James Warne
# December 13, 2019
# -----------------------------------------------------

from flask import Blueprint, abort, flash, g, render_template, request, url_for
from werkzeug.security import generate_password_hash

from checklist_app import db
from checklist_app.auth import admin_required, login_required
from checklist_app.forms import AddUserForm, EditUserForm
from checklist_app.models import AccountStatus, User, get_user, get_user_or_404

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
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@bp.route('/users/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_user(id: int):
    """Edit the user with the id."""
    form = EditUserForm()
    user = get_user_or_404(id=id)
    saved = False

    # If the user isn't an admin check that user id matches the logged in user.
    # If not then abort the request with a 401-Unauthorized error
    if not g.user.is_admin:
        if id != g.user.id:
            abort(401)

    deactivated = 0

    if form.validate_on_submit():
        username = form.username.data
        given_name = form.given_name.data
        family_name = form.family_name.data
        is_admin = form.is_admin.data
        if checked('account_flag'):
            account_flag = int(request.form.get('account_flag'))
        else:
            account_flag = 0

        error = None
        deactivated = account_flag

        if not username:
            error = 'Username must not be blank.'
        elif g.user.id == id:
            # Make it impossible to remove oneself as an admin.
            # This ensures that there is always at least on admin.
            if user.is_admin and not is_admin:
                error = 'Cannot remove admin rights from your own account.'
            elif account_flag:
                error = "Cannot deactivate your own account."

        if error:
            flash(error)
        else:
            user.email = username
            user.given_name = given_name
            user.family_name = family_name
            user.is_admin = is_admin
            user.account_status = AccountStatus(deactivated)
            db.session.add(user)
            db.session.commit()
            saved = True

    return render_template('admin/edit_user.html', form=form, user=user,
                           deactivated=deactivated, success=saved)


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
                     f"{url_for('admin.edit_user', id=user_check.id)}",
                     f"\">Edit</a>")
            flash(error)
        else:
            user = User(email=username, given_name=given_name,
                        family_name=family_name, is_admin=is_admin,
                        password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            saved = True

    return render_template('admin/add_user.html', form=form, success=saved)
