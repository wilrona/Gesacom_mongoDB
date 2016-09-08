__author__ = 'Ronald'

from application import db

class Client(db.Document):
    name = db.StringField()
    ref = db.StringField()
    bp = db.StringField()
    adresse = db.StringField()
    ville = db.StringField()
    pays = db.StringField()
    email = db.StringField()
    phone = db.StringField()
    date_created = db.DateTimeField()
    prospect = db.BooleanField(default=False)
    myself = db.BooleanField(default=False)


class Contact(db.Document):
    first_name = db.StringField()
    last_name = db.StringField()
    email = db.StringField()
    phone1 = db.StringField()
    phone2 = db.StringField()
    client_id = db.ReferenceField(Client)