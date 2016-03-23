# coding:utf-8
from url import url
import tornado.web
import os, sys

reload(sys)
sys.setdefaultencoding('utf-8')

app = tornado.web.Application(
    handlers=url,
    template_path=os.path.join(os.path.dirname(__file__), "template"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    debug=True,
)

