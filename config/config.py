from pymongo import *
import os

config_dict = dict(
    USER_AVATAR_DIR='static/user_avatar/',
    PRODUCT_PIC_DIR='static/product_pic/',
    UPLOAD_FILE_DIR='static/files/',
    PRODUCT_PIC_EXT='png',
    CDN_URL='http://opguqe876.bkt.clouddn.com/',
    CDN_USER_AVATAR_DIR='/user_avatar/',
    CDN_PRODUCT_PIC_DIR='/product_pic/',
    CDN_BUCKET='buy-suzumiya',
    QINIU_CALLBACK_URL='https://buy.suzumiya.cc/callback/all',
    PIC_UPLOAD_URL='https://up-z1.qbox.me/',
    SEND_EMAIL_URL='https://api.mailgun.net/v3/mg.suzumiya.cc/messages',
    SEND_EMAIL_FROM='Suzumiya <no-replay@mg.suzumiya.cc>',
    BASE_URL='http://localhost:8001',
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    ALLOWED_UPLOAD_TYPE=['jpg', 'jpeg', 'gif', 'png', 'ico'],
    PINGPP_PRIVATE_KEY_PATH=os.path.join(os.path.dirname(__file__), 'mtk_rsa.pem'),
    ALIPAY_PRIVATE_KEY_PATH=os.path.join(os.path.dirname(__file__), 'mtk_rsa.pem'),
    ALIPAY_PUBLIC_KEY_PATH=os.path.join(os.path.dirname(__file__), 'ali_pub.pem'),
    ALIPAY_CALLBACK_URL="http://yc.miteke.com/callback/ali",
    ALIPAY_RETURN_URL="http://yc.miteke.com/user/profile",
    ALIPAY_APPID="2017092008837195",
)

# mongodb config
db_name = 'mongo_sc'
client = MongoClient("mongodb://localhost:27017")
db = client[db_name]
