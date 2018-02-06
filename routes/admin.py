from routes import *
from models.category import Category
from models.product import Product
from models.order import Order
from models.user import User
from models.server import Server
from models.wl import Wl
from models.notice import Notice
from flask import current_app as app

# import qiniu
from config import key

# q = qiniu.Auth(key.qiniu_access_key, key.qiniu_secret_key)

main = Blueprint('admin', __name__)


# ------------------------- 分类管理 --------------------------

@main.route('/category/new', methods=['POST'])
@admin_required
def category_new():
    form = request.form
    status, msgs = Category.valid(form)
    if status is True:
        Category.new(form)
    return redirect(url_for('admin.category'))


@main.route('/category')
@admin_required
def category():
    u = current_user()
    ms = Category.find(father_name='')
    for m in ms:
        m.sons = Category.find(father_name=m.name)
    return render_template('admin/category.html', ms=ms, u=u)


@main.route('/category/del/<uuid>')
@admin_required
def category_del(uuid):
    m = Category.find_one(uuid=uuid)
    m.delete()
    return redirect(url_for('admin.category'))


@main.route('/category/<uuid>', methods=['POST'])
@admin_required
def category_update(uuid):
    p = Product.find_one(uuid=uuid)
    form = request.form
    p.update(form)
    return redirect(url_for('admin.product', uuid=p.uuid))


# ------------------------- 产品管理 --------------------------
@main.route('/product/new')
@admin_required
def product_new_page():
    u = current_user()
    u.cates = Category.find(father_name={'$ne': ''})
    return render_template('admin/product_new.html', u=u)


@main.route('/product/new', methods=['POST'])
@admin_required
def product_new():
    u = current_user()
    form = request.form
    status, msgs = Product.valid(form)
    if status is True:
        p = Product.new(form)
        return redirect(url_for('admin.product', uuid=p.uuid))
    else:
        return render_template('admin/product_new.html', msgs=msgs, u=u)


@main.route('/products')
@admin_required
def products():
    u = current_user()
    ms = Product.all()
    ms.reverse()
    return render_template('admin/products.html', ms=ms, u=u)


@main.route('/products', methods=['POST'])
@admin_required
def products_search():
    u = current_user()
    form = request.form
    ms = Product.search_or(form)
    ms.reverse()
    return render_template('admin/products.html', u=u, ms=ms)


@main.route('/product/<uuid>')
@admin_required
def product(uuid):
    u = current_user()
    p = Product.find_one(uuid=uuid)
    policy = {
        'callbackUrl': app.config['QINIU_CALLBACK_URL'],
        'callbackBody': 'filename=$(fname)&filesize=$(fsize)&route=$(x:route)&',
        'mimeLimit': 'image/*',
    }
    t = timestamp()
    qiniu_key = '{}{}_{}.{}'.format(app.config['CDN_PRODUCT_PIC_DIR'], uuid, t, app.config['PRODUCT_PIC_EXT'])
    # u.token = q.upload_token(app.config['CDN_BUCKET'], key=qiniu_key, policy=policy)
    u.upload_url = app.config['PIC_UPLOAD_URL']
    u.key = qiniu_key
    u.url = url_for('admin.ajax_pic', uuid=uuid)
    p.cates = Category.find(father_name={'$ne': ''})
    return render_template('admin/product.html', p=p, u=u)


@main.route('/product/<uuid>', methods=['POST'])
@admin_required
def product_update(uuid):
    p = Product.find_one(uuid=uuid)
    form = request.form
    p.update(form)
    return redirect(url_for('admin.product', uuid=p.uuid))


@main.route('/product/picture/url/<uuid>', methods=['POST'])
@admin_required
def set_product_pic_url(uuid):
    p = Product.find_one(uuid=uuid)
    url = request.form.get('file_url')
    p.set_pic_url(url)
    return redirect(url_for('admin.product', uuid=p.uuid))


@main.route('/picture/ajax/<uuid>', methods=['POST'])
@admin_required
def ajax_pic(uuid):
    p = Product.find_one(uuid=uuid)
    qiniu_key = request.form.get('key')
    p.qiniu_pic(qiniu_key)
    return redirect(url_for('admin.product', uuid=p.uuid))


@main.route('/product/<uuid>/pic/upload', methods=['POST'])
@admin_required
def pic_upload(uuid):
    p = Product.find_one(uuid=uuid)
    pic = request.files['pic']
    pic = p.pic_upload(pic)
    if pic is not False:
        return json.dumps({'status': 'success', 'msg': '上传成功：' + pic, 'pic': pic})
    else:
        return json.dumps({'status': 'danger', 'msg': '上传失败'})


@main.route('/product/<uuid>/pic/del/<pic>', methods=['GET'])
@admin_required
def pic_del(uuid, pic):
    p = Product.find_one(uuid=uuid)
    p.pic_del(pic)
    return json.dumps({'status': 'success', 'msg': '已删除：' + pic})


@main.route('/delete/<int:id>')
@admin_required
def product_delete(id):
    # p = Model.get(id)
    # p.delete()
    # TODO 先不让删
    return redirect(url_for('admin.products'))


# ------------------------- 用户管理 --------------------------
@main.route('/users')
@manager_required
def users():
    u = current_user()
    ms = User.all()
    return render_template('admin/users.html', ms=ms, u=u)


@main.route('/users', methods=['POST'])
@manager_required
def users_search():
    u = current_user()
    form = request.form
    ms = User.search_or(form)
    return render_template('admin/users.html', u=u, ms=ms)


@main.route('/user/<int:id>')
@manager_required
def user(id):
    u = current_user()
    m = User.get(id)
    ps = m.get_cart_detail()
    return render_template('admin/user.html', m=m, ps=ps, u=u)


