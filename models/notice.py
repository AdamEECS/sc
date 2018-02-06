import time

from . import ModelMixin
from . import db_sql as db
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Notice(Base, ModelMixin):
    __tablename__ = 'mt4_notice'
    id = db.Column(db.Integer, primary_key=True)
    mt4_id = db.Column(db.Integer)
    title = db.Column(db.String())
    author = db.Column(db.String())
    content = db.Column(db.String())

    @classmethod
    def new(cls, form):
        m = cls()
        m.mt4_id = form.get('mt4_id')
        m.title = form.get('title')
        m.author = form.get('author')
        m.content = form.get('content')
        return m

