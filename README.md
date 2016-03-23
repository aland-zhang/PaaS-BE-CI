# tornaREST
![](art/logo.jpg)

## Description
TornaREST is a simple RESTful Web Service build with **[Tornado](http://www.tornadoweb.org/en/stable/)** Web Server.It's a demo and a base framework for learning how to build a web service provides RESTful API.

### Detail
**[How to use Python to build a RESTful Web Service](http://zhuanlan.zhihu.com/kotandroid/20488077)**

### Run server
- Create `config.py` in the project root path:   
```
DOMAIN = 'http://127.0.0.1'

DB_HOST = 'localhost'
DB_PORT = 27017
DB_NAME = 'test'
DB_USER = 'root'
DB_PWD = 'your password'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

AES_KEY = 'your aes key'
TOKEN_TIMEOUT = 60 * 60 * 24 * 30

QINIU_AK = ''
QINIU_SK = ''
QINIU_BUCKET_NAME = ''
QINIU_HOST = ''   
```

- Run `util/init_db.py`
- Run `server.py`

### API response format  
```
{
    'code': code,
    'msg': msg,
    'data': data
}
```

## Features
- Using tornado
- Using mongodb
- Using redis
- Using [qiniu](http://www.qiniu.com/) for image storage

## Note
- You can use **[apidoc](https://github.com/apidoc/apidoc)** to generate your api doc