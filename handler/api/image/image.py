# coding:utf-8
import tornado
from tornado import gen
from tornado.web import HTTPError
from urllib import quote,unquote
from handler.api import errors
from handler.api.base import BaseHandler

import dbopt.jsonobjs

from util.jenkins_opt import jenkinscls

import sys

reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')
class imageLoadHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        obj = None
        try:
            obj = self.loadjson(self.request.body)
        except:
            self.write_httperror('', **errors.status_4)
        try:
            j = jenkinscls()
            re = yield j.create_docker_load_job(obj)
            self.write_json_byobj(re)
        except Exception as e:
            self.write_httperror(e.message, **errors.status_7)

class imageSyncHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        obj = None
        try:
            obj = self.loadjson(self.request.body)
        except:
            self.write_httperror('', **errors.status_4)
        try:
            j = jenkinscls()
            re = yield j.create_docker_sync_job(obj)
            self.write_json_byobj(re)
        except Exception as e:
            self.write_httperror(e.message, **errors.status_7)
