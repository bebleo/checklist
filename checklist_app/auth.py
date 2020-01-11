# ----------------------------------------------------------------------
# checklist.auth
# Handles user, authentication, registration and related matters. Based
# heavily on the Flask tutorial
#
# James Warne
# December 12, 2019
# ----------------------------------------------------------------------

import functools

from flask import (Blueprint, abort, current_app, flash, g, redirect,
                   render_template, request, session, url_for)
from flask_mail import Mail
from werkzeug.security import generate_password_hash

from checklist_app.db import get_db
from checklist_app.forms import (LoginForm, RegistrationForm,
                                 SendPasswordChangeForm, UpdatePasswordForm)
from checklist_app.models.password_token import (
    TokenExpiredError, TokenInvalidError, save_token, validate_token)

from .models.user import get_user

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def check_login(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        elif g.user['deactivated']:
            return redirect(url_for('auth.deactivated'))

        return view(**kwargs)

    return check_login


def admin_required(view):
    @functools.wraps(view)
    @login_required
    def check_admin(**kwargs):
        if not g.user['is_admin']:
            abort(401)

        return view(**kwargs)

    return check_admin


@bp.route('/forgotpassword', methods=('GET', 'POST'))
def send_password_change():
    """Get the user email and send the link with the reset token."""
    form = SendPasswordChangeForm()
    sent = False
    token = None

    if form.validate_on_submit():
        email = form.username.data
        current_app.logger.debug(f"{email} sent for password reset.")
        user = get_user(username=email)

        if user is None:
            # If no user exists with that email flash that message.
            flash("No user found with email.")
        else:
            token = save_token(user['id'])
            _body = render_template('emails/send_password_change.txt',
                                    host=request.host, user=user,
                                    token=token)
            mail = Mail(current_app)
            mail.send_message(subject='Reset Password Link',
                              recipients=[user['email']],
                              sender='Bebleo <noreply@bebleo.url>',
                              body=_body)
            sent = True

    return render_template('auth/send_password_change.html', email_sent=sent,
                           debug=current_app.debug, token=token, form=form)


@bp.route('/forgotpassword/<string:token>', methods=('GET', 'POST'))
def forgot_password(token=None):
    """Allow user to change the password based on providing a token"""

    try:
        validate_token(token)
        form = UpdatePasswordForm()

        if form.validate_on_submit():
            # save the password
            username = form.username.data
            password = form.password.data

            # get the user and validate that it is that.
            user = get_user(username=username)
            validate_token(token, user['id'])

            db = get_db()
            db.execute('UPDATE users SET password = ? WHERE id = ?',
                       (generate_password_hash(password), user['id']))
            db.execute('DELETE FROM password_tokens WHERE token = ?',
                       (token, ))
            db.commit()

            mail = Mail(current_app)
            mail.send_message(subject='Password reset',
                              recipients=[user['email']],
                              sender='Bebleo <noreply@bebleo.url>',
                              body=render_template('emails/password_reset.txt',
                                                   user=user))

            current_app.logger.info((f"Password reset for user with id ",
                                     f"{user['id']}."))
            return redirect(url_for('home.index'))

        return render_template('auth/update_password.html',
                               token=token, form=form)

    except (TokenExpiredError, TokenInvalidError):
        flash('Token is incorrect or expired.')
        current_app.logger.warning((f"Incorrect or expired token {token} ",
                                    f"used for password reset."))
        return redirect(url_for('auth.send_password_change'))


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Return the form to register the user and handle the response."""
    if g.user is not None:
        # There's a logged in user so no legitmate reason to register.
        abort(401)

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        given_name = form.given_name.data
        family_name = form.family_name.data
        password = form.password.data

        db = get_db()

        if get_user(username=username) is not None:
            form.username.errors.append('Username is already used.')
        else:
            db.execute(
                """INSERT INTO users
                   (email, given_name, family_name, password)
                   VALUES (?, ?, ?, ?);""",
                (username, given_name, family_name,
                 generate_password_hash(password),))
            db.commit()

            current_app.logger.info(f'Registered user: {username}')
            return redirect(url_for('home.index'))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Login."""
    form = LoginForm(request.form)

    if form.validate_on_submit():
        if form._user['deactivated']:
            return redirect(url_for('auth.deactivated'))

        session.clear()
        session['user_id'] = form._user['id']
        return redirect(url_for('home.index'))

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    g.user = None
    return redirect(url_for('home.index'))


@bp.before_app_request
def fetch_logged_in_user():
    user_id = session.get('user_id')
    g.user = get_user(id=user_id) if user_id else None


@bp.route('/disabled', methods=('GET', 'POST'))
def deactivated():
    """Returns the account disabled page."""
    if g.user:
        if not g.user['deactivated']:
            return redirect(url_for('home.index'))

    return render_template('auth/account_disabled.html')
