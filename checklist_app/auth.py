# ----------------------------------------------------------------------
# checklist.auth
# Handles user, authentication, registration and related matters. Based
# heavily on the Flask tutorial
# 
# James Warne
# December 12, 2019
# ----------------------------------------------------------------------

import functools
# import uuid

from flask import (Blueprint, abort, current_app, flash, g, logging, redirect,
                   render_template, request, session, url_for)
from flask_mail import Mail
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from .forms.login_form import LoginForm
from .models.password_token import (TokenExpiredError, TokenInvalidError,
                                    TokenPurpose, save_token, validate_token)
from .models.user import AccountStatus, get_user

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
    sent = False
    token = None

    if request.method == 'POST':
        email = request.form['username']
        user = get_user(username=email)

        if user is None:
            # If no user exists with that email flash that message.
            flash("No user found with email.")
        else:
            token = save_token(user['id'])

            mail = Mail(current_app)
            mail.send_message(subject='Reset Password Link',
                              recipients=[user['email']],
                              sender='Bebleo <noreply@bebleo.url>',
                              body=render_template('emails/send_password_change.txt',
                                                   host=request.host, 
                                                   user=user, 
                                                   token=token))
            sent = True

    return render_template('auth/send_password_change.html', 
                           email_sent=sent, 
                           debug=current_app.debug, 
                           token=token)

@bp.route('/forgotpassword/<string:token>', methods=('GET', 'POST'))
def forgot_password(token = None):
    """Allow user to change the password based on providing a token"""

    try: 
        validate_token(token)

        if request.method == 'POST':
            # save the password
            username = request.form['username']
            password = request.form['password']
            confirm = request.form['confirm']

            # get the user and validate that it is that.
            user = get_user(username=username)
            validate_token(token, user['id'])

            if password == confirm:
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

                current_app.logger.info(f"Password reset for user with id {user['id']}.")
                return redirect(url_for('home.index'))
            else:
                flash('Password and confirmation must match.')

        return render_template('auth/update_password.html', token=token)

    except (TokenExpiredError, TokenInvalidError):
        flash('Token is incorrect or expired.')
        current_app.logger.warning(f'Incorrect or expired token {token} used for password reset.')
        return redirect(url_for('auth.send_password_change'))

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Return the form to register the user and handle the response."""
    if g.user is not None:
        # There's a logged in user so no legitmate reason to register.
        abort(401)

    if request.method == 'POST':
        username = request.form['username'].strip()
        given_name = request.form['given_name']
        family_name = request.form['family_name']
        password = request.form['password'].strip()
        confirm = request.form['confirm'].strip()
        
        db = get_db()
        error = None

        print(f"username being registered is {username} with {password}")

        if not username:
            error = 'Username cannot be empty.'
        elif not password:
            error = 'Password cannot be empty.'
        elif password != confirm:
            error = 'Password and confirmation must match.'
        elif get_user(username=username) is not None:
            error = 'Username is already used.'

        if error is None:
            # Insert the user into database
            cur = db.cursor()
            cur.execute(
                'INSERT INTO users (email, given_name, family_name, password) VALUES (?, ?, ?, ?);', 
                (username, given_name, family_name, generate_password_hash(password), ))
            user_id = cur.lastrowid
            db.commit()

            current_app.logger.info(f'Registered user with id {user_id}')
            return redirect(url_for('home.index'))
        else:
            flash(error)

    return render_template('auth/register.html')

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
