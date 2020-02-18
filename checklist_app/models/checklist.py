from datetime import datetime

from checklist_app import db
from sqlalchemy.ext.hybrid import hybrid_property

__all__ = (
    "Checklist",
    "ChecklistFactory",
    "ChecklistHistory",
    "ChecklistItem"
)


class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                           nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'),
                            nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    created_by = db.relationship('User')
    assigned_to = db.relationship('User')

    @hybrid_property
    def active_items(self):
        return self.items.query.filter_by(active=True).all()

    @hybrid_property
    def percent_complete(self):
        if len(self.items) == 0:
            return 0

        done = sum([1 for i in self.items if i.done])
        return done / len(self.items)

    def record_change(self, description, user):
        _desc = f"{user.full_name} {description}"
        record = ChecklistHistory(description=_desc, checklist=self,
                                  user=user, created=datetime.utcnow())
        self.history.append(record)

    def add_item(self, text, user, done=False):
        item = ChecklistItem(text=text, done=done)
        self.items.append(item)
        self.record_change(f"added {item.text}.", user)
        return item

    def delete_item(self, item, user):
        item.active = False
        self.record_change(f"deleted {item.text}.", user)
        return item


class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'),
                             nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    checklist = db.relationship('Checklist',
                                backref=db.backref('items', lazy=False))

    def toggle(self, user):
        self.done = not self.done

        if self.done:
            _desc = f"marked {self.text} as done."
        else:
            _desc = f"marked {self.text} as not done."

        self.checklist.record_change(_desc, user)
        return self


class ChecklistFactory():
    def get(self, user):
        return Checklist.query.filter_by(user=user).all()

    def save(self, checklist):
        db.session.add(checklist)
        db.session.commit()


class ChecklistHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    checklist = db.relationship('Checklist',
                                backref=db.backref('history', lazy=True))
    user = db.relationship('User')
