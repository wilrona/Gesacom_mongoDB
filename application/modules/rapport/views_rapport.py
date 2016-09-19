__author__ = 'Ronald'

from ...modules import *
from ..temps.models_temps import DetailTemps, Users, Tache
from ..budget.models_budget import Budget, BudgetPrestation, Prestation, Client
from ..conge.models_conge import Ferier

prefix = Blueprint('stat', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'stat')])
def index():
    menu = 'stat'
    submenu = ''
    context = 'list'
    title_page = 'Statistique et rapport'

    # Algorithme pour les dates qui se trouvent dans les details pour les filtres
    # for bud in temps_year:
    #     year = {}
    #     year['date'] = bud.date.year
    #     years.append(year)
    #
    # list_year = []
    # for key, group in groupby(years, lambda item: item["date"]):
    #     if key != now_year:
    #         if key not in list_year:
    #             list_year.append(key)
    #
    # for i in range(now_year, now_year+2):
    #     if i not in list_year:
    #         list_year.append(i)

    return render_template('rapport/index.html', **locals())


@prefix.route('/collaborateur')
@login_required
@roles_required([('super_admin', 'stat')])
def collaborateur():
    menu = 'stat'
    submenu = 'collaborateur'
    title_page = 'Remplissage des feuilles du temps par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    current_day = datetime.datetime.now(time_zones)
    now_year = datetime.datetime.now(time_zones).year
    First_day_of_year = datetime.date(now_year, 1, 1)


    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')       
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(First_day_of_year, current_day):
                current_sigle = detail.temps_id.tache_id.prestation_id.sigle
                if current_sigle == 'CONG':
                    if detail.parent:
                        have = True
                        infos = {}
                        infos['user'] = user
                        infos['user_id'] = user.id
                        infos['user_infos'] = 1
                        infos['prestation'] = current_sigle
                        if detail.temps_id.tache_id.facturable:
                            infos['facturable'] = 1
                        else:
                            infos['facturable'] = 0

                        infos['time'] = round(detail.conversion, 1)
                        analyse.append(infos)
                else:
                    have = True
                    infos = {}
                    infos['user'] = user
                    infos['user_id'] = user.id
                    infos['user_infos'] = 1
                    infos['prestation'] = current_sigle
                    if detail.temps_id.tache_id.facturable:
                        infos['facturable'] = 1
                    else:
                        infos['facturable'] = 0

                    infos['time'] = round(detail.conversion, 1)
                    analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['user_infos'] = 1
            infos['prestation'] = 'RIEN'
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)


    jour_ferier = [date.date for date in Ferier.objects(Q(apply=True) & Q(date__gte=function.get_first_day(First_day_of_year)) & Q(date__lte=current_day))]

    Nbr_jr_passe = function.networkdays(datetime.datetime.combine(function.get_first_day(First_day_of_year), datetime.datetime.min.time()), datetime.datetime.combine(current_day, datetime.datetime.min.time()), jour_ferier)
    Nbr_heure_passe = Nbr_jr_passe*8


    grouper = itemgetter("user_id", "user")

    # REGROUPEMENT DES MONTANTS PAR DESTINATION
    analyses = []

    total_abs = 0
    total_cong = 0
    total_fer = 0

    total_dev = 0
    total_adm = 0
    total_form = 0
    total_prod_fact = 0
    total_prod_nfact = 0
    total_h_ncharge = 0
    total = 0
    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))
        temp_dict['dev_time'] = 0.0
        temp_dict['form_time'] = 0.0
        temp_dict['prod_time_fact'] = 0.0
        temp_dict['prod_time_nfact'] = 0.0
        temp_dict['adm_time'] = 0.0

        temp_dict['abs_time'] = 0.0
        temp_dict['cong_time'] = 0.0
        temp_dict['fer_time'] = 0.0

        temp_dict['total'] = 0.0


        abs_tot = 0.0
        cong_tot = 0.0
        fer_tot = 0.0

        dev_tot = 0.0
        adm_tot = 0.0
        prod_tot_fact = 0.0
        prod_tot_nfact = 0.0
        form_tot = 0.0
        for item in grp:
            if item['prestation'] == 'DEV':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']

            if item['prestation'] == 'FOR':
                temp_dict['form_time'] += item['time']
                form_tot += item['time']

            if item['prestation'] == 'ADM':
                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']

            if item['prestation'] == 'ABS':
                temp_dict['abs_time'] += item['time']
                abs_tot += item['time']

            if item['prestation'] == 'CONG':
                temp_dict['cong_time'] += item['time']
                cong_tot += item['time']

            if item['prestation'] == 'FER':
                temp_dict['fer_time'] += item['time']
                fer_tot += item['time']

            if item['prestation'] == 'PRO' and item['facturable']:
                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']

            if item['prestation'] == 'PRO' and not item['facturable']:
                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']

            if item['prestation'] == 'RIEN':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']

                temp_dict['form_time'] += item['time']
                form_tot += item['time']

                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']

                temp_dict['abs_time'] += item['time']
                abs_tot += item['time']

                temp_dict['cong_time'] += item['time']
                cong_tot += item['time']

                temp_dict['fer_time'] += item['time']
                fer_tot += item['time']

                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']

                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']


        temp_dict['total'] = temp_dict['prod_time_nfact']
        temp_dict['total'] += temp_dict['prod_time_fact']
        temp_dict['total'] += temp_dict['dev_time']
        temp_dict['total'] += temp_dict['adm_time']
        temp_dict['total'] += temp_dict['form_time']

        temp_dict['total'] += temp_dict['abs_time']
        temp_dict['total'] += temp_dict['cong_time']
        temp_dict['total'] += temp_dict['fer_time']

        total_budg = 0
        total_budg = temp_dict['prod_time_nfact']
        total_budg += temp_dict['prod_time_fact']
        total_budg += temp_dict['dev_time']
        total_budg += temp_dict['adm_time']
        total_budg += temp_dict['form_time']
        total_budg += temp_dict['abs_time']
        total_budg += temp_dict['cong_time']

        temp_dict['H_NCharge'] = Nbr_heure_passe - total_budg
        temp_dict['total'] += temp_dict['H_NCharge']

        total_dev += dev_tot
        total_adm += adm_tot
        total_prod_fact += prod_tot_fact
        total_prod_nfact += prod_tot_nfact
        total_form += form_tot

        total_abs += abs_tot
        total_cong += cong_tot
        total_fer += fer_tot

        total_h_ncharge += temp_dict['H_NCharge']

        total += temp_dict['total']
        total += total_h_ncharge

        analyses.append(temp_dict)

    return render_template('rapport/collaborateur.html', **locals())


@prefix.route('/collaborateur/refresh', methods=['GET','POST'])
def collaborateur_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))

    printer = request.args.get('print')
    title_page = 'Remplissage des feuilles du temps par collaborateur'

    # time_zones = pytz.timezone('Africa/Douala')
    # current_month = datetime.datetime.now(time_zones).month
    # current_day = datetime.datetime.now(time_zones)

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            current_sigle = detail.temps_id.tache_id.prestation_id.sigle
            if current_sigle == 'CONG':
                if detail.parent:
                    have = True
                    infos = {}
                    infos['user'] = user
                    infos['user_id'] = user.id
                    infos['user_infos'] = 1
                    infos['prestation'] = current_sigle
                    if detail.temps_id.tache_id.facturable:
                        infos['facturable'] = 1
                    else:
                        infos['facturable'] = 0

                    infos['time'] = round(detail.conversion, 1)
                    analyse.append(infos)
            else:
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['user_infos'] = 1
                infos['prestation'] = current_sigle
                if detail.temps_id.tache_id.facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0

                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['user_infos'] = 1
            infos['prestation'] = 'RIEN'
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)

    jour_ferier = [date.date for date in Ferier.objects(Q(apply=True) & Q(date__gte=date_start) & Q(date__lte=date_end))]

    Nbr_jr_passe = function.networkdays(datetime.datetime.combine(date_start, datetime.datetime.min.time()), datetime.datetime.combine(date_end, datetime.datetime.min.time()), jour_ferier)
    Nbr_heure_passe = Nbr_jr_passe*8


    grouper = itemgetter("user_id", "user")

    # REGROUPEMENT DES MONTANTS PAR DESTINATION
    analyses = []

    total_abs = 0
    total_cong = 0
    total_fer = 0

    total_dev = 0
    total_adm = 0
    total_form = 0
    total_prod_fact = 0
    total_prod_nfact = 0
    total_h_ncharge = 0
    total = 0
    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))
        temp_dict['dev_time'] = 0.0
        temp_dict['form_time'] = 0.0
        temp_dict['prod_time_fact'] = 0.0
        temp_dict['prod_time_nfact'] = 0.0
        temp_dict['adm_time'] = 0.0

        temp_dict['abs_time'] = 0.0
        temp_dict['cong_time'] = 0.0
        temp_dict['fer_time'] = 0.0

        temp_dict['total'] = 0.0


        abs_tot = 0.0
        cong_tot = 0.0
        fer_tot = 0.0

        dev_tot = 0.0
        adm_tot = 0.0
        prod_tot_fact = 0.0
        prod_tot_nfact = 0.0
        form_tot = 0.0
        for item in grp:
            if item['prestation'] == 'DEV':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']

            if item['prestation'] == 'FOR':
                temp_dict['form_time'] += item['time']
                form_tot += item['time']

            if item['prestation'] == 'ADM':
                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']

            if item['prestation'] == 'ABS':
                temp_dict['abs_time'] += item['time']
                abs_tot += item['time']

            if item['prestation'] == 'CONG':
                temp_dict['cong_time'] += item['time']
                cong_tot += item['time']

            if item['prestation'] == 'FER':
                temp_dict['fer_time'] += item['time']
                fer_tot += item['time']

            if item['prestation'] == 'PRO' and item['facturable']:
                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']

            if item['prestation'] == 'PRO' and not item['facturable']:
                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']

            if item['prestation'] == 'RIEN':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']

                temp_dict['form_time'] += item['time']
                form_tot += item['time']

                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']

                temp_dict['abs_time'] += item['time']
                abs_tot += item['time']

                temp_dict['cong_time'] += item['time']
                cong_tot += item['time']

                temp_dict['fer_time'] += item['time']
                fer_tot += item['time']

                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']

                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']



        temp_dict['total'] = temp_dict['prod_time_nfact']
        temp_dict['total'] += temp_dict['prod_time_fact']
        temp_dict['total'] += temp_dict['dev_time']
        temp_dict['total'] += temp_dict['adm_time']
        temp_dict['total'] += temp_dict['form_time']

        temp_dict['total'] += temp_dict['abs_time']
        temp_dict['total'] += temp_dict['cong_time']
        temp_dict['total'] += temp_dict['fer_time']

        total_budg = 0
        total_budg = temp_dict['prod_time_nfact']
        total_budg += temp_dict['prod_time_fact']
        total_budg += temp_dict['dev_time']
        total_budg += temp_dict['adm_time']
        total_budg += temp_dict['form_time']
        total_budg += temp_dict['abs_time']
        total_budg += temp_dict['cong_time']

        temp_dict['H_NCharge'] = Nbr_heure_passe - total_budg
        temp_dict['total'] += temp_dict['H_NCharge']

        total_dev += dev_tot
        total_adm += adm_tot
        total_prod_fact += prod_tot_fact
        total_prod_nfact += prod_tot_nfact
        total_form += form_tot

        total_abs += abs_tot
        total_cong += cong_tot
        total_fer += fer_tot

        total_h_ncharge += temp_dict['H_NCharge']

        total += temp_dict['total']
        total += total_h_ncharge

        analyses.append(temp_dict)

    return render_template('rapport/collaborateur_refresh.html', **locals())


