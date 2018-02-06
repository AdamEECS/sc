import time

from . import ModelMixin
from . import db_sql as db
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Wl(Base, ModelMixin):
    __tablename__ = 'mt4_whitelabel_info'
    id = db.Column(db.Integer, primary_key=True)
    mt4_id = db.Column(db.Integer)
    url = db.Column(db.String())
    company = db.Column(db.String())
    company_address = db.Column(db.String())
    tag = db.Column(db.String())

