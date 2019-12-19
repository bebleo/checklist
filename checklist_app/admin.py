# -----------------------------------------------------
# Admin controller for the checklist solution
#
# James Warne
# December 13, 2019
# -----------------------------------------------------

from flask import (Blueprint, current_app, flash, g, redirect, render_template,
                   request)
from werkzeug.exceptions import abort

from checklist_app.auth import admin_required
from checklist_app.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

def checked(field):
    """Returns a boolean figure based on whether a checkbox has been
    found and checked on the form.

    Limited in that the way to determine is if the checkbox has been
    returned in the form data. If the name doesn't match, therefore,
    this method will always return False not an error."""
    if request.form.get(field):
        return True

    return False

@bp.route('/users')
@admin_required
def list_users():
    """List all of the users in the application."""
    db = get_db()
    users_query = 'SELECT * FROM users'
    users = db.execute(users_query).fetchall()

    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:id>', methods=('GET', 'POST'))
@admin_required
def edit_user(id):
    """Edit the user with the id.

    :param id: the id for the user."""
    db = get_db()
    user_query = 'SELECT * FROM users WHERE id = ?'
    user = db.execute(user_query, (id, )).fetchone()
    success = False

    if not user:
        # ID doesn't exist in the database so return
        # page not found.
        abort(404)

    if request.method == 'POST':
        username = request.form['username'].strip()
        given_name = request.form['given_name'].strip()
        family_name = request.form['family_name'].strip()
        is_admin = checked('is_admin')
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
            db.execute("""UPDATE 
                            users 
                          SET 
                            email = ?, 
                            given_name = ?, 
                            family_name = ?, 
                            is_admin = ? 
                          WHERE 
                            id = ?""", 
                          (username, 
                           given_name, 
                           family_name, 
                           is_admin, 
                           id))
            user = db.execute(user_query, (id, )).fetchone()
            db.commit()
            success = True

    return render_template('admin/edit_user.html', user=user, success=success)
