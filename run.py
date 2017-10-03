# -*- coding: utf-8 -*-
from flask import Flask
app = Flask(__name__,instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

from views.views import *

if __name__ == '__main__':
    from config import LISTEN_IP,LISTEN_PORT
    app.run(host=LISTEN_IP,port=int(LISTEN_PORT))
