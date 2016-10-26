__author__ = 'Ronald'

from ...modules import *
from ..temps.models_temps import Temps, Tache, DetailTemps, DetailFrais, Users
from forms_temps import FormTemps


prefix = Blueprint('temps', __name__)
prefix_tache = Blueprint('temps_tache', __name__)

@prefix.route('/')
@login_required
def index():
    menu = 'temps'
    submenu = ''
    context = ''
    title_page = 'Feuille de temps'

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

    user = Users.objects.get(id=session.get('user_id'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    temps_year = Temps.objects(
        user_id = user.id
    )
    for bud in temps_year:
        year = {}
        year['date'] = bud.date_start.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            if key not in list_year:
                list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    analyse = []
    for detail in temps_year:
        infos = {}
        infos['date_start'] = detail.date_start
        infos['date_end'] = detail.date_end
        analyse.append(infos)

    grouper = itemgetter("date_start", "date_end")

    datas = []
    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["date_start", "date_end"], key))
        datas.append(temp_dict)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='Feuille de temps')

    if len(datas) > 10:
        offset_start = (page - 1) * 10
        offset_end = page * 10
        datas = datas[offset_start:offset_end]

    return render_template('temps/index.html', **locals())


@prefix.route('/periode-details/<date_start>/<date_end>')
@login_required
def view(date_start, date_end):

    date_start = datetime.datetime.combine(function.date_convert(date_start), datetime.datetime.min.time())
    date_end = datetime.datetime.combine(function.date_convert(date_end), datetime.datetime.min.time())

    user = Users.objects.get(id=session.get('user_id'))

    temps_day = DetailTemps.objects()

    analyse = []
    for temps in temps_day:
        if temps.temps_id.date_start == date_start and temps.temps_id.date_end == date_end and temps.temps_id.user_id.id == user.id:
            infos = {}
            infos['identique'] = 1
            infos['date'] = temps.date
            infos['heure'] = temps.heure
            infos['conversion'] = temps.conversion
            analyse.append(infos)

    grouper = itemgetter("date", "identique")

    datas = []
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["date", "identique"], key))
        temp_dict['conversion'] = 0
        temp_dict['heure'] = timedelta(hours=00, minutes=00)
        for item in grp:
            temp_dict['conversion'] += item['conversion']
            temp_dict['heure'] += timedelta(hours=item['conversion'])
        datas.append(temp_dict)

    return render_template('temps/periode_detail.html', **locals())


@prefix.route('/jour-detail/<date>')
@login_required
def view_day(date):

    date = datetime.datetime.combine(function.date_convert(date), datetime.datetime.min.time())

    day = date.strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)

    user = Users.objects.get(id=session.get('user_id'))

    temps_day = DetailTemps.objects(
        date = date
    )

    datas = []
    total = timedelta(hours=00, minutes=00)
    for temps in temps_day:
        if temps.temps_id.user_id.id == user.id:
            infos = {}
            infos['tache'] = temps.temps_id.tache_id.titre
            infos['projet'] = "Aucun"
            if temps.temps_id.tache_id.projet_id :
                infos['projet'] = temps.temps_id.tache_id.projet_id.titre
            infos['details'] = temps.description
            infos['heure'] = temps.heure
            total += timedelta(hours=temps.conversion)
            datas.append(infos)

    return render_template("temps/jour_detail.html", **locals())


@prefix_tache.route('/temps/<objectid:tache_id>')
@login_required
def index(tache_id):

    menu = 'tache'
    submenu = 'tache'
    context = 'fdt'
    title_page = 'Taches - Details - Feuille de temps'

    tache = Tache.objects.get(id=tache_id)

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)


    temps = Temps.objects(
        Q(tache_id= tache.id) & Q(date_start = start) & Q(date_end = end)
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
        count = DetailTemps.objects(temps_id =temps.id).order_by('-date', 'ordre').count()
        datas = DetailTemps.objects(temps_id =temps.id).order_by('-date', 'ordre').skip(offset).limit(limit)
        pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=count, search=search, record_name='Feuille de temps')


    return render_template('temps/temps_tache.html', **locals())


@prefix_tache.route('/temps/edit/<objectid:tache_id>', methods=['GET', 'POST'])
@prefix_tache.route('/temps/edit/<objectid:tache_id>/<objectid:detail_fdt_id>', methods=['GET', 'POST'])
@login_required
def edit(tache_id, detail_fdt_id=None):

    tache = Tache.objects.get(id=tache_id)

    if detail_fdt_id:
        detail_fdt = DetailTemps.objects.get(id=detail_fdt_id)
        form = FormTemps(obj=detail_fdt)
    else:
        detail_fdt = DetailTemps()
        form = FormTemps()

    success = False
    if form.validate_on_submit():
        day = datetime.date.today().strftime('%d/%m/%Y')
        dt = datetime.datetime.strptime(day, '%d/%m/%Y')
        start = dt - timedelta(days=dt.weekday())
        end = start + timedelta(days=6)


        temps = Temps.objects(
            Q(tache_id = tache.id) & Q(date_start = start) & Q(date_end = end)
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
            detail_fdt.temps_id = temps
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
                temps_id = detail_fdt.temps_id.id
            )

            if len(exist_temps):
                ordre += len(exist_temps)

            detail_fdt.ordre = ordre

        detail_fdt.save()

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('temps/temps_tache_edit.html', **locals())


@prefix_tache.route('/temps/delete/<objectid:detail_fdt_id>')
@login_required
def delete(detail_fdt_id):

    # information du details de la FDT
    details_temps = DetailTemps.objects.get(id=detail_fdt_id)

    # Recuperation des details taches correspondant a la meme FDT de la tache a supprimer
    temps_details_count = DetailTemps.objects(
        Q(temps_id=details_temps.temps_id.id) & Q(id__ne=details_temps.id)
    )

    # Recuperation des detaisl frais correspondant a la meme FDT de la tache a supprimer
    frais_temps_count = DetailFrais.objects(
        temps_id=details_temps.temps_id.id
    )

    # id de la feuille de temps de la semaine
    temps_id = details_temps.temps_id.id

    # id de la tache de la semaine
    tache_id = details_temps.temps_id.tache_id.id

    # Si il n'existe plus de details temps correspondant a la FDT de la semaine, on le supprime.
    if not temps_details_count and not frais_temps_count:
        temps = Temps.objects.get(id=temps_id)
        temps.delete()
    #
    details_temps.delete()
    flash('Suppression reussie', 'success')

    if request.args.get('conge'):

        if request.args.get('conge') == '1':
            return redirect(url_for('conge.temps_absence', prestation_id=tache_id.user_id.id))
        elif request.args.get('conge') == '2':
            return redirect(url_for('conge.temps_conge', prestation_id=tache_id.user_id.id))

    else:
        return redirect(url_for('temps_tache.index', tache_id=tache_id))

    # return render_template('index/test.html', **locals())


@prefix_tache.route('/historique/<objectid:tache_id>')
@login_required
def historique(tache_id):

    menu = 'tache'
    submenu = 'tache'
    context = 'historique'
    title_page = 'Taches - Details - Feuille de temps - Historique'

    tache = Tache.objects.get(id=tache_id)

    temps_tache = Temps.objects(
        tache_id=tache.id
    ).order_by('-date_start')

    datas = []
    for temps in temps_tache:
        details = DetailTemps.objects(
            temps_id = temps.id
        ).order_by('-date','ordre')
        for detail in details:
            datas.append(detail)


    return render_template('temps/historique.html', **locals())

