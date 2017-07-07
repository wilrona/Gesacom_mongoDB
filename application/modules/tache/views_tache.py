__author__ = 'Ronald'

from ...modules import *
from ..tache.models_tache import Projet
from ..prestation.models_prest import Prestation
from ..temps.models_temps import Users, Temps, Tache, DetailTemps
from forms_tache import FormTache


prefix = Blueprint('tache', __name__)
prefix_projet = Blueprint('tache_projet', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'tache')])
def index():
    menu = 'tache'
    submenu = 'tous'
    context = ''
    title_page = 'Taches'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    limit = 25
    offset = ((page - 1) * 25)

    #id Prestatation Ferier, Conge et Absence

    prest_ferier = Prestation.objects(sigle='FER').first()
    prest_conge = Prestation.objects(sigle='CONG').first()
    prest_absence = Prestation.objects(sigle='ABS').first()

    if prest_absence and prest_conge and prest_ferier:

        count = Tache.objects(
            Q(end=False) & Q(closed=False) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne=prest_ferier.id)
        ).count()

        datas = Tache.objects(
            Q(end=False) & Q(closed=False) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne=prest_ferier.id)
        ).skip(offset).limit(limit).order_by('-date_start')

        if request.args.get('filtre') and request.args.get('filtre') is not None:

            if request.args.get('filtre') == 'end':
                count = Tache.objects(
                    Q(end=True) & Q(closed=False) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne=prest_ferier.id)
                ).count()

                datas = Tache.objects(
                    Q(end=True) & Q(closed=False) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne=prest_ferier.id)
                ).skip(offset).limit(limit).order_by('-date_start')

                small_title = 'terminees'

            if request.args.get('filtre') == 'cloture':
                count = Tache.objects(
                    Q(end=False) & Q(closed=True) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne=prest_ferier.id)
                ).count()
                datas = Tache.objects(
                    Q(end=False) & Q(closed=True) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne=prest_ferier.id)
                ).skip(offset).limit(limit).order_by('-date_start')
                small_title = 'cloturees'

        pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Taches')
    else:
        if current_user.has_roles(['prestation']):
            flash('Demandez a l\'administrateur de configurer au mieux les prestations de l\'application', 'warning')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Creer SVP les prestations de conge, absence et ferier', 'warning')
            return redirect(url_for('prestation.index'))

    return render_template('tache/index.html', **locals())


@prefix.route('/me')
def me():
    menu = 'tache'
    submenu = 'my'
    context = ''
    title_page = 'Taches'

    user = Users.objects.get(id=session.get('user_id'))

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    limit = 25
    offset = ((page - 1) * 25)

    #id Prestatation Ferier, Conge et Absence

    prest_ferier = Prestation.objects(sigle='FER').first()
    prest_conge = Prestation.objects(sigle='CONG').first()
    prest_absence = Prestation.objects(sigle='ABS').first()

    if prest_absence and prest_conge and prest_ferier:

        count = Tache.objects(
            Q(user_id=user.id) & Q(end=False) & Q(closed=False) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne= prest_ferier.id)
        ).count()
        datas = Tache.objects(
            Q(user_id=user.id) & Q(end=False) & Q(closed=False) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne= prest_ferier.id)
        ).skip(offset).limit(limit).order_by('-date_start')

        if request.args.get('filtre') and request.args.get('filtre') is not None:
            if request.args.get('filtre') == 'end':
                count = Tache.objects(
                    Q(user_id=user.id) & Q(end=True) & Q(closed=False) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne= prest_ferier.id)
                ).count()
                datas = Tache.objects(
                    Q(user_id=user.id) & Q(end=True) & Q(closed=False) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne= prest_ferier.id)
                ).skip(offset).limit(limit).order_by('-date_start')
                small_title = 'terminees'

            if request.args.get('filtre') == 'cloture':
                count = Tache.objects(
                    Q(user_id=user.id) & Q(end=True) & Q(closed=True) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne= prest_ferier.id)
                ).count()
                datas = Tache.objects(
                    Q(user_id=user.id) & Q(end=True) & Q(closed=True) & Q(prestation_id__ne=prest_conge.id) & Q(prestation_id__ne=prest_absence.id) & Q(prestation_id__ne= prest_ferier.id)
                ).skip(offset).limit(limit).order_by('-date_start')
                small_title = 'cloturees'

        pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Taches')

    else:
        flash('Demandez a l\'administrateur de configurer au mieux les prestations de l\'application', 'warning')
        return redirect(url_for('dashboard.index'))

    return render_template('tache/me.html', **locals())


