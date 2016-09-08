__author__ = 'Ronald'

from ...modules import *
from models_frais import Frais, FraisProjet, Projet
from forms_frais import FormFrais, FormFraisProjet, FormFraisTache
from ..temps.models_temps import Temps, Tache, DetailFrais, DetailTemps


prefix = Blueprint('frais', __name__)
prefix_projet = Blueprint('frais_projet', __name__)
prefix_tache = Blueprint('frais_tache', __name__)


@prefix.route('/frais')
@login_required
@roles_required([('super_admin', 'frais')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'frais'
    title_page = 'Parametre - Frais'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Frais.objects()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='frais')
    datas.paginate(page=page, per_page=10)

    return render_template('frais/index.html', **locals())


@prefix.route('/frais/edit',  methods=['GET', 'POST'])
@prefix.route('/frais/edit/<objectid:frais_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'frais')], ['edit'])
def edit(frais_id=None):

    if frais_id:
        fraiss = Frais.objects.get(id=frais_id)
        form = FormFrais(obj=fraiss)
    else:
        fraiss = Frais()
        form = FormFrais()

    success = False
    if form.validate_on_submit():

        fraiss.libelle = form.libelle.data
        fraiss.factu = form.factu.data
        fraiss.nfactu = form.nfactu.data
        fraiss.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('frais/edit.html', **locals())


@prefix.route('/frais/delete/<objectid:frais_id>')
@login_required
@roles_required([('super_admin', 'frais')], ['delete'])
def delete(frais_id):
    fraiss = Frais.objects.get(id=frais_id)

    frais_projet = FraisProjet.objects(
        frais_id = fraiss.id
    )
    if len(frais_projet):
        flash('Impossible de supprimer cet element', 'danger')
    else:
        fraiss.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('frais.index'))


# LISTE DES FRAIS DANS UN PROJET
@prefix_projet.route('/frais/<objectid:projet_id>')
@login_required
def index(projet_id):
    menu = 'projet'
    submenu = 'projet'
    context = 'frais'
    title_page = 'Projets - Frais'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    projet = Projet.objects.get(id=projet_id)
    datas = FraisProjet.objects(projet_id = projet.id)
    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='Projets')

    datas.paginate(page=page, per_page=10)

    return render_template('frais/frais_projet.html', **locals())


@prefix_projet.route('/frais/edit/<objectid:projet_id>',  methods=['GET', 'POST'])
@prefix_projet.route('/frais/edit/<objectid:projet_id>/<objectid:frais_projet_id>',  methods=['GET', 'POST'])
@login_required
def edit(projet_id, frais_projet_id=None):

    projet = Projet.objects.get(id=projet_id)
    if frais_projet_id:
        frais_projet = FraisProjet.objects.get(id=frais_projet_id)
        form = FormFraisProjet(obj=frais_projet)
        form.frais_id.data = frais_projet.frais_id.id
        if frais_projet.frais_id.factu:
            form.facturable.data = '1'
        else:
            form.facturable.data = '2'
    else:
        frais_projet = FraisProjet()
        form = FormFraisProjet()

    form.frais_id.choices = [(0, 'Selectionnez un frais')]
    for frais in Frais.objects():
        form.frais_id.choices.append((str(frais.id), frais.libelle))

    if form.frais_id.data:
        frais = Frais.objects.get(id=form.frais_id.data)
        list_factu = {}
        if frais.nfactu:
            list_factu[2] = 'Non Facturable'
        if frais.factu:
            list_factu[1] = 'Facturable'

    success = False
    if form.validate_on_submit():

        frais_projet.projet_id = projet

        frais = Frais.objects.get(id=form.frais_id.data)
        frais_projet.frais_id = frais

        if form.facturable.data == '2':
            frais_projet.facturable = False
        if form.facturable.data == '1':
            frais_projet.facturable = True

        frais_projet.montant = form.montant.data
        frais_projet.save()

        success = True

    return render_template('frais/frais_projet_edit.html', **locals())

@prefix_projet.route('/frais/delete/<objectid:frais_projet_id>')
@login_required
def delete(frais_projet_id):
    frais = FraisProjet.objects.get(id=frais_projet_id)

    projet_id = frais.projet_id.id

    frais_tache = DetailFrais.objects(
        frais_projet_id = frais.id
    )

    if len(frais_tache):
        flash('Impossible de supprimer', 'danger')
    else:
        flash('Enregistrement effectue avec succes', 'success')
        frais.delete()
    return redirect(url_for('frais_projet.index', projet_id=projet_id))



