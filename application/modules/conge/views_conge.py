__author__ = 'Ronald'

from ...modules import *
from ..tache.models_tache import Prestation
from ..temps.models_temps import Temps, DetailTemps, Tache, Users
from ..temps.forms_temps import FormTemps
from models_conge import Ferier
from forms_conge import FormFerier

prefix = Blueprint('conge', __name__)
prefix_param = Blueprint('ferier', __name__)


@prefix.route('/absence/<objectid:user_id>')
@login_required
def index(user_id):
    menu = 'user'
    submenu = 'conge'
    context = 'conge'
    title_page = 'Parametre - Utilisateurs'

    user = Users.objects.get(id=user_id)

    datas = Prestation.objects(Q(sigle='CONG') | Q(sigle='ABS'))

    return render_template('conge/index.html', **locals())


@prefix.route('/temps/absence/<objectid:user_id>')
@login_required
def temps_absence(user_id):

    menu = 'user'
    submenu = 'absence'
    context = 'absence'
    title_page = 'Parametre - Utilisateurs- absence'

    current_prestation = Prestation.objects(sigle='ABS').first()
    user = Users.objects.get(id=user_id)


    exist_tache = Tache.objects(Q(prestation_id=current_prestation.id) & Q(user_id=user.id))

    if not exist_tache:

        tache = Tache()
        tache.titre = 'Tache pour renseigner les '+current_prestation.libelle
        tache.user_id = user
        tache.prestation_id = current_prestation
        tache.save()

        return redirect(url_for('conge.temps_absence', user_id=user_id))
    else:

        tache = Tache.objects(Q(prestation_id = current_prestation.id) & Q(user_id = user.id)).first()

        temps = Temps.objects(
            Q(tache_id=tache.id)
        ).first()

        search = False
        q = request.args.get('q')
        if q:
            search = True
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        offset = 0
        limit = 25
        if page > 1:
            offset = ((page - 1) * 25)

        datas = []
        pagination = None
        if temps:
            datas = DetailTemps.objects(temps_id= temps.id).order_by("-date", "order").skip(offset).limit(limit)
            count = DetailTemps.objects(temps_id= temps.id).count()
            pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Feuille de temps')

        return render_template('conge/temps_absence.html', **locals())


@prefix.route('/temps/absence/edit/<objectid:tache_id>', methods=['GET', 'POST'])
@prefix.route('/temps/absence/edit/<objectid:tache_id>/<objectid:detail_fdt_id>', methods=['GET', 'POST'])
@login_required
def temps_absence_edit(tache_id, detail_fdt_id=None):

    tache = Tache.objects.get(id=tache_id)
    context = 'absence'

    if detail_fdt_id:
        detail_fdt = DetailTemps.objects.get(id=detail_fdt_id)
        form = FormTemps(obj=detail_fdt)
    else:
        detail_fdt = DetailTemps()
        form = FormTemps()

    form.jour.data = 0

    success = False
    if form.validate_on_submit():

        day = datetime.date.today().strftime('%d/%m/%Y')
        dt = datetime.datetime.strptime(day, '%d/%m/%Y')
        start = dt - timedelta(days=dt.weekday())
        end = start + timedelta(days=6)


        temps = Temps.objects(
            Q(tache_id = tache.id) & Q(date_start=start) & Q(date_end=end)
        ).first()

        detail_fdt.date = datetime.datetime.combine(function.date_convert(form.date.data), datetime.datetime.min.time())
        detail_fdt.description = form.description.data
        detail_fdt.heure = function.datetime_convert(form.heure.data)

        time = str(form.heure.data)
        time = time.split(':')

        conversion = 0.0

        if int(time[0]) > 0:
            conversion += float(time[0])

        if int(time[1]) > 0:
            min = float(time[1])/60
            conversion += min

        detail_fdt.conversion = conversion

        if temps:
            detail_fdt.temps_id = temps.id
        else:
            temps = Temps()
            temps.user_id = tache.user_id
            temps.date_start = datetime.datetime.combine(function.date_convert(start), datetime.datetime.min.time())
            temps.date_end = datetime.datetime.combine(function.date_convert(end), datetime.datetime.min.time())
            temps.tache_id = tache
            time = temps.save()
            detail_fdt.temps_id = time

        if not detail_fdt_id:
            ordre = 1
            exist_temps = DetailTemps.objects(
                temps_id=detail_fdt.temps_id.id
            )

            if len(exist_temps):
                ordre += exist_temps

            detail_fdt.ordre = ordre

        detail_fdt.save()

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('temps/temps_tache_edit.html', **locals())


