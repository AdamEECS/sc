import time

from . import ModelMixin
from . import db_sql as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Notice(Base, ModelMixin):
    __tablename__ = 'system_notice'
    id = db.Column(db.Integer, primary_key=True)
    mt4_id = db.Column(db.Integer)
    title = db.Column(db.String())
    status = db.Column(db.Integer)
    istop = db.Column(db.Integer)
    isbox = db.Column(db.Integer)
    content = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP, default=func.now())
    updated_at = db.Column(db.TIMESTAMP, default=func.now())
    dateTimeStatus = db.Column(db.TIMESTAMP, default=func.now())

    @classmethod
    def new(cls, form):
        m = cls()
        m.mt4_id = form.get('mt4_id')
        m.title = form.get('title')
        m.status = 1
        m.content = form.get('content')
        m.istop = form.get('istop', 2)
        m.isbox = form.get('isbox', 2)
        return m
