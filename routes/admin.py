from routes import *
from models.category import Category
from models.product import Product
from models.order import Order
from models.user import User
from models.server import Server
from models.wl import Wl, WlLocal
from models.notice import Notice
from models.bill import Bill
from models.log import Log
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
@manager_required
def product_new_page():
    u = current_user()
    u.cates = Category.find(father_name={'$ne': ''})
    return render_template('admin/product_new.html', u=u)


@main.route('/product/new', methods=['POST'])
@manager_required
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
@manager_required
def products():
    u = current_user()
    ms = Product.all()
    ms.reverse()
    return render_template('admin/products.html', ms=ms, u=u)


@main.route('/products', methods=['POST'])
@manager_required
def products_search():
    u = current_user()
    form = request.form
    ms = Product.search_or(form)
    ms.reverse()
    return render_template('admin/products.html', u=u, ms=ms)


@main.route('/product/<uuid>')
@manager_required
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
@manager_required
def product_update(uuid):
    p = Product.find_one(uuid=uuid)
    form = request.form
    p.update(form)
    return redirect(url_for('admin.product', uuid=p.uuid))


@main.route('/product/picture/url/<uuid>', methods=['POST'])
@manager_required
def set_product_pic_url(uuid):
    p = Product.find_one(uuid=uuid)
    url = request.form.get('file_url')
    p.set_pic_url(url)
    return redirect(url_for('admin.product', uuid=p.uuid))


@main.route('/picture/ajax/<uuid>', methods=['POST'])
@manager_required
def ajax_pic(uuid):
    p = Product.find_one(uuid=uuid)
    qiniu_key = request.form.get('key')
    p.qiniu_pic(qiniu_key)
    return redirect(url_for('admin.product', uuid=p.uuid))


@main.route('/product/<uuid>/pic/upload', methods=['POST'])
@manager_required
def pic_upload(uuid):
    p = Product.find_one(uuid=uuid)
    pic = request.files['pic']
    pic = p.pic_upload(pic)
    if pic is not False:
        return json.dumps({'status': 'success', 'msg': '上传成功：' + pic, 'pic': pic})
    else:
        return json.dumps({'status': 'danger', 'msg': '上传失败'})


@main.route('/product/<uuid>/pic/del/<pic>', methods=['GET'])
@manager_required
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
@finance_required
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
@finance_required
def user(id):
    u = current_user()
    m = User.get(id)
    ps = m.get_cart_detail()
    return render_template('admin/user.html', m=m, ps=ps, u=u)


@main.route('/user/delete/<uuid>')
@admin_required
def user_delete(uuid):
    m = User.get_uuid(uuid)
    m.deleted = True
    m.save()
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


@main.route('/user/<int:id>/point', methods=['POST'])
@manager_required
def user_point_add(id):
    m = User.get(id)
    form = request.form
    m.point += int(form.get('point', 0))
    m.save()
    cu = current_user()
    d = dict(
        user_id=cu.id,
        user_name=cu.username,
        model='admin',
        action='point_add',
        content='管理员操作用户点数，用户：{} 点数：{}'.format(m.username, form.get('point')),
    )
    Log.new(d)
    return redirect(url_for('admin.user', id=m.id))


@main.route('/user/new', methods=['POST'])
@manager_required
def user_new():
    form = request.form
    status, msgs = User.valid(form)
    print(status, msgs)
    if status is True:
        User.new(form)
        cu = current_user()
        d = dict(
            user_id=cu.id,
            user_name=cu.username,
            model='admin',
            action='user_new',
            content='管理员创建用户，用户：{}'.format(form.get('username')),
        )
        Log.new(d)
    return redirect(url_for('admin.users'))


# ------------------------- 白标管理 --------------------------
def connect_db(ip):
    if ip is None:
        return
    s = Server.find_one(ip=ip)
    if s is None:
        flash('请先链接到数据库', 'warning')
        return
    db_uri = 'mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8'.format(s.username, s.password, s.ip, s.dbname)
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import OperationalError
    try:
        engine = create_engine(db_uri)
        # print(time_str(timestamp()), 'engine', engine)
        Se = sessionmaker(bind=engine)
        se = Se()
        # print(time_str(timestamp()), se, se.is_active)
        return se
    except OperationalError as e:
        flash('数据库拒绝链接，请联系数据库管理员：{}'.format(e), 'danger')
        return


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


@main.route('/server/del', methods=['GET'])
@manager_required
def server_del():
    ip = request.args.get('ip')
    # print(form)
    s = Server.find_one(ip=ip)
    s.delete()
    return redirect(url_for('admin.servers'))


@main.route('/wls')
@finance_required
def wls():
    u = current_user()
    ms = WlLocal.all()
    return render_template('admin/wls.html', u=u, ms=ms)


@main.route('/wl/new', methods=['POST'])
@manager_required
def wl_new():
    form = request.form
    if WlLocal.valid(form):
        WlLocal.new(form)
        cu = current_user()
        d = dict(
            user_id=cu.id,
            user_name=cu.username,
            model='admin',
            action='wl_new',
            content='管理员添加白标，白标id：{} 公司名：{}'.format(form.get('mt4_id'), form.get('name')),
        )
        Log.new(d)
    return redirect(url_for('admin.wls'))


