# coding:utf-8
import tornado
from tornado import gen
from tornado.web import HTTPError
from util.json_util import JsonUtil,dumps
from handler.api.base import BaseHandler



"""
@api {put} /api/user Edit Profile
@apiVersion 0.1.0
@apiGroup User
@apiDescription 修改用户资料

@apiHeader {String} Token 用户登陆 Token

@apiParam {String} [nickname] 用户昵称
@apiParam {Int} [gender] 用户性别 {0：女，1：男}
@apiParam {String} [description] 一句话描述
"""


"""
@api {get} /api/user Get Profile
@apiVersion 0.1.0
@apiGroup User
@apiDescription 获取用户资料

@apiHeader {String} Token 用户登陆 Token

@apiParam {String} [id] 用户 id
"""


class ProfileHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        # li=self.get_query_arguments('id')
        n=self.get_argument('a',None)
        m=self.get_argument('b','bbb')

        uid = self.is_logined()

        user_id = self.get_argument('id', uid)
        user_id = user_id if user_id != '' else uid

        self.vaildate_id(user_id)

        user = yield User.objects.get(user_id)
        self.vaildate_resource(user)
        self.write_json(user.to_dict())
    @tornado.web.asynchronous
    @gen.coroutine
    def delete(self):
        # li=self.get_query_arguments('id')
        n=self.get_argument('a',None)
        m=self.get_argument('b','bbb')
        pass
    @tornado.web.asynchronous
    @gen.coroutine
    def put(self):
        uid = self.is_logined()
        user = yield User.objects.get(uid)
        self.vaildate_resource(user)

        need_edit = 0
        nickname = self.get_argument('nickname', None)
        if self.vaildate_nickname(nickname):
            user.nickname = nickname
            need_edit += 1

        gender = self.get_argument('gender', '')
        if gender in ['0', '1']:
            user.gender = int(gender)
            need_edit += 1

        description = self.get_argument('description', None)
        if self.vaildate_description(description):
            user.description = description
            need_edit += 1

        if need_edit != 0:
            yield user.save()

        self.write_json(user.to_dict())

    # TODO：对昵称和描述进行限制
    @staticmethod
    def vaildate_nickname(nickname):
        if nickname is not None and len(nickname) > 0:
            return True
        else:
            return False

    @staticmethod
    def vaildate_description(description):
        if description is not None and len(description) > 0:
            return True
        else:
            return False


"""
@api {post} /api/user/avatar Upload Avatar
@apiVersion 0.1.0
@apiGroup User
@apiDescription 上传用户头像，使用 `multipart/form-data` 类型 Post
@apiSampleRequest off

@apiHeader {String} Token 用户登陆 Token

@apiParam {File} avatar 头像图片数据
"""


class AvatarUploadHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        uid = self.is_logined()

        url = self.upload_file_from_request('avatar', 'avatar/')

        # TODO: 需要添加压缩操作
        user = yield User.objects.get(uid)
        self.vaildate_resource(user)

        user.avatar_url = url
        yield user.save()

        self.write_json(user.to_dict())


