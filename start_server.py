# coding: utf-8
import json
from gevent.pywsgi import WSGIServer
from flask import Flask, request, Response, jsonify
from app.create import create_app
# from gevent import monkey;monkey.patch_all()
from utils.config import SERVER_PORT
from module.mtqq import mqtt_start_subscribe


app = create_app(True)

if __name__ == '__main__':
    mqtt_start_subscribe() #启动mqtt订阅服务
    WSGIServer(('0.0.0.0', SERVER_PORT), app).serve_forever()