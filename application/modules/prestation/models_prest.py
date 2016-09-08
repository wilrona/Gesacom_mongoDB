__author__ = 'Ronald'

from application import db


class Prestation(db.Document):
    libelle = db.StringField()
    factu = db.BooleanField()
    nfactu = db.BooleanField()
    sigle = db.StringField()