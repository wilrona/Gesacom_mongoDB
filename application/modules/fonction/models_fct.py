__author__ = 'Ronald'

from application import db

class Fonction(db.Document):
    libelle = db.StringField()

    def count_user(self):
        from ..user.models_user import Users
        user_exist = Users.objects(fonction=self.id)

        return len(user_exist)