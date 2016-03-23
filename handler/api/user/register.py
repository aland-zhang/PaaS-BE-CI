# coding:utf-8
from bson import ObjectId
import tornado
from tornado import gen
from tornado.web import HTTPError
import json
from handler.api import errors
from handler.api.base import BaseHandler
from dbopt.collections import User, School
from util.token import create_token


"""
@api {post} /api/user/register Register
@apiVersion 0.1.0
@apiGroup User
@apiDescription 注册接口

@apiParam {String} mobile 用户手机号
@apiParam {String} pwd 用户密码`（使用加盐 md5 处理）`
@apiParam {String} school_id 学校 id
"""


class RegisterHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        # 注册用户 TODO: 手机号验证
        try:
            obj=self.loadjson(self.request.body)
        except:
            self.write_error()

        mobile = self.get_argument('mobile')
        pwd = self.get_argument('pwd')
        users = yield User.objects.filter(mobile=mobile).find_all()
        if len(users) != 0:
            # 手机号码已经被注册
            raise HTTPError(**errors.status_21)

        school_id = self.get_argument('school_id')
        self.vaildate_id(school_id)

        school = yield School.objects.get(self.get_argument('school_id'))
        self.vaildate_resource(school)

        # 注册成功
        user = User(mobile=mobile, password=pwd, nickname='test', school_id=ObjectId(school_id))
        yield user.save()

        user = user.to_dict()
        user['token'] = create_token(str(user['id']))
        self.write_json(user)


"""
@api {get} /api/user/schools Schools
@apiVersion 0.1.0
@apiGroup User
@apiDescription 获取学校列表
@apiSampleRequest http://192.168.10.99/api/user/schools
"""


class SchoolsHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        # 获取所有学校列表
        schools = yield School.objects.find_all()
        self.write_json([school.to_dict() for school in schools])


