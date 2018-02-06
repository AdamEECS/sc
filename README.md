# S.C.

## mongo服务启动方法：

```
mongod --dbpath /Users/username/data/db
```

程序启动方法：

```
sh start.sh
```

注：为调试css和js，应在 chrome - Network 启用「disable cache」。

## Pillow安装方法

debian直接安装pillow不成功，可能是缺少依赖，使用以下命令安装

```
apt-get update
apt-get install libjpeg62-turbo-dev libopenjpeg-dev libfreetype6-dev libtiff5-dev liblcms2-dev libwebp-dev tk8.6-dev python3-tk
apt-get install libpq-dev python-dev python3.4-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev
apt-get install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 libssl-dev

```

然后重新安装pillow

```
pip3 uninstall pillow
pip3 install pillow
```

mongo导出


```
mongoexport -d mongo_sc -c User -o /Users/san/pros/sc/db/user.dat
mongoexport -d mongo_sc -c Category -o /Users/san/pros/sc/db/category.dat
mongoexport -d mongo_sc -c Product -o /Users/san/pros/sc/db/product.dat
```

mongo导入


```
mongoimport -d mongo_sc -c User --upsert --drop /var/www/sc/db/user.dat
mongoimport -d mongo_sc -c Category --upsert --drop /var/www/sc/db/category.dat
mongoimport -d mongo_sc -c Product --upsert --drop /var/www/sc/db/product.dat
```

todo

直接消费
用户按照uuid查询


## 增加支付接口

1，安装 pingpp

```
pip3 install pingpp
```

2，更新 config 目录下的 key.py config.py，并增加 *.pem 私钥。

3，安装支付宝接口

```
pip3 install python-alipay-sdk --upgrade
```

update

```
pip3 install pymysql
```