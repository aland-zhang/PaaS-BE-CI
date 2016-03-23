# coding:utf-8

from datetime import date, datetime
import calendar
import bson
from bson.objectid import ObjectId
from bson import SON
import json
# from bson.py3compat import string_type
import decimal
import sys
import jsonpickle
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')

# json_lib = True
# def default(obj):
#     if isinstance(obj, ObjectId):
#         return str(obj)
#     if isinstance(obj, datetime.datetime):
#         # TODO share this code w/ bson.py?
#         if obj.utcoffset() is not None:
#             obj = obj - obj.utcoffset()
#         millis = int(calendar.timegm(obj.timetuple()) * 1000 +
#                      obj.microsecond / 1000)
#         return millis
#     if bson.has_uuid() and isinstance(obj, bson.uuid.UUID):
#         return obj.hex
#     raise TypeError("%r is not JSON serializable" % obj)
#
# def _json_convert(obj):
#     """Recursive helper method that converts BSON types so they can be
#     converted into json.
#     """
#     if hasattr(obj, 'iteritems') or hasattr(obj, 'items'):  # PY3 support
#         return SON(((k, _json_convert(v)) for k, v in obj.iteritems()))
#     elif hasattr(obj, '__iter__') and not isinstance(obj, string_type):
#         return list((_json_convert(v) for v in obj))
#     try:
#         return default(obj)
#     except TypeError:
#         return obj
#
# def dumps(obj, *args, **kwargs):
#     """Helper function that wraps :class:`json.dumps`.
#
#     Recursive function that handles all BSON types including
#     :class:`~bson.binary.Binary` and :class:`~bson.code.Code`.
#
#     .. versionchanged:: 2.7
#        Preserves order when rendering SON, Timestamp, Code, Binary, and DBRef
#        instances. (But not in Python 2.4.)
#     """
#     if not json_lib:
#         raise Exception("No json library available")
#     return json.dumps(_json_convert(obj), *args, **kwargs)


# 举一个例子：
#
# ebay中时间格式为‘Sep-21-09 16:34’
#
# 则通过下面代码将这个字符串转换成datetime
#
# >>> c = datetime.datetime.strptime('Sep-21-09 16:34','%b-%d-%y %H:%M');
# >>> c
# datetime.datetime(2009, 9, 21, 16, 34)
#
# 又如：datetime转换成字符串
#
# >>> datetime.datetime.now().strftime('%b-%d-%y %H:%M:%S');
# 'Sep-22-09 16:48:08'


# class DecimalEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, decimal.Decimal):
#             return float(o)
#         return super(DecimalEncoder, self).default(o)
class JsonUtil:

    def __default(self,obj):
       if isinstance(obj, datetime):
         return obj.strftime('%Y-%m-%d %H:%M:%S')
       elif isinstance(obj, date):
         return obj.strftime('%Y-%m-%d')
       else:
        raise TypeError('%r is not JSON serializable' % obj)

    #对象转json
    def parseJsonObj(self,obj):
        jsonpickle.set_preferred_backend('json')
        jsonpickle.set_encoder_options('json',default=self.__default, ensure_ascii=False,separators=(',', ': '))
        frozen = jsonpickle.encode(obj,unpicklable=False)
        # self.finish(frozen)
        # jsonstr=json.dumps(obj,default=self.__default,ensure_ascii=False,separators=(',',':')) #cls=DecimalEncoder
        return frozen
    #对象转json包括对象内容
    def parseJsonAll(self,obj):
        jsonpickle.set_preferred_backend('json')
        jsonpickle.set_encoder_options('json', ensure_ascii=False,separators=(',', ': '))
        frozen = jsonpickle.encode(obj,unpicklable=True)
        # self.finish(frozen)
        # jsonstr=json.dumps(obj,default=self.__default,ensure_ascii=False,separators=(',',':')) #cls=DecimalEncoder
        return frozen
    #json转对象
    def parseJsonString(self,jsonstring):
        jsonpickle.set_preferred_backend('json')
        jsonpickle.set_encoder_options('json',ensure_ascii=False,separators=(',', ': '))
        obj = jsonpickle.decode(jsonstring)
        # obj=json.loads(jsonstring)
        # assert obj.name == result['name'] == 'Awesome'
        return obj
if __name__ == '__main__':
    pass

# 在使用的时候，你可以这样使用：
# jsonUtil=JsonUtil()
# retstr=jsonUtil.parseJsonObj(retobj)
# class MyEncoder(json.JSONEncoder):
#     def default(self,obj):
#         #convert object to a dict
#         d = {}
#         d['__class__'] = obj.__class__.__name__
#         d['__module__'] = obj.__module__
#         d.update(obj.__dict__)
#         return d
#
# class MyDecoder(json.JSONDecoder):
#     def __init__(self):
#         json.JSONDecoder.__init__(self,object_hook=self.dict2object)
#     def dict2object(self,d):
#         #convert dict to object
#         if'__class__' in d:
#             class_name = d.pop('__class__')
#             module_name = d.pop('__module__')
#             module = __import__(module_name)
#             class_ = getattr(module,class_name)
#             args = dict((key.encode('ascii'), value) for key, value in d.items()) #get args
#             inst = class_(**args) #create new instance
#         else:
#             inst = d
#         return inst
#
#
# d = MyEncoder().encode(p)
# o =  MyDecoder().decode(d)
