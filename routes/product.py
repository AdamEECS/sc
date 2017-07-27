from . import *
from models.product import Product

main = Blueprint('product', __name__)


@main.route('/detail/<uuid>')
@login_required
def detail(uuid):
    u = current_user()
    p = Product.find_one(uuid=uuid)

    return render_template('product/detail.html', p=p, u=u, cats=get_cats())


@main.route('/category/<category>')
@login_required
def products(category):
    u = current_user()
    ps = Product.find(category=category)
    return render_template('product/products.html', ps=ps, u=u, category=category, cats=get_cats())
