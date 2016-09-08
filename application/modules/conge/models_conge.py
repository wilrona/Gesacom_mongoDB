__author__ = 'Ronald'

from application import db


class Ferier(db.Document):
    date = db.DateTimeField()
    description = db.StringField()
    apply = db.BooleanField(default=False)