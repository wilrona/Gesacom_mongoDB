__author__ = 'Ronald'

from ...modules import *
from ..temps.models_temps import Temps, Tache, DetailTemps, DetailFrais, Users
from forms_temps import FormTemps

prefix_tache_breack = Blueprint('temps_tache_breack', __name__)


@prefix_tache_breack.route('/break')
@prefix_tache_breack.route('/break/<objectid:tache_id>/<objectid:tache_temps_id>')
@login_required
def temps_breack(tache_id=None, tache_temps_id=None):

    title_page = 'Taches - breack'

    if request.args.get('tache'):
        tache_id = request.args.get('tache')
        the_tache = Tache.objects.get(id=tache_id)
        tache_id = the_tache.id

    user = Users.objects.get(id=session.get('user_id'))

    tache_user = Tache.objects(
        Q(user_id=user.id) & Q(end=False)
    )

    tache_group = []
    for t_user in tache_user:
        data = {}
        if t_user.projet_id:
            data['projet'] = t_user.projet_id.titre
            data['projet_code'] = t_user.projet_id.code
        else:
            data['projet'] = 'Classe'
            data['projet_code'] = 'Non'
        data['tache'] = t_user.titre
        data['tache_id'] = t_user.id
        tache_group.append(data)

    grouper = itemgetter("projet", "projet_code")
    tache_users = []
    for key, grp in groupby(sorted(tache_group, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["projet", "projet_code"], key))
        temp_dict['taches'] = []
        for item in grp:
            data = {
                'tache_id': item['tache_id'],
                'tache': item['tache']
            }
            temp_dict['taches'].append(data)
        tache_users.append(temp_dict)

    details_tache = []
    temps_tache = []

    if tache_id:

        current_tache = Tache.objects.get(id=tache_id)

        temps_taches = Temps.objects(
            tache_id=current_tache.id
        )

        analyse = []
        for detail in temps_taches:
            infos = {}
            infos['date_start'] = detail.date_start
            infos['date_end'] = detail.date_end
            infos['id_temps'] = detail.id
            analyse.append(infos)

        grouper = itemgetter("date_start", "date_end")

        for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
            temp_dict = dict(zip(["date_start", "date_end"], key))
            for item in grp:
                temp_dict['id_temps'] = item['id_temps']
            temps_tache.append(temp_dict)

        if tache_temps_id:

            current_temps = Temps.objects.get(id=tache_temps_id)

            details_tache = DetailTemps.objects(
                temps_id= current_temps.id
            ).order_by("-date", "ordre")

    return render_template("temps/temps_tache_break.html", **locals())


@prefix_tache_breack.route('/break/edit', methods=['GET', 'POST'])
@prefix_tache_breack.route('/break/edit/<objectid:tache_id>', methods=['GET', 'POST'])
@prefix_tache_breack.route('/break/edit/<objectid:tache_id>/<objectid:temps_id>', methods=['GET', 'POST'])
@prefix_tache_breack.route('/break/edit/<objectid:tache_id>/<objectid:temps_id>/<objectid:detail_fdt_id>', methods=['GET', 'POST'])
@login_required
def temps_breack_edit(tache_id, temps_id=None, detail_fdt_id=None):

    tache = Tache.objects.get(id=tache_id)

    if detail_fdt_id:
        detail_fdt = DetailTemps.objects.get(id=detail_fdt_id)
        form = FormTemps(obj=detail_fdt)
        form.derob.data = 1
    else:
        detail_fdt = DetailTemps()
        form = FormTemps()
        form.derob.data = 1

    success = False
    if form.validate_on_submit():

        day = function.datetime_convert(form.date.data).strftime('%d/%m/%Y')
        dt = datetime.datetime.strptime(day, '%d/%m/%Y')
        start = dt - timedelta(days=dt.weekday())
        end = start + timedelta(days=6)

        detail_fdt.date = datetime.datetime.combine(function.datetime_convert(form.date.data), datetime.datetime.min.time())
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

        start_temps = datetime.datetime.combine(function.date_convert(start), datetime.datetime.min.time())
        end_temps = datetime.datetime.combine(function.date_convert(end), datetime.datetime.min.time())

        temps = Temps.query(
            Q(tache_id=tache.id) & Q(date_start=start_temps) & Q(date_end=end_temps)
        ).first()


        if temps:
            if not temps_id:
                detail_fdt.temps_id = temps.id
                temps_id = temps.id
            else:
                temps_send = Temps.objects.get(id=temps_id)

                if temps.id == temps_send.id:
                    detail_fdt.temps_id = temps_send
                    temps_id = temps_send.id
                else:
                    temps = Temps()
                    temps.user_id = tache.user_id
                    temps.date_start = datetime.datetime.combine(function.date_convert(start), datetime.datetime.min.time())
                    temps.date_end = datetime.datetime.combine(function.date_convert(end), datetime.datetime.min.time())
                    temps.tache_id = tache
                    item = temps.save()
                    detail_fdt.temps_id = item
                    temps_id = item
        else:
            temps = Temps()
            temps.user_id = tache.user_id
            temps.date_start = datetime.datetime.combine(function.date_convert(start), datetime.datetime.min.time())
            temps.date_end = datetime.datetime.combine(function.date_convert(end), datetime.datetime.min.time())
            temps.tache_id = tache
            item = temps.save()
            detail_fdt.temps_id = item
            temps_id = item

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

    return render_template('temps/temps_tache_break_edit.html', **locals())


@prefix_tache_breack.route('/break/tache/delete/<objectid:tache_id>/<objectid:temps_id>/<objectid:detail_fdt_id>')
@login_required
def tache_breack_delete(tache_id, temps_id, detail_fdt_id):

    # information du details de la FDT
    details_temps = DetailTemps.objects.get(id=detail_fdt_id)

    # Recuperation des details taches correspondant a la meme FDT de la tache a supprimer
    temps_details_count = DetailTemps.objects(
        Q(temps_id=details_temps.temps_id.id) & Q(id__ne=details_temps.id)
    )

    # Recuperation des detaisl frais correspondant a la meme FDT de la tache a supprimer
    frais_temps_count = DetailFrais.objects(
        temps_id = details_temps.temps_id.id
    )

    # id de la feuille de temps de la semaine
    # temps_id = details_temps.temps_id.get().key.id()

    # Si il n'existe plus de details temps correspondant a la FDT de la semaine, on le supprime.
    if not len(temps_details_count) and not len(frais_temps_count):
        temps = Temps.objects.get(id=temps_id)
        temps.delete()
        temps_id = None
    #
    details_temps.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('temps_tache_breack.temps_breack', tache_id=tache_id, tache_temps_id=temps_id))