__author__ = 'Ronald'

from application import db
from mongoengine.queryset.visitor import Q
from ..domaine.models_domaine import Domaine, Service
from ..client.models_client import Client
from ..user.models_user import Users
from ..frais.models_frais import Frais


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
    attente = db.BooleanField(default=False)
    rejet = db.BooleanField(default=False)

    def ratio_user(self, user_id):
        from ..tache.models_tache import Tache, Users

        user = Users.objects.get(id=user_id)

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

    def besoin(self, rejet=False, attente=True):
        besoins = BesoinFinancier.objects(
            Q(projet_id=self.id) & Q(rejet=rejet) & Q(attente=attente)
        ).order_by('-date_echeance')
        return besoins

    def besoin_unsolde(self):
        besoin = []
        besoins = BesoinFinancier.objects(
            Q(projet_id=self.id) & Q(attente=False) & Q(parent=None)
        ).order_by('-date_echeance')
        for bes in besoins:
            if len(bes.child()):
                if bes.lasted_child().paye < bes.lasted_child().montant:
                    besoin.append(bes)
            else:
                if bes.paye < bes.montant:
                    besoin.append(bes)
        return besoin


class FraisProjet(db.Document):
    montant = db.FloatField()
    facturable = db.BooleanField()
    projet_id = db.ReferenceField(Projet)
    frais_id = db.ReferenceField(Frais)


class BesoinFinancier(db.Document):
    commande = db.StringField()
    fournisseur = db.StringField()
    montant = db.FloatField()
    avance = db.FloatField()
    paye = db.FloatField()
    date_echeance = db.DateTimeField()
    projet_id = db.ReferenceField(Projet)
    attente = db.BooleanField(default=True)
    rejet = db.BooleanField(default=False)
    parent = db.ReferenceField('self')
    last_child = db.BooleanField(default=False)

    def child(self):
        childs = BesoinFinancier.objects(parent=self.id)
        return childs

    def lasted_child(self):
        last = BesoinFinancier.objects(Q(parent=self.id) & Q(last_child=True)).first()
        return last