@prefix_projet.route('/facturation')
@prefix_projet.route('/facturation/<frais_id>')
def facturations(frais_id = None):
    data = {}
    data['fact'] = 0
    data['nfact'] = 0
    if frais_id:
        frais = Frais.objects.get(id=frais_id)
        if frais.factu:
            data['fact'] = 1
        if frais.nfactu:
            data['nfact'] = 1
    resp = jsonify(data)
    return resp


@prefix_tache.route('/frais/<objectid:tache_id>/')
@login_required
def index(tache_id):
    menu = 'tache'
    submenu = 'tache'
    context = 'frais'
    title_page = 'Taches - Details - Frais'

    tache = Tache.objects.get(id=tache_id)

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)

    temps = Temps.objects(
        Q(tache_id=tache.id) & Q(date_start=start) & Q(date_end=end)
    ).first()

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = []
    pagination = None
    if temps:
        datas = DetailFrais.objects(temps_id=temps.id)

        pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='Frais de la tache')
        datas.paginate(page=page, per_page=10)

    return render_template('frais/frais_tache.html', **locals())


@prefix_tache.route('/frais/edit/<int:tache_id>', methods=['GET', 'POST'])
@prefix_tache.route('/frais/edit/<int:tache_id>/<int:detail_frais_id>', methods=['GET', 'POST'])
@login_required
def edit(tache_id, detail_frais_id=None):

    tache = Tache.get_by_id(tache_id)

    if detail_frais_id:
        detail_frais = DetailFrais.get_by_id(detail_frais_id)
        form = FormFraisTache(obj=detail_frais)
        form.frais_projet_id.data = detail_frais.frais_projet_id.get().key.id()
        if detail_frais.detail_fdt:
            form.detail_fdt.data = detail_frais.detail_fdt.get().key.id()
    else:
        detail_frais = DetailFrais()
        form = FormFraisTache()

    form.frais_projet_id.choices = [(0, 'Selectionnez le frais applique')]
    for frais in FraisProjet.query(FraisProjet.projet_id == tache.projet_id):
        form.frais_projet_id.choices.append((str(frais.id), frais.frais_id.get().libelle))

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)


    temps = Temps.query(
        Temps.tache_id == tache.key,
        Temps.date_start == start,
        Temps.date_end == end
    ).get()

    form.detail_fdt.choices = [(0, 'Selectionnez la FDT concernee')]
    if temps:
        for frais in DetailTemps.query(DetailTemps.temps_id == temps.key):
            form.detail_fdt.choices.append((frais.key.id(), frais.description))

    success = False
    if form.validate_on_submit():

        detail_frais.date = function.datetime_convert(form.date.data)
        detail_frais.montant = form.montant.data
        detail_frais.description = form.description.data

        frais_projet = FraisProjet.get_by_id(form.frais_projet_id.data)
        detail_frais.frais_projet_id = frais_projet.key

        if form.detail_fdt.data:
            details_DFT = DetailTemps.get_by_id(form.detail_fdt.data)
            detail_frais.detail_fdt = details_DFT.key

        if temps:
            detail_frais.temps_id = temps.key
        else:
            temps = Temps()
            temps.user_id = tache.user_id
            temps.date_start = function.datetime_convert(start)
            temps.date_end = function.datetime_convert(end)
            temps.tache_id = tache.key
            time = temps.put()
            detail_frais.temps_id = time

        detail_frais.put()

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('frais/frais_tache_edit.html', **locals())


@prefix_tache.route('/frais/delete/<int:detail_frais_id>')
@login_required
def delete(detail_frais_id):

    # Information du details des frais du FDT
    details_temps = DetailFrais.get_by_id(detail_frais_id)

    # Recuperation des details des frais correspondant a la meme FDT du frais a supprimer
    frais_detail_count = DetailFrais.query(
        details_temps.temps_id == details_temps.temps_id,
        details_temps.key != details_temps.key
    )

    temps_detail_count = DetailFrais.query(
        DetailFrais.temps_id == details_temps.temps_id
    )

    # id de la feuille de temps de la semaine
    temps_id = details_temps.temps_id.get().key.id()

    # id de la tache de la semaine
    tache_id = tache_id = details_temps.temps_id.get().tache_id.get().key.id()

    # if il n'existe plus de details temps correspondant a la FDT de la semaine, on le supprime.
    if not frais_detail_count.count() and not temps_detail_count.count():
        temps = Temps.get_by_id(temps_id)
        temps.key.delete()

    details_temps.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('frais_tache.index', tache_id=tache_id))