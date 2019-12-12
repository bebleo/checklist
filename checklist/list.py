from flask import Blueprint, g, render_template, request

from checklist.auth import login_required
from checklist.db import get_db


bp = Blueprint('list', __name__, url_prefix='/checklist')


@login_required
@bp.route('/create', methods=('GET', 'POST'))
def create():
    return render_template('list/create.html')


@login_required
@bp.route('/')
def index():
    user_id = g.user['id']
    db = get_db()
    checklists = db.execute(
        'SELECT * FROM checklists WHERE created_by = ?',
        (user_id, )
    ).fetch()

    return render_template('list/index.html', lists=checklists)
