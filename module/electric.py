#!/usr/bin/env python
# coding:utf8
import sys, MySQLdb, json
from flask import request, jsonify, Blueprint
from utils.common import get_db_res, get_method, LOG_INFO, get_conn
from utils.resp import ret_data
from utils.config import MQTTHOST, MQTTPORT
import paho.mqtt.client as mqtt

ele_module = Blueprint('ele_module',__name__)
funcs = sys.modules[__name__]


# 增加rule集、rule到数据库
# def add_at001(api, token, my_type, uid, query, oa_conn, at_conn):
#     # 校验type
#     func_name = sys._getframe().f_code.co_name
#     ret, type_flag = verify_type(api, my_type, func_name)
#     if not type_flag:
#         return ret
#     # 获取参数
#     name = query.get("name", "")
#     # 获取用户的email
#     where_str = "where id=%s" % uid
#     res = select_sql(oa_conn, "user", ["email"], where_str)
#     email = res[0][0].encode("utf-8")
#     # 参数只有name为增加rule group ，有其他参数为增加rule
#     if name != "":
#         data, insert_flag = insert_sql(at_conn, "rule_group", ["name", "operator"], [name, email])
#         if not insert_flag:
#             return data
#     else:
#         return ret_data.null_data(90068, "参数错误")
#     return ret_data.null_data(0, "add success")

# 记录入库
def record(ele_id,value,action):
    record_conn = get_conn("record")
    sql_str = "insert into record values((select distinct host_id \
        from electric where id = {}),{},{},'{}',NOW())".format(ele_id,ele_id,value,action)
    get_db_res(record_conn,sql_str)

# 向设备发布消息
def public(ele_id,value):
    mqttClient = mqtt.Client("public_server_192.168.99.52")
    mqttClient.connect(MQTTHOST, MQTTPORT, 60)
    ele_conn = get_conn()
    sql_str = "select distinct topic from electric where id = {}".format(ele_id)
    res = get_db_res(ele_conn,sql_str)
    topic = res[0][0].decode()
    print("[INFO]public",topic,value)
    mqttClient.publish(topic, value, 1)
    ele_conn.close()

def electric(query):
    ele_id = query.get("ele_id")
    ele_action = query.get("action")
    if not ele_id or not ele_action:
        return ret_data.null_data(7001,"ele_id和action是必要的")
    if ele_action not in ["show", "set", "up", "down"]:
        return ret_data.null_data(7001,"ele_action参数错误")
        
    #获取数据库连接
    db_conn = {
        "ele_conn": get_conn()
    }
    resp_data = {}
    if ele_action == "show":
        sql_str = "select value from electric where id = {}".format(ele_id)
        res = get_db_res(db_conn["ele_conn"],sql_str)
        if len(res)<1:
            return ret_data.null_data(7001,"ele_id:{}电器不存在".format(ele_id))
        ele_value = res[0][0]
        resp_data["ele_value"] = ele_value
        #记录入库
        record(ele_id,ele_value,ele_action)
    elif ele_action == "up" or ele_action == "down":
        ele_action_value = query.get("value")
        if not ele_action_value and ele_action_value != 0:
            return ret_data.null_data(7001,"value参数是必要的")
        sql_str = "select value from electric where id = {}".format(ele_id)
        res = get_db_res(db_conn["ele_conn"],sql_str)
        if len(res)<1:
            return ret_data.null_data(7001,"ele_id:{}电器不存在".format(ele_id))
        ele_value = res[0][0]
        if ele_action == "up":
            set_value = ele_value + ele_action_value
        if ele_action == "down":
            set_value = ele_value - ele_action_value
        print("[DEBUG]ELE_VALUE:{},SET_VALUE:{}".format(ele_value,set_value))
        sql_up_str = "update electric set value = {} where id = {}".format(set_value, ele_id)
        get_db_res(db_conn["ele_conn"],sql_up_str)
        resp_data["ele_value"] = set_value
        # 消息发布
        public(ele_id,set_value)
        # 记录入库
        record(ele_id,ele_action_value,ele_action)
    elif ele_action == "set":
        ele_action_value = query.get("value")
        if not ele_action_value:
            if ele_action_value == 0:
                pass
            else:
                return ret_data.null_data(7001,"value参数是必要的")
        sql_up_str = "update electric set value = {} where id = {}".format(ele_action_value, ele_id)
        get_db_res(db_conn["ele_conn"],sql_up_str)
        resp_data["ele_value"] = ele_action_value
        # 消息发布
        public(ele_id,ele_action_value)
        # 记录入库
        record(ele_id,ele_action_value,ele_action)
    #关闭数据库连接
    for key in db_conn:
        db_conn[key].close()
    return ret_data.complex_data(resp_data)


def check_func(my_type, query, mode):
    if my_type == "api1001":
        if mode == "electric":
            resp = electric(query)
    elif my_type == "api1002":
        resp = ret_data.null_data(7002, "预留的接口")
    else:
        resp = ret_data.null_data(90069, "不存在的接口")
    return resp


@ele_module.route('/smart', methods=['GET', 'POST', 'OPTIONS', 'HEAD'])
def req_type():
    method = request.method
    data, res_flag = get_method(method)
    # 参数错误直接返回
    if not res_flag:
        return data
    query = data["query"]
    mode = data["mode"]
    my_type = data["type"]
    qid = data["qid"]
    LOG_INFO("[AT][REQ][qid=%s][Method=%s][URL=%s] \nBODY:%s\n" % (qid, method, request.url, request.data))
    resp = check_func(my_type, query, mode)
    LOG_INFO("[AT][RESP][qid=%s][%s]:%s\n" % (qid, my_type, resp))
    return resp