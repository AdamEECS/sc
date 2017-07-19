from . import MongoModel
from .brought import Brought
from enum import Enum


class Status(Enum):
    pending = 1
    payed = 2
    delivery = 3
    finish = 4


class Order(MongoModel):
    @classmethod
    def _fields(cls):
        fields = [
            ('orderNo', str, ''),
            ('address', dict, {}),
            ('payment', str, ''),
            ('items', list, []),
            ('amount', str, ''),
            ('user_id', int, -1),
            ('user_uuid', str, ''),
            ('username', str, ''),
            ('comment', str, ''),
            ('status', str, ''),
        ]
        fields.extend(super()._fields())
        return fields

    @classmethod
    def new(cls, form):
        m = super().new(form)
        m.set_uuid('orderNo')
        m.status = 'pending'
        m.save()
        return m

    def payed(self):
        self.status = 'payed'
        self.save()
        return self

    def delivery(self):
        self.status = 'delivery'
        self.save()
        return self

    def finish(self):
        self.status = 'finish'
        self.save()
        # 管理员手动激活
        self.active()
        return self

    def active(self):
        user_uuid = self.user_uuid
        for i in self.items:
            d = dict(
                user_uuid=user_uuid,
                product_name=i.get('name'),
                mode=i.get('mode'),
            )
            if d['mode'] == 'TIMES':
                d['times'] = i.get('count') * int(i.get('unit', 1))
            elif d['mode'] == 'MONTH':
                d['month'] = i.get('count') * int(i.get('unit', 1))
            Brought.new(d)
