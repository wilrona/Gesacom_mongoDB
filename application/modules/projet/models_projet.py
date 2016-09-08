__author__ = 'Ronald'

from application import db
from mongoengine.queryset.visitor import Q
from ..domaine.models_domaine import Domaine, Service
from ..client.models_client import Client
from ..user.models_user import Users


class Projet(db.Document):
    code = db.StringField()
    titre = db.StringField()
    heure = db.IntField()
    montant = db.FloatField()
    date_start = db.DateTimeField()
    date_end = db.DateTimeField()
    facturable = db.BooleanField()
    domaine_id = db.ReferenceField(Domaine)
    client_id = db.ReferenceField(Client)
    service_id = db.ReferenceField(Service)
    prospect_id = db.ReferenceField(Client)
    responsable_id = db.ReferenceField(Users)
    closed = db.BooleanField(default=False)
    suspend = db.BooleanField(default=False)
    montant_projet_fdt = db.FloatField()

    def ratio_user(self, user_id):
        from ..tache.models_tache import Tache, Users

        user = Users.objects(id=user_id).first()

        tache_projet = Tache.objects(
            Q(projet_id=self.id) & Q(user_id=user.id)
        )

        total = 0.0
        for tache in tache_projet:
            if tache.prestation_sigle() == 'PRO' and tache.facturable:
                user_taux = tache.get_user().tauxH
                time = tache.detail_heure

                pre_total = user_taux * time

                total += pre_total
        ratio = 0.0
        if self.montant_projet_fdt:
            ratio = total / self.montant_projet_fdt

        return round(ratio, 1)