@prefix.route('/collaborateur/feuille_de_temps_par_collaborateur')
def collaborateur_export_excel():

    date_start = function.date_convert(request.args.get('date_start'))
    date_end = function.date_convert(request.args.get('date_end'))

    title_page = 'Remplissage des feuilles du temps par collaborateur'

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')            
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            current_sigle = detail.temps_id.tache_id.prestation_id.sigle
            if current_sigle == 'CONG':
                if detail.parent:
                    have = True
                    infos = {}
                    infos['user'] = user
                    infos['user_id'] = user.id
                    infos['user_infos'] = 1
                    infos['prestation'] = current_sigle
                    if detail.temps_id.tache_id.facturable:
                        infos['facturable'] = 1
                    else:
                        infos['facturable'] = 0

                    infos['time'] = round(detail.conversion, 1)
                    analyse.append(infos)
            else:
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['user_infos'] = 1
                infos['prestation'] = current_sigle
                if detail.temps_id.tache_id.facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0

                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['user_infos'] = 1
            infos['prestation'] = 'RIEN'
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)

    jour_ferier = [date.date for date in Ferier.objects(Q(apply=True) & Q(date__gte=date_start) & Q(date__lte=date_end))]

    Nbr_jr_passe = function.networkdays(datetime.datetime.combine(date_start, datetime.datetime.min.time()), datetime.datetime.combine(date_end, datetime.datetime.min.time()), jour_ferier)
    Nbr_heure_passe = Nbr_jr_passe*8


    grouper = itemgetter("user_id", "user")

    # REGROUPEMENT DES MONTANTS PAR DESTINATION
    analyses = []

    total_abs = 0
    total_cong = 0
    total_fer = 0

    total_dev = 0
    total_adm = 0
    total_form = 0
    total_prod_fact = 0
    total_prod_nfact = 0
    total_h_ncharge = 0
    total = 0
    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))
        temp_dict['dev_time'] = 0
        temp_dict['form_time'] = 0
        temp_dict['prod_time_fact'] = 0
        temp_dict['prod_time_nfact'] = 0
        temp_dict['adm_time'] = 0

        temp_dict['abs_time'] = 0
        temp_dict['cong_time'] = 0
        temp_dict['fer_time'] = 0

        temp_dict['total'] = 0


        abs_tot = 0
        cong_tot = 0
        fer_tot = 0

        dev_tot = 0
        adm_tot = 0
        prod_tot_fact = 0
        prod_tot_nfact = 0
        form_tot = 0
        for item in grp:
            if item['prestation'] == 'DEV':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']

            if item['prestation'] == 'FOR':
                temp_dict['form_time'] += item['time']
                form_tot += item['time']

            if item['prestation'] == 'ADM':
                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']

            if item['prestation'] == 'ABS':
                temp_dict['abs_time'] += item['time']
                abs_tot += item['time']

            if item['prestation'] == 'CONG':
                temp_dict['cong_time'] += item['time']
                cong_tot += item['time']

            if item['prestation'] == 'FER':
                temp_dict['fer_time'] += item['time']
                fer_tot += item['time']

            if item['prestation'] == 'PRO' and item['facturable']:
                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']

            if item['prestation'] == 'PRO' and not item['facturable']:
                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']

            if item['prestation'] == 'RIEN':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']

                temp_dict['form_time'] += item['time']
                form_tot += item['time']

                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']

                temp_dict['abs_time'] += item['time']
                abs_tot += item['time']

                temp_dict['cong_time'] += item['time']
                cong_tot += item['time']

                temp_dict['fer_time'] += item['time']
                fer_tot += item['time']

                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']

                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']


        temp_dict['total'] = temp_dict['prod_time_nfact']
        temp_dict['total'] += temp_dict['prod_time_fact']
        temp_dict['total'] += temp_dict['dev_time']
        temp_dict['total'] += temp_dict['adm_time']
        temp_dict['total'] += temp_dict['form_time']

        temp_dict['total'] += temp_dict['abs_time']
        temp_dict['total'] += temp_dict['cong_time']
        temp_dict['total'] += temp_dict['fer_time']

        total_budg = 0
        total_budg = temp_dict['prod_time_nfact']
        total_budg += temp_dict['prod_time_fact']
        total_budg += temp_dict['dev_time']
        total_budg += temp_dict['adm_time']
        total_budg += temp_dict['form_time']
        total_budg += temp_dict['abs_time']
        total_budg += temp_dict['cong_time']

        temp_dict['H_NCharge'] = Nbr_heure_passe - total_budg
        temp_dict['total'] += temp_dict['H_NCharge']

        total_dev += dev_tot
        total_adm += adm_tot
        total_prod_fact += prod_tot_fact
        total_prod_nfact += prod_tot_nfact
        total_form += form_tot

        total_abs += abs_tot
        total_cong += cong_tot
        total_fer += fer_tot

        total_h_ncharge += temp_dict['H_NCharge']

        total += temp_dict['total']
        total += total_h_ncharge

        analyses.append(temp_dict)

    workbook = Workbook()
    sheet = workbook.add_sheet('FDT par collaborateur')

    fnt = Font()
    fnt.height = 16*20
    fnt.bold = True
    style = XFStyle()
    style.font = fnt
    sheet.row(0).set_style(style)
    sheet.row(2).set_style(style)

    style_string = "font: height 320, bold on;"
    style_string_2 = "font: bold on; borders: bottom dashed; align: wrap 1;"
    style_string_3 = "align: wrap 1;"
    style = easyxf(style_string)
    style_2 = easyxf(style_string_2)
    style_3 = easyxf(style_string_3)

    sheet.write(0, 0, title_page, style)

    sheet.write(2, 0, 'Periode du '+str(function.format_date(date_start,'%d/%m/%Y'))+' au '+str(function.format_date(date_end,'%d/%m/%Y'))+'', style)

    sheet.write(3, 0, 'Collaborateur', style_2)
    sheet.write(3, 1, 'Absence', style_2)
    sheet.write(3, 2, 'Conge', style_2)
    sheet.write(3, 3, 'Ferier', style_2)
    sheet.write(3, 4, 'Admin.', style_2)
    sheet.write(3, 5, 'Formation', style_2)
    sheet.write(3, 6, 'Develop.', style_2)
    sheet.write(3, 7, 'Prod. Nfact', style_2)
    sheet.write(3, 8, 'Prod. fact', style_2)
    sheet.write(3, 9, 'H. Non chargee', style_2)
    sheet.write(3, 10, 'Total', style_2)

    start = 4
    for datas in analyses:
        sheet.write(start, 0, datas['user'].last_name+" "+datas['user'].first_name, style_3)
        sheet.write(start, 1, datas['abs_time'], style_3)
        sheet.write(start, 2, datas['cong_time'], style_3)
        sheet.write(start, 3, datas['fer_time'], style_3)
        sheet.write(start, 4, datas['adm_time'], style_3)
        sheet.write(start, 5, datas['form_time'], style_3)
        sheet.write(start, 6, datas['dev_time'], style_3)
        sheet.write(start, 7, datas['prod_time_nfact'], style_3)
        sheet.write(start, 8, datas['prod_time_fact'], style_3)
        sheet.write(start, 9, datas['H_NCharge'], style_3)
        sheet.write(start, 10, datas['total'], style_3)
        start += 1

    sheet.write(start, 0, 'Total', style_2)
    sheet.write(start, 1, total_abs, style_2)
    sheet.write(start, 2, total_cong, style_2)
    sheet.write(start, 3, total_fer, style_2)
    sheet.write(start, 4, total_adm, style_2)
    sheet.write(start, 5, total_form, style_2)
    sheet.write(start, 6, total_dev, style_2)
    sheet.write(start, 7, total_prod_nfact, style_2)
    sheet.write(start, 8, total_prod_fact, style_2)
    sheet.write(start, 9, total_h_ncharge, style_2)
    sheet.write(start, 10, total, style_2)

    out = StringIO()
    workbook.save(out)

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response


