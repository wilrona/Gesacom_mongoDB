__author__ = 'Ronald'

from application import db


class Domaine(db.Document):
    code = db.StringField()
    libelle = db.StringField()

    def count_service(self):
        ser = Service.objects(
            domaine = self.id
        )
        return len(ser)


class Service(db.Document):
    code = db.StringField()
    libelle = db.StringField()
    domaine = db.ReferenceField(Domaine)