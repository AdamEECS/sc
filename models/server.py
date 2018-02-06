from . import MongoModel
from flask import current_app as app


class Server(MongoModel):
    @classmethod
    def _fields(cls):
        fields = [
            ('ip', str, ''),
            ('dbname', str, ''),
            ('username', str, ''),
            ('password', str, ''),
            ('comment', str, ''),
        ]
        fields.extend(super()._fields())
        return fields
