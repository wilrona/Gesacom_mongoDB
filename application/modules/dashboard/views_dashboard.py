__author__ = 'Ronald'

from ...modules import *
from ..societe.models_societe import Societe


prefix = Blueprint('dashboard', __name__)


@prefix.route('/')
@login_required
def index():
    title_page = 'Tableau de bord'

    entreprise = Societe.objects.first()
    if not entreprise:
        return redirect(url_for('societe.index'))

    return render_template('dashboard/index.html', **locals())