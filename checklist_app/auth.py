# ----------------------------------------------------------------------
# checklist.auth
# Handles user, authentication, registration and related matters. Based
# heavily on the Flask tutorial
#:
# James Warne
# December 12, 2019
# ----------------------------------------------------------------------

import functools
import uuid

from flask import (Blueprint, current_app, flash, g, logging, redirect,
                   render_template, request, session, url_for)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from checklist_app.db import get_db
from flask_mail import Mail

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/forgotpassword', methods=('GET', 'POST'))
def send_password_change():
    """Get the user email and send the link with the reset token."""
    sent = False
    token = uuid.uuid4().hex

    if request.method == 'POST':
        email = request.form['username']
        db = get_db()

        user = db.execute(
            'SELECT * FROM users WHERE email = ?',
            (email, )
        ).fetchone()
        db.execute(
            'INSERT INTO password_tokens (user_id, token, token_type) VALUES (?, ?, ?)',
            (user['id'], token, 'password_reset')
        )
        db.commit()

        if not user:
            flash("No user found with email.")
        else:
            mail = Mail(current_app)
            mail.send_message(subject='Reset Password Link',
                              recipients=[user['email']],
                              sender='Bebleo <bebleo@mail.localhost>',
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
    if request.method == 'POST':
        # save the password
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        db = get_db()

        # Check the token is valid and get the user_id from the db
        user = db.execute('SELECT id FROM users WHERE email = ?', (username, )).fetchone()
        token_query = 'SELECT * FROM password_tokens WHERE token = ? AND user_id = ?'
        token = db.execute(token_query, (token, user['id'])).fetchone()

        if token is None:
            flash('Token is incorrect or expired.')
            current_app.logger.warn('Incorrect or expired token {} used for password reset.'.format(token))
            return redirect(url_for('auth.send_password_change'))

        if password == confirm:
            password_hash = generate_password_hash(password)
            user_id = token['user_id']
            db.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (password_hash, user_id)
            )
            db.execute(
                'DELETE FROM password_tokens WHERE id = ?',
                (token['id'], )
            )
            user = db.execute(
                'SELECT * FROM users WHERE id = ?;',
                (user_id, )
            ).fetchone()
            db.commit()

            mail = Mail(current_app)
            mail.send_message(subject='Password reset',
                               recipients=[user['email']],
                               sender='james.warne@outlook.com',
                               body=render_template('emails/password_reset.txt', user=user))
            current_app.logger.info('Password reset for user with id {}.'.format(user_id))
            return redirect(url_for('home.index'))
        else:
            flash('Password and confirmation must match.')

    return render_template('auth/update_password.html', token=token)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Return the form to register the user and handle the response."""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm = request.form['confirm'].strip()
        db = get_db()
        error = None

        if not username:
            error = 'Username cannot be empty.'
        elif not password:
            error = 'Password cannot be empty.'
        elif not password == confirm:
            error = 'Password and confirmation must match.'
        elif db.execute(
            'SELECT id FROM users WHERE email = ?', (username, )
        ).fetchone() is not None:
            error = 'Username is already used.'

        if error is None:
            hash = generate_password_hash(password)
            insert_user_query = 'INSERT INTO users (email, password) VALUES (?, ?);'
            insert_user_vars = (username, hash, )
            db.execute(insert_user_query, insert_user_vars)
            user_id = db.execute('SELECT last_insert_rowid()').fetchone()
            db.commit()
            current_app.logger.info('Registered user with id {}'.format(user_id))
            return redirect(url_for('home.index'))
        else:
            flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Login."""
    session.pop('_flashes', None)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', 
            (username.strip(), )
        ).fetchone()

        if not username.strip():
            error = 'Username cannot be empty.'
        elif not password.strip():
            error = 'Passowrd cannot be blank.'
        elif (user is None) or (not check_password_hash(user['password'], password)):
            error = 'Login incorrect, please try again.'
        
        if not error:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home.index'))
        else:
            flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    g.user = None
    return redirect(url_for('home.index'))

@bp.before_app_request
def fetch_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id, )
        ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def check_login(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return check_login

def admin_required(view):
    @functools.wraps(view)
    def check_admin(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        elif not g.user['is_admin']:
            abort(401)
        
        return view(**kwargs)

    return check_admin
