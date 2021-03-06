from . import *
from models.product import Product

main = Blueprint('index', __name__)


@main.route('/')
@login_required
def index():
    u = current_user()
    ps = Product.all()
    return render_template('index.html', u=u, ps=ps, cats=get_cats())


@main.route('/', methods=['POST'])
@login_required
def index_search():
    u = current_user()
    search = request.form.get('search', None)
    if search is not None:
        ps = Product.find(name={'$regex': search, '$options': '$i'})
        return render_template('index.html', u=u, ps=ps)
    else:
        return redirect(url_for('index.index'))
