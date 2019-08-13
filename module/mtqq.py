# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
from multiprocessing import Process
from utils.common import get_db_res, get_conn
from utils.config import MQTTHOST, MQTTPORT

mqttClient = mqtt.Client("subscribe_server_192.168.99.52")

# 连接MQTT服务器
def on_mqtt_connect():
    mqttClient.connect(MQTTHOST, MQTTPORT, 60)
    mqttClient.loop_start()
    # mqttClient.loop_forever()

# publish 消息
def on_publish(topic, payload, qos):
    mqttClient.publish(topic, payload, qos)

# 消息处理函数
def on_message_come(lient, userdata, msg):
    try:
        value = int(msg.payload.decode())
    except Exception as e:
        return None
    topic = msg.topic.split("/server",1)[1] #去掉开头的/server
    print("[INFO]"+ topic + " " + ":" + str(value))
    on_publish(topic,value,1)
    ele_conn = get_conn()
    sql_str = "update electric set value = {} where topic='{}'".format(value, topic)
    get_db_res(ele_conn,sql_str)
    ele_conn.close()

# subscribe 消息
def on_subscribe():
    ele_conn = get_conn()
    sql_str = "select topic from electric where need_subscribe = 1"
    res_list = get_db_res(ele_conn,sql_str)
    topic_list = []
    for topic in res_list:
        topic_list.append(("/server"+topic[0].decode(),1))
    print("[INFO]topic_list",topic_list)
    ele_conn.close()
    mqttClient.subscribe(topic_list)
    # mqttClient.subscribe("/light/light_01", 1)
    mqttClient.on_message = on_message_come # 消息到来处理函数

def mqtt_subscribe_server():
    on_mqtt_connect()
    on_subscribe()
    while True:
        pass

def mqtt_start_subscribe():
    p = Process(target=mqtt_subscribe_server)
    p.start()


if __name__ == '__main__':
    pass


