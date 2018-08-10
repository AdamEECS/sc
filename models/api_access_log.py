import time
import os
from os.path import abspath
from os.path import dirname
from flask import current_app as app
from . import MongoModel
from .user import User
from .wl import WlLocal


class ApiAccessLog(MongoModel):
    @classmethod
    def _fields(cls):
        fields = [
            ('args', str, ''),
            ('url', str, ''),
            ('mt4id', str, ''),
            ('content', str, ''),
            ('user_agent', str, ''),
            ('ip', str, ''),
        ]
        fields.extend(super()._fields())
        return fields

    @classmethod
    def log(cls, request, content=None):
        ip = request.headers.get("X-real-ip")
        if ip is None:
            ip = request.remote_addr

        d = dict(
            args=request.args.to_dict(),
            mt4id=request.args.get('id'),
            url=request.url,
            ip=ip,
            content=content,
            user_agent=request.user_agent.string,
        )
        cls.new(d)
