__author__ = 'Ronald'


from application import db
from ..projet.models_projet import Projet, Users
from ..prestation.models_prest import Prestation


class Tache(db.Document):
    titre = db.StringField()
    description = db.StringField()
    heure = db.IntField()
    date_start = db.DateTimeField()
    facturable = db.BooleanField()
    projet_id = db.ReferenceField(Projet)
    user_id = db.ReferenceField(Users)
    prestation_id = db.ReferenceField(Prestation)
    end = db.BooleanField(default=False)
    closed = db.BooleanField(default=False)
    detail_heure = db.FloatField()

    def prestation_sigle(self):
        prest = Prestation.objects.get(id=self.prestation_id.id).only('sigle')
        return prest

    def get_user(self):
        current_user = Users.objects.get(id=self.user_id.id)
        return current_user

    def get_projet(self):
        current_projet = Projet.objects.get(id=self.projet_id.id)
        return current_projet

    # def time_tache(self):
    #     from ..temps.models_temps import Temps, DetailTemps
    #
    #     time_taches = []
    #
    #     for temps in Temps.query(Temps.tache_id == self.key):
    #         details = DetailTemps.query(
    #             DetailTemps.temps_id == temps.key
    #         )
    #         for detail in details:
    #             time_taches.append(detail)
    #
    #     return time_taches

