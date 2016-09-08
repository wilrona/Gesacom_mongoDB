__author__ = 'Ronald'

from application import db


class Societe(db.Document):
    name = db.StringField()
    bp = db.StringField()
    adress = db.StringField()
    ville = db.StringField()
    pays = db.StringField()
    phone = db.StringField()
    capital = db.StringField()
    numcontr = db.StringField()
    registcom = db.StringField()
    email = db.StringField()
    siteweb = db.StringField()
    slogan = db.StringField()
    typEnt = db.StringField()

