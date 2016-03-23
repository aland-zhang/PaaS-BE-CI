# coding:utf-8
import redis
import config
import sys
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')
# TODO: add to config
pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
redis = redis.Redis(connection_pool=pool)




