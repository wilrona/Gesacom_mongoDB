__author__ = 'Ronald'


from application import db
from ..societe.models_societe import Societe


class Charge(db.Document):
    libelle = db.StringField()
    societe = db.ReferenceField(Societe)

    def count_budget(self):
        from ..budget.models_budget import ChargeBudget

        bugdet = ChargeBudget.objects(
            charge_id = self.id
        )

        return len(bugdet)

