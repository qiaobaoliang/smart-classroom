#!/usr/bin/env python
# coding: utf8
from flask import Flask
from flask_cors import *



def create_app(debug=False):

    app = Flask(__name__)
    app.debug = debug

    from module.electric import ele_module

    app.register_blueprint(ele_module)

    CORS(app, supports_credentials=True)

    return app