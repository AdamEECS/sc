from . import MongoModel
from enum import Enum


class Status(Enum):
    pending = 1
    payed = 2
    delivery = 3
    finish = 4


class Brought(MongoModel):
    @classmethod
    def _fields(cls):
        fields = [
            ('user_uuid', str, ''),
            ('product_name', str, ''),
            ('mode', str, ''),
            ('times', int, 0),
            ('month', int, 0),

        ]
        fields.extend(super()._fields())
        return fields

    @classmethod
    def new(cls, form):
        m = super().new(form)
        m.save()
        return m

    @classmethod
    def get_by_user(cls, user_uuid):
        rs = cls.find(user_uuid=user_uuid)
        rs = [cls.check_status(r) for r in rs]
        return rs

    @staticmethod
    def check_status(r):
        r.status = '生效中'
        return r

