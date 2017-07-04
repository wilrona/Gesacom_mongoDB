__author__ = 'Ronald'

from ...modules import *
from models_projet import BesoinFinancier, Projet, Users, Update_Besoin
from forms_projet import FormBesoin

prefix_besoin = Blueprint('besoin', __name__)


@prefix_besoin.route('/')
@login_required
def index():
    menu = 'finance'
    context = ''
    title_page = 'Besoins financiers'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = []
    if request.args.get('filtre') and request.args.get('filtre') is not None:
        if request.args.get('filtre') == 'rejet':
            besoin = BesoinFinancier.objects(
                Q(rejet=True) & Q(attente=False)
            ).order_by('-date_echeance')
            for bes in besoin:
                datas.append(bes)
            small_title = 'rejetes'
        if request.args.get('filtre') == 'applique':
            besoin = BesoinFinancier.objects(
                Q(rejet=False) & Q(attente=False)
            ).order_by('-date_echeance')
            for bes in besoin:
                datas.append(bes)
            small_title = 'valides'

    else:
        besoin = BesoinFinancier.objects(
            Q(rejet=False) & Q(attente=True)
        ).order_by('-date_echeance')
        for bes in besoin:
            if not bes.child():
                datas.append(bes)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='Besoins Financiers')

    if len(datas) > 25:
        offset_start = (page - 1) * 25
        offset_end = page * 25
        datas = datas[offset_start:offset_end]

    return render_template('projet/besoin.html', **locals())


@prefix_besoin.route('/print')
def printer():

    title_page = 'Besoin financier a traiter'
    analyses = []
    besoin = BesoinFinancier.objects(
        Q(rejet=False) & Q(attente=True)
    ).order_by('-date_echeance')
    for bes in besoin:
        if not bes.child():
            analyses.append(bes)

    return render_template('projet/besoin_print.html', **locals())


@prefix_besoin.route('/validation/<objectid:besoin_id>')
def validation(besoin_id):

    besoin = BesoinFinancier.objects.get(id=besoin_id)
    besoin.attente = False
    besoin.rejet = False

    update = Update_Besoin()
    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones)
    the_user = Users.objects.get(id=session.get('user_id'))

    update.date = date_now
    update.user = the_user
    update.action = 'valide_besoin'
    update.notified = True

    besoin.updated.append(update)

    besoin.save()

    flash('Validation effectue avec succes', 'success')

    return redirect(url_for('besoin.index'))


@prefix_besoin.route('/rejet/<objectid:besoin_id>')
def rejet(besoin_id):

    besoin = BesoinFinancier.objects.get(id=besoin_id)
    besoin.attente = False
    besoin.rejet = True

    update = Update_Besoin()
    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones)
    the_user = Users.objects.get(id=session.get('user_id'))

    update.date = date_now
    update.user = the_user
    update.action = 'rejet_besoin'
    update.notified = True

    besoin.updated.append(update)

    besoin.save()

    flash('Rejet effectue avec succes', 'success')

    return redirect(url_for('besoin.index'))


@prefix_besoin.route('/user')
@login_required
def index_user():

    menu = 'self_finance'
    context = ''
    title_page = 'Mes besoins financiers'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    user = Users.objects.get(id=session.get('user_id'))
    user_projet = Projet.objects(responsable_id=user.id)

    datas = []
    if request.args.get('filtre') and request.args.get('filtre') is not None:
        if request.args.get('filtre') == 'rejet':
            for projet in user_projet:
                for prod in projet.besoin(rejet=True, attente=False):
                    datas.append(prod)
            small_title = 'rejetes'
        if request.args.get('filtre') == 'applique':
            for projet in user_projet:
                for prod in projet.besoin(rejet=False, attente=False):
                    datas.append(prod)
            small_title = 'valides'
    else:
        small_title = 'en cours'
        for projet in user_projet:
            for prod in projet.besoin():
                datas.append(prod)

            for prod in projet.besoin_unsolde():
                datas.append(prod)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='Besoins Financiers')

    if len(datas) > 25:
        offset_start = (page - 1) * 25
        offset_end = page * 25
        datas = datas[offset_start:offset_end]

    return render_template('projet/besoin_user.html', **locals())


@prefix_besoin.route('/edit/user', methods=['GET', 'POST'])
@prefix_besoin.route('/edit/user/<objectid:besoin_id>', methods=['GET', 'POST'])
@login_required
def edit_user(besoin_id=None):

    relance = False
    if request.args.get('relance'):
        relance = True

    solde = False
    if request.args.get('solde'):
        solde = True

    if besoin_id:
        besoin = BesoinFinancier.objects.get(id=besoin_id)
        form = FormBesoin(obj=besoin)
        form.projet_id.data = str(besoin.projet_id.id)
        form.id.data = str(besoin.id)
    else:
        besoin = BesoinFinancier()
        form = FormBesoin()

    if relance:
        form.relance.data = 1

    if solde:
        form.solde.data = 1

    user = Users.objects.get(id=session.get('user_id'))
    form.projet_id.choices = [(0, 'Selectionnez un projet')]
    for projet in Projet.objects(responsable_id=user.id):
        form.projet_id.choices.append((str(projet.id), projet.titre))

    success = False
    if form.validate_on_submit():

        if not solde:

            besoin.commande = form.commande.data
            besoin.avance = float(form.avance.data)
            besoin.montant = float(form.montant.data)
            besoin.fournisseur = form.fournisseur.data

            if not form.avance.data:
                besoin.paye = float(form.montant.data)
            else:
                besoin.paye = float(form.avance.data)

            proj = Projet.objects.get(id=form.projet_id.data)
            besoin.projet_id = proj

            update = Update_Besoin()
            time_zones = pytz.timezone('Africa/Douala')
            date_now = datetime.datetime.now(time_zones)
            the_user = Users.objects.get(id=session.get('user_id'))

            update.date = date_now
            update.user = the_user
            update.action = 'creation_besoin'

            if relance:
                besoin.attente = True
                besoin.rejet = False
                update.action = 'relance_besoin'

            update.notified = True

            besoin.updated.append(update)

            besoin.date_echeance = datetime.datetime.combine(function.date_convert(form.date_echeance.data), datetime.datetime.min.time())
            besoin.save()
            success = True

        else:

            # traitement a faire quand nous devons enregistrer une demande de solde
            besoin_new = BesoinFinancier()
            besoin_new.commande = form.commande.data
            besoin_new.avance = float(form.avance.data)
            besoin_new.montant = float(form.montant.data)
            besoin_new.fournisseur = form.fournisseur.data

            besoin_new.paye = float(form.avance.data) + besoin.paye

            besoin_new.last_child = True
            besoin_new.parent = besoin

            proj = Projet.objects.get(id=form.projet_id.data)
            besoin_new.projet_id = proj
            besoin_new.attente = True
            besoin_new.rejet = False

            update = Update_Besoin()
            time_zones = pytz.timezone('Africa/Douala')
            date_now = datetime.datetime.now(time_zones)
            the_user = Users.objects.get(id=session.get('user_id'))

            update.date = date_now
            update.user = the_user
            update.action = 'solde_besoin'

            update.notified = True

            besoin_new.updated.append(update)

            besoin_new.date_echeance = datetime.datetime.combine(function.date_convert(form.date_echeance.data), datetime.datetime.min.time())
            besoin_new.save()
            success = True

        flash('Enregistrement effectue avec succes', 'success')

    return render_template('projet/besoin_edit_user.html', **locals())


@prefix_besoin.route('/user/delete/<objectid:besoin_id>')
def delete_user(besoin_id):

    besoin = BesoinFinancier.objects.get(id=besoin_id)

    if besoin.last_child:
        parent_besoin = BesoinFinancier.objects.get(id=besoin.parent)
        parent_besoin.last_child = True
        parent_besoin.save()

    from ..user.models_user import Update_User
    userC = Users.objects.get(id=session.get('user_id'))

    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    save = False
    for action in besoin.notified():
        if action.notified:
            dif = datetime.datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(action.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            if dif.seconds >= 3600:
                save = True

    if save:
        update = Update_User()

        update.date = function.datetime_convert(date_now)
        update.user = str(besoin.projet_id.responsable_id.id)
        update.action = 'delete_besoin'
        update.notified = True
        update.content = besoin.commande+' au fournisseur '+besoin.fournisseur

        userC.updated.append(update)
        userC.save()

    besoin.delete()
    flash('Suppression effectue avec succes', 'success')

    return redirect(url_for('besoin.index_user', filtre=request.args.get('filtre')))

