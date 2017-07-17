from . import MongoModel
from flask import current_app as app


class Category(MongoModel):
    @classmethod
    def _fields(cls):
        fields = [
            ('name', str, ''),
            ('father_name', str, ''),
        ]
        fields.extend(super()._fields())
        return fields

    @classmethod
    def valid(cls, form):
        name = form.get('name', '')
        valid_name = cls.find_one(name=name) is None
        msgs = []
        if not valid_name:
            message = '商品已经存在'
            msgs.append(message)
        status = valid_name
        return status, msgs

    @classmethod
    def new(cls, form):
        m = super().new(form)
        return m
