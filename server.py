#!/usr/bin/env python
# coding:utf-8

import tornado.ioloop
import tornado.options
import tornado.httpserver
from application import app
from tornado.options import define, options, parse_command_line
from motorengine import connect
import config

define("port", type=int, default=8088, help="run on the given port")


def main():
    parse_command_line()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(config.PORT,'0.0.0.0')
    print 'Server is running at http://0.0.0.0:%s/' % options.port
    print 'Quit the server with Control-C'
    io_loop = tornado.ioloop.IOLoop.instance()
    # connect("local", host=config.DB_HOST, port=config.DB_PORT, io_loop=io_loop)
    io_loop.start()


if __name__ == "__main__":
    main()
