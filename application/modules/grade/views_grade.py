__author__ = 'Ronald'

from ...modules import *
from models_grade import Grade
from forms_grade import FormGrade


prefix = Blueprint('grade', __name__)


@prefix.route('/grade')
@login_required
@roles_required([('super_admin', 'grade')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'grade'
    title_page = 'Parametre - Grades'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Grade.objects()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='grades')

    datas.paginate(page=page, per_page=10)

    return render_template('grade/index.html', **locals())


@prefix.route('/grade/edit',  methods=['GET', 'POST'])
@prefix.route('/grade/edit/<objectid:grade_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'grade')], ['edit'])
def edit(grade_id=None):

    if grade_id:
        grades = Grade.objects.get(id=grade_id)
        form = FormGrade(obj=grades)
    else:
        grades = Grade()
        form = FormGrade()

    success = False
    if form.validate_on_submit():

        grades.libelle = form.libelle.data
        grades.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('grade/edit.html', **locals())


@prefix.route('/grade/delete/<objectid:grade_id>')
@login_required
@roles_required([('super_admin', 'grade')], ['delete'])
def delete(grade_id):
    grades = Grade.objects.get(id=grade_id)
    if not grades.count_user():
        grades.delete()
        flash('Suppression reussie', 'success')
    else:
        flash('Impossible de supprimer', 'danger')
    return redirect(url_for('grade.index'))