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
        username = data.get('body')
        trade_no = data.get('out_trade_no')
        from decimal import Decimal
        charge = int(Decimal(data.get('total_amount')) * 100)
        print("[{}] succeed user: {}, charge: {} order: {}".format(time_str(timestamp()), username, charge, trade_no))
        u = User.find_one(username=username)
        if trade_no not in u.charge_orders:
            u.charge_orders.append(trade_no)
            u.point += charge
            u.save()
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
