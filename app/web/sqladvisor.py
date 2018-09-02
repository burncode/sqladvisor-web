#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
============================================================================
    FileName: sqladvisor.py
    Desc:
    Author: zhoubangjun
    Date: 2018/5/4
=============================================================================
"""

from flask import render_template, request, jsonify

from config import *
from . import web
import commands
import redis
from mylog import getLogger

LOG = getLogger('root')


@web.route('/', methods=['GET', 'POST'])
def analysis_sql():
    if request.is_xhr and request.method == 'POST':
        db_host = request.form.get('db_host')
        db_name = request.form.get('db_name')
        sql_content = request.form.get('sql_content').strip().replace('\'', '\"')
        sql_content = [ i.strip('\r\n') for i in sql_content.split(';') if i ]

        try:
            redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            redis_conn.exists('a')
        except redis.exceptions.ConnectionError, e:
            LOG.warning("连接redis错误: %s" % e)

            sqladvisor_result = exec_sql(db_host=db_host, db_name=db_name, sql_content=sql_content)
            analysis_result = {'query_counts': 'N',
                               'query_sql_counts': 'N',
                               'current_query_sql_counts': 'N',
                               'result': sqladvisor_result}

            return jsonify(analysis_result)

        query_counts = redis_conn.incr('sqladvisor_query_counts')
        query_sql_counts = redis_conn.incrby('sqladvisor_query_sql_counts', len(sql_content))
        analysis_result = {}
        sqladvisor_result = exec_sql(db_host=db_host, db_name=db_name, sql_content=sql_content)
        analysis_result['result'] = sqladvisor_result
        analysis_result['query_counts'] = query_counts
        analysis_result['query_sql_counts'] = query_sql_counts
        analysis_result['current_query_sql_counts'] = len(sql_content)

        return jsonify(analysis_result)

    return render_template('sqladvisor.html', db_list=[], db_host_list=DB_HOSTLIST)


@web.route('/show_db/', methods=['GET', 'POST'])
def show_db():
    db_host = request.args.get('db_host', '')

    if not db_host:
        db_host_list = {'result': ''}
        return jsonify(db_host_list)

    status, output = commands.getstatusoutput("\
            mysql -u%s -p%s -P%s -h%s -e'show databases' \
            | grep -Ev 'mysql|schema|Database'" % (DB_USER, DB_PWD, DB_PORT, db_host))
    if status == 0:
        db_list = output.split('\n')
        db_list = {'result': db_list}
    else:
        LOG.error('连接mysql错误: %s' % output)
        db_list = {'result': ''}
    return jsonify(db_list)


def exec_sql(db_host="", db_name="", sql_content=""):
    """
    执行sql分析
    """
    sql_result = []
    for sql in sql_content:
        status, output = commands.getstatusoutput('sqladvisor -h %s -u %s -p %s -P %s -d %s -q \' %s \' -v 1'
                                                  % (db_host, DB_USER, DB_PWD, DB_PORT, db_name, sql))
        sql_result.append(output)
    sql_result = zip(sql_content, sql_result)
    return sql_result
