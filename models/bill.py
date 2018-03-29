import time
import os
from os.path import abspath
from os.path import dirname
from flask import current_app as app
from . import MongoModel
from . import timestamp


class Bill(MongoModel):
    @classmethod
    def _fields(cls):
        fields = [
            ('mt4_id', str, ''),
            ('title', str, ''),
            ('amount', int, 0),
            ('mode', int, 0),
            ('file', str, ''),
            ('content', str, ''),
            ('status', int, 0),
        ]
        fields.extend(super()._fields())
        return fields

    @classmethod
    def new(cls, form=None, **kwargs):
        file = kwargs.get('file')
        m = super().new(form)
        if file is not None and file.filename != '':
            path = os.path.join(abspath(dirname(__file__)), '../', app.config['UPLOAD_FILE_DIR'], file.filename)
            file.save(path)
            m.file = file.filename
        m.save()
        return m

    @classmethod
    def find(cls, **kwargs):
        ms = super().find(**kwargs)
        ms.reverse()
        for m in ms:
            if m.mode == 0:
                m.amount_point = round(m.amount * 6.45)
            else:
                m.amount_point = m.amount
        return ms

    @property
    def url(self):
        from flask import url_for
        return url_for('static', filename='files/'+self.file)

    def pay(self):
        if self.status == 0:
            self.status = 1
            self.ut = timestamp()
            self.save()
