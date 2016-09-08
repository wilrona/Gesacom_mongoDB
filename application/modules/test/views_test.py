__author__ = 'Ronald'

from ...modules import *

prefix = Blueprint('home', __name__)

@prefix.route('/')
def index():

    return render_template('user/test.html', **locals())
