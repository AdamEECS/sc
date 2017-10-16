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
        from decimal import Decimal
        charge = int(Decimal(data.get('total_amount')) * 100)
        print("trade succeed user: {}, charge: {}".format(username, charge))
        u = User.find(username=username)
        u.point += charge
        u.save()


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