@main.route('/user/delete/<int:id>')
@admin_required
def user_delete(id):
    # m = User.get(id)
    # m.delete()
    ms = User.find(id=id)
    for m in ms:
        m.delete()
    return redirect(url_for('admin.users'))


@main.route('/user/update/<int:id>', methods=['POST'])
@manager_required
def user_update(id):
    m = User.get(id)
    form = request.form
    m.update_user(form)
    return redirect(url_for('admin.user', id=m.id))


@main.route('/user/update/role/<int:id>', methods=['POST'])
@admin_required
def user_update_role(id):
    m = User.get(id)
    form = request.form
    m.update_user_role(form)
    return redirect(url_for('admin.user', id=m.id))


@main.route('/user/new', methods=['POST'])
@manager_required
def user_new():
    form = request.form
    status, msgs = User.valid(form)
    print(status, msgs)
    if status is True:
        User.new(form)
    return redirect(url_for('admin.users'))


# ------------------------- 白标管理 --------------------------
def connect_db(ip):
    if ip is None:
        return redirect(url_for('admin.servers'))
    s = Server.find_one(ip=ip)
    db_uri = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8'.format(s.username, s.password, s.ip, s.dbname)
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import OperationalError
    try:
        engine = create_engine(db_uri, echo=True)
        Se = sessionmaker(bind=engine)
        se = Se()
        return se
    except OperationalError as e:
        flash('数据库拒绝链接，请联系数据库管理员：{}'.format(e), 'error')
        return redirect(url_for('admin.servers'))


@main.route('/servers')
@manager_required
def servers():
    u = current_user()
    ms = Server.all()
    return render_template('admin/servers.html', ms=ms, u=u)


@main.route('/server/new', methods=['POST'])
@manager_required
def server_new():
    form = request.form
    # print(form)
    Server.new(form)
    return redirect(url_for('admin.servers'))


@main.route('/wls')
@manager_required
def wls():
    u = current_user()
    dbs = Server.all()
    return render_template('admin/wls.html', dbs=dbs, u=u)


@main.route('/wls', methods=['POST'])
@manager_required
def wls_link():
    u = current_user()
    dbs = Server.all()
    form = request.form
    ip = form.get('ip', None)
    se = connect_db(ip)
    ms = se.query(Wl).all()
    return render_template('admin/wls.html', dbs=dbs, u=u, ms=ms)


@main.route('/notices')
@manager_required
def notices():
    u = current_user()
    dbs = Server.all()
    return render_template('admin/notices.html', dbs=dbs, u=u)


@main.route('/notices', methods=['POST'])
@manager_required
def notices_link():
    u = current_user()
    dbs = Server.all()
    form = request.form
    ip = form.get('ip', None)
    se = connect_db(ip)
    ms = se.query(Notice).all()
    wls_all = se.query(Wl).all()
    wls_simple = []
    counter = []
    for i in wls_all:
        if i.mt4_id not in counter:
            wls_simple.append(i)
            counter.append(i.mt4_id)
    return render_template('admin/notices.html', dbs=dbs, u=u, ms=ms, wls=wls_simple, ip=ip)


@main.route('/notices/new', methods=['POST'])
@manager_required
def notice_new():
    form = request.form
    ip = form.get('ip', None)
    se = connect_db(ip)
    n = Notice.new(form)
    se.add(n)
    se.commit()
    return redirect(url_for('admin.notices_link', _method='POST', ip=form.get('ip')), code=307)


# ------------------------- 订单管理 --------------------------
@main.route('/orders')
@admin_required
def orders():
    u = current_user()
    ms = Order.all()
    ms.reverse()
    return render_template('admin/orders.html', ms=ms, u=u)


@main.route('/orders', methods=['POST'])
@admin_required
def orders_search():
    u = current_user()
    form = request.form
    ms = Order.search_or(form)
    ms.reverse()
    return render_template('admin/orders.html', u=u, ms=ms)


@main.route('/order/<orderNo>')
@admin_required
def order(orderNo):
    u = current_user()
    o = Order.find_one(orderNo=orderNo)
    o.user = User.get(o.user_id)
    return render_template('admin/order.html', o=o, u=u)


@main.route('/order/delivery/<orderNo>')
@admin_required
def order_delivery(orderNo):
    o = Order.find_one(orderNo=orderNo)
    o.delivery()
    return redirect(url_for('admin.orders'))


@main.route('/order/finish/<orderNo>')
@admin_required
def order_finish(orderNo):
    o = Order.find_one(orderNo=orderNo)
    o.finish()
    return redirect(url_for('admin.orders'))

# # 管理员初始化
# @main.route('/root')
# @login_required
# def root_set():
#     root = User.find_one(username='root')
#     root.role = 'admin'
#     root.save()
#     return redirect(url_for('admin.products'))

# @main.route('/uuid_reset_all')
# @admin_required
# def order_no_reset():
#     os = Order.all()
#     us = User.all()
#     ps = Product.all()
#     for o in os:
#         o.set_uuid('orderNo')
#         o.set_uuid()
#     for u in us:
#         u.set_uuid()
#     for p in ps:
#         p.set_uuid()
#     return redirect(url_for('admin.products'))
#
#
# @main.route('/clear_order_items')
# @admin_required
# def clear_order_items():
#     os = Order.all()
#     for o in os:
#         o.items = []
#         o.save()
#     return redirect(url_for('admin.products'))


# @main.route('/clear_orders')
# @admin_required
# def clear_orders():
#     os = Order.all()
#     for o in os:
#         o.delete()
#     return redirect(url_for('admin.products'))
#
#
# @main.route('/clear_carts')
# @admin_required
# def clear_carts():
#     us = User.all()
#     for u in us:
#         u.cart_clear()
#     return redirect(url_for('admin.products'))
