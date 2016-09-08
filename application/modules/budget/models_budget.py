__author__ = 'Ronald'


from application import db
from ..user.models_user import Users
from ..prestation.models_prest import Prestation
from ..charge.models_charge import Charge
from ..client.models_client import Client


class Budget(db.Document):
    heure = db.FloatField()
    user_id = db.ReferenceField(Users)
    date_start = db.DateTimeField()


class BudgetPrestation(db.Document):
    prestation_id = db.ReferenceField(Prestation)
    budget_id = db.ReferenceField(Budget)
    heure = db.FloatField()


class ChargeBudget(db.Document):
    charge_id = db.ReferenceField(Charge)
    montant = db.FloatField()
    date_app = db.DateTimeField()


class ClientBudget(db.Document):
    date_app = db.DateTimeField()
    montant = db.FloatField()
    client_id = db.ReferenceField(Client)