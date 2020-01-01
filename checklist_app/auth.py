# ----------------------------------------------------------------------
# checklist.auth
# Handles user, authentication, registration and related matters. Based
# heavily on the Flask tutorial
# 
# James Warne
# December 12, 2019
# ----------------------------------------------------------------------

import functools
import uuid

from flask import (Blueprint, abort, current_app, flash, g, logging, redirect,
                   render_template, request, session, url_for)
from flask_mail import Mail
from werkzeug.security import check_password_hash, generate_password_hash

from checklist_app.db import get_db

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

        if not user:
            flash("No user found with email.")
        else:
            db.execute(
                'INSERT INTO password_tokens (user_id, token, token_type) VALUES (?, ?, ?)',
                (user['id'], token, 'password_reset')
            )
            db.commit()

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
    db=get_db()

    t = db.execute(
        'SELECT * FROM password_tokens WHERE token = ?;',
        (token, )
    ).fetchone()

    if t is None:
        flash('Token is incorrect or expired.')
        current_app.logger.warn(f'Incorrect or expired token {token} used for password reset.')
        return redirect(url_for('auth.send_password_change'))

    if request.method == 'POST':
        # save the password
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        # Check the token is valid and get the user_id from the db
        user = db.execute('SELECT id FROM users WHERE email = ?', (username, )).fetchone()
        token_query = 'SELECT * FROM password_tokens WHERE token = ? AND user_id = ?'
        t = db.execute(token_query, (token, user['id'])).fetchone()

        if t is None:
            flash('Token is incorrect or expired.')
            current_app.logger.warn(f'Incorrect or expired token {token} used for password reset.')
            return redirect(url_for('auth.send_password_change'))

        if password == confirm:
            password_hash = generate_password_hash(password)
            user_id = t['user_id']
            db.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (password_hash, user_id))
            db.execute(
                'DELETE FROM password_tokens WHERE id = ?',
                (t['id'], ))
            user = db.execute(
                'SELECT * FROM users WHERE id = ?;',
                (user_id, )).fetchone()
            db.commit()

            mail = Mail(current_app)
            mail.send_message(subject='Password reset',
                               recipients=[user['email']],
                               sender='Bebleo <noreply@bebleo.url>',
                               body=render_template('emails/password_reset.txt', user=user))
            current_app.logger.info('Password reset for user with id {}.'.format(user_id))
            return redirect(url_for('home.index'))
        else:
            flash('Password and confirmation must match.')

    return render_template('auth/update_password.html', token=token)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Return the form to register the user and handle the response."""
    if g.user is not None:
        # There's a logged in user so no legitmate reason to register.
        abort(401)

    if request.method == 'POST':
        username = request.form['username'].strip()
        given_name = request.form['given_name'].strip()
        family_name = request.form['family_name'].strip()
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

        if not username:
            error = 'Username cannot be empty.'
        elif not password:
            error = 'Password cannot be blank.'
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
