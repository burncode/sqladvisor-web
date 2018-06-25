# -*- coding: utf-8 -*-
"""
    config.py
    ~~~~~~~~~
    basic configuration
"""

DEBUG = True
LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 60001


# redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# mysql
DB_HOSTLIST = (
            '127.0.0.1',
            'localhost'
            )


# 连接上面的mysql使用的用户名和密码
DB_USER='root'
DB_PWD='123456'
DB_PORT=3306
