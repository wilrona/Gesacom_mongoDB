__author__ = 'Ronald'


from ...modules import *
import urlfetch

prefix = Blueprint('upload', __name__)


@prefix.route('/')
def index():
    url = "http://accentcom-time.com/api/roles"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..role.models_role import Roles

    role_admin = Roles.objects(valeur='super_admin').first()

    for data in result['data']:
        existe_role = Roles.objects(valeur=data['valeur']).first()
        if data['valeur'] != role_admin.valeur and not existe_role:
            role = Roles()
            role.titre = data['titre']
            role.valeur = data['valeur']
            role.description = data['description']
            role.action = data['action']
            role.active = data['active']
            role.save()

    # Enregistrement des references des parents au role concerne
    for data in result['data']:
        if data['parent']:
            current_role = Roles.objects(valeur=data['valeur']).first()
            parent_role = Roles.objects(valeur=data['parent']).first()
            current_role.parent = parent_role
            current_role.save()


    url = "http://accentcom-time.com/api/profil"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..profil.models_profil import Profil, ProfilRole
    for data in result['data']:
        existe_profil = Profil.objects(name=data['name']).first()
        if not existe_profil:
            profil = Profil()
            profil.name = data['name']
            profil.description = data['description']
            profil.active = data['active']
            profil_id = profil.save()

            for profil_role in data['roles']:
                pro_role = ProfilRole()
                pro_role.edit = profil_role['edit']
                pro_role.deleted = profil_role['delecte']

                role_profil = Roles.objects(valeur=profil_role['role']).first()
                pro_role.role_id = role_profil
                pro_role.profil_id = profil_id
                pro_role.save()



    url = "http://accentcom-time.com/api/societe"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..societe.models_societe import Societe
    for data in result['data']:
        existe_societe = Societe.objects.first()
        if not existe_societe:
            societe = Societe()
            societe.name = data['name']
            societe.adress = data['adress']
            societe.bp = data['bp']
            societe.capital = data['capital']
            societe.email = data['email']
            societe.numcontr = data['numcontr']
            societe.pays = data['pays']
            societe.phone = data['phone']
            societe.registcom = data['registcom']
            societe.siteweb = data['siteweb']
            societe.slogan = data['slogan']
            societe.typEnt = data['typEnt']
            societe.ville = data['ville']
            societe.save()


    url = "http://accentcom-time.com/api/site"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..site.models_site import Site
    existe_societe = Societe.objects.first()
    for data in result['data']:
        exist_data = Site.objects(libelle=data['libelle']).first()
        if existe_societe and not exist_data:
            site = Site()
            site.libelle = data['libelle']
            site.societe = existe_societe
            site.save()



    url = "http://accentcom-time.com/api/departement"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..departement.models_dep import Departement
    for data in result['data']:
        exist_data = Departement.objects(libelle=data['libelle']).first()
        if existe_societe and not exist_data:
            dep = Departement()
            dep.libelle = data['libelle']
            dep.societe = existe_societe
            dep.save()



    url = "http://accentcom-time.com/api/fonction"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..fonction.models_fct import Fonction
    for data in result['data']:
        exist_data = Fonction.objects(libelle=data['libelle']).first()
        if not exist_data:
            fonction = Fonction()
            fonction.libelle = data['libelle']
            fonction.save()



    url = "http://accentcom-time.com/api/grade"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..grade.models_grade import Grade
    for data in result['data']:
        exist_data = Grade.objects(libelle=data['libelle']).first()
        if not exist_data:
            grade = Grade()
            grade.libelle = data['libelle']
            grade.save()



    url = "http://accentcom-time.com/api/prestation"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..prestation.models_prest import Prestation
    for data in result['data']:
        exist_data = Prestation.objects(sigle=data['sigle']).first()
        if not exist_data:
            prest = Prestation()
            prest.libelle = data['libelle']
            prest.factu = data['factu']
            prest.nfactu = data['nfactu']
            prest.sigle = data['sigle']
            prest.save()


    url = "http://accentcom-time.com/api/frais"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..frais.models_frais import Frais
    for data in result['data']:
        exist_data = Frais.objects(libelle=data['libelle']).first()
        if not exist_data:
            frais = Frais()
            frais.libelle = data['libelle']
            frais.factu = data['factu']
            frais.nfactu = data['nfactu']
            frais.save()




    url = "http://accentcom-time.com/api/charge"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..charge.models_charge import Charge
    from ..budget.models_budget import ChargeBudget
    for data in result['data']:
        exist_data = Charge.objects(libelle=data['libelle']).first()
        if existe_societe and not exist_data:
            charge = Charge()
            charge.libelle = data['libelle']
            charge.societe = existe_societe
            charge_id = charge.save()

            for budget in data['budget']:
                bud = ChargeBudget()

                date_app = datetime.datetime.combine(function.date_convert(budget['date_app']), datetime.datetime.min.time())
                bud.date_app = date_app

                bud.montant = budget['montant']
                bud.charge_id = charge_id
                bud.save()



    url = "http://accentcom-time.com/api/client"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..client.models_client import Client, Contact
    from ..budget.models_budget import ClientBudget
    for data in result['data']:
        exist_data = Client.objects(ref=data['ref']).first()
        if not exist_data:
            client = Client()
            client.name = data['name']
            client.ref = data['ref']
            client.ville = data['ville']
            client.adresse = data['adresse']
            client.bp = data['bp']
            client.date_created = function.datetime_convert(data['date_created'])
            client.email = data['email']
            client.myself = data['myself']
            client.pays = data['pays']
            client.phone = data['phone']
            client.prospect = data['prospect']
            client_id = client.save()

            for contact in data['contacts']:
                cont = Contact()
                cont.first_name = contact['first_name']
                cont.last_name = contact['last_name']
                cont.email = contact['email']
                cont.phone1 = contact['phone1']
                cont.phone2 = contact['phone2']
                cont.client_id = client_id
                cont.save()

            for budget in data['budgets']:
                bud = ClientBudget()

                date_app = datetime.datetime.combine(function.date_convert(budget['date_app']), datetime.datetime.min.time())
                bud.date_app = date_app

                bud.montant = budget['montant']
                bud.client_id = client_id
                bud.save()


    url = "http://accentcom-time.com/api/domaine"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..domaine.models_domaine import Domaine, Service
    for data in result['data']:
        exist_data = Domaine.objects(code=data['code']).first()
        if not exist_data:
            doma = Domaine()
            doma.code = data['code']
            doma.libelle = data['libelle']
            domaine_id = doma.save()

            for services in data['services']:
                serv = Service()
                serv.code = services['code']
                serv.libelle = services['libelle']
                serv.domaine = domaine_id
                serv.save()




    url = "http://accentcom-time.com/api/user"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..user.models_user import Users, UserRole, Horaire
    for data in result['data']:
        exist_data = Users.objects(email=data['email']).first()
        if not exist_data:
            user = Users()
            user.email = data['email']
            user.date_create = function.datetime_convert(data['date_create'])
            user.matricule = data['matricule']
            user.is_enabled = data['is_enabled']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.logged = data['logged']
            if data['date_last_logged'] != 'None':
                user.date_last_logged = data['date_last_logged']
            user.google_id = data['google_id']
            user.date_update = function.datetime_convert(data['date_update'])
            user.tauxH = data['tauxH']

            if data['date_start'] != 'None':
                date_start = datetime.datetime.combine(function.date_convert(data['date_start']), datetime.datetime.min.time())
                user.date_start = date_start

            if data['fonction_id']:
                fonction = Fonction.objects(libelle=data['fonction_id']).first()
                user.fonction_id = fonction

            if data['departement_id']:
                departement = Departement.objects(libelle=data['departement_id']).first()
                user.departement_id = departement

            if data['grade_id']:
                grade = Grade.objects(libelle=data['grade_id']).first()
                user.grade_id = grade

            if data['site_id']:
                site = Site.objects(libelle=data['site_id']).first()
                user.site_id = site

            user_id = user.save()

            for role in data['roles']:
                userR = UserRole()
                userR.deleted = role['delete']
                userR.edit = role['edit']

                rol_id = Roles.objects(valeur=role['role']).first()
                userR.role_id = rol_id

                userR.user_id = user_id
                userR.save()

            for horaire in data['horaires']:
                horai = Horaire()

                date_start = datetime.datetime.combine(function.date_convert(horaire['date_start']), datetime.datetime.min.time())
                horai.date_start = date_start

                horai.montant = horaire['montant']
                horai.user = user_id
                horai.save()



    url = "http://accentcom-time.com/api/budget"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..budget.models_budget import Budget, BudgetPrestation
    for data in result['data']:
        user_id = Users.objects(email=data['user_id']).first()
        date_start = datetime.datetime.combine(function.date_convert(data['date_start']), datetime.datetime.min.time())
        exist_data = Budget.objects(
            Q(date_start=date_start) & Q(user_id=user_id.id)
        ).first()
        if not exist_data:
            budget = Budget()
            budget.date_start = date_start
            budget.heure  = data['heure']
            budget.user_id = user_id
            bud_id = budget.save()

            for buds in data['budget_prestation']:
                bud_pres = BudgetPrestation()
                bud_pres.heure = buds['heure']

                prest_id = Prestation.objects(sigle=buds['prestation_id']).first()
                bud_pres.prestation_id = prest_id

                bud_pres.budget_id = bud_id

                bud_pres.save()

    if result['status'] == 200:
        return 'True'
    else:
        return 'False'


