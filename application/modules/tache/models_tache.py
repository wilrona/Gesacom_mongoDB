__author__ = 'Ronald'


from application import db
from ..projet.models_projet import Projet, Users
from ..prestation.models_prest import Prestation


class Update_Tache(db.EmbeddedDocument):
    date = db.DateTimeField()
    action = db.StringField()
    user = db.ReferenceField(Users)
    notified = db.BooleanField(default=True)


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
    officiel = db.BooleanField(default=False)
    suspend = db.BooleanField(default=False)
    updated = db.ListField(db.EmbeddedDocumentField(Update_Tache))

    def prestation_sigle(self):
        prest = Prestation.objects.get(id=self.prestation_id.id)
        return prest.sigle

    def get_user(self):
        current_user = Users.objects.get(id=self.user_id.id)
        return current_user

    def get_projet(self):
        current_projet = Projet.objects.get(id=self.projet_id.id)
        return current_projet

    def nbr_temps(self):
        from ..temps.models_temps import Temps

        nbr_temp = Temps.objects(
            tache_id = self.id
        ).count()

        return nbr_temp

    def notified(self):
        data = []
        for notifie in self.updated:
            if notifie.notified:
                data.append(notifie)

        return data



