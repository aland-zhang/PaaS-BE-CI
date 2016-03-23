# coding:utf-8
from handler.api.base import APINotFoundHandler
from handler.api.build.builds import buildHandler
from handler.api.build.repositories import RepoHandler
from handler.api.build.hook import hookHandler
from handler.api.image.image import imageLoadHandler,imageSyncHandler
# from handler.api.user.logopt import LoginHandler, LogoutHandler
# from handler.api.user.profile import ProfileHandler, AvatarUploadHandler
# from handler.api.user.register import RegisterHandler, SchoolsHandler
import sys

reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')

url = [
    (r'/v1/builds', buildHandler),
    (r'/v1/hook', hookHandler),
    (r'/v1/repositories', RepoHandler),
    (r'/v1/image', imageLoadHandler),
    (r'/v1/imagesync', imageSyncHandler),
    (r'.*', APINotFoundHandler),
]