@prefix.route('/temps/conge/<objectid:user_id>')
@login_required
def temps_conge(user_id):

    menu = 'user'
    submenu = 'conge'
    context = 'conge'
    title_page = 'Parametre - Utilisateurs - Conge'

    current_prestation = Prestation.objects(sigle='CONG').first()
    user = Users.objects.get(id=user_id)


    exist_tache = Tache.objects(
        Q(prestation_id = current_prestation.id) & Q(user_id = user.id)
    )

    if not exist_tache:

        tache = Tache()
        tache.titre = 'Tache pour renseigner les '+current_prestation.libelle
        tache.user_id = user
        tache.prestation_id = current_prestation
        tache.save()

        return redirect(url_for('conge.temps_conge', user_id=user_id))

    else:

        tache = Tache.objects(
            Q(prestation_id = current_prestation.id) & Q(user_id = user.id)
        ).first()

        temps = Temps.objects(
            Q(tache_id = tache.id)
        ).first()

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

        datas = []
        pagination = None
        if temps:
            datas = DetailTemps.objects(Q(temps_id=temps.id) & Q(parent=None)).order_by("-date", "ordre").skip(offset).limit(limit)
            count = DetailTemps.objects(Q(temps_id=temps.id) & Q(parent=None)).count()
            pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Feuille de temps')

        return render_template('conge/temps_conge.html', **locals())


@prefix.route('/temps/conge/edit/<objectid:tache_id>', methods=['GET', 'POST'])
@prefix.route('/temps/conge/edit/<objectid:tache_id>/<objectid:detail_fdt_id>', methods=['GET', 'POST'])
@login_required
def temps_conge_edit(tache_id, detail_fdt_id=None):

    tache = Tache.objects.get(id=tache_id)
    context = 'conge'

    if detail_fdt_id:
        detail_fdt = DetailTemps.objects.get(id=detail_fdt_id)
        form = FormTemps(obj=detail_fdt)
    else:
        detail_fdt = DetailTemps()
        form = FormTemps()

    form.derob_day.data = 1
    form.derob.data = 1

    success = False
    if form.validate_on_submit():

        time_zones = pytz.timezone('Africa/Douala')
        date_auto_nows = datetime.datetime.now(time_zones)

        start = function.get_first_day(date_auto_nows)
        end = function.get_last_day(date_auto_nows)

        temps = Temps.objects(
            Q(tache_id=tache.id) & Q(date_start=start) & Q(date_end=end)
        ).first()

        date_insert = datetime.datetime.combine(function.datetime_convert(form.date.data), datetime.datetime.min.time())
        if detail_fdt_id:
            if detail_fdt.date != date_insert or detail_fdt.jour != int(form.jour.data):
                delete_fdt = DetailTemps.objects(
                    parent=detail_fdt_id.id
                )
                for delete in delete_fdt:
                    delete.delete()

        detail_fdt.date = date_insert
        detail_fdt.description = form.description.data

        detail_fdt.jour = int(form.jour.data)

        jour = 8 * int(form.jour.data)

        if jour >= 10:
            heure = str(jour)+':00'
        else:
            heure = '0'+str(jour)+":00"

        time = str(heure)
        time = time.split(':')

        conversion = 0.0

        if int(time[0]) > 0:
            conversion += float(time[0])

        if int(time[1]) > 0:
            min = float(time[1])/60
            conversion += min

        detail_fdt.conversion = conversion

        if temps:
            detail_fdt.temps_id = temps.id
        else:
            temps = Temps()
            temps.user_id = tache.user_id
            temps.date_start = datetime.datetime.combine(function.date_convert(start), datetime.datetime.min.time())
            temps.date_end = datetime.datetime.combine(function.date_convert(end), datetime.datetime.min.time())
            temps.tache_id = tache
            time = temps.save()
            detail_fdt.temps_id = time

        if not detail_fdt_id:
            ordre = 1
            exist_temps = DetailTemps.objects(
                temps_id=detail_fdt.temps_id.id
            )

            if len(exist_temps):
                ordre += exist_temps

            detail_fdt.ordre = ordre

        parent = detail_fdt.save()
        parent = DetailTemps.objects.get(id=parent.id)

        start = 0
        for day in range(0, int(form.jour.data)):
            detail_fdt = DetailTemps()
            date_1 = datetime.datetime.strptime(function.date_convert(form.date.data).strftime('%m/%d/%y'), "%m/%d/%y")
            date_2 = date_1 + timedelta(days=start)

            add = False
            if date_2.weekday() == 5:
                start += 2
                date_2 = date_1 + timedelta(days=start)
                add = True

            detail_fdt.date = date_2
            detail_fdt.conversion = 8.0
            detail_fdt.temps_id = parent.temps_id
            detail_fdt.heure = function.datetime_convert(str('08:00:00'))
            detail_fdt.parent = int(parent.id)
            detail_fdt.save()

            start += 1

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('temps/temps_tache_edit.html', **locals())


@prefix_param.route('/ferier')
@login_required
def jour_ferier():

    title_page = 'Parametre - Jour Ferier'
    menu = 'societe'
    submenu = 'ferier'

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones)

    year = date_auto_nows.year

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    offset = 0
    limit = 10
    if page > 1:
        offset = ((page - 1) * 10)

    datas = Ferier.objects().order_by('-date').skip(offset).limit(limit)
    count = Ferier.objects().count()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=count, search=search, record_name='Ferier')

    return render_template('conge/jour_ferier.html', **locals())


