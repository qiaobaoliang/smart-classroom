# !/usr/bin/python
# coding: utf-8
import sys

import MySQLdb
from DBUtils.PooledDB import PooledDB


def INIT_SQLPOOL(host='127.0.0.1', user='writer', passwd='ITgzs2019',
                 db='electric', maxconnections=30):
    mysql_db_pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=2,
                             maxconnections=maxconnections, host=host, port=3306, user=user,
                             passwd=passwd, db=db, charset='utf8', use_unicode=False, blocking=True)
    return mysql_db_pool

# from gevent import pool
# POOL = pool.Pool(30)
