# -*- coding: utf-8 -*-
from flask import Flask, render_template
from run import app
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# 添加SQLAdvisor平台
from sqladvisor import sqladvisor
app.register_blueprint(sqladvisor)
