__author__ = 'Ronald'

from application import db

class Frais(db.Document):
    libelle = db.StringField()
    factu = db.BooleanField()
    nfactu = db.BooleanField()