@prefix.route('/edit', methods=['GET', 'POST'])
@prefix.route('/edit/<objectid:tache_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'tache')], ['edit'])
def edit(tache_id=None):
    from models_tache import Update_Tache
    hors_projet = False
    if tache_id:
        tache = Tache.objects.get(id=tache_id)
        form = FormTache(obj=tache)
        form.user_id.data = str(tache.user_id.id)
        form.prestation_id.data = str(tache.prestation_id.id)
        form.projet_id.data = str(tache.projet_id.id)
        if tache.facturable:
            form.facturable.data = '1'
        else:
            form.facturable.data = '2'
        form.id.data = str(tache.id)
    else:
        tache = Tache()
        form = FormTache()
    form.contact.data = "contact"

    form.projet_id.choices = [(0, 'Selectionnez un projet')]
    for projet in Projet.objects(closed=False):
        form.projet_id.choices.append((str(projet.id), projet.titre))

    form.user_id.choices = [(0, 'Selectionnez l\'utilisateur')]
    for user in Users.objects(email__ne='admin@accentcom-cm.com'):
        form.user_id.choices.append((str(user.id), user.first_name+" "+user.last_name))

    if form.prestation_id.data:
        prest = Prestation.objects.get(id=form.prestation_id.data)
        list_factu = {}
        if prest.nfactu:
            list_factu[2] = 'Non Facturable'
        if prest.factu:
            list_factu[1] = 'Facturable'

    if not tache_id:
        list_prestation = Prestation.objects(
            Q(sigle__ne=None) & Q(sigle__ne='CONG') & Q(sigle__ne='ABS') & Q(sigle__ne='FER')
        )

    success = False
    if form.validate_on_submit():
        tache.titre = form.titre.data
        tache.description = form.description.data
        tache.heure = int(form.heure.data)

        user = Users.objects.get(id=form.user_id.data)
        tache.user_id = user

        if form.facturable.data == '2':
            tache.facturable = False
        if form.facturable.data == '1':
            tache.facturable = True

        prestation = Prestation.objects.get(id=form.prestation_id.data)
        tache.prestation_id = prestation

        projet = Projet.objects.get(id=form.projet_id.data)
        tache.projet_id = projet

        correct = True
        if form.id.data and tache_id:
            if datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time()) < tache.date_start:
                form.date_start.errors.append('La date de debut ne peut etre anterieure a la precedente')
                correct = False
            else:
                tache.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())
        else:
            tache.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())

        ## Controle de la somme des heures par rapport au projet
        if correct:
            heure = projet.heure
            taches = Tache.objects(projet_id=projet.id)
            heure_total = 0
            for tache_heure in taches:
                heure_total += int(tache_heure.heure)

            if tache_id:
                heure_total -= int(form.heure.data)
            else:
                heure_total += int(form.heure.data)

            heure_restant = heure - heure_total
            if heure_restant < 0:
                form.heure.errors.append('Heure ventillee superieur a l\'heure total du projet')
            else:
                update = Update_Tache()
                time_zones = pytz.timezone('Africa/Douala')
                date_now = datetime.datetime.now(time_zones)
                the_user = Users.objects.get(id=session.get('user_id'))

                update.date = date_now
                update.user = the_user

                if tache_id:
                    update.action = 'modification'
                else:
                    update.action = 'creation'

                update.notified = True

                tache.updated.append(update)

                tache.save()
                success = True

    return render_template('tache/edit.html', **locals())