@prefix_param.route('/ferier/edit', methods=['GET', 'POST'])
@prefix_param.route('/ferier/edit/<objectid:ferier_id>', methods=['GET', 'POST'])
@login_required
def jour_ferier_edit(ferier_id=None):

    if ferier_id:
        feriers = Ferier.objects.get(id=ferier_id)
        form = FormFerier(obj=feriers)
    else:
        feriers = Ferier()
        form = FormFerier()

    success = False
    if form.validate_on_submit():
        date_field = datetime.datetime.combine(function.date_convert(form.date.data), datetime.datetime.min.time())
        feriers.date = date_field
        feriers.description = form.description.data

        feriers.save()

        update = False
        if not ferier_id:
            time_zones = pytz.timezone('Africa/Douala')
            date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

            if date_field <= function.datetime_convert(date_auto_nows):
                update = True

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('conge/jour_ferier_edit.html', **locals())


@prefix_param.route('/ferier/delete/<objectid:ferier_id>')
@login_required
def jour_ferier_delete(ferier_id):

    if request.args.get('confirmation'):
        return render_template('conge/jour_ferier_confirnation.html', **locals())

    ferier = Ferier.objects.get(id=ferier_id)
    prest_ferier = Prestation.objects(sigle= 'FER').first()

    # Ensemble des utilisateurs
    all_user = Users.objects(email__ne='admin@accentcom-cm.com')

    day = function.datetime_convert(ferier.date).strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)


    for user in all_user:

        tache_ferier = Tache.objects(Q(prestation_id =prest_ferier.id) & Q(user_id=user.id)).first()

        if tache_ferier:

            the_temps_ferier = Temps.objects(Q(tache_id=tache_ferier.id) & Q(date_start=start) & Q(date_end=end)).first()

            if the_temps_ferier:

                all_detailTemps = DetailTemps.objects(Q(temps_id=the_temps_ferier.id) & Q(date=function.datetime_convert(ferier.date)))

                for detailTemps in all_detailTemps:
                    detailTemps.delete()

                details = DetailTemps.objects(temps_id=the_temps_ferier.id)

                if details:
                    the_temps_ferier.delete()

    ferier.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('ferier.jour_ferier'))


@prefix_param.route('/ferier/tache/refresh')
def jour_ferier_tache():

    # Ensemble des utilisateurs
    all_user = Users.objects(email__ne='admin@accentcom-cm.com')
    prest_ferier = Prestation.objects(sigle='FER').first()

    for user in all_user:

        exist_tache = Tache.objects(Q(prestation_id=prest_ferier.id) & Q(user_id=user.id))

        if not exist_tache:
            tache_conge = Tache()
            tache_conge.titre = 'Tache pour suivre les jours feriers'
            tache_conge.prestation_id = prest_ferier.id
            tache_conge.user_id = user.id
            tache_conge = tache_conge.save()

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    all_jour_ferier = Ferier.objects(
        Q(date__lte=function.datetime_convert(date_auto_nows)) & Q(apply=False)
    )

    for ferier in all_jour_ferier:

        day = ferier.date.strftime('%d/%m/%Y')
        dt = datetime.datetime.strptime(day, '%d/%m/%Y')

        if dt.weekday() < 5:

            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)

            for user in all_user:

                tache = Tache.objects(
                    Q(prestation_id=prest_ferier.id) & Q(user_id=user.id)
                ).first()

                temps = Temps.objects(
                    Q(tache_id=tache.id) & Q(date_start=start) & Q(date_end=end)
                ).first()

                detail_fdt = DetailTemps()
                detail_fdt.date = datetime.datetime.combine(function.date_convert(ferier.date), datetime.datetime.min.time())
                detail_fdt.description = ferier.description
                detail_fdt.heure =  datetime.datetime(2000, 1, 1, 8, 0, 0)

                time = '08:00'
                time = time.split(':')

                conversion = 0.0

                if int(time[0]) > 0:
                    conversion += float(time[0])

                if int(time[1]) > 0:
                    min = float(time[1])/60
                    conversion += min

                detail_fdt.conversion = conversion

                if temps:
                    detail_fdt.temps_id = temps
                else:
                    temps = Temps()
                    temps.user_id = tache.user_id
                    temps.date_start = datetime.datetime.combine(function.date_convert(start), datetime.datetime.min.time())
                    temps.date_end = datetime.datetime.combine(function.date_convert(end), datetime.datetime.min.time())
                    temps.tache_id = tache
                    time = temps.save()
                    detail_fdt.temps_id = time


                ordre = 1
                exist_temps = DetailTemps.objects(
                    Q(temps_id=detail_fdt.temps_id.id)
                )

                if len(exist_temps):
                    ordre += exist_temps

                detail_fdt.ordre = ordre

                detail_fdt.save()

            ferier.apply = True
            ferier.save()

    if request.args.get('return'):
        return redirect(url_for('ferier.jour_ferier'))
    else:
        return render_template('401.html')