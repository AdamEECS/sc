import time
import os
from os.path import abspath
from os.path import dirname
from flask import current_app as app
from . import MongoModel


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

    # @classmethod
    # def new(cls, form=None, **kwargs):
    #     file = kwargs.get('file')
    #     path = os.path.join(abspath(dirname(__file__)), '../', app.config['UPLOAD_FILE_DIR'], file.filename)
    #     file.save(path)
    #     m = super().new(form)
    #     m.file = file.filename
    #     m.save()
    #     return m

    @classmethod
    def find(cls, **kwargs):
        ms = super().find(**kwargs)
        ms.reverse()
        return ms
