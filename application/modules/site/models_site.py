__author__ = 'Ronald'

from application import db
from ..societe.models_societe import Societe


class Site(db.Document):
    libelle = db.StringField()
    societe = db.ReferenceField(Societe, dbref=True)

    def count_user(self):
        from ..user.models_user import Users
        user_exist = Users.objects(id=self.id)
        return len(user_exist)