@prefix.route('/no_projet/edit', methods=['GET', 'POST'])
@prefix.route('/no_projet/edit/<objectid:tache_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'tache')], ['edit'])
def hors_projet(tache_id=None):

    from models_tache import Update_Tache
    hors_projet = True

    if tache_id:
        tache = Tache.objects.get(id=tache_id)
        form = FormTache(obj=tache)
        form.user_id.data = tache.user_id.id
        form.prestation_id.data = tache.prestation_id.id
        # form.projet_id.data = tache.projet_id.get().key.id()
        if tache.facturable:
            form.facturable.data = '1'
        else:
            form.facturable.data = '2'
        form.id.data = tache.id
    else:
        tache = Tache()
        form = FormTache()
    # form.contact.data = "contact"

    form.projet_id.choices = [('', 'Selectionnez un projet')]
    for projet in Projet.objects(closed=False):
        form.projet_id.choices.append((str(projet.id), projet.titre))

    form.user_id.choices = [(0, 'Selectionnez l\'utilisateur')]
    for user in Users.objects(email__ne='admin@accentcom-cm.com'):
        form.user_id.choices.append((str(user.id), user.first_name+" "+user.last_name))

    if form.prestation_id.data:
        prest = Prestation.objects.get(id=form.prestation_id.data)
        list_factu = {}
        if prest.nfactu:
            list_factu[2] = 'Non Facturable'
        if prest.factu:
            list_factu[1] = 'Facturable'

    if not tache_id:
        list_prestation = Prestation.objects(
            Q(sigle__ne=None) & Q(sigle__ne='CONG') & Q(sigle__ne='ABS') & Q(sigle__ne='FER')
        )

    success = False
    if form.validate_on_submit():
        tache.titre = form.titre.data
        tache.description = form.description.data
        tache.heure = int(form.heure.data)

        user = Users.objects.get(id=form.user_id.data)
        tache.user_id = user

        if form.facturable.data == '2':
            tache.facturable = False
        if form.facturable.data == '1':
            tache.facturable = True

        prestation = Prestation.objects.get(id=form.prestation_id.data)
        tache.prestation_id = prestation
        #
        # projet = Projet.get_by_id(int(form.projet_id.data))
        #
        # tache.projet_id = projet.key

        correct = True
        if form.id.data and tache_id:
            if datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time()) < tache.date_start:
                form.date_start.errors.append('La date de debut ne peut etre anterieure a la precedente')
                correct = False
            else:
                tache.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())
        else:
            tache.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())

        ## Controle de la somme des heures par rapport au projet
        # if correct:
        #     heure = projet.heure
        #     taches = Tache.query(Tache.projet_id == projet.key)
        #     heure_total = 0
        #     for tache_heure in taches:
        #         heure_total += tache_heure.heure
        #
        #     heure_total += form.heure.data
        #     heure_restant = heure - heure_total
        #     if heure_restant < 0:
        #         form.heure.errors.append('Heure ventillee superieur a l\'heure total du projet')
        #     else:
        if correct:
            update = Update_Tache()
            time_zones = pytz.timezone('Africa/Douala')
            date_now = datetime.datetime.now(time_zones)
            the_user = Users.objects.get(id=session.get('user_id'))

            update.date = date_now
            update.user = the_user

            if tache_id:
                update.action = 'modification'
            else:
                update.action = 'creation'

            update.notified = True

            tache.updated.append(update)

            tache.save()
            success = True

    return render_template('tache/edit.html', **locals())


