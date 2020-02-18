from flask import (Blueprint, abort, flash, g, redirect, render_template,
                   request, url_for)

from checklist_app import db
from checklist_app.auth import login_required
from checklist_app.forms import AddItemForm, CreateListForm, EditListForm
from checklist_app.models import Checklist, ChecklistItem

bp = Blueprint('checklist', __name__, url_prefix='/checklist')


def get_checklist(id):
    """Gets the checklist identified by the id."""
    checklist = Checklist.query.filter_by(id=id).first_or_404()
    return checklist


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = CreateListForm()

    if form.validate_on_submit():
        checklist = Checklist(
            title=form.list_title.data,
            description=form.list_description.data,
            created_by=g.user,
            assigned_to=g.user
        )
        db.session.add(checklist)
        db.session.commit()

        return redirect(url_for('checklist.view', id=checklist.id))

    return render_template('checklist/create.html', header=None, form=form)


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    """Edit the checklist header with primary key matchig the id."""
    form = EditListForm()

    checklist = get_checklist(id)

    if form.validate_on_submit():
        checklist.title = form.list_title.data
        checklist.description = form.list_description.data
        db.session.add(checklist)
        db.session.commit()

        return redirect(url_for('checklist.view', id=id))

    form.list_title.data = checklist.title
    form.list_description.data = checklist.description
    return render_template('checklist/create.html', form=form)


@bp.route('/delete/<int:id>', methods=('GET', 'POST'))
@login_required
def delete(id):
    """Mark the checklist identified by the id as deleted."""
    checklist = get_checklist(id)

    if request.method == 'POST':
        # Check that the confirmation has been given and return.
        confirm_delete = request.form['confirm_delete']

        if not confirm_delete:
            abort(401)

        checklist.is_deleted = True
        db.session.add(checklist)
        db.session.commit()

        # redirect the user to their list of checklists.
        return redirect(url_for('checklist.index'))

    # Create a little confirmation form and return it as a message
    flash(render_template('checklist/partial/delete.html', id=id))
    return redirect(url_for('checklist.view', id=id))


@bp.route('/')
@bp.route('')
@login_required
def index():
    checklists = Checklist.query.filter_by(
        created_by=g.user,
        is_deleted=False
    ).all()
    return render_template('checklist/index.html', lists=checklists)


@bp.route('/<int:id>')
@login_required
def view(id):
    checklist = get_checklist(id)
    form = AddItemForm()
    return render_template('checklist/view_list.html', checklist=checklist, form=form)


@bp.route('/<int:id>/check/<int:item_id>')
@login_required
def toggle_item(id, item_id):
    get_checklist(id)
    item = ChecklistItem.query.filter_by(id=item_id).first_or_404()

    if item.checklist_id == id:
        item.toggle(g.user)
        db.session.commit()

    return redirect(url_for('checklist.view', id=id))


@bp.route('/<int:id>/check/all')
@login_required
def toggle_all(id):
    checklist = get_checklist(id)

    [i.toggle(g.user) for i in checklist.items if i.done is False]
    db.session.commit()

    return redirect(url_for('checklist.view', id=id))


@bp.route('/<int:id>/add', methods=('GET', 'POST'))
@login_required
def add_item(id):
    checklist = get_checklist(id)
    form = AddItemForm()

    if form.validate_on_submit():
        checklist.add_item(form.item_text.data, g.user)
        db.session.add(checklist)
        db.session.commit()
        return redirect(url_for('checklist.view', id=id))

    return render_template('checklist/view_list.html', checklist=checklist, form=form)