@prefix.route('/etape2')
def etape2():

    url = "http://accentcom-time.com/api/projet"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)
    #
    from ..projet.models_projet import Projet, Domaine, Client, Service, Users, Frais
    for data in result['data']:
        exist_data = Projet.objects(code=data['code']).first()
        if not exist_data:
            proj = Projet()
            proj.code = data['code']
            proj.titre = data['titre']
            proj.heure = data['heure']
            proj.montant = data['montant']

            date_start = datetime.datetime.combine(function.date_convert(data['date_start']), datetime.datetime.min.time())
            proj.date_start = date_start

            date_end = datetime.datetime.combine(function.date_convert(data['date_end']), datetime.datetime.min.time())
            proj.date_end = date_end

            proj.facturable = data['facturable']

            domaine = Domaine.objects(code=data['domaine_id']).first()
            proj.domaine_id = domaine

            client = Client.objects(ref=data['client_id']).first()
            proj.client_id = client

            service = Service.objects(code=data['service_id']).first()
            proj.service_id = service

            if data['prospect_id']:
                prospect = Client.objects(ref=data['prospect_id']).first()
                proj.prospect_id = prospect

            user = Users.objects(matricule=data['responsable_id']).first()
            proj.responsable_id = user

            proj.closed = data['closed']
            proj.suspend = data['suspend']
            proj.montant_projet_fdt = data['montant_projet_fdt']

            proj_ = proj.save()

            # from ..frais.models_frais import FraisProjet
            from ..projet.models_projet import FraisProjet
            for frais in data['frais']:

                frais_id = Frais.objects(libelle=frais['frais_id']).first()

                frai = FraisProjet()
                frai.facturable = frais['facturable']
                frai.frais_id = frais_id
                frai.projet_id = proj_
                frai.montant = frais['montant']
                frai.save()


    if result['status'] == 200:
        return 'True'
    else:
        return 'False'


