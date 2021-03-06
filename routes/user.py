from routes import *
from models.user import User
from models.order import Order
from models.brought import Brought
from models.wl import WlLocal
from models.bill import Bill
from models.log import Log
from decimal import Decimal
from flask import current_app as app

main = Blueprint('user', __name__)

Model = User


@main.route('/login')
def index():
    return render_template('user/login.html')


@main.route('/login', methods=['POST'])
def login():
    form = request.form
    username = form.get('username', '')
    captcha = form.get('captcha', '').lower()
    if captcha != session.get('captcha', 'no captcha!'):
        flash('验证码错误', 'warning')
        return redirect(url_for('user.index'))
    u = User.find_one(username=username)
    if u is not None and u.validate_login(form):
        session['uid'] = u.id
        return redirect(url_for('index.index'))
    else:
        flash('用户名密码错误', 'warning')
        return redirect(url_for('user.index'))


@main.route('/register')
@login_required
def register_page():
    return render_template('user/register.html')


@main.route('/register', methods=['POST'])
@login_required
def register():
    form = request.form
    captcha = form.get('captcha', '').lower()
    if captcha != session.get('captcha', 'no captcha!'):
        flash('验证码错误', 'warning')
        return redirect(url_for('user.register'))
    status, msgs = User.valid(form)
    if status is True:
        u = User.new(form)
        u.send_email_verify(u.email)
        session['uid'] = u.id
        flash('验证邮件已发送，请查收', 'info')
        return redirect(url_for('index.index'))
    else:
        for msg in msgs:
            flash(msg, 'warning')
        return redirect(url_for('user.register'))


@main.route('/password/forget')
@login_required
def forget_password():
    return render_template('user/forget_password.html')


@main.route('/password/forget', methods=['POST'])
@login_required
def forget_password_send():
    form = request.form
    captcha = form.get('captcha', '').lower()
    if captcha != session.get('captcha', 'no captcha!'):
        flash('验证码错误', 'warning')
        return redirect(url_for('user.forget_password'))
    r = User.forget_password(form)
    if r:
        flash('密码重置邮件已经发送，请查收邮箱', 'success')
    else:
        flash('用户名或邮箱不匹配', 'warning')
    return redirect(url_for('user.forget_password'))


@main.route('/email/verify/<tb64>')
@login_required
def email_verify(tb64):
    if User.email_verify(tb64):
        flash('邮箱验证通过', 'success')
    else:
        flash('邮箱验证失败', 'danger')
    return redirect(url_for('user.profile'))


@main.route('/password/forget/verify/<tb64>')
@login_required
def forget_password_verify(tb64):
    if User.forget_password_verify(tb64):
        flash('重置邮件验证通过', 'success')
        return render_template('user/reset_password.html', tb64=tb64)
    else:
        flash('重置邮件验证失败', 'danger')
        return redirect(url_for('user.index'))


@main.route('/password/reset/<tb64>', methods=['POST'])
@login_required
def reset_password(tb64):
    password = request.form.get('password', '')
    if User.forget_password_verify(tb64):
        u = User.get_user_by_tb64(tb64)
        u.reset_password(password)
        session['uid'] = u.id
        flash('密码已重置', 'success')
        return redirect(url_for('index.index'))
    else:
        flash('重置邮件验证失败', 'warning')
        return redirect(url_for('user.index'))


@main.route('/product')
@login_required
def product():
    cu = current_user()
    os = Brought.get_by_user(cu.uuid)
    return render_template('user/product.html', u=cu, os=os)


@main.route('/bills')
@login_required
def bills():
    cu = current_user()
    m = WlLocal.find_one(mt4_id=cu.mt4_id)
    m.bills = Bill.find(mt4_id=cu.mt4_id)
    return render_template('user/bills.html', u=cu, m=m)


@main.route('/bill/<uuid>/pay')
@login_required
def bill_pay(uuid):
    cu = current_user()
    b = Bill.find_one(uuid=uuid)
    if b.amount_point > cu.point:
        flash('为支付当前账单，请充值：{}'.format(b.amount_point - cu.point), 'warning')
        return redirect(url_for('user.profile'))
    cu.point -= b.amount_point
    cu.save()
    b.status = 1
    b.save()
    d = dict(
        user_id=cu.id,
        user_name=cu.username,
        model='user',
        action='bill_pay',
        content='用户支付订单：{}，支付成功。 支付方式：扣除余额{}'.format(b.title, b.amount_point),
    )
    Log.new(d)
    flash('支付成功', 'success')
    return redirect(url_for('user.bills'))


@main.route('/bill/<uuid>/pay_now')
@login_required
def bill_pay_now(uuid):
    cu = current_user()
    wl = WlLocal.find_one(mt4_id=cu.mt4_id)
    b = Bill.find_one(uuid=uuid)
    from alipay import AliPay
    alipay = AliPay(
        appid=app.config['ALIPAY_APPID'],
        app_notify_url=app.config['ALIPAY_CALLBACK_URL'],  # 默认回调url
        app_private_key_path=app.config['ALIPAY_PRIVATE_KEY_PATH'],
        alipay_public_key_path=app.config['ALIPAY_PUBLIC_KEY_PATH'],  # 支付宝的公钥
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False,  # 默认False
    )
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=short_uuid(),
        total_amount=b.amount_point,
        body='bill:{}'.format(b.uuid),
        subject='{} - {} - {}'.format(wl.mt4_id, wl.name, b.title),
        return_url=app.config['ALIPAY_RETURN_URL'],
    )
    url = 'https://openapi.alipay.com/gateway.do?' + order_string
    return redirect(url)


