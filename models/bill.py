import time
import os
from os.path import abspath
from os.path import dirname
from flask import current_app as app
from . import MongoModel


class Bill(MongoModel):
    @classmethod
    def _fields(cls):
        fields = [
            ('mt4_id', str, ''),
            ('title', str, ''),
            ('amount', int, 0),
            ('file', str, ''),
            ('content', str, ''),
            ('status', int, 0),
        ]
        fields.extend(super()._fields())
        return fields

    @classmethod
    def new(cls, form=None, **kwargs):
        file = kwargs.get('file')
        path = os.path.join(abspath(dirname(__file__)), '../', app.config['UPLOAD_FILE_DIR'], file.filename)
        file.save(path)
        m = super().new(form)
        m.file = file.filename
        m.save()
        return m

    @classmethod
    def find(cls, **kwargs):
        ms = super().find(**kwargs)
        ms.reverse()
        for m in ms:
            m.amount_point = round(m.amount * 6.55)
        return ms

    @property
    def url(self):
        from flask import url_for
        return url_for('static', filename='files/'+self.file)