@prefix.route('/delete/<objectid:tache_id>')
@login_required
def delete(tache_id):
    # from ..temps.models_temps import Temps

    tache = Tache.objects.get(id=tache_id)

    projet_id = tache.projet_id.id

    feuille_temps = Temps.objects(
        tache_id = tache.id
    )
    if feuille_temps:
        flash('Impossible de supprimer l\'element ', 'danger')
    else:
        from ..user.models_user import Update_User
        userC = Users.objects.get(id=session.get('user_id'))

        time_zones = pytz.timezone('Africa/Douala')
        date_now = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

        save = False
        for action in tache.notified():
            if action.notified:
                dif = datetime.datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(action.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                if dif.seconds >= 3600:
                    save = True

        if save:
            update = Update_User()

            update.date = function.datetime_convert(date_now)
            update.user = str(tache.user_id.id)
            update.action = 'delete_tache'
            update.notified = True
            update.content = tache.titre

            userC.updated.append(update)
            userC.save()

        flash('Suppression reussie', 'success')
        tache.delete()
    return redirect(url_for('tache_projet.index', projet_id=projet_id))


@prefix.route('/detail/<objectid:tache_id>')
@login_required
def detail(tache_id):

    menu = 'tache'
    submenu = 'tache'
    context = 'information'
    title_page = 'Taches - Details'

    tache = Tache.objects.get(id=tache_id)

    return render_template('tache/detail.html', **locals())


@prefix.route('/end/<objectid:tache_id>')
@login_required
def end(tache_id):

    from models_tache import Update_Tache

    tache = Tache.objects.get(id=tache_id)

    update = Update_Tache()
    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones)
    the_user = Users.objects.get(id=session.get('user_id'))

    update.date = date_now
    update.user = the_user
    update.notified = True

    if tache.end:
        update.action = 'modification'
        tache.end = False
        tache.save()
    else:
        update.action = 'open_end'
        tache.end = True
        if not tache.projet_id:
            tache.updated.append(update)
            tache.closed = True
            tache.save()
        else:
            tache.updated.append(update)
            tache.save()

    if tache.officiel:
        return redirect(url_for('user_param.formation_detail', tache_id=tache.id))
    else:
        return redirect(url_for('tache.detail', tache_id=tache_id))


@prefix.route('/closed/<objectid:tache_id>')
@login_required
def closed(tache_id):

    from models_tache import Update_Tache

    tache = Tache.objects.get(id=tache_id)

    update = Update_Tache()
    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones)
    the_user = Users.objects.get(id=session.get('user_id'))

    update.date = date_now
    update.user = the_user
    update.notified = True

    if tache.closed:
        update.action = 'modification'
        tache.closed = False
        flash('Modification reussie avec success', 'success')
    else:
        update.action = 'end_close'
        tache.closed = True
        flash('Cloture de la tache reussie', 'success')

    tache.updated.append(update)
    tache.save()
    if tache.officiel:
        return redirect(url_for('user_param.formation_detail', tache_id=tache.id))
    else:
        return redirect(url_for('tache.detail', tache_id=tache_id))


## LISTE DES TACHES D'UN PROJET
@prefix_projet.route('/tache/<objectid:projet_id>')
@login_required
def index(projet_id):
    menu = 'projet'
    submenu = 'projet'
    context = 'tache'
    title_page = 'Projets - Taches'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1


    limit = 25
    offset = ((page - 1) * 25)

    projet = Projet.objects.get(id=projet_id)

    count = Tache.objects(projet_id=projet.id).count()
    datas = Tache.objects(projet_id=projet.id).skip(offset).limit(limit)

    pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Taches')

    return render_template('tache/tache_projet.html', **locals())


