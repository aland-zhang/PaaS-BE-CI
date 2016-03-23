# coding:utf-8
from util.common import time_default
import sys
import datetime

reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')


class createrespo(object):
    def __init__(self, namespace, repo_name, tag, status, created_at):
        self.namespace = namespace
        self.repo_name = repo_name
        self.tag = tag
        self.status = status
        self.created_at = time_default(created_at)


class delrespo(object):
    def __init__(self, namespace, repo_name, status):
        self.namespace = namespace
        self.repo_name = repo_name
        self.status = status


class build(object):
    def __init__(self, build_id, started_at, duration, status):
        self.build_id = build_id
        self.started_at = started_at
        self.duration = duration
        self.status = status


class getbuilds(object):
    def __init__(self, namespace, repo_name, count, next, previous, results):
        self.namespace = namespace
        self.repo_name = repo_name
        self.count = count
        self.next = next
        self.previous = previous
        self.results = results


class delbuild(object):
    def __init__(self, namespace, repo_name, build_id, status):
        self.namespace = namespace
        self.repo_name = repo_name
        self.build_id = build_id
        self.status = status


class postbuild(object):
    def __init__(self, namespace, repo_name,image_name, build_id, tag, time, status):
        self.namespace = namespace
        self.repo_name = repo_name
        self.image_name = image_name
        self.build_id = build_id
        self.tag = tag
        self.created_at = time_default(time)
        self.status = status


class build_detail(object):
    def __init__(self, namespace, repo_name, build_id, building, started_at, duration, status, stdout):
        self.namespace = namespace
        self.repo_name = repo_name
        self.build_id = build_id
        self.building = building
        self.started_at = started_at
        self.duration = duration
        self.status = status
        self.stdout = stdout


class uploadimage(object):
    def __init__(self, image_name, tag, time, status):
        self.image_name = image_name
        self.tag = tag
        self.time = time_default(time)
        self.status = status


class editimage(object):
    def __init__(self, image_name, tag, totag, time, status):
        self.image_name = image_name
        self.tag = tag
        self.totag = totag
        self.time = time_default(time)
        self.status = status


class delimage(object):
    def __init__(self, image_name, tag, status):
        self.image_name = image_name
        self.tag = tag
        self.time = time_default(datetime.datetime.now())
        self.status = status


class callback(object):
    des = None
    callback_url = None
    namespace = None
    repo_name = None
    tag = None
    build_id = None
    duration = None
    time = None
    status = None
    image_name=None


class jobinfo(object):
    namespace = None
    repo_name = None
    info = None


class hook(object):
    namespace = None
    repo_name = None
    tag = None
    build_id = None
    duration = None
    time = None
    status = None
    callurl = None
    callreturn = None


class image(object):
    image_name = None
    tag = None
    export_file_url = None
    post_callback_url = None


class postimage(object):
    image_name = None
    tag = None
    build_id=None
    time = None
    status = None
    export_file_url=None
    post_callback_url = None
    callreturn = None
class postimagesync(object):
    image_name = None
    tag = None
    sync_cloud_id=None
    time = None
    status = None
    post_callback_url = None
    callreturn = None
