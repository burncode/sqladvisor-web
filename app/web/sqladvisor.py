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
from hashlib import md5
import commands
import redis
from mylog import getLogger

LOG = getLogger('root')


@web.route('/', methods=['GET', 'POST'])
def analysis_sql():
    if request.is_xhr and request.method == 'POST':
        dbhost = request.form.get('dbhost')
        dbname = request.form.get('dbname')
        sqlcontent = request.form.get('sqlcontent').strip().replace('\'', '\"')

        try:
            redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            redis_conn.exists('a')
        except redis.exceptions.ConnectionError, e:
            LOG.warning("连接redis错误: %s" % e)

            sqladvisor_result = exec_sql(dbhost=dbhost, dbname=dbname, sqlcontent=sqlcontent)
            analysis_result = {'totalQueryCounts': 'N', 'sqladvisor_xxx': 'N',
                               'result': sqladvisor_result}

            return jsonify(analysis_result)

        categoryQueryKey = 'sqladvisor_categoryQueryCounts' + '_' + md5(dbname + '_' + sqlcontent).hexdigest()

        '''
        记录总的查询次数
        '''
        totalQueryCounts = redis_conn.incr('sqladvisor_totalQueryCounts')

        '''
        记录每个类别的查询次数
        '''
        categoryQueryCounts = redis_conn.incr(categoryQueryKey)

        analysis_result = {}
        sqladvisor_result = exec_sql(dbhost=dbhost, dbname=dbname, sqlcontent=sqlcontent)
        analysis_result['result'] = sqladvisor_result
        analysis_result[categoryQueryKey] = categoryQueryCounts
        analysis_result['totalQueryCounts'] = totalQueryCounts
        return jsonify(analysis_result)

    return render_template('sqladvisor.html', dblist=[], dbhostlist=DB_HOSTLIST)


@web.route('/display_db/', methods=['GET', 'POST'])
def display_db():
    dbhost = request.args.get('dbhost')

    if not dbhost:
        dbhostlist = {'result': ''}
        return jsonify(dbhostlist)

    status, output = commands.getstatusoutput("\
            mysql -u%s -p%s -P%s -h%s -e'show databases' \
            | grep -Ev 'mysql|schema|Database'" % (DB_USER, DB_PWD, DB_PORT, dbhost))
    if status == 0:
        dblist = output.split('\n')
        dblist = {'result': dblist}
    else:
        LOG.error('连接mysql错误: %s' % output)
        dblist = {'result': ''}
    return jsonify(dblist)


def exec_sql(dbhost, dbname, sqlcontent):
    """
    执行sql分析
    """
    status, output = commands.getstatusoutput('sqladvisor -h %s -u %s -p %s -P %s -d %s -q \' %s \' -v 1'
                                              % (dbhost, DB_USER, DB_PWD, DB_PORT, dbname, sqlcontent))
    return output
