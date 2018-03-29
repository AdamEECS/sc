import time
import os
from os.path import abspath
from os.path import dirname
from flask import current_app as app
from . import MongoModel
from .user import User
from .wl import WlLocal


class Log(MongoModel):
    @classmethod
    def _fields(cls):
        fields = [
            ('user_id', int, 0),
            ('user_name', str, ''),
            ('model', str, ''),
            ('action', str, ''),
            ('content', str, ''),
            ('status', str, ''),
        ]
        fields.extend(super()._fields())
        return fields

    @classmethod
    def all(cls):
        ms = super().all()
        ms.reverse()
        for m in ms:
            u = User.find_one(id=m.user_id)
            if u.role == 'client':
                wl = WlLocal.find_one(mt4_id=u.mt4_id)
                m.company = wl.name
            else:
                m.company = 'MTK'
        return ms

    @classmethod
    def search_or(cls, form):
        ms = super().search_or(form)
        ms.reverse()
        for m in ms:
            u = User.find_one(id=m.user_id)
            if u.role == 'client':
                wl = WlLocal.find_one(mt4_id=u.mt4_id)
                m.company = wl.name
            else:
                m.company = 'MTK'
        return ms