@main.route('/charge', methods=['POST'])
@login_required
def charge():
    cu = current_user()
    wl = WlLocal.find_one(mt4_id=cu.mt4_id)
    form = request.form
    from alipay import AliPay
    alipay = AliPay(
        appid=app.config['ALIPAY_APPID'],
        app_notify_url=app.config['ALIPAY_CALLBACK_URL'],  # 默认回调url
        app_private_key_path=app.config['ALIPAY_PRIVATE_KEY_PATH'],
        alipay_public_key_path=app.config['ALIPAY_PUBLIC_KEY_PATH'],  # 支付宝的公钥
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False,  # 默认False
    )
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=short_uuid(),
        total_amount=form.get('charge'),
        body='charge:{}'.format(cu.username),
        subject='{} - {} - {}'.format(wl.mt4_id, wl.name, '充值'),
        return_url=app.config['ALIPAY_RETURN_URL'],
    )
    url = 'https://openapi.alipay.com/gateway.do?' + order_string

    return redirect(url)


@main.route('/profile')
@login_required
def profile():
    cu = current_user()
    return render_template('user/profile.html', u=cu)


@main.route('/profile', methods=['POST'])
@login_required
def profile_update():
    cu = current_user()
    form = request.form
    cu.safe_update_user(form)
    flash('信息已更新', 'success')
    return redirect(url_for('user.profile'))


@main.route('/email/update', methods=['POST'])
@login_required
def update_email():
    u = current_user()
    form = request.form
    new_email = form.get('email', '')
    captcha = form.get('captcha', '').lower()
    if captcha != session.get('captcha', 'no captcha!'):
        return json.dumps({'status': 'warning', 'msg': '验证码错误'})
    if User.has(email=new_email) and User.find_one(email=new_email).uuid != u.uuid:
        return json.dumps({'status': 'warning', 'msg': '该邮箱已被占用'})
    if u.validate_login(form):
        u.send_email_verify(new_email)
        return json.dumps({'status': 'info', 'msg': '已发送验证邮件，请查收'})
    else:
        return json.dumps({'status': 'warning', 'msg': '密码错误'})


@main.route('/avatar/upload', methods=['POST'])
@login_required
def avatar():
    u = current_user()
    avatar = request.files['avatar']
    u.update_avatar(avatar)
    return redirect(url_for('.profile'))


@main.route('/cart/add', methods=['GET'])
@login_required
def cart_add():
    u = current_user()
    product_uuid = request.args.get('product_uuid', None)
    u.cart_add(product_uuid)
    return redirect(url_for('user.cart'))


@main.route('/cart/sub', methods=['GET'])
@login_required
def cart_sub():
    u = current_user()
    product_uuid = request.args.get('product_uuid', None)
    u.cart_sub(product_uuid)
    return redirect(url_for('user.cart'))


@main.route('/cart')
@login_required
def cart():
    u = current_user()
    ps = u.get_cart_detail()
    u.count_num = u.get_cart_count()
    u.count_price = str(sum([Decimal(p.sum) for p in ps]))
    return render_template('user/cart.html', u=u, ps=ps)


@main.route('/cart/clear')
@login_required
def cart_clear():
    u = current_user()
    u.cart_clear()
    return redirect(url_for('user.cart'))


@main.route('/logout')
@login_required
def logout():
    p = session.pop('uid')

    flash('账号已安全退出', 'success')
    return redirect(url_for('index.index'))


@main.route('/order/check')
@login_required
@cart_not_empty_required
# @email_verify_required
def check_order():
    u = current_user()
    u.add = u.get_default_add()
    ps = u.get_cart_detail()
    u.count_num = u.get_cart_count()
    u.count_price = str(sum([Decimal(p.sum) for p in ps]))
    return render_template('user/check_order.html', u=u, ps=ps)


@main.route('/pay', methods=['POST'])
@login_required
@cart_not_empty_required
# @email_verify_required
def pay():
    u = current_user()
    form = request.form
    u.buy(form)
    return redirect(url_for('user.orders'))


@main.route('/orders')
@login_required
def orders():
    u = current_user()
    os = u.orders()
    return render_template('user/orders.html', os=os, u=u)


@main.route('/order/<orderNo>')
@login_required
def order(orderNo):
    u = current_user()
    o = Order.find_one(orderNo=orderNo)
    if o is not None and o.user_id == u.id:
        return render_template('user/order.html', o=o, u=u)
    else:
        return redirect(url_for('user.orders'))


@main.route('/address')
@login_required
def address():
    cu = current_user()
    address_id = int(request.args.get('id', -1))
    if address_id >= 0:
        address_editing = safe_list_get(cu.add_list, address_id, None)
        if address_editing:
            address_editing['id'] = address_id
    else:
        address_editing = None
    return render_template('user/address.html', u=cu, a=address_editing)


@main.route('/address', methods=['POST'])
@login_required
def address_add():
    cu = current_user()
    form = request.form
    add = form.to_dict()
    cu.add_list.append(add)
    cu.save()
    return render_template('user/address.html', u=cu)


@main.route('/address/update/<int:id>', methods=['POST'])
@login_required
def address_update(id):
    cu = current_user()
    form = request.form
    add = form.to_dict()
    try:
        cu.add_list[id] = add
        cu.save()
    except IndexError:
        pass
    return redirect(url_for('user.address'))


@main.route('/address/default/<int:id>')
@login_required
def address_default(id):
    cu = current_user()
    cu.add_default = id
    cu.save()
    return redirect(url_for('user.address'))