@main.route('/wl/<mt4_id>/status/toggle')
@manager_required
def wl_toggle(mt4_id):
    m = WlLocal.find_one(mt4_id=mt4_id)
    if m.status == 2:
        m.status = 1
    else:
        m.status = 2
    m.save()
    cu = current_user()
    d = dict(
        user_id=cu.id,
        user_name=cu.username,
        model='admin',
        action='wl_toggle',
        content='管理员修改白标状态，白标id：{} 公司名：{} 修改值：{}'.format(m.mt4_id, m.name, m.status),
    )
    Log.new(d)
    return redirect(url_for('admin.wls'))


@main.route('/wl/<uuid>/del')
@admin_required
def wl_del(uuid):
    m = WlLocal.find_one(uuid=uuid)
    m.delete()
    return redirect(url_for('admin.wls'))


@main.route('/wl/<mt4_id>/detail')
@finance_required
def wl_detail(mt4_id):
    u = current_user()
    m = WlLocal.find_one(mt4_id=mt4_id)
    m.bills = Bill.find(mt4_id=mt4_id)
    return render_template('admin/wl_detail.html', u=u, m=m)


@main.route('/bill/new', methods=['POST'])
@finance_required
def bill_new():
    form = request.form
    mt4_id = form.get('mt4_id')
    file = request.files.get('file')
    Bill.new(form, file=file)
    cu = current_user()
    d = dict(
        user_id=cu.id,
        user_name=cu.username,
        model='admin',
        action='bill_new',
        content='管理员创建账单，白标id：{} 标题：{}'.format(form.get('mt4_id'), form.get('title')),
    )
    Log.new(d)
    return redirect(url_for('admin.wl_detail', mt4_id=mt4_id))


@main.route('/bill/<mt4_id>/<uuid>/del')
@finance_required
def bill_del(mt4_id, uuid):
    b = Bill.find_one(uuid=uuid)
    if b.status != 0:
        flash('该订单已被支付，不可删除', 'danger')
        return redirect(url_for('admin.wl_detail', mt4_id=mt4_id))
    else:
        b.delete()
        cu = current_user()
        d = dict(
            user_id=cu.id,
            user_name=cu.username,
            model='admin',
            action='bill_del',
            content='管理员删除账单，白标id：{} 标题：{}'.format(mt4_id, b.title),
        )
        Log.new(d)
        return redirect(url_for('admin.wl_detail', mt4_id=mt4_id))


@main.route('/notices')
@manager_required
def notices():
    u = current_user()
    dbs = Server.all()
    return render_template('admin/notices.html', dbs=dbs, u=u)


@main.route('/notices_link', methods=['GET'])
@manager_required
def notices_link():
    u = current_user()
    dbs = Server.all()
    form = request.args
    ip = form.get('ip', None)
    try:
        se = connect_db(ip)
        ms = se.query(Notice).all()
        ms.reverse()
    except Exception as e:
        ms = []
        flash('数据库拒绝链接，请联系数据库管理员：{}'.format(e), 'danger')
    # wls_all = se.query(Wl).all()
    # wls_simple = []
    # counter = []
    # for i in wls_all:
    #     if i.mt4_id not in counter:
    #         wls_simple.append(i)
    #         counter.append(i.mt4_id)
    return render_template('admin/notices.html', dbs=dbs, u=u, ms=ms, ip=ip)


@main.route('/notices/new', methods=['POST'])
@manager_required
def notice_new():
    form = request.form
    ip = form.get('ip', None)
    se = connect_db(ip)
    if se is not None:
        n = Notice.new(form)
        se.add(n)
        se.commit()
        cu = current_user()
        d = dict(
            user_id=cu.id,
            user_name=cu.username,
            model='admin',
            action='notice_new',
            content='管理员发布通知，白标id：{} 标题：{}'.format(n.mt4_id, n.title),
        )
        Log.new(d)
        return redirect(url_for('admin.notices_link', _method='GET', ip=form.get('ip')))
    return redirect(url_for('admin.notices'))


@main.route('/notice/<ip>/<id>/del')
@manager_required
def notice_del(ip, id):
    se = connect_db(ip)
    if se is not None:
        n = se.query(Notice).get(id)
        se.delete(n)
        se.commit()
        return redirect(url_for('admin.notices_link', _method='GET', ip=ip))
    return redirect(url_for('admin.notices'))


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


# ------------------------- 日志管理 --------------------------
@main.route('/logs')
@manager_required
def logs():
    u = current_user()
    ms = Log.all()
    return render_template('admin/logs.html', ms=ms, u=u)


@main.route('/logs', methods=['POST'])
@admin_required
def logs_search():
    u = current_user()
    form = request.form
    ms = Log.search_or(form)
    return render_template('admin/logs.html', u=u, ms=ms)

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


@main.route('/clear_bill_point')
@admin_required
def clear_bill_point():
    bs = Bill.all()
    for b in bs:
        if '（' in str(b.amount):
            b.amount = int(str(b.amount).split('（')[0])
            b.save()
    return redirect(url_for('admin.wls'))
