from routes import *
from models.wl import WlLocal

main = Blueprint('api', __name__)


@main.route('/cart/add', methods=['POST'])
@login_required
def cart_add():
    u = current_user()
    product_uuid = request.json.get('product_uuid', None)
    response = dict(
        status='error',
    )
    u.cart_add(product_uuid)
    response['status'] = 'OK'
    return json.dumps(response)


@main.route('/cart/sub', methods=['POST'])
@login_required
def cart_sub():
    u = current_user()
    product_uuid = request.json.get('product_uuid', None)
    response = dict(
        status='error',
    )
    u.cart_sub(product_uuid)
    response['status'] = 'OK'
    return json.dumps(response)


@main.route('/wlstatus', methods=['GET'])
def wl_status():
    mt4_id = request.args.get('id', None)
    key = request.args.get('key', None)
    if key != 'dcc4ec5c5612':
        return json.dumps('permission denied')
    m = WlLocal.find_one(mt4_id=mt4_id)
    if m is None:
        return json.dumps('permission denied')
    return json.dumps(m.status)
