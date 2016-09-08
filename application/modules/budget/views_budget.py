__author__ = 'Ronald'

from ...modules import *
from models_budget import Budget, BudgetPrestation, Prestation, ChargeBudget, Charge, ClientBudget, Client
from ..user.models_user import Users
from forms_budget import FormBudget

prefix = Blueprint('budget', __name__)


@prefix.route('/budget')
@login_required
@roles_required([('super_admin', 'budget_userH')])
def index():
    menu = 'societe'
    submenu = 'budget'
    context = 'collaborateur'
    title_page = 'Parametre - Budget Collaborateur'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    #liste des budgets collaborateurs
    users = Users.objects(email__ne='admin@accentcom-cm.com')

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year
    # date = datetime.date(date_auto_nows, 1, 1)

    if request.args.get('year') and request.args.get('year') is not None:
        current_year = int(request.args.get('year'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    budget_year = Budget.objects()
    for bud in budget_year:
        year = {}
        year['date'] = bud.date_start.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    datas = users
    datas.paginate(page=page, per_page=10)

    # Traitement du tableau des budgets a afficher
    list_budget = []
    for user in datas:
        data = {}
        data['id'] = user.id
        data['full_name'] = user.first_name+" "+user.last_name
        data['taux'] = user.tauxH

        budget = Budget.objects(Q(date_start=datetime.date(current_year, 1, 1),) & Q(user_id=user.id)).first()

        data['disponible'] = 0
        data['budget_id'] = None

        data['budget_prestation'] = []

        if budget:
            data['disponible'] = budget.heure
            data['budget_id'] = budget.id

            budget_prest = BudgetPrestation.objects(budget_id= budget.id)

            for prestation in budget_prest:
                data2 = {}
                data2['id'] = prestation.prestation_id.id
                data2['prestation'] = prestation.prestation_id.libelle
                data2['sigle'] = prestation.prestation_id.sigle
                data2['time'] = prestation.heure

                data['budget_prestation'].append(data2)

        list_budget.append(data)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(users), search=search, record_name='Budget')

    return render_template('budget/index.html', **locals())


@prefix.route('/budget/valeur')
@login_required
@roles_required([('super_admin', 'budget_userV')])
def valeur():
    menu = 'societe'
    submenu = 'budget'
    context = 'collaborateur'
    title_page = 'Parametre - Budget Collaborateur'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    #liste des budgets collaborateurs
    users = Users.objects(email__ne='admin@accentcom-cm.com')

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year
    # date = datetime.date(date_auto_nows, 1, 1)

    if request.args.get('year') and request.args.get('year') is not None:
        current_year = int(request.args.get('year'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    budget_year = Budget.objects()
    for bud in budget_year:
        year = {}
        year['date'] = bud.date_start.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    # Traitement du tableau des budgets a afficher
    list_budget = []

    datas = users
    datas.paginate(page=page, per_page=10)

    for user in datas:
        data = {}
        data['id'] = user.id
        data['full_name'] = user.first_name+" "+user.last_name
        data['taux'] = user.tauxH

        budget = Budget.objects(Q(date_start=datetime.date(current_year, 1, 1)) & Q(user_id=user.id)).first()

        data['heure'] = 0

        if budget:
            budget_prest = BudgetPrestation.objects(budget_id=budget.id)
            for prestation in budget_prest:
                if prestation.prestation_id.sigle == 'PRO':
                    data['heure'] = prestation.heure
                    break

        list_budget.append(data)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(users), search=search, record_name='Budget')


    return render_template('budget/valeur.html', **locals())


@prefix.route('/budget/<objectid:user_id>/<int:page>/<int:current_year>', methods=['GET', 'POST'])
@prefix.route('/budget/<objectid:user_id>/<int:page>/<int:current_year>/<objectid:budget_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'budget_userH')], ['edit'])
def edit(user_id, page, current_year, budget_id=None):

    user = Users.objects.get(id=user_id)

    if budget_id:
        budget = Budget.objects.get(id=budget_id)

        disponible = budget.heure

        prest1 = BudgetPrestation.objects(budget_id=budget.id)

        for pres in prest1:

            if pres.prestation_id.sigle == 'FOR':
                formation = pres.heure
            if pres.prestation_id.sigle == 'DEV':
                developpement = pres.heure
            if pres.prestation_id.sigle == 'ADM':
                administration = pres.heure
            if pres.prestation_id.sigle == 'PRO':
                production = pres.heure
    else:
        budget = Budget()

    success = False
    dispo = 0.0
    dispo2 = 0.0

    if request.method == 'POST':

        disponible = request.form['disponible']
        production = request.form['production']
        formation = request.form['formation']
        developpement = request.form['developpement']
        administration = request.form['administration']

        dispo = float(request.form['disponible']) - float(request.form['administration'])
        dispo -= float(request.form['production'])
        dispo -= float(request.form['formation'])
        dispo -= float(request.form['developpement'])
        dispo = round(dispo,1)

        error = False
        if dispo > 0.0:
            error = True
            message = 'La somme des heures de prestation n\'est pas egale aux heures disponibles'
        if dispo < 0.0:
            error = True
            message = 'La somme des heures de prestation est superieure aux heures disponibles '+str(dispo)

        if not error:
            if not budget_id:
                budget.date_start = datetime.date(current_year, 1, 1)
                budget.user_id = user

            budget.heure = float(request.form['disponible'])
            bud_id = budget.save()

            prest = Prestation.objects(sigle__ne=None)

            for pres in prest:

                presti = BudgetPrestation.objects(Q(prestation_id=pres.id) & Q(budget_id=bud_id)).first()

                if presti:

                    if pres.sigle == 'FOR':
                        presti.heure = float(request.form['formation'])
                    if pres.sigle == 'DEV':
                        presti.heure = float(request.form['developpement'])
                    if pres.sigle == 'ADM':
                        presti.heure = float(request.form['administration'])
                    if pres.sigle == 'PRO':
                        presti.heure = float(request.form['production'])

                    presti.budget_id = bud_id
                    presti.prestation_id = pres
                    presti.save()

                else:

                    prestis = BudgetPrestation()

                    if pres.sigle == 'FOR':
                        prestis.heure = float(request.form['formation'])
                    if pres.sigle == 'DEV':
                        prestis.heure = float(request.form['developpement'])
                    if pres.sigle == 'ADM':
                        prestis.heure = float(request.form['administration'])
                    if pres.sigle == 'PRO':
                        prestis.heure = float(request.form['production'])

                    prestis.budget_id = bud_id
                    prestis.prestation_id = pres
                    prestis.save()

            flash('Enregistement effectue avec succes', 'success')
            success = True

    return render_template('budget/edit.html', **locals())


# Traitement des charges et impots
@prefix.route('/budget/charge')
@login_required
@roles_required([('super_admin', 'budget_charge')])
def charge():
    menu = 'societe'
    submenu = 'budget'
    context = 'charge'
    title_page = 'Parametre - Budget Charge/Impot'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    if request.args.get('year') is not None:
        current_year = int(request.args.get('year'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    charge_year = ChargeBudget.objects()
    for bud in charge_year:
        year = {}
        year['date'] = bud.date_app.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    datas = Charge.objects()

    # Traitement du tableau des charges a afficher
    list_charge = []

    data_fecth = datas
    data_fecth.paginate(page=page, per_page=10)

    for charge in data_fecth:
        data = {}
        data['id'] = charge.id
        data['name'] = charge.libelle

        charg = ChargeBudget.objects(Q(date_app=datetime.date(current_year, 1, 1)) & Q(charge_id=charge.id)).first()

        data['montant'] = 0

        if charg:
            data['montant'] = charg.montant

        list_charge.append(data)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='Charges')

    return render_template('budget/charge.html', **locals())


@prefix.route('/budget/charge/edit', methods=['POST'])
@login_required
@roles_required([('super_admin', 'budget_charge')], ['edit'])
def charge_edit():

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if request.form['year']:

        charges = Charge.objects.paginate(page=page, per_page=10)
        for char in charges:
            budget = ChargeBudget.objects(Q(charge_id=char.id) & Q(date_app=function.datetime_convert(datetime.date(int(request.form['year']), 1, 1)))).first()

            clef = 'name['+str(char.id)+']'

            if budget:
                if float(request.form[clef]) > 0:
                    budget.montant = float(request.form[clef])
                    budget.save()
                else:
                    budget.delete()
            else:
                budget_new = ChargeBudget()
                if float(request.form[clef]) > 0:
                    budget_new.montant = float(request.form[clef])
                else:
                    budget_new.montant = float(0)
                budget_new.date_app = function.datetime_convert(datetime.date(int(request.form['year']), 1, 1))
                budget_new.charge_id = char
                budget_new.save()

        flash('Enregistrement effectue avec succes', 'success')

    return redirect(url_for('budget.charge', page=page, year=str(request.form['year'])))

@prefix.route('/budget/client')
@login_required
@roles_required([('super_admin', 'budget_client')])
def client():
    menu = 'societe'
    submenu = 'budget'
    context = 'client'
    title_page = 'Parametre - Budget Previsionnel Client'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    if request.args.get('year') is not None:
        current_year = int(request.args.get('year'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    charge_year = ClientBudget.objects()
    for bud in charge_year:
        year = {}
        year['date'] = bud.date_app.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    datas = Client.objects(prospect=False)

    data_fecth = datas
    data_fecth.paginate(page=page, per_page=10)

    # Traitement du tableau des charges a afficher
    list_charge = []
    for client in data_fecth:
        data = {}
        data['id'] = client.id
        data['name'] = client.name

        charg = ClientBudget.objects(Q(date_app=datetime.date(current_year, 1, 1)) & Q(client_id=client.id)).first()

        data['montant'] = 0

        if charg:
            data['montant'] = charg.montant

        list_charge.append(data)


    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='Clients')

    return render_template('budget/client.html', **locals())


@prefix.route('/budget/client/edit', methods=['POST'])
@login_required
@roles_required([('super_admin', 'budget_client')], ['edit'])
def client_edit():

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if request.form['year']:

        clients = Client.objects.paginate(page=page, per_page=10)

        for client in clients:
            budget = ClientBudget.objects(
                Q(client_id=client.id) & Q(date_app=function.datetime_convert(datetime.date(int(request.form['year']), 1, 1)))
            ).first()

            clef = 'name['+str(client.id)+']'

            if budget:
                if float(request.form[clef]) > 0:
                    budget.montant = float(request.form[clef])
                    budget.save()
                else:
                    budget.delete()
            else:
                budget_new = ClientBudget()
                if float(request.form[clef]) > 0:
                    budget_new.montant = float(request.form[clef])
                else:
                    budget_new.montant = float(0)
                budget_new.date_app = function.datetime_convert(datetime.date(int(request.form['year']), 1, 1))
                budget_new.client_id = client.id
                budget_new.save()

        flash('Enregistrement effectue avec succes', 'success')

    return redirect(url_for('budget.client', page=page, year=request.form['year']))


