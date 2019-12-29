from flask import (Blueprint, abort, current_app, flash, g, logging, redirect,
                   render_template, request, url_for)
from flask_wtf.csrf import generate_csrf

from checklist_app.auth import login_required
from checklist_app.db import get_db

bp = Blueprint('checklist', __name__, url_prefix='/checklist')

class Checklist:
    def __init__(self):
        self.header = None
        self.items = None
        self.history = None

    def percent_complete(self):
        """Return the percentage complete of the items on a checklist."""
        value = 0

        if self.items:
            value = sum([1 for i in self.items if i['done']]) / len(self.items)

        return value

def get_checklist(id):
    """Gets the checklist identified by the id."""
    db = get_db()
    checklist = Checklist()

    checklist.header = db.execute(
        'SELECT * FROM checklists WHERE id = ?',
        (id, )
    ).fetchone()

    if checklist.header:
        # Get the items
        checklist.items = db.execute(
            'SELECT * FROM checklist_items WHERE checklist_id = ? ORDER BY id',
            (checklist.header['id'], )
        ).fetchall()
        checklist.history = db.execute(
            'SELECT * FROM checklist_history WHERE checklist_id = ? ORDER BY change_date',
            (checklist.header['id'], )
        ).fetchall()
    
    return checklist

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create(id=None):
    if request.method == 'POST':
        db = get_db()
        title = request.form['list_title']
        desc = request.form['list_description']
        error = None

        if not title:
            error = "Title for the list is required."

        if error:
            flash(error)
        else:
            cur = db.cursor()
            cur.execute(
                'INSERT INTO checklists (title, [description], created_by, assigned_to) VALUES (?, ?, ?, ?)',
                (title, desc, g.user['id'], g.user['id'])
            )
            list_id = cur.lastrowid
            change_history = "{} created the list called, \"{}\".".format(g.user['given_name'], title)
            cur.execute(
                'INSERT INTO checklist_history (change_description, checklist_id, user_id) VALUES (?, ?, ?);',
                (change_history, list_id, g.user['id'])
            )
            db.commit()

            return redirect(url_for('checklist.view', id=list_id))

    return render_template('checklist/create.html', header=None)

@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    """Edit the checklist header with primary key matchig the id."""
    db = get_db()
    checklist = get_checklist(id)

    if checklist is None:
        abort(401)

    if request.method == 'POST':
        title = request.form['list_title']
        desc = request.form['list_description']

        current_app.logger.debug(f'{title}')
        current_app.logger.debug(f'{desc}')

        if title != checklist.header["title"]:
            current_app.logger.debug(f"{title} not {checklist.header['title']}")
            change_history = f"{g.user['given_name']} updated the list title from \"{checklist.header['title']}\" to \"{title}\""
            db.execute("UPDATE checklists SET title = ? WHERE id = ?", (title, id,))
            db.execute(
                'INSERT INTO checklist_history (change_description, checklist_id, user_id) VALUES (?, ?, ?);',
                (change_history, checklist.header['id'], g.user['id'],)
            )

        if desc != checklist.header["description"]:
            change_history = f"{g.user['given_name']} updated the description from \"{checklist.header['description']}\" to \"{desc}\""
            db.execute("UPDATE checklists SET [description] = ? WHERE id = ?", (desc, id,))
            db.execute(
                'INSERT INTO checklist_history (change_description, checklist_id, user_id) VALUES (?, ?, ?);',
                (change_history, checklist.header['id'], g.user['id'],)
            )
        
        db.commit()
        return redirect(url_for('checklist.view', id=id))
            
    return render_template('checklist/create.html', header=checklist.header)

@bp.route('/delete/<int:id>', methods=('GET', 'POST'))
@login_required
def delete(id):
    """Mark the checklist identified by the id as deleted."""
    db = get_db()
    checklist = get_checklist(id)

    if checklist is None:
        abort(404)

    if request.method == 'POST':
        # Check that the confirmation has been given and return.
        confirm_delete = request.form['confirm_delete']

        if not confirm_delete:
            abort(401)

        # TODO Handle the actual deletion.
        db.execute("UPDATE checklists SET is_deleted = ? WHERE id = ?", (True, id,))
        db.execute(
            """INSERT INTO checklist_history
                   (change_description, checklist_id, user_id)
               VALUES
                   (?, ?, ?);
            """,
            (
                f"{g.user['given_name']} deleted the \"{checklist.header['title']}\" checklist.",
                id,
                g.user['id']
            )
        )
        db.commit()

        # redirect the user to their list of checklists.
        return redirect(url_for('checklist.index'))
        

    # Create a little confirmation form and return it as a message
    confirm = f"""
        <form action="{url_for('checklist.delete', id=id)}" method="post">
        Please click the button to confirm that you want to delete this form. This action cannot be undone.
        <input type="hidden" name="csrf_token" value="{generate_csrf()}">
        <input type="hidden" name="confirm_delete" id="confirm_delete" value="1">
        <input type="submit" value="Delete">
        </form>
    """
    flash(confirm)
    return redirect(url_for('checklist.view', id=id))

@bp.route('/')
@bp.route('')
@login_required
def index():
    db = get_db()
    checklists = [get_checklist(r['id']) for r in db.execute(
        'SELECT id FROM checklists WHERE created_by = ? AND is_deleted = False',
        (g.user['id'],)
    ).fetchall()]

    return render_template('checklist/index.html', lists=checklists)

@bp.route('/<int:id>')
@login_required
def view(id):
    checklist = get_checklist(id)

    if checklist.header:
        return render_template('checklist/view_list.html', checklist=checklist)

    # No checklist with the ID so return a 404 - Not Found error.
    abort(404)

@bp.route('/<int:id>/check/<int:item_id>')
@login_required
def toggle_item(id, item_id):
    db = get_db()
    checklist = get_checklist(id)

    if checklist:
        # Get the current state...
        current = [i for i in checklist.items if i['id'] == item_id]
        if current:
            current = current[0]
        else:
            abort(404)
        
        # Switches whether this is finished or not.
        complete = not current['done']

        change_history = '{} unchecked {}'
        if complete:
            change_history = '{} checked {}'
        
        change_history = change_history.format(g.user['given_name'], current['item_text'])

        db.execute(
            'INSERT INTO checklist_history (change_description, checklist_id, user_id) VALUES (?, ?, ?);',
            (change_history, checklist.header['id'], g.user['id'])
        )
        db.execute(
            'UPDATE checklist_items SET done = ? WHERE id = ?',
            (complete, current['id'])
        )
        db.commit()

        # Refresh the list and return it.
        checklist=get_checklist(id)

        return redirect(url_for('checklist.view', id=id))

    # No checklist found with that id so abort
    abort(404)

@bp.route('/<int:id>/add', methods=('GET', 'POST'))
@login_required
def add_item(id):
    checklist = get_checklist(id)

    if not checklist:
        abort(404)

    if request.method == 'POST':
        item_text = request.form['item_text']

        change_history = '{} added {} to the list.'.format(g.user['given_name'], item_text)

        db = get_db()
        db.execute(
            'INSERT INTO checklist_items (item_text, checklist_id) VALUES (?, ?)',
            (item_text, id)
        )
        db.execute(
            'INSERT INTO checklist_history (change_description, checklist_id, user_id) VALUES (?, ?, ?);',
            (change_history, checklist.header['id'], g.user['id'])
        )
        db.commit()

    return redirect(url_for('checklist.view', id=id))