@prefix.route('/taux-chargeabilite-heure-production')
@login_required
@roles_required([('super_admin', 'stat')])
def taux_HProd():
    menu = 'stat'
    submenu = 'taux_HProd'
    title_page = 'Taux du chargeabilite des heures du production'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')        
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(First_day_of_year, current_day):
            if detail.temps_id.tache_id.prestation_id.sigle == 'PRO':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                if detail.temps_id.tache_id.facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")


    analyses = []
    total_bud = 0.0
    total_HP_charge = 0.0
    total_HP_fact = 0.0
    total_pourc_c = 0.0
    total__budget = 0.0
    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=First_day_of_year)
        ).first()

        if budget:

            prest_prod = Prestation.objects(
                sigle='PRO'
            ).first()

            budget_prod = BudgetPrestation.objects(
                Q(budget_id=budget.id) & Q(prestation_id=prest_prod.id)
            ).first()

            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == current_day.year:
                Nbre_Days_start = function.networkdays(
                        function.date_convert(function.get_first_day(First_day_of_year)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )

                Nbre_current_day = function.networkdays(
                    function.date_convert(temp_dict['user'].date_start),
                    function.date_convert(current_day),
                    [],
                    ()
                )

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur
                production = Nbre_days_reste * budget_prod.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste
            else:

                Nbre_current_day = function.networkdays(
                    function.date_convert(function.get_first_day(First_day_of_year)),
                    function.date_convert(current_day),
                    [],
                    ()
                )
                current_heure = budget_prod.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)
            temp_dict['HProd_Charg'] = 0.0
            temp_dict['HProd_Fact'] = 0.0

            HProd_Charg = 0.0
            HProd_Fact = 0.0

            for item in grp:
                temp_dict['HProd_Charg'] += item['time']
                HProd_Charg += item['time']
                if item['facturable']:
                    temp_dict['HProd_Fact'] += item['time']
                    HProd_Fact += item['time']

            temp_dict['Pourc_Charg'] = 0.0
            if temp_dict['HProd_Charg']:
                temp_dict['Pourc_Charg'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['HProd_Charg'], 1)

            temp_dict['Pourc_Bubget'] = 0.0
            if temp_dict['budget']:
                temp_dict['Pourc_Bubget'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['budget'], 1)
            temp_dict['ecart'] = round((temp_dict['Pourc_Charg'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HP_charge += round(HProd_Charg, 1)
            total_HP_fact += round(HProd_Fact, 1)
            if total_HP_charge:
                total_pourc_c = round((total_HP_fact * 100)/total_HP_charge, 1)
            if total_bud:
                total__budget = round((total_HP_fact*100)/total_bud, 1)

            analyses.append(temp_dict)

    return render_template('rapport/taux_heure_production.html', **locals())


@prefix.route('/taux-chargeabilite-heure-production/refresh', methods=['GET','POST'])
def taux_HProd_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Taux du chargeabilite des heures du production'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle == 'PRO':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                if detail.temps_id.tache_id.facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_bud = 0.0
    total_HP_charge = 0.0
    total_HP_fact = 0.0
    total_pourc_c = 0.0
    total__budget = 0.0
    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):

        temp_dict = dict(zip(["user_id", "user"], key))
        date_query = datetime.datetime.combine(datetime.date(now_year, 1, 1), datetime.datetime.min.time())

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=date_query)
        ).first()

        if budget:

            prest_prod = Prestation.objects(sigle='PRO').first()

            budget_prod = BudgetPrestation.objects(
                Q(budget_id=budget.id) & Q(prestation_id=prest_prod.id)
            ).first()

            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == now_year:

                Nbre_Days_start = function.networkdays(
                        function.date_convert(datetime.date(now_year, 1, 1)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )
                if datetime.datetime.combine(date_start, datetime.datetime.min.time()) > temp_dict['user'].date_start:

                    Nbre_current_day = function.networkdays(
                        function.date_convert(date_start),
                        function.date_convert(date_end),
                        [],
                        ()
                    )
                else:
                    if datetime.datetime.combine(date_end, datetime.datetime.min.time()) > temp_dict['user'].date_start:
                        Nbre_current_day = function.networkdays(
                            function.date_convert(temp_dict['user'].date_start),
                            function.date_convert(date_end),
                            [],
                            ()
                        )
                    else:
                        Nbre_current_day = 0

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur au proratat
                production = Nbre_days_reste * budget_prod.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste

            else:

                Nbre_current_day = function.networkdays(
                    date_start,
                    date_end,
                    [],
                    ()
                )
                current_heure = budget_prod.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)
            temp_dict['HProd_Charg'] = 0.0
            temp_dict['HProd_Fact'] = 0.0

            HProd_Charg = 0.0
            HProd_Fact = 0.0

            for item in grp:
                temp_dict['HProd_Charg'] += item['time']
                HProd_Charg += item['time']
                if item['facturable']:
                    temp_dict['HProd_Fact'] += item['time']
                    HProd_Fact += item['time']

            temp_dict['Pourc_Charg'] = 0.0
            if temp_dict['HProd_Charg']:
                temp_dict['Pourc_Charg'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['HProd_Charg'], 1)

            temp_dict['Pourc_Bubget'] = 0.0
            if temp_dict['budget']:
                temp_dict['Pourc_Bubget'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['budget'], 1)
            temp_dict['ecart'] = round((temp_dict['Pourc_Charg'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HP_charge += round(HProd_Charg, 1)
            total_HP_fact += round(HProd_Fact, 1)
            if total_HP_charge:
                total_pourc_c = round((total_HP_fact * 100)/total_HP_charge, 1)
            if total_bud:
                total__budget = round((total_HP_fact*100)/total_bud, 1)

            analyses.append(temp_dict)

    return render_template('rapport/taux_heure_production_refresh.html', **locals())


@prefix.route('/collaborateur/taux_de_chargeabilite_heure_de_production')
def taux_HProd_export_excel():

    date_start = function.date_convert(request.args.get('date_start'))
    date_end = function.date_convert(request.args.get('date_end'))

    title_page = 'Taux du chargeabilite des heures du production'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') &  Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle == 'PRO':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                if detail.temps_id.tache_id.facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_bud = 0.0
    total_HP_charge = 0.0
    total_HP_fact = 0.0
    total_pourc_c = 0.0
    total__budget = 0.0
    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        if budget:

            prest_prod = Prestation.objects(
                sigle='PRO'
            ).first()

            budget_prod = BudgetPrestation.objects(
                Q(budget_id=budget.id) & Q(prestation_id=prest_prod.id)
            ).first()

            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == now_year:

                Nbre_Days_start = function.networkdays(
                        function.date_convert(datetime.date(now_year, 1, 1)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )
                if datetime.datetime.combine(date_start, datetime.datetime.min.time()) > temp_dict['user'].date_start:

                    Nbre_current_day = function.networkdays(
                        function.date_convert(date_start),
                        function.date_convert(date_end),
                        [],
                        ()
                    )
                else:
                    if datetime.datetime.combine(date_end, datetime.datetime.min.time()) > temp_dict['user'].date_start:
                        Nbre_current_day = function.networkdays(
                            function.date_convert(temp_dict['user'].date_start),
                            function.date_convert(date_end),
                            [],
                            ()
                        )
                    else:
                        Nbre_current_day = 0

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur au proratat
                production = Nbre_days_reste * budget_prod.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste

            else:

                Nbre_current_day = function.networkdays(
                    date_start,
                    date_end,
                    [],
                    ()
                )
                current_heure = budget_prod.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)
            temp_dict['HProd_Charg'] = 0.0
            temp_dict['HProd_Fact'] = 0.0

            HProd_Charg = 0.0
            HProd_Fact = 0.0

            for item in grp:
                temp_dict['HProd_Charg'] += item['time']
                HProd_Charg += item['time']
                if item['facturable']:
                    temp_dict['HProd_Fact'] += item['time']
                    HProd_Fact += item['time']

            temp_dict['Pourc_Charg'] = 0.0
            if temp_dict['HProd_Charg']:
                temp_dict['Pourc_Charg'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['HProd_Charg'], 1)

            temp_dict['Pourc_Bubget'] = 0.0
            if temp_dict['budget']:
                temp_dict['Pourc_Bubget'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['budget'], 1)
            temp_dict['ecart'] = round((temp_dict['Pourc_Charg'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HP_charge += round(HProd_Charg, 1)
            total_HP_fact += round(HProd_Fact, 1)
            if total_HP_charge:
                total_pourc_c = round((total_HP_fact * 100)/total_HP_charge, 1)
            if total_bud:
                total__budget = round((total_HP_fact*100)/total_bud, 1)

            analyses.append(temp_dict)

    workbook = Workbook()
    sheet = workbook.add_sheet('Taux Heures de production')

    fnt = Font()
    fnt.height = 16*20
    fnt.bold = True
    style = XFStyle()
    style.font = fnt
    sheet.row(0).set_style(style)
    sheet.row(2).set_style(style)

    style_string = "font: height 320, bold on;"
    style_string_2 = "font: bold on; borders: bottom dashed; align: wrap 1;"
    style_string_3 = "align: wrap 1;"
    style = easyxf(style_string)
    style_2 = easyxf(style_string_2)
    style_3 = easyxf(style_string_3)

    sheet.write(0, 0, title_page, style)

    sheet.write(2, 0, 'Periode du '+str(function.format_date(date_start,'%d/%m/%Y'))+' au '+str(function.format_date(date_end,'%d/%m/%Y'))+'', style)

    sheet.write(3, 0, 'Collaborateur', style_2)
    sheet.write(3, 1, 'Budget Prod', style_2)
    sheet.write(3, 2, 'H. Prod Chargee', style_2)
    sheet.write(3, 3, 'H. Prod Facturee', style_2)
    sheet.write(3, 4, '% heure chargees', style_2)
    sheet.write(3, 5, '% sur budget', style_2)
    sheet.write(3, 6, 'Ecart', style_2)

    start = 4
    for datas in analyses:
        sheet.write(start, 0, datas['user'].last_name+" "+datas['user'].first_name, style_3)
        sheet.write(start, 1, datas['budget'], style_3)
        sheet.write(start, 2, datas['HProd_Charg'], style_3)
        sheet.write(start, 3, datas['HProd_Fact'], style_3)
        sheet.write(start, 4, datas['Pourc_Charg'], style_3)
        sheet.write(start, 5, datas['Pourc_Bubget'], style_3)
        sheet.write(start, 6, datas['ecart'], style_3)
        start += 1

    sheet.write(start, 0, 'Total', style_2)
    sheet.write(start, 1, total_bud, style_2)
    sheet.write(start, 2, total_HP_charge, style_2)
    sheet.write(start, 3, total_HP_fact, style_2)
    sheet.write(start, 4, total_pourc_c, style_2)
    sheet.write(start, 5, total__budget, style_2)
    sheet.write(start, 6, '', style_2)

    out = StringIO()
    workbook.save(out)

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response


@prefix.route('/taux-chargeabilite-heure-disponible')
@login_required
@roles_required([('super_admin', 'stat')])
def taux_HDispo():
    menu = 'stat'
    submenu = 'taux_HDispo'
    title_page = 'Taux du chargeabilite des heures disponibles'


    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(First_day_of_year, current_day):
            if detail.temps_id.tache_id.prestation_id.sigle != 'FER':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                if detail.temps_id.tache_id.facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_bud = 0.0
    total_HDispo = 0.0
    total_HFact = 0.0
    total_pourc_c = 0.0
    total__budget = 0.0
    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=First_day_of_year)
        ).first()

        if budget:

            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == current_day.year:
                Nbre_Days_start = function.networkdays(
                        function.date_convert(function.get_first_day(First_day_of_year)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )

                Nbre_current_day = function.networkdays(
                    function.date_convert(temp_dict['user'].date_start),
                    function.date_convert(current_day),
                    [],
                    ()
                )

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur
                production = Nbre_days_reste * budget.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste
            else:

                Nbre_current_day = function.networkdays(
                    function.date_convert(function.get_first_day(First_day_of_year)),
                    function.date_convert(current_day),
                    [],
                    ()
                )
                current_heure = budget.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)

            # temp_dict['budget'] = 0.0
            # if budget:
            #     temp_dict['budget'] = budget.heure
            temp_dict['HDispo'] = 0.0
            temp_dict['HFact'] = 0.0

            HDispo = 0.0
            HFact = 0.0

            for item in grp:
                temp_dict['HDispo'] += item['time']
                HDispo += item['time']
                if item['facturable']:
                    temp_dict['HFact'] += item['time']
                    HFact += item['time']

            temp_dict['Pourc_HD'] = 0.0
            if temp_dict['HDispo']:
                temp_dict['Pourc_HD'] = round(((temp_dict['HFact'] * 100) / temp_dict['HDispo']), 1)

            temp_dict['Pourc_Bubget'] = 0.0
            if temp_dict['budget']:
                temp_dict['Pourc_Bubget'] = round(((temp_dict['HFact'] * 100) / temp_dict['budget']), 1)

            temp_dict['ecart'] = round((temp_dict['Pourc_HD'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HDispo += round(HDispo, 1)
            total_HFact += round(HFact, 1)
            if total_HDispo:
                total_pourc_c = round((total_HFact*100)/total_HDispo, 1)
            if total_bud:
                total__budget = round((total_HFact*100)/total_bud, 1)

            analyses.append(temp_dict)

    return render_template('rapport/taux_heure_disponible.html', **locals())


@prefix.route('/taux-chargeabilite-heure-disponible/refresh', methods=['GET', 'POST'])
def taux_HDispo_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Taux du chargeabilite des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') &  Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle != 'FER':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                if detail.temps_id.tache_id.facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_bud = 0
    total_HDispo = 0
    total_HFact = 0
    total_pourc_c = 0
    total__budget = 0
    for key, grp in groupby(sorted(analyse, key=grouper,reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        if budget:

            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == now_year:

                Nbre_Days_start = function.networkdays(
                        function.date_convert(datetime.date(now_year, 1, 1)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )
                if datetime.datetime.combine(date_start, datetime.datetime.min.time()) > temp_dict['user'].date_start:

                    Nbre_current_day = function.networkdays(
                        function.date_convert(date_start),
                        function.date_convert(date_end),
                        [],
                        ()
                    )
                else:
                    if datetime.datetime.combine(date_end, datetime.datetime.min.time()) > temp_dict['user'].date_start:
                        Nbre_current_day = function.networkdays(
                            function.date_convert(temp_dict['user'].date_start),
                            function.date_convert(date_end),
                            [],
                            ()
                        )
                    else:
                        Nbre_current_day = 0

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur au proratat
                production = Nbre_days_reste * budget.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste

            else:

                Nbre_current_day = function.networkdays(
                    date_start,
                    date_end,
                    [],
                    ()
                )
                current_heure = budget.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)
            temp_dict['HDispo'] = 0
            temp_dict['HFact'] = 0

            HDispo = 0
            HFact = 0

            for item in grp:
                temp_dict['HDispo'] += item['time']
                HDispo += item['time']
                if item['facturable']:
                    temp_dict['HFact'] += item['time']
                    HFact += item['time']

            temp_dict['Pourc_HD'] = 0.0
            if temp_dict['HDispo']:
                temp_dict['Pourc_HD'] = round(((temp_dict['HFact'] * 100) / temp_dict['HDispo']), 1)

            temp_dict['Pourc_Bubget'] = 0.0
            if temp_dict['budget']:
                temp_dict['Pourc_Bubget'] = round(((temp_dict['HFact'] * 100) / temp_dict['budget']), 1)

            temp_dict['ecart'] = round((temp_dict['Pourc_HD'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HDispo += round(HDispo, 1)
            total_HFact += round(HFact, 1)
            if total_HDispo:
                total_pourc_c = round((total_HFact*100)/total_HDispo, 1)
            if total_bud:
                total__budget = round((total_HFact*100)/total_bud, 1)

            analyses.append(temp_dict)


    return render_template('rapport/taux_heure_disponible_refresh.html', **locals())


@prefix.route('/collaborateur/taux_chargeabilite_heure_disponible')
def taux_HDispo_export_excel():

    date_start = function.date_convert(request.args.get('date_start'))
    date_end = function.date_convert(request.args.get('date_end'))

    title_page = 'Taux du chargeabilite des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle != 'FER':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                if detail.temps_id.tache_id.facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['facturable'] = 0
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")




    analyses = []
    total_bud = 0
    total_HDispo = 0
    total_HFact = 0
    total_pourc_c = 0
    total__budget = 0
    for key, grp in groupby(sorted(analyse, key=grouper,reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        if budget:

            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == now_year:

                Nbre_Days_start = function.networkdays(
                        function.date_convert(datetime.date(now_year, 1, 1)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )
                if date_start > temp_dict['user'].date_start:

                    Nbre_current_day = function.networkdays(
                        function.date_convert(date_start),
                        function.date_convert(date_end),
                        [],
                        ()
                    )
                else:
                    if date_end > temp_dict['user'].date_start:
                        Nbre_current_day = function.networkdays(
                            function.date_convert(temp_dict['user'].date_start),
                            function.date_convert(date_end),
                            [],
                            ()
                        )
                    else:
                        Nbre_current_day = 0

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur au proratat
                production = Nbre_days_reste * budget.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste

            else:

                Nbre_current_day = function.networkdays(
                    date_start,
                    date_end,
                    [],
                    ()
                )
                current_heure = budget.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)
            temp_dict['HDispo'] = 0
            temp_dict['HFact'] = 0

            HDispo = 0
            HFact = 0

            for item in grp:
                temp_dict['HDispo'] += item['time']
                HDispo += item['time']
                if item['facturable']:
                    temp_dict['HFact'] += item['time']
                    HFact += item['time']

            temp_dict['Pourc_HD'] = 0.0
            if temp_dict['HDispo']:
                temp_dict['Pourc_HD'] = round(((temp_dict['HFact'] * 100) / temp_dict['HDispo']), 1)

            temp_dict['Pourc_Bubget'] = 0.0
            if temp_dict['budget']:
                temp_dict['Pourc_Bubget'] = round(((temp_dict['HFact'] * 100) / temp_dict['budget']), 1)

            temp_dict['ecart'] = round((temp_dict['Pourc_HD'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HDispo += round(HDispo, 1)
            total_HFact += round(HFact, 1)
            if total_HDispo:
                total_pourc_c = round((total_HFact*100)/total_HDispo, 1)
            if total_bud:
                total__budget = round((total_HFact*100)/total_bud, 1)

            analyses.append(temp_dict)

    workbook = Workbook()
    sheet = workbook.add_sheet('Taux Heures de disponible')

    fnt = Font()
    fnt.height = 16*20
    fnt.bold = True
    style = XFStyle()
    style.font = fnt
    sheet.row(0).set_style(style)
    sheet.row(2).set_style(style)

    style_string = "font: height 320, bold on;"
    style_string_2 = "font: bold on; borders: bottom dashed; align: wrap 1;"
    style_string_3 = "align: wrap 1;"
    style = easyxf(style_string)
    style_2 = easyxf(style_string_2)
    style_3 = easyxf(style_string_3)

    sheet.write(0, 0, title_page, style)

    sheet.write(2, 0, 'Periode du '+str(function.format_date(date_start,'%d/%m/%Y'))+' au '+str(function.format_date(date_end,'%d/%m/%Y'))+'', style)

    sheet.write(3, 0, 'Collaborateur', style_2)
    sheet.write(3, 1, 'Budget annuel', style_2)
    sheet.write(3, 2, 'Heure Dispo', style_2)
    sheet.write(3, 3, 'Heure Facturee', style_2)
    sheet.write(3, 4, '% sur dispo', style_2)
    sheet.write(3, 5, '% sur budget', style_2)
    sheet.write(3, 6, 'Ecart', style_2)

    start = 4
    for datas in analyses:
        sheet.write(start, 0, datas['user'].last_name+" "+datas['user'].first_name, style_3)
        sheet.write(start, 1, datas['budget'], style_3)
        sheet.write(start, 2, datas['HDispo'], style_3)
        sheet.write(start, 3, datas['HFact'], style_3)
        sheet.write(start, 4, datas['Pourc_HD'], style_3)
        sheet.write(start, 5, datas['Pourc_Bubget'], style_3)
        sheet.write(start, 6, datas['ecart'], style_3)
        start += 1

    sheet.write(start, 0, 'Total', style_2)
    sheet.write(start, 1, total_bud, style_2)
    sheet.write(start, 2, total_HDispo, style_2)
    sheet.write(start, 3, total_HFact, style_2)
    sheet.write(start, 4, total_pourc_c, style_2)
    sheet.write(start, 5, total__budget, style_2)
    sheet.write(start, 6, '', style_2)

    out = StringIO()
    workbook.save(out)

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response


@prefix.route('/etat-consommation-heures-disponible')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_conso():
    menu = 'stat'
    submenu = 'etat_conso'
    title_page = 'Etat du consommation des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    exept_temps_year = [
        'FER',
        'ABS',
        'CONG'
    ]
    all_user = Users.objects(
        Q(email__ne= 'admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(First_day_of_year, current_day):
            if detail.temps_id.tache_id.prestation_id.sigle not in exept_temps_year:
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = detail.temps_id.tache_id.prestation_id.sigle
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = 'RIEN'
                infos['time'] = 0.0
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_budget = 0.0
    total_adm = 0.0
    total_form = 0.0
    total_dev = 0.0
    total_prod = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        if budget:

            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == current_day.year:
                Nbre_Days_start = function.networkdays(
                        function.date_convert(function.get_first_day(First_day_of_year)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )

                Nbre_current_day = function.networkdays(
                    function.date_convert(temp_dict['user'].date_start),
                    function.date_convert(current_day),
                    [],
                    ()
                )

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur
                production = Nbre_days_reste * budget.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste
            else:

                Nbre_current_day = function.networkdays(
                    function.date_convert(function.get_first_day(First_day_of_year)),
                    function.date_convert(current_day),
                    [],
                    ()
                )
                current_heure = budget.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0

            dev_tot = 0.0
            adm_tot = 0.0
            prod_tot = 0.0
            form_tot = 0.0
            for item in grp:
                if item['prestation'] == 'DEV':
                    temp_dict['dev_time'] += item['time']
                    dev_tot += item['time']
                if item['prestation'] == 'FOR':
                    temp_dict['form_time'] += item['time']
                    form_tot += item['time']
                if item['prestation'] == 'ADM':
                    temp_dict['adm_time'] += item['time']
                    adm_tot += item['time']
                if item['prestation'] == 'PRO':
                    temp_dict['prod_time'] += item['time']
                    prod_tot += item['time']

                if item['prestation'] == 'RIEN':
                    temp_dict['dev_time'] += item['time']
                    dev_tot += item['time']

                    temp_dict['form_time'] += item['time']
                    form_tot += item['time']

                    temp_dict['adm_time'] += item['time']
                    adm_tot += item['time']

                    temp_dict['prod_time'] += item['time']
                    prod_tot += item['time']

            total_budget += temp_dict['budget']
            total_adm += adm_tot
            total_form += form_tot
            total_dev += dev_tot
            total_prod += prod_tot

            analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_disponible.html', **locals())


@prefix.route('/etat-consommation-heures-disponible/refresh', methods=['GET', 'POST'])
def etat_conso_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Etat du consommation des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year

    exept_temps_year = [
        'FER',
        'CONG',
        'ABS'
    ]

    all_user = Users.objects(
        Q(email__ne= 'admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle not in exept_temps_year:
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = detail.temps_id.tache_id.prestation_id.sigle
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = 'RIEN'
                infos['time'] = 0.0
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")


    analyses = []
    total_budget = 0.0
    total_adm = 0.0
    total_form = 0.0
    total_dev = 0.0
    total_prod = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        if budget:

            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == now_year:

                Nbre_Days_start = function.networkdays(
                        function.date_convert(datetime.date(now_year, 1, 1)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )
                if datetime.datetime.combine(date_start, datetime.datetime.min.time()) > temp_dict['user'].date_start:

                    Nbre_current_day = function.networkdays(
                        function.date_convert(date_start),
                        function.date_convert(date_end),
                        [],
                        ()
                    )
                else:
                    if datetime.datetime.combine(date_end, datetime.datetime.min.time()) > temp_dict['user'].date_start:
                        Nbre_current_day = function.networkdays(
                            function.date_convert(temp_dict['user'].date_start),
                            function.date_convert(date_end),
                            [],
                            ()
                        )
                    else:
                        Nbre_current_day = 0

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur au proratat
                production = Nbre_days_reste * budget.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste

            else:

                Nbre_current_day = function.networkdays(
                    date_start,
                    date_end,
                    [],
                    ()
                )
                current_heure = budget.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0

            dev_tot = 0.0
            adm_tot = 0.0
            prod_tot = 0.0
            form_tot = 0.0
            for item in grp:
                if item['prestation'] == 'DEV':
                    temp_dict['dev_time'] += item['time']
                    dev_tot += item['time']
                if item['prestation'] == 'FOR':
                    temp_dict['form_time'] += item['time']
                    form_tot += item['time']
                if item['prestation'] == 'ADM':
                    temp_dict['adm_time'] += item['time']
                    adm_tot += item['time']
                if item['prestation'] == 'PRO':
                    temp_dict['prod_time'] += item['time']
                    prod_tot += item['time']

                if item['prestation'] == 'RIEN':
                    temp_dict['dev_time'] += item['time']
                    dev_tot += item['time']

                    temp_dict['form_time'] += item['time']
                    form_tot += item['time']

                    temp_dict['adm_time'] += item['time']
                    adm_tot += item['time']

                    temp_dict['prod_time'] += item['time']
                    prod_tot += item['time']

            total_budget += temp_dict['budget']
            total_adm += adm_tot
            total_form += form_tot
            total_dev += dev_tot
            total_prod += prod_tot

            analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_disponible_refresh.html', **locals())


@prefix.route('/collaborateur/etat_consommation_heures_disponible')
def etat_conso_export_excel():

    date_start = function.date_convert(request.args.get('date_start'))
    date_end = function.date_convert(request.args.get('date_end'))

    title_page = 'Etat du consommation des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year

    exept_temps_year = [
        'FER',
        'CONG',
        'ABS'
    ]

    all_user = Users.objects(
        Q(email__ne= 'admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle not in exept_temps_year:
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = detail.temps_id.tache_id.prestation_id.sigle
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = 'RIEN'
                infos['time'] = 0.0
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_budget = 0.0
    total_adm = 0.0
    total_form = 0.0
    total_dev = 0.0
    total_prod = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        if budget:

            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == now_year:

                Nbre_Days_start = function.networkdays(
                        function.date_convert(datetime.date(now_year, 1, 1)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )
                if date_start > temp_dict['user'].date_start:

                    Nbre_current_day = function.networkdays(
                        function.date_convert(date_start),
                        function.date_convert(date_end),
                        [],
                        ()
                    )
                else:
                    if date_end > temp_dict['user'].date_start:
                        Nbre_current_day = function.networkdays(
                            function.date_convert(temp_dict['user'].date_start),
                            function.date_convert(date_end),
                            [],
                            ()
                        )
                    else:
                        Nbre_current_day = 0

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur au proratat
                production = Nbre_days_reste * budget.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste

            else:

                Nbre_current_day = function.networkdays(
                    date_start,
                    date_end,
                    [],
                    ()
                )
                current_heure = budget.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure, 1)
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0

            dev_tot = 0.0
            adm_tot = 0.0
            prod_tot = 0.0
            form_tot = 0.0
            for item in grp:
                if item['prestation'] == 'DEV':
                    temp_dict['dev_time'] += item['time']
                    dev_tot += item['time']
                if item['prestation'] == 'FOR':
                    temp_dict['form_time'] += item['time']
                    form_tot += item['time']
                if item['prestation'] == 'ADM':
                    temp_dict['adm_time'] += item['time']
                    adm_tot += item['time']
                if item['prestation'] == 'PRO':
                    temp_dict['prod_time'] += item['time']
                    prod_tot += item['time']

                if item['prestation'] == 'RIEN':
                    temp_dict['dev_time'] += item['time']
                    dev_tot += item['time']

                    temp_dict['form_time'] += item['time']
                    form_tot += item['time']

                    temp_dict['adm_time'] += item['time']
                    adm_tot += item['time']

                    temp_dict['prod_time'] += item['time']
                    prod_tot += item['time']

            total_budget += temp_dict['budget']
            total_adm += adm_tot
            total_form += form_tot
            total_dev += dev_tot
            total_prod += prod_tot

            analyses.append(temp_dict)

    workbook = Workbook()
    sheet = workbook.add_sheet('Etat consommation des heures disponible')

    fnt = Font()
    fnt.height = 16*20
    fnt.bold = True
    style = XFStyle()
    style.font = fnt
    sheet.row(0).set_style(style)
    sheet.row(2).set_style(style)

    style_string = "font: height 320, bold on;"
    style_string_2 = "font: bold on; borders: bottom dashed; align: wrap 1;"
    style_string_3 = "align: wrap 1;"
    style = easyxf(style_string)
    style_2 = easyxf(style_string_2)
    style_3 = easyxf(style_string_3)

    sheet.write(0, 0, title_page, style)

    sheet.write(2, 0, 'Periode du '+str(function.format_date(date_start,'%d/%m/%Y'))+' au '+str(function.format_date(date_end,'%d/%m/%Y'))+'', style)

    sheet.write(3, 0, 'Collaborateur', style_2)
    sheet.write(3, 1, 'Heure Dispo', style_2)
    sheet.write(3, 2, 'Heure Admin.', style_2)
    sheet.write(3, 3, 'Heure Forma.', style_2)
    sheet.write(3, 4, 'Heure Devpt', style_2)
    sheet.write(3, 5, 'Heure Prod', style_2)

    start = 4
    for datas in analyses:
        sheet.write(start, 0, datas['user'].last_name+" "+datas['user'].first_name, style_3)
        sheet.write(start, 1, datas['budget'], style_3)
        sheet.write(start, 2, datas['adm_time'], style_3)
        sheet.write(start, 3, datas['form_time'], style_3)
        sheet.write(start, 4, datas['dev_time'], style_3)
        sheet.write(start, 5, datas['prod_time'], style_3)
        start += 1

    sheet.write(start, 0, 'Total', style_2)
    sheet.write(start, 1, total_budget, style_2)
    sheet.write(start, 2, total_adm, style_2)
    sheet.write(start, 3, total_form, style_2)
    sheet.write(start, 4, total_dev, style_2)
    sheet.write(start, 5, total_prod, style_2)

    out = StringIO()
    workbook.save(out)

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response


@prefix.route('/solde_heures_disponible')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_conso_prod():
    menu = 'stat'
    submenu = 'etat_conso_prod'
    title_page = 'Solde des heures a effectuer par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    exept_temps_year = [
        'FER',
        'ABS',
        'CONG'
    ]

    all_user = Users.objects(
        Q(email__ne= 'admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(First_day_of_year, current_day):
            if detail.temps_id.tache_id.prestation_id.sigle not in exept_temps_year:
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = detail.temps_id.tache_id.prestation_id.sigle
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)
        if not have:
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = 'RIEN'
                infos['time'] = 0.0
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_budget = 0.0
    total_budget_origine = 0.0
    total_adm = 0.0
    total_form = 0.0
    total_dev = 0.0
    total_prod = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=First_day_of_year)
        ).first()

        if budget:

            budget_origine = budget.heure
            Nbre_days_reste = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == current_day.year:
                Nbre_Days_start = function.networkdays(
                        function.date_convert(function.get_first_day(First_day_of_year)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur
                production = Nbre_days_reste * budget.heure
                production /= 365

                budget_origine = production


            temp_dict['budget_origine'] = round(budget_origine, 1)
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0


            dev = 0.0
            adm = 0.0
            form = 0.0
            prod = 0.0

            for item in grp:
                if item['prestation'] == 'DEV':
                    dev += item['time']
                if item['prestation'] == 'FOR':
                    form += item['time']
                if item['prestation'] == 'ADM':
                    adm += item['time']
                if item['prestation'] == 'PRO':
                    prod += item['time']
                if item['prestation'] == 'RIEN':
                    dev += item['time']
                    form += item['time']
                    adm += item['time']
                    prod += item['time']


            budget_prest = BudgetPrestation.objects(
                budget_id=budget.id
            )

            for budgets in budget_prest:

                if budgets.prestation_id.sigle == 'DEV':
                    current_budget = budgets.heure
                    if Nbre_days_reste:
                        current_budget = Nbre_days_reste * budgets.heure
                        current_budget /= 365
                        current_budget = round(current_budget, 1)
                    temp_dict['dev_time'] = current_budget - dev
                    if current_budget - dev < 0:
                        temp_dict['dev_time'] = 0.0

                if budgets.prestation_id.sigle == 'FOR':
                    current_budget = budgets.heure
                    if Nbre_days_reste:
                        current_budget = Nbre_days_reste * budgets.heure
                        current_budget /= 365
                        current_budget = round(current_budget, 1)
                    temp_dict['form_time'] = current_budget - form
                    if current_budget - form < 0:
                        temp_dict['form_time'] = 0.0

                if budgets.prestation_id.sigle == 'ADM':
                    current_budget = budgets.heure
                    if Nbre_days_reste:
                        current_budget = Nbre_days_reste * budgets.heure
                        current_budget /= 365
                        current_budget = round(current_budget, 1)
                    temp_dict['adm_time'] = current_budget - adm
                    if current_budget - adm < 0:
                        temp_dict['adm_time'] = 0.0

                if budgets.prestation_id.sigle == 'PRO':
                    current_budget = budgets.heure
                    if Nbre_days_reste:
                        current_budget = Nbre_days_reste * budgets.heure
                        current_budget /= 365
                        current_budget = round(current_budget, 1)
                    temp_dict['prod_time'] = current_budget - prod
                    if current_budget - prod < 0:
                        temp_dict['prod_time'] = 0.0


            temp_dict['budget'] = 0.0
            temp_dict['budget'] += temp_dict['dev_time']
            temp_dict['budget'] += temp_dict['form_time']
            temp_dict['budget'] += temp_dict['adm_time']
            temp_dict['budget'] += temp_dict['prod_time']

            if not temp_dict['budget']:
                temp_dict['budget'] = budget.heure

            total_budget_origine += temp_dict['budget_origine']
            total_budget += temp_dict['budget']
            total_adm += temp_dict['adm_time']
            total_form += temp_dict['form_time']
            total_dev += temp_dict['dev_time']
            total_prod += temp_dict['prod_time']

            analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_production.html', **locals())


@prefix.route('/solde_heures_disponible/refresh', methods=['GET', 'POST'])
def etat_conso_prod_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Solde des heures a effectuer par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year

    exept_temps_year = [
        'FER',
        'ABS',
        'CONG'
    ]

    all_user = Users.objects(
        Q(email__ne= 'admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle not in exept_temps_year:
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = detail.temps_id.tache_id.prestation_id.sigle
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)
        if not have:
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = 'RIEN'
                infos['time'] = 0.0
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_budget = 0.0
    total_budget_origine = 0.0
    total_adm = 0.0
    total_form = 0.0
    total_dev = 0.0
    total_prod = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        if budget:

            temp_dict['budget_origine'] = budget.heure
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0


            dev = 0.0
            adm = 0.0
            form = 0.0
            prod = 0.0

            for item in grp:
                if item['prestation'] == 'DEV':
                    dev += item['time']
                if item['prestation'] == 'FOR':
                    form += item['time']
                if item['prestation'] == 'ADM':
                    adm += item['time']
                if item['prestation'] == 'PRO':
                    prod += item['time']
                if item['prestation'] == 'RIEN':
                    dev += item['time']
                    form += item['time']
                    adm += item['time']
                    prod += item['time']


            budget_prest = BudgetPrestation.objects(
                budget_id=budget.id
            )

            for budgets in budget_prest:
                if budgets.prestation_id.sigle == 'DEV':
                    temp_dict['dev_time'] = budgets.heure - dev
                    if budgets.heure - dev < 0:
                        temp_dict['dev_time'] = 0.0

                if budgets.prestation_id.sigle == 'FOR':
                    temp_dict['form_time'] = budgets.heure - form
                    if budgets.heure - form < 0:
                        temp_dict['form_time'] = 0.0

                if budgets.prestation_id.sigle == 'ADM':
                    temp_dict['adm_time'] = budgets.heure - adm
                    if budgets.heure - adm < 0:
                        temp_dict['adm_time'] = 0.0

                if budgets.prestation_id.sigle == 'PRO':
                    temp_dict['prod_time'] = budgets.heure - prod
                    if budgets.heure - prod < 0:
                        temp_dict['prod_time'] = 0.0


            temp_dict['budget'] = 0.0
            temp_dict['budget'] += temp_dict['dev_time']
            temp_dict['budget'] += temp_dict['form_time']
            temp_dict['budget'] += temp_dict['adm_time']
            temp_dict['budget'] += temp_dict['prod_time']

            if not temp_dict['budget']:
                temp_dict['budget'] = budget.heure

            total_budget_origine += temp_dict['budget_origine']
            total_budget += temp_dict['budget']
            total_adm += temp_dict['adm_time']
            total_form += temp_dict['form_time']
            total_dev += temp_dict['dev_time']
            total_prod += temp_dict['prod_time']

            analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_production_refresh.html', **locals())


@prefix.route('/collaborateur/solde_heures_disponible')
def etat_conso_prod_export_excel():

    date_start = function.date_convert(request.args.get('date_start'))
    date_end = function.date_convert(request.args.get('date_end'))

    title_page = 'Solde des heures a effectuer par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year

    exept_temps_year = [
        'FER',
        'ABS',
        'CONG'
    ]

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle not in exept_temps_year:
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = detail.temps_id.tache_id.prestation_id.sigle
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)
        if not have:
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['prestation'] = 'RIEN'
                infos['time'] = 0.0
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_budget = 0.0
    total_budget_origine = 0.0
    total_adm = 0.0
    total_form = 0.0
    total_dev = 0.0
    total_prod = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        if budget:

            temp_dict['budget_origine'] = budget.heure
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0


            dev = 0.0
            adm = 0.0
            form = 0.0
            prod = 0.0

            for item in grp:
                if item['prestation'] == 'DEV':
                    dev += item['time']
                if item['prestation'] == 'FOR':
                    form += item['time']
                if item['prestation'] == 'ADM':
                    adm += item['time']
                if item['prestation'] == 'PRO':
                    prod += item['time']
                if item['prestation'] == 'RIEN':
                    dev += item['time']
                    form += item['time']
                    adm += item['time']
                    prod += item['time']


            budget_prest = BudgetPrestation.objects(
                budget_id=budget.id
            )

            for budgets in budget_prest:
                if budgets.prestation_id.sigle == 'DEV':
                    temp_dict['dev_time'] = budgets.heure - dev
                    if budgets.heure - dev < 0:
                        temp_dict['dev_time'] = 0.0

                if budgets.prestation_id.sigle == 'FOR':
                    temp_dict['form_time'] = budgets.heure - form
                    if budgets.heure - form < 0:
                        temp_dict['form_time'] = 0.0

                if budgets.prestation_id.sigle == 'ADM':
                    temp_dict['adm_time'] = budgets.heure - adm
                    if budgets.heure - adm < 0:
                        temp_dict['adm_time'] = 0.0

                if budgets.prestation_id.sigle == 'PRO':
                    temp_dict['prod_time'] = budgets.heure - prod
                    if budgets.heure - prod < 0:
                        temp_dict['prod_time'] = 0.0


            temp_dict['budget'] = 0.0
            temp_dict['budget'] += temp_dict['dev_time']
            temp_dict['budget'] += temp_dict['form_time']
            temp_dict['budget'] += temp_dict['adm_time']
            temp_dict['budget'] += temp_dict['prod_time']

            if not temp_dict['budget']:
                temp_dict['budget'] = budget.heure

            total_budget_origine += temp_dict['budget_origine']
            total_budget += temp_dict['budget']
            total_adm += temp_dict['adm_time']
            total_form += temp_dict['form_time']
            total_dev += temp_dict['dev_time']
            total_prod += temp_dict['prod_time']

            analyses.append(temp_dict)

    workbook = Workbook()
    sheet = workbook.add_sheet('Solde heures diponibles')

    fnt = Font()
    fnt.height = 16*20
    fnt.bold = True
    style = XFStyle()
    style.font = fnt
    sheet.row(0).set_style(style)
    sheet.row(2).set_style(style)

    style_string = "font: height 320, bold on;"
    style_string_2 = "font: bold on; borders: bottom dashed; align: wrap 1;"
    style_string_3 = "align: wrap 1;"
    style = easyxf(style_string)
    style_2 = easyxf(style_string_2)
    style_3 = easyxf(style_string_3)

    sheet.write(0, 0, title_page, style)

    sheet.write(2, 0, 'Periode du '+str(function.format_date(date_start,'%d/%m/%Y'))+' au '+str(function.format_date(date_end,'%d/%m/%Y'))+'', style)

    sheet.write(3, 0, 'Collaborateur', style_2)
    sheet.write(3, 1, 'Heure Dispo', style_2)
    sheet.write(3, 2, 'H. Dispo Restant', style_2)
    sheet.write(3, 3, 'Heure Admin.', style_2)
    sheet.write(3, 4, 'Heure Forma.', style_2)
    sheet.write(3, 5, 'Heure Devpt', style_2)
    sheet.write(3, 6, 'Heure Prod', style_2)

    start = 4
    for datas in analyses:
        sheet.write(start, 0, datas['user'].last_name+" "+datas['user'].first_name, style_3)
        sheet.write(start, 1, datas['budget_origine'], style_3)
        sheet.write(start, 2, datas['budget'], style_3)
        sheet.write(start, 3, datas['adm_time'], style_3)
        sheet.write(start, 4, datas['form_time'], style_3)
        sheet.write(start, 5, datas['dev_time'], style_3)
        sheet.write(start, 6, datas['prod_time'], style_3)
        start += 1

    sheet.write(start, 0, 'Total', style_2)
    sheet.write(start, 1, total_budget_origine, style_2)
    sheet.write(start, 2, total_budget, style_2)
    sheet.write(start, 3, total_adm, style_2)
    sheet.write(start, 4, total_form, style_2)
    sheet.write(start, 5, total_dev, style_2)
    sheet.write(start, 6, total_prod, style_2)

    out = StringIO()
    workbook.save(out)

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response


@prefix.route('/heure-de-developpement-chargee')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_dev_charge():
    menu = 'stat'
    submenu = 'dev_charge'
    title_page = 'Heures du developpement chargees'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    all_user = Users.objects(
        Q(email__ne= 'admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        for detail in user.time_user(First_day_of_year, current_day):
            if detail.temps_id.tache_id.prestation_id.sigle == 'DEV':
                infos = {}
                infos['user'] = user
                if detail.temps_id.tache_id.projet_id:
                    infos['ref_client'] = detail.temps_id.tache_id.projet_id.client_id.ref
                    infos['client'] = detail.temps_id.tache_id.projet_id.client_id.name
                    infos['prospect'] = None
                    if detail.temps_id.tache_id.projet_id.prospect_id:
                        infos['prospect'] = detail.temps_id.tache_id.projet_id.prospect_id
                    infos['client_ent'] = detail.temps_id.tache_id.projet_id.client_id.myself
                else:
                    client_accent = Client.objects(
                        myself= True
                    ).first()
                    infos['ref_client'] = client_accent.ref
                    infos['client'] = client_accent.name
                    infos['prospect'] = None
                    infos['client_ent'] = client_accent.myself

                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        temp_dict['clients'] = []
        under_grouper = itemgetter("ref_client", "client")
        temp_dict['total'] = 0
        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["ref_client", "client"], key))
            temp_dict_under['time'] = 0
            for item in grp:
                temp_dict_under['time'] += item['time']
                temp_dict_under['prospect'] = None
                if item['client_ent']:
                    if item['prospect']:
                        temp_dict_under['prospect'] = item['prospect']
            temp_dict['clients'].append(temp_dict_under)
            temp_dict['total'] += temp_dict_under['time']
        analyses.append(temp_dict)

    return render_template('rapport/heure-de-developpement-chargee.html', **locals())


@prefix.route('/heure-de-developpement-chargee/refresh', methods=['GET', 'POST'])
def etat_dev_charge_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Heures du developpement chargees'

    all_user = Users.objects(
        Q(email__ne= 'admin@accentcom-cm.com') & Q(email__ne= 'henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle == 'DEV':
                infos = {}
                infos['user'] = user
                if detail.temps_id.tache_id.projet_id:
                    infos['ref_client'] = detail.temps_id.tache_id.projet_id.client_id.ref
                    infos['client'] = detail.temps_id.tache_id.projet_id.client_id.name
                    infos['prospect'] = None
                    if detail.temps_id.tache_id.projet_id.prospect_id:
                        infos['prospect'] = detail.temps_id.tache_id.projet_id.prospect_id
                    infos['client_ent'] = detail.temps_id.tache_id.projet_id.client_id.myself
                else:
                    client_accent = Client.objects(
                        myself= True
                    ).first()
                    infos['ref_client'] = client_accent.ref
                    infos['client'] = client_accent.name
                    infos['prospect'] = None
                    infos['client_ent'] = client_accent.myself

                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        temp_dict['clients'] = []
        under_grouper = itemgetter("ref_client", "client")
        temp_dict['total'] = 0
        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["ref_client", "client"], key))
            temp_dict_under['time'] = 0
            for item in grp:
                temp_dict_under['time'] += item['time']
                temp_dict_under['prospect'] = None
                if item['client_ent']:
                    if item['prospect']:
                        temp_dict_under['prospect'] = item['prospect']
            temp_dict['clients'].append(temp_dict_under)
            temp_dict['total'] += temp_dict_under['time']
        analyses.append(temp_dict)

    return render_template('rapport/heure-de-developpement-chargee_refresh.html', **locals())


@prefix.route('/collaborateur/heure-de-developpement-chargee')
def etat_dev_charge_export_excel():

    date_start = function.date_convert(request.args.get('date_start'))
    date_end = function.date_convert(request.args.get('date_end'))

    title_page = 'Heures du developpement chargees'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year


    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle == 'DEV':
                infos = {}
                infos['user'] = user
                if detail.temps_id.tache_id.projet_id:
                    infos['ref_client'] = detail.temps_id.tache_id.projet_id.client_id.ref
                    infos['client'] = detail.temps_id.tache_id.projet_id.client_id.name
                    infos['prospect'] = None
                    if detail.temps_id.tache_id.projet_id.prospect_id:
                        infos['prospect'] = detail.temps_id.tache_id.projet_id.prospect_id
                    infos['client_ent'] = detail.temps_id.tache_id.projet_id.client_id.myself
                else:
                    client_accent = Client.objects(
                        myself=True
                    ).first()
                    infos['ref_client'] = client_accent.ref
                    infos['client'] = client_accent.name
                    infos['prospect'] = None
                    infos['client_ent'] = client_accent.myself

                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        temp_dict['clients'] = []
        under_grouper = itemgetter("ref_client", "client")
        temp_dict['total'] = 0
        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["ref_client", "client"], key))
            temp_dict_under['time'] = 0
            for item in grp:
                temp_dict_under['time'] += item['time']
                temp_dict_under['prospect'] = None
                if item['client_ent']:
                    if item['prospect']:
                        temp_dict_under['prospect'] = item['prospect']
            temp_dict['clients'].append(temp_dict_under)
            temp_dict['total'] += temp_dict_under['time']
        analyses.append(temp_dict)

    workbook = Workbook()
    sheet = workbook.add_sheet('Heure develop. charge')

    fnt = Font()
    fnt.height = 16*20
    fnt.bold = True
    style = XFStyle()
    style.font = fnt
    sheet.row(0).set_style(style)
    sheet.row(2).set_style(style)

    style_string = "font: height 320, bold on;"
    style_string_2 = "font: bold on; borders: bottom dashed; align: wrap 1;"
    style_string_3 = "align: wrap 1;"\

    style = easyxf(style_string)
    style_2 = easyxf(style_string_2)
    style_3 = easyxf(style_string_3)
    style_4 = easyxf('font: height 240, bold on;')

    sheet.write(0, 0, title_page, style)

    sheet.write(2, 0, 'Periode du '+str(function.format_date(date_start,'%d/%m/%Y'))+' au '+str(function.format_date(date_end,'%d/%m/%Y'))+'', style)


    start = 4
    for datas in analyses:
        sheet.write(start, 0, 'Collaborateur: '+datas['user'].last_name+" "+datas['user'].first_name, style_4)
        # sheet.write(start, 1, datas['user'].last_name+" "+datas['user'].first_name, style_4)
        # sheet.write(start, 2, 'Total', style_4)
        # sheet.write(start, 3, datas['total'], style_4)

        start += 1
        sheet.write(start, 0, 'Code Client', style_2)
        sheet.write(start, 1, 'Nom du Client', style_2)
        sheet.write(start, 2, 'Prospect', style_2)
        sheet.write(start, 3, 'Heure devlp', style_2)

        start += 1
        for client in datas['clients']:
               sheet.write(start, 0, client['ref_client'], style_3)
               sheet.write(start, 1, client['client'], style_3)
               prospect = ' - '
               if client['prospect']:
                   prospect = client['prospect'].name
               sheet.write(start, 2, prospect, style_3)
               sheet.write(start, 3, client['time'], style_3)
               start += 1

        start += 1

    out = StringIO()
    workbook.save(out)

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response


@prefix.route('/production-par-collaborateur-et-par-client')
@login_required
@roles_required([('super_admin', 'stat')])
def production_par_coll_client():
    menu = 'stat'
    submenu = 'prod_coll_client'
    title_page = 'Production par collaborateur et par client'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        for detail in user.time_user(First_day_of_year, current_day):
            if detail.temps_id.tache_id.prestation_id.sigle == 'PRO':
                infos = {}
                infos['user'] = user
                if detail.temps_id.tache_id.projet_id:
                    infos['ref_client'] = detail.temps_id.tache_id.projet_id.client_id.ref
                    infos['client'] = detail.temps_id.tache_id.projet_id.client_id.name
                    infos['prospect'] = None
                    if detail.temps_id.tache_id.projet_id.prospect_id:
                        infos['prospect'] = detail.temps_id.tache_id.projet_id.prospect_id
                    infos['client_ent'] = detail.temps_id.tache_id.projet_id.client_id.myself
                else:
                    client_accent = Client.objects(
                        myself=True
                    ).first()
                    infos['ref_client'] = client_accent.ref
                    infos['client'] = client_accent.name
                    infos['prospect'] = None
                    infos['client_ent'] = client_accent.myself

                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        temp_dict['clients'] = []
        under_grouper = itemgetter("ref_client", "client")
        temp_dict['total'] = 0.0
        temp_dict['total_gene'] = 0.0
        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["ref_client", "client"], key))
            temp_dict_under['time'] = 0.0
            for item in grp:
                temp_dict_under['time'] += item['time']
                temp_dict_under['prospect'] = None
                if item['client_ent']:
                    if item['prospect']:
                        temp_dict_under['prospect'] = item['prospect']

            temp_dict_under['montant'] = 0.0
            if temp_dict['user'].tauxH:
                temp_dict_under['montant'] = temp_dict_under['time'] * temp_dict['user'].tauxH
            temp_dict['clients'].append(temp_dict_under)
            temp_dict['total'] += round(temp_dict_under['time'], 1)
            temp_dict['total_gene'] += round(temp_dict_under['montant'], 1)
        analyses.append(temp_dict)

    return render_template('rapport/production-par-collaborateur-et-par-client.html', **locals())


@prefix.route('/production-par-collaborateur-et-par-client/refresh', methods=['GET', 'POST'])
def production_par_coll_client_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Production par collaborateur et par client'

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle == 'PRO':
                infos = {}
                infos['user'] = user
                if detail.temps_id.tache_id.projet_id:
                    infos['ref_client'] = detail.temps_id.tache_id.projet_id.client_id.ref
                    infos['client'] = detail.temps_id.tache_id.projet_id.client_id.name
                    infos['prospect'] = None
                    if detail.temps_id.tache_id.projet_id.prospect_id:
                        infos['prospect'] = detail.temps_id.tache_id.projet_id.prospect_id
                    infos['client_ent'] = detail.temps_id.tache_id.projet_id.client_id.myself
                else:
                    client_accent = Client.objects(
                        myself = True
                    ).first()
                    infos['ref_client'] = client_accent.ref
                    infos['client'] = client_accent.name
                    infos['prospect'] = None
                    infos['client_ent'] = client_accent.myself

                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        temp_dict['clients'] = []
        under_grouper = itemgetter("ref_client", "client")
        temp_dict['total'] = 0.0
        temp_dict['total_gene'] = 0.0
        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["ref_client", "client"], key))
            temp_dict_under['time'] = 0.0
            for item in grp:
                temp_dict_under['time'] += item['time']
                temp_dict_under['prospect'] = None
                if item['client_ent']:
                    if item['prospect']:
                        temp_dict_under['prospect'] = item['prospect']

            temp_dict_under['montant'] = 0.0
            if temp_dict['user'].tauxH:
                temp_dict_under['montant'] = temp_dict_under['time'] * temp_dict['user'].tauxH
            temp_dict['clients'].append(temp_dict_under)
            temp_dict['total'] += round(temp_dict_under['time'], 1)
            temp_dict['total_gene'] += round(temp_dict_under['montant'], 1)
        analyses.append(temp_dict)

    return render_template('rapport/production-par-collaborateur-et-par-client_refresh.html', **locals())


@prefix.route('/collaborateur/production-par-collaborateur-et-par-client')
def production_par_coll_client_export_excel():

    date_start = function.date_convert(request.args.get('date_start'))
    date_end = function.date_convert(request.args.get('date_end'))

    title_page = 'Production par collaborateur et par client'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year


    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_id.sigle == 'PRO':
                infos = {}
                infos['user'] = user
                if detail.temps_id.tache_id.projet_id:
                    infos['ref_client'] = detail.temps_id.tache_id.projet_id.client_id.ref
                    infos['client'] = detail.temps_id.tache_id.projet_id.client_id.name
                    infos['prospect'] = None
                    if detail.temps_id.tache_id.projet_id.prospect_id:
                        infos['prospect'] = detail.temps_id.tache_id.projet_id.prospect_id
                    infos['client_ent'] = detail.temps_id.tache_id.projet_id.client_id.myself
                else:
                    client_accent = Client.objects(
                        myself=True
                    ).first()
                    infos['ref_client'] = client_accent.ref
                    infos['client'] = client_accent.name
                    infos['prospect'] = None
                    infos['client_ent'] = client_accent.myself

                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        temp_dict['clients'] = []
        under_grouper = itemgetter("ref_client", "client")
        temp_dict['total'] = 0.0
        temp_dict['total_gene'] = 0.0
        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["ref_client", "client"], key))
            temp_dict_under['time'] = 0.0
            for item in grp:
                temp_dict_under['time'] += item['time']
                temp_dict_under['prospect'] = None
                if item['client_ent']:
                    if item['prospect']:
                        temp_dict_under['prospect'] = item['prospect']

            temp_dict_under['montant'] = 0.0
            if temp_dict['user'].tauxH:
                temp_dict_under['montant'] = temp_dict_under['time'] * temp_dict['user'].tauxH
            temp_dict['clients'].append(temp_dict_under)
            temp_dict['total'] += round(temp_dict_under['time'], 1)
            temp_dict['total_gene'] += round(temp_dict_under['montant'], 1)
        analyses.append(temp_dict)

    workbook = Workbook()
    sheet = workbook.add_sheet('Production collaborateur par client')

    fnt = Font()
    fnt.height = 16*20
    fnt.bold = True
    style = XFStyle()
    style.font = fnt
    sheet.row(0).set_style(style)
    sheet.row(2).set_style(style)

    style_string = "font: height 320, bold on;"
    style_string_2 = "font: bold on; borders: bottom dashed; align: wrap 1;"
    style_string_3 = "align: wrap 1;"\

    style = easyxf(style_string)
    style_2 = easyxf(style_string_2)
    style_3 = easyxf(style_string_3)
    style_4 = easyxf('font: height 240, bold on;')

    sheet.write(0, 0, title_page, style)

    sheet.write(2, 0, 'Periode du '+str(function.format_date(date_start,'%d/%m/%Y'))+' au '+str(function.format_date(date_end,'%d/%m/%Y'))+'', style)


    start = 4
    for datas in analyses:
        sheet.write(start, 0, 'Collaborateur: '+datas['user'].last_name+" "+datas['user'].first_name, style_4)
        # sheet.write(start, 1, datas['user'].last_name+" "+datas['user'].first_name, style_4)
        # sheet.write(start, 2, 'Total', style_4)
        # sheet.write(start, 3, datas['total'], style_4)

        start += 1
        sheet.write(start, 0, 'Code Client', style_2)
        sheet.write(start, 1, 'Nom du Client', style_2)
        sheet.write(start, 2, 'Prospect', style_2)
        sheet.write(start, 3, 'Heure', style_2)
        sheet.write(start, 4, 'Montant', style_2)

        start += 1
        for client in datas['clients']:
               sheet.write(start, 0, client['ref_client'], style_3)
               sheet.write(start, 1, client['client'], style_3)
               prospect = ' - '
               if client['prospect']:
                   prospect = client['prospect'].name
               sheet.write(start, 2, prospect, style_3)
               sheet.write(start, 3, client['time'], style_3)
               sheet.write(start, 4, function.format_price(client['montant']), style_3)
               start += 1
        sheet.write(start, 0, 'Total', style_2)
        sheet.write(start, 4, function.format_price(datas.total_gene), style_2)
        start += 1

    out = StringIO()
    workbook.save(out)

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response


@prefix.route('/taux-mali-global')
@login_required
@roles_required([('super_admin', 'stat')])
def taux_mali_global():
    menu = 'stat'
    submenu = 'taux_mali'
    title_page = 'Taux du mali global'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(First_day_of_year, current_day):
            if detail.temps_id.tache_id.prestation_sigle() == 'PRO':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_bud = 0.0
    total_facturable = 0.0
    total_facturee = 0.0
    total_mali_tech = 0.0
    total_mali_com = 0.0
    total_global = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) & Q(date_start=First_day_of_year)
        ).first()

        prest_prod = Prestation.objects(
            sigle='PRO'
        ).first()

        if budget:

            budget_prod = BudgetPrestation.objects(
                Q(budget_id = budget.id) & Q(prestation_id = prest_prod.id)
            ).first()

            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == current_day.year:
                Nbre_Days_start = function.networkdays(
                        function.date_convert(function.get_first_day(First_day_of_year)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )

                Nbre_current_day = function.networkdays(
                    function.date_convert(temp_dict['user'].date_start),
                    function.date_convert(current_day),
                    [],
                    ()
                )

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur
                production = Nbre_days_reste * budget_prod.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste
            else:

                Nbre_current_day = function.networkdays(
                    function.date_convert(function.get_first_day(First_day_of_year)),
                    function.date_convert(current_day),
                    [],
                    ()
                )
                current_heure = budget_prod.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure * temp_dict['user'].tauxH, 1)
            temp_dict['HFacturable'] = 0.0
            temp_dict['HFacturee'] = 0.0

            HFacturable = 0.0
            HFacturee = 0.0

            for item in grp:
                temp_dict['HFacturable'] += item['time'] * temp_dict['user'].tauxH
                HFacturable += item['time'] * temp_dict['user'].tauxH

            temp_dict['HFacturee'] = temp_dict['user'].valeur_facture()
            HFacturee += temp_dict['user'].valeur_facture()

            temp_dict['mali_tech'] = 0.0
            if temp_dict['budget']:
                temp_dict['mali_tech'] = round((temp_dict['budget'] - temp_dict['HFacturee']) / temp_dict['budget'], 1)
            temp_dict['mali_com'] = 0.0
            if temp_dict['HFacturee']:
                temp_dict['mali_com'] = round((temp_dict['HFacturable'] - temp_dict['HFacturee']) / temp_dict['HFacturable'],1)
            temp_dict['mali_global'] = round((temp_dict['mali_tech'] + temp_dict['mali_com'])/2,1)


            total_bud += temp_dict['budget']
            total_facturable += temp_dict['HFacturable']
            total_facturee += temp_dict['HFacturee']
            if total_bud:
                total_mali_tech = round((total_bud - total_facturable) / total_bud, 1)
            if total_facturable:
                total_mali_com = round((total_facturable - total_facturee) / total_facturable, 1)
            total_global = (total_mali_com + total_mali_tech) / 2


            analyses.append(temp_dict)

    return render_template('rapport/taux-mali-global.html', **locals())


@prefix.route('/taux-mali-global/refresh', methods=['GET', 'POST'])
def taux_mali_global_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Taux du mali global'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_sigle() == 'PRO':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    analyses = []
    total_bud = 0.0
    total_facturable = 0.0
    total_facturee = 0.0
    total_mali_tech = 0.0
    total_mali_com = 0.0
    total_global = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) &  Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        prest_prod = Prestation.objects(
            sigle='PRO'
        ).first()

        if budget:

            budget_prod = BudgetPrestation.objects(
                Q(budget_id= budget.id) &  Q(prestation_id= prest_prod.id)
            ).first()


            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == now_year:

                Nbre_Days_start = function.networkdays(
                        function.date_convert(datetime.date(now_year, 1, 1)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )
                if datetime.datetime.combine(date_start,datetime.datetime.min.time()) > temp_dict['user'].date_start:

                    Nbre_current_day = function.networkdays(
                        function.date_convert(date_start),
                        function.date_convert(date_end),
                        [],
                        ()
                    )
                else:
                    if datetime.datetime.combine(date_end,datetime.datetime.min.time()) > temp_dict['user'].date_start:
                        Nbre_current_day = function.networkdays(
                            function.date_convert(temp_dict['user'].date_start),
                            function.date_convert(date_end),
                            [],
                            ()
                        )
                    else:
                        Nbre_current_day = 0

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur au proratat
                production = Nbre_days_reste * budget_prod.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste

            else:

                Nbre_current_day = function.networkdays(
                    date_start,
                    date_end,
                    [],
                    ()
                )
                current_heure = budget_prod.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure * temp_dict['user'].tauxH, 1)
            temp_dict['HFacturable'] = 0.0
            temp_dict['HFacturee'] = 0.0

            HFacturable = 0.0
            HFacturee = 0.0

            for item in grp:
                temp_dict['HFacturable'] += item['time'] * temp_dict['user'].tauxH
                HFacturable += item['time'] * temp_dict['user'].tauxH

            temp_dict['HFacturee'] = temp_dict['user'].valeur_facture()
            HFacturee += temp_dict['user'].valeur_facture()

            temp_dict['mali_tech'] = 0.0
            if temp_dict['budget']:
                temp_dict['mali_tech'] = round((temp_dict['budget'] - temp_dict['HFacturee']) / temp_dict['budget'], 1)
            temp_dict['mali_com'] = 0.0
            if temp_dict['HFacturee']:
                temp_dict['mali_com'] = round((temp_dict['HFacturable'] - temp_dict['HFacturee']) / temp_dict['HFacturable'],1)
            temp_dict['mali_global'] = round((temp_dict['mali_tech'] + temp_dict['mali_com'])/2,1)


            total_bud += temp_dict['budget']
            total_facturable += temp_dict['HFacturable']
            total_facturee += temp_dict['HFacturee']
            if total_bud:
                total_mali_tech = round((total_bud - total_facturable) / total_bud, 1)
            if total_facturable:
                total_mali_com = round((total_facturable - total_facturee) / total_facturable, 1)
            total_global = (total_mali_com + total_mali_tech) / 2

            analyses.append(temp_dict)

    return render_template('rapport/taux-mali-global_refresh.html', **locals())


@prefix.route('/collaborateur/taux-mali-global')
def taux_mali_global_export_excel():

    date_start = function.date_convert(request.args.get('date_start'))
    date_end = function.date_convert(request.args.get('date_end'))

    title_page = 'Taux du mali global'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year

    all_user = Users.objects(
        Q(email__ne='admin@accentcom-cm.com') & Q(email__ne='henri@accentcom-cm.com')
    )

    analyse = []
    for user in all_user:
        have = False
        for detail in user.time_user(date_start, date_end):
            if detail.temps_id.tache_id.prestation_sigle() == 'PRO':
                have = True
                infos = {}
                infos['user'] = user
                infos['user_id'] = user.id
                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)

        if not have:
            infos = {}
            infos['user'] = user
            infos['user_id'] = user.id
            infos['time'] = 0.0
            analyse.append(infos)

    grouper = itemgetter("user_id", "user")

    Nbre_current_day = function.networkdays(
        date_start,
        date_end,
        [],
        ()
    )

    analyses = []
    total_bud = 0.0
    total_facturable = 0.0
    total_facturee = 0.0
    total_mali_tech = 0.0
    total_mali_com = 0.0
    total_global = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper, reverse=True), grouper):
        temp_dict = dict(zip(["user_id", "user"], key))

        budget = Budget.objects(
            Q(user_id=temp_dict['user'].id) &  Q(date_start=datetime.date(now_year, 1, 1))
        ).first()

        prest_prod = Prestation.objects(
            sigle='PRO'
        ).first()

        if budget:

            budget_prod = BudgetPrestation.objects(
                Q(budget_id=budget.id) & Q(prestation_id=prest_prod.id)
            ).first()


            Nbre_Days_start = 0.0
            if temp_dict['user'].date_start and temp_dict['user'].date_start.year == now_year:

                Nbre_Days_start = function.networkdays(
                        function.date_convert(datetime.date(now_year, 1, 1)),
                        function.date_convert(temp_dict['user'].date_start),
                        [],
                        ()
                    )
                if date_start > temp_dict['user'].date_start:

                    Nbre_current_day = function.networkdays(
                        function.date_convert(date_start),
                        function.date_convert(date_end),
                        [],
                        ()
                    )
                else:
                    if date_end > temp_dict['user'].date_start:
                        Nbre_current_day = function.networkdays(
                            function.date_convert(temp_dict['user'].date_start),
                            function.date_convert(date_end),
                            [],
                            ()
                        )
                    else:
                        Nbre_current_day = 0

                Nbre_days_reste = 365 - Nbre_Days_start

                # Trouver la production d'un utilisateur au proratat
                production = Nbre_days_reste * budget_prod.heure
                production /= 365

                current_heure = production * Nbre_current_day
                current_heure /= Nbre_days_reste

            else:

                Nbre_current_day = function.networkdays(
                    date_start,
                    date_end,
                    [],
                    ()
                )
                current_heure = budget_prod.heure * Nbre_current_day
                current_heure /= 365

            temp_dict['budget'] = round(current_heure * temp_dict['user'].tauxH, 1)
            temp_dict['HFacturable'] = 0.0
            temp_dict['HFacturee'] = 0.0

            HFacturable = 0.0
            HFacturee = 0.0

            for item in grp:
                temp_dict['HFacturable'] += item['time'] * temp_dict['user'].tauxH
                HFacturable += item['time'] * temp_dict['user'].tauxH

            temp_dict['HFacturee'] = temp_dict['user'].valeur_facture()
            HFacturee += temp_dict['user'].valeur_facture()

            temp_dict['mali_tech'] = 0.0
            if temp_dict['budget']:
                temp_dict['mali_tech'] = round((temp_dict['budget'] - temp_dict['HFacturee']) / temp_dict['budget'], 1)
            temp_dict['mali_com'] = 0.0
            if temp_dict['HFacturee']:
                temp_dict['mali_com'] = round((temp_dict['HFacturable'] - temp_dict['HFacturee']) / temp_dict['HFacturable'],1)
            temp_dict['mali_global'] = round((temp_dict['mali_tech'] + temp_dict['mali_com'])/2,1)


            total_bud += temp_dict['budget']
            total_facturable += temp_dict['HFacturable']
            total_facturee += temp_dict['HFacturee']
            if total_bud:
                total_mali_tech = round((total_bud - total_facturable) / total_bud, 1)
            if total_facturable:
                total_mali_com = round((total_facturable - total_facturee) / total_facturable, 1)
            total_global = (total_mali_com + total_mali_tech) / 2

            analyses.append(temp_dict)

    workbook = Workbook()
    sheet = workbook.add_sheet('Taux du mali global')

    fnt = Font()
    fnt.height = 16*20
    fnt.bold = True
    style = XFStyle()
    style.font = fnt
    sheet.row(0).set_style(style)
    sheet.row(2).set_style(style)

    style_string = "font: height 320, bold on;"
    style_string_2 = "font: bold on; borders: bottom dashed; align: wrap 1;"
    style_string_3 = "align: wrap 1;"
    style = easyxf(style_string)
    style_2 = easyxf(style_string_2)
    style_3 = easyxf(style_string_3)

    sheet.write(0, 0, title_page, style)

    sheet.write(2, 0, 'Periode du '+str(function.format_date(date_start,'%d/%m/%Y'))+' au '+str(function.format_date(date_end,'%d/%m/%Y'))+'', style)

    sheet.write(3, 0, 'Collaborateur', style_2)
    sheet.write(3, 1, 'Prod. Brute', style_2)
    sheet.write(3, 2, 'Prod. Brute Facturable', style_2)
    sheet.write(3, 3, 'Prod. Brute Facturee', style_2)
    sheet.write(3, 4, 'Taux Mali Tech.', style_2)
    sheet.write(3, 5, 'Taux Mali Com.', style_2)
    sheet.write(3, 6, 'Taux Mali Global', style_2)

    start = 4
    for datas in analyses:
        sheet.write(start, 0, datas['user'].last_name+" "+datas['user'].first_name, style_3)
        sheet.write(start, 1, datas['budget'], style_3)
        sheet.write(start, 2, datas['HFacturable'], style_3)
        sheet.write(start, 3, datas['HFacturee'], style_3)
        sheet.write(start, 4, datas['mali_tech'] * 100, style_3)
        sheet.write(start, 5, datas['mali_com'] * 100, style_3)
        sheet.write(start, 6, datas['mali_global'] * 100, style_3)
        start += 1

    sheet.write(start, 0, 'Total', style_2)
    sheet.write(start, 1, total_bud, style_2)
    sheet.write(start, 2, total_facturable, style_2)
    sheet.write(start, 3, total_facturee, style_2)
    sheet.write(start, 4, total_mali_tech * 100, style_2)
    sheet.write(start, 5, total_mali_com * 100, style_2)
    sheet.write(start, 6, total_global * 100, style_2)

    out = StringIO()
    workbook.save(out)

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response