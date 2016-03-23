#!/usr/bin/env python
# coding:utf-8
import time
import config
from redisopt import redis
from util.crypt import aesc



def create_token(uid):
    rt = int(time.time())
    token = aesc.encrypt('%d@%s' % (rt, uid))
    redis.set('token:' + uid, token)
    return token


def validate_token(token):
    rt = int(time.time())
    token_raw = aesc.decrypt(token)

    if token_raw is None:
        return False, None

    try:
        sp = token_raw.split('@')
        tk_rt = int(sp[0])
        tk_uid = sp[1]

        active_token = redis.get('token:' + tk_uid)
        if token != active_token:
            return False, None

        if tk_rt <= rt and (rt-tk_rt) <= config.TOKEN_TIMEOUT:
            return True, tk_uid
        else:
            # token 过期
            return False, None

    except Exception:
        return False, None


def clear_token(uid):
    redis.delete('token:' + uid)


