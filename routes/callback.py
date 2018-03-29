from routes import *
from flask import current_app as app

import qiniu
from config import key

q = qiniu.Auth(key.qiniu_access_key, key.qiniu_secret_key)

main = Blueprint('callback', __name__)


@main.route('/ali', methods=["GET", "POST"])
def ali():
    data = request.form.to_dict()
    signature = data.pop("sign")

    # print(json.dumps(data))
    # print(signature)

    # verify
    from alipay import AliPay
    alipay = AliPay(
        appid=app.config['ALIPAY_APPID'],
        app_notify_url=app.config['ALIPAY_CALLBACK_URL'],  # 默认回调url
        app_private_key_path=app.config['ALIPAY_PRIVATE_KEY_PATH'],
        alipay_public_key_path=app.config['ALIPAY_PUBLIC_KEY_PATH'],  # 支付宝的公钥
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False,  # 默认False
    )
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        body = data.get('body')
        body_split = body.split(':')
        if body_split[0] == 'charge':
            username = body_split[1]
            trade_no = data.get('out_trade_no')
            from decimal import Decimal
            charge = int(Decimal(data.get('total_amount')))
            print("[{}] succeed user: {}, charge: {} order: {}".format(time_str(timestamp()), username, charge, trade_no))
            u = User.find_one(username=username)
            if trade_no not in u.charge_orders:
                u.charge_orders.append(trade_no)
                u.point += charge
                u.save()
                d = dict(
                    user_id=u.id,
                    user_name=u.username,
                    model='user',
                    action='charge',
                    content='用户充值成功，点数：{}'.format(charge),
                )
                Log.new(d)
        elif body_split[0] == 'bill':
            bill_uuid = body_split[1]
            bill = Bill.find_one(uuid=bill_uuid)
            if bill.status == 0:
                bill.pay()
                u = User.find_one(mt4_id=bill.mt4_id)
                d = dict(
                    user_id=u.id,
                    user_name=u.username,
                    model='user',
                    action='bill_pay_now',
                    content='用户支付订单：{}，支付成功。 支付方式：直接支付{}'.format(bill.title, bill.amount_point),
                )
                Log.new(d)
        return json.dumps({"success": True})
    return json.dumps({"success": False})


@main.route('/all', methods=['POST'])
def product_add():
    body = request.get_data()
    body = body.decode('utf-8')
    form = request.form
    auth = request.headers.get('Authorization')
    url = app.config['QINIU_CALLBACK_URL']

    verify = q.verify_callback(auth, url, body)
    if verify:
        pass
    r = {"success": True}
    return json.dumps(r)
