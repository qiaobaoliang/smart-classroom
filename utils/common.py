#!/usr/bin/env python
# coding: utf8
import MySQLdb
import random
import hashlib
import time
import os
import sys
import json
from flask import request, jsonify
from utils.resp import ret_data
from utils.sqlpool import INIT_SQLPOOL
from utils.config import ELE_DB, RECORD_DB, HOST_DB

def get_db_res(conn, sql, cur_type=0, data=None):
    if cur_type == 1:
        cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    elif cur_type == 2:
        cur = conn.cursor(cursorclass=MySQLdb.cursors.SSCursor)
    else:
        cur = conn.cursor()
    try:
        if data:
            cur.execute(sql, data)
        else:
            cur.execute(sql)
        res = cur.fetchall()
    except Exception as e:
        res = str(e)
        print("[DEBUG]mysql error：{}".format(res))
    finally:
        cur.close()
        conn.commit()
    # print res
    return res

# 获取method、参数等信息
def get_method(method):
    res_flag = True
    if method == 'POST':
        params = request.data
        params = params.decode()
        LOG_INFO(params)
        my_type = request.args.get("type","")
        qid = request.args.get("qid","")
        try:
            params = json.loads(params)
        except Exception as e:
            print("[ERROR]",e)
            res_flag = False
            data = ret_data.null_data(90063, "参数错误，不能被json.loads")
            return data, res_flag
        query = params.get("query","")
        mode = params.get("mode","")
        if not my_type:
            res_flag = False
            data = ret_data.null_data(90062, "no type")
            return data, res_flag
        if not qid:
            res_flag = False
            data = ret_data.null_data(90062, "no qid")
            return data, res_flag
        if not mode:
            mode = ""
        data = {"query":query,"mode":mode,"type":my_type,"qid":qid}
        return data, res_flag
    else:
        res_flag = False
        data = ret_data.null_data(90064, "only POST method allow")
        return data, res_flag

#打印日志
def LOG_INFO(str):
    info = '[INFO][%s][%d]%s\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), os.getpid(), str)
    sys.stderr.write(info)

# 数据库连接
def get_conn(my_db="electric"):
    if my_db == "electric":
        conn = INIT_SQLPOOL(**ELE_DB).connection()
    elif my_db == "host":
        conn = INIT_SQLPOOL(**HOST_DB).connection()
    elif my_db == "record":
        conn = INIT_SQLPOOL(**RECORD_DB).connection()
    return conn

# select 查询语句
def select_sql(conn, table_name, col_list, where_str="", cur_type=0):
    par_str = ",".join(col_list)
    sql = "select %s from %s " % (par_str, table_name)
    sql1 = sql + where_str
    if cur_type:
        res = get_db_res(conn, sql1, cur_type)
    else:
        res = get_db_res(conn,sql1)
    return res

# 准变成str格式
def data2str(data_list):
    ret_flag = True
    for cur in range(len(data_list)):
        data = data_list[cur]
        if isinstance(data, int):
            data = str(data)
        elif isinstance(data, list):
            data = json.dumps(data)
        elif isinstance(data, dict):
            try:
                data = json.dumps(data, ensure_ascii=False)
            except Exception as e:
                print(e)
                ret_flag = False
                data = ret_data.null_data(90066, "json dump {0}失败".format(data))
        elif isinstance(data, float):
            data = str(data)
        else:
            pass
        if not ret_flag:
            break
        data_list[cur] = data
    return data_list

# insert SQL
def insert_sql(at_conn, table, field_list, data_list):
    ret_flag = True
    data = ""
    field_list1 = data2str(field_list)
    field = ",".join(field_list1)
    field_str = "'%s'," * len(field_list)
    sql = "insert into `%s`(%s) VALUES (%s)" % (table, field, field_str[:-1])
    sql1 = sql % (tuple(data_list))
    try:
        get_db_res(at_conn, sql1)
    except Exception as e:
        print(e)
        ret_flag = False
        data = ret_data.null_data(7001, "数据插入报错:{}".format(e))
    return data, ret_flag

# update SQL
def update_sql(at_conn, table, field_list, data_list, where_field, where_value):
    ret_flag = True
    data = ""
    field_str = "='%s'," .join(field_list)
    sql = "update `%s` set %s where %s=%s" % (table, field_str+"='%s'", where_field, where_value)
    sql1 = sql % (tuple(data_list))
    try:
        get_db_res(at_conn, sql1)
    except Exception as e:
        print(e)
        ret_flag = False
        data = ret_data.null_data(90067, "update {0}表失败".format(table))
    return data, ret_flag

#delete SQL
# def delete_sql(at_conn,table,param,id, field_str=None, param_data=None):
#     ret_flag = True
#     data = ""
#     if field_str is None:
#         sql = "delete from `%s` where %s=%s" % (table, param, id)
#     else:
#         sql = "delete from `%s` where %s=%s and %s=%s" % (table, param, id, field_str, param_data)
#     try:
#         get_db_res(at_conn, sql)
#     except Exception as e:
#         print(e)
#         ret_flag = False
#         data = ret_data.null_data(90067, "delete {0}表失败".format(table))
#     return data, ret_flag

if __name__ == "__main__":
    pass