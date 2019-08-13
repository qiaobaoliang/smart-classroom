#!/usr/bin/python
# coding: utf8

from flask import jsonify

class Data(object):
    def __init__(self):
        pass

    def complex_data(self, data, error_id=0, error_str="Success"):
        data = {
            'data': data,
            'error': {
                'id': error_id,
                'reason': error_str
            }
        }
        return jsonify(data)

    def null_data(self, error_id, error_str):
        data = {
            'data': {},
            'error': {
                'id': error_id,
                'reason': error_str
            }
        }
        return jsonify(data)


ret_data = Data()