## EDITION D'UNE TACHE DEPUIS UN PROJET
@prefix_projet.route('/tache/edit/<objectid:projet_id>', methods=['GET', 'POST'])
@prefix_projet.route('/tache/edit/<objectid:projet_id>/<objectid:tache_id>', methods=['GET', 'POST'])
@login_required
def edit(projet_id, tache_id=None):
    from models_tache import Update_Tache
    projet = Projet.objects.get(id=projet_id)

    if tache_id:
        tache = Tache.objects.get(id=tache_id)
        form = FormTache(obj=tache)
        form.user_id.data = tache.user_id.id
        form.prestation_id.data = tache.prestation_id.id
        form.projet_id.data = tache.projet_id.id
        if tache.facturable:
            form.facturable.data = '1'
        else:
            form.facturable.data = '2'
        form.id.data = tache.id
    else:
        tache = Tache()
        form = FormTache()

    form.projet_id.choices = [(str(projet.id), projet.titre)]

    form.user_id.choices = [(0, 'Selectionnez l\'utilisateur')]
    for user in Users.objects(email__ne='admin@accentcom-cm.com'):
        form.user_id.choices.append((str(user.id), user.first_name+" "+user.last_name))

    if form.prestation_id.data:
        prest = Prestation.objects.get(id=form.prestation_id.data)
        list_factu = {}
        if prest.nfactu:
            list_factu[2] = 'Non Facturable'
        if prest.factu:
            list_factu[1] = 'Facturable'

    list_prestation = Prestation.objects(
        Q(sigle__ne=None) & Q(sigle__ne='CONG') & Q(sigle__ne='ABS') & Q(sigle__ne='FER')
    )

    success = False
    if form.validate_on_submit():
        tache.titre = form.titre.data
        tache.description = form.description.data
        tache.heure = form.heure.data

        user = Users.objects.get(id=form.user_id.data)
        tache.user_id = user

        if form.facturable.data == '2':
            tache.facturable = False
        if form.facturable.data == '1':
            tache.facturable = True

        prestation = Prestation.objects.get(id=form.prestation_id.data)
        tache.prestation_id = prestation
        tache.projet_id = projet

        correct = True
        if form.id.data and tache_id:
            if datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time()) < tache.date_start:
                form.date_start.errors.append('La date de debut ne peut etre anterieure a la precedente')
                correct = False
            else:
                tache.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())
        else:
            tache.date_start = datetime.datetime.combine(function.date_convert(form.date_start.data), datetime.datetime.min.time())

        ## Controle de la somme des heures par rapport au projet
        if correct:
            heure = projet.heure
            taches = Tache.objects(projet_id = projet.id)
            heure_total = 0
            for tache_heure in taches:
                heure_total += int(tache_heure.heure)

            heure_total += int(form.heure.data)
            heure_restant = heure - heure_total
            if heure_restant < 0:
                form.heure.errors.append('Heure ventillee superieur a l\'heure total du projet' + str(heure_restant))
            else:
                update = Update_Tache()
                time_zones = pytz.timezone('Africa/Douala')
                date_now = datetime.datetime.now(time_zones)
                the_user = Users.objects.get(id=session.get('user_id'))

                update.date = date_now
                update.user = the_user

                if tache_id:
                    update.action = 'modification'
                else:
                    update.action = 'creation'

                update.notified = True

                tache.updated.append(update)

                tache.save()
                success = True

    return render_template('tache/tache_projet_edit.html', **locals())


@prefix_projet.route('/prestation')
@prefix_projet.route('/prestation/<prestation_id>')
def facturations(prestation_id = None):
    data = {}
    data['fact'] = 0
    data['nfact'] = 0
    if prestation_id:
        prestation = Prestation.objects.get(id=prestation_id)
        if prestation.factu:
            data['fact'] = 1
        if prestation.nfactu:
            data['nfact'] = 1
    resp = jsonify(data)
    return resp


# cron temps remplit sur une tache
@prefix.route('/fdt_tache')
def fdt_tache():
    # from ..temps.models_temps import Temps, DetailTemps

    for tache in Tache.objects():
        total = 0.0
        for temps in Temps.objects(tache_id=tache.id):
            details = DetailTemps.objects(
                temps_id=temps.id
            )
            for detail in details:
                total += detail.conversion

        tache.detail_heure = total
        tache.save()

    return render_template('401.html')


@prefix.route('/montant_projet_fdt')
def montant_projet_fdt():
    # from ..tache.models_tache import Tache, Projet

    for projet in Projet.objects():

        tache_projet = Tache.objects(
            projet_id =projet.id
        )

        total = 0.0
        for tache in tache_projet:
            if tache.prestation_sigle() == 'PRO' and tache.facturable:
                user_taux = tache.user_id.tauxH
                time = tache.detail_heure

                pre_total = user_taux * time

                total += pre_total

        projet.montant_projet_fdt = total
        projet.save()

    msg = Message()
    msg.recipients = ["ronald@accentcom-cm.com"]
    msg.subject = 'Notification FDT'
    msg.sender = ('Application FDT', 'no_reply@accentcom.agency')

    msg.html = render_template('mail/notification_mail.html')
    mail.send(msg)

    return render_template('401.html')