@prefix.route('/etape3')
def etape3():

    url = "http://accentcom-time.com/api/tache"
    result = urlfetch.get(url)
    result = result.content
    result = json.loads(result)

    from ..tache.models_tache import Tache, Projet, Users, Prestation
    from ..temps.models_temps import Temps, DetailTemps
    for data in result['data']:
        taches = Tache()
        taches.titre = data['titre']
        taches.description = data['description']
        taches.heure = data['heure']

        date_starts = None
        if data['date_start'] != 'None':
            date_starts = datetime.datetime.combine(function.date_convert(data['date_start']), datetime.datetime.min.time())
        taches.date_start = date_starts

        taches.facturable = data['facturable']

        if data['projet_id']:
            projet = Projet.objects(code=data['projet_id']).first()
            taches.projet_id = projet

        if data['user_id']:
            user = Users.objects(email=data['user_id']).first()
            taches.user_id = user

        if data['prestation_id']:
            prestation = Prestation.objects(sigle=data['prestation_id']).first()
            taches.prestation_id = prestation

        taches.end = data['end']
        taches.closed = data['closed']
        taches.detail_heure = data['detail_heure']
        tache_id = taches.save()

        for temps in data['temps']:
            t = Temps()

            date_start_t = datetime.datetime.combine(function.date_convert(temps['date_start_t']), datetime.datetime.min.time())
            t.date_start = date_start_t

            date_end_t = datetime.datetime.combine(function.date_convert(temps['date_end_t']), datetime.datetime.min.time())
            t.date_end = date_end_t

            user = Users.objects(email=temps['user_id']).first()
            t.user_id = user

            t.tache_id = tache_id
            t_id = t.save()

            for detail in temps['list_details']:
                d = DetailTemps()

                date = datetime.datetime.combine(function.date_convert(detail['date']), datetime.datetime.min.time())
                d.date = date

                d.description = detail['description']
                d.heure = function.datetime_convert(str('08:00:00'))
                if detail['heure'] != 'None':
                    d.heure = function.datetime_convert(detail['heure'])
                d.jour = detail['jour']
                d.conversion = detail['conversion']
                d.temps_id = t_id
                d.ordre = detail['ordre']
                d.parent = detail['parent']
                d.save()

    if result['status'] == 200:
        return 'True'
    else:
        return 'False'


@prefix.route('/reset')
def reset():

    from ..tache.models_tache import Tache, Projet

    prod = Projet.objects()

    ok = 'False'
    if prod:
        for proj in prod:
            prof = Projet.objects().get(id=proj.id)
            if prof.code:
                prof.attente = False
                prof.rejet = False
            else:
                prof.attente = True
                prof.rejet = False
            prof.save()
            ok = 'True Projet'

    tac = Tache.objects()
    for tach in tac:
        tache = Tache.objects().get(id=tach.id)
        tache.officiel = False
        tache.save()
        ok = 'True Tache'

    return ok
