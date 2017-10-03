# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, Response
from flask import Blueprint
from hashlib import md5
import os
import commands

import json
import redis

from config import *
from instance.config import *
import mylog as logging

LOG = logging.getLogger()

sqladvisor = Blueprint('sqladvisor',__name__)

@sqladvisor.route('/',methods=['GET','POST'])
def analysis_sql():
    if request.is_xhr and request.method == 'POST':
        dbhost = request.form.get('dbhost')
        dbname = request.form.get('dbname')
        isflush =  request.form.get('isflush')
        sqlcontent= request.form.get('sqlcontent').strip(' ').replace('\'','\"')

        redis_conn = redis.Redis(host=REDIS_HOST,port=REDIS_PORT,db=0)
        querykey = 'sqladvisor_' + md5(dbname + '_' + sqlcontent).hexdigest()
        countsCatagoryKey='sqladvisor_counts' + '_' + querykey

        try:
            if redis_conn.exists('sqladvisor_totalQueryCounts') == 0:
                redis_conn.set('sqladvisor_totalQueryCounts',1)
                totalQueryCounts=1
            else:
                totalQueryCounts=int(redis_conn.get('sqladvisor_totalQueryCounts'))
                redis_conn.set('sqladvisor_totalQueryCounts',totalQueryCounts + 1)
                totalQueryCounts=totalQueryCounts + 1

            '''
            记录每个类别的查询次数
            '''
            if redis_conn.exists(countsCatagoryKey) == 0:
                redis_conn.set(countsCatagoryKey,1)
                catagoryQueryCounts=1
#                LOG.info("cache_status: MISS")
            else:
                catagoryQueryCounts=int(redis_conn.get(countsCatagoryKey))
                redis_conn.set(countsCatagoryKey,catagoryQueryCounts + 1)
                catagoryQueryCounts=catagoryQueryCounts + 1

                if isflush == 'noflush':
                    analysis_result = redis_conn.get(querykey)
                    analysis_result=eval(analysis_result)
                    analysis_result[countsCatagoryKey]=catagoryQueryCounts
                    analysis_result['sqladvisor_totalQueryCounts']=totalQueryCounts
#                    LOG.info("cache_status: HIT")
                    cacheStatus=1
                    analysis_result['cacheStatus']=cacheStatus
                    return Response(json.dumps(analysis_result), mimetype="application/json")
        except:
            LOG.warning("连接redis错误")
            sqladvisor_result = sqladvisor_exec(dbhost=dbhost,dbname=dbname,sqlcontent=sqlcontent)
            analysis_result={'cacaheStatus':0,'sqladvisor_totalQueryCounts':'N','sqladvisor_xxx':'N','result':sqladvisor_result}
            return Response(json.dumps(analysis_result), mimetype="application/json")
#        LOG.info("cache_status: MISS")
        cacheStatus=0
        analysis_result = {}
        sqladvisor_result = sqladvisor_exec(dbhost=dbhost,dbname=dbname,sqlcontent=sqlcontent)
        analysis_result['result']=sqladvisor_result
        analysis_result[countsCatagoryKey]=catagoryQueryCounts
        analysis_result['sqladvisor_totalQueryCounts']=totalQueryCounts
        analysis_result['cacheStatus']=cacheStatus
        redis_conn.set(querykey,analysis_result)
        return Response(json.dumps(analysis_result), mimetype="application/json")
    return render_template('sqladvisor.html',dblist=[],dbhostlist=DB_HOSTLIST)

@sqladvisor.route('/display_db/',methods=['GET','POST'])
def display_db():
    if request.is_xhr and request.method == 'GET':
        dbhost = request.args.get('dbhost')
        if not dbhost:
            dbhostlist = { 'result':'' }
            return Response(json.dumps(dbhostlist),mimetype="application/json")
        status, output = commands.getstatusoutput("\
                mysql -u%s -p%s -P%s -h%s -e'show databases' \
                | grep -Ev 'mysql|schema|Database'" % (DB_USER,DB_PWD,DB_PORT,dbhost))
        if status == 0:
            dblist = output.split('\n')
            dblist = { 'result': dblist }
        else:
            LOG.error('连接mysql错误')
            dblist = { 'result':'' }
        return Response(json.dumps(dblist),mimetype="application/json")

def sqladvisor_exec(dbhost,dbname,sqlcontent):
    '''
    执行sql分析
    '''
    status, output = commands.getstatusoutput('sqladvisor -h %s -u %s -p %s -P %s -d %s -q \' %s \' -v 1'
            % (dbhost,DB_USER,DB_PWD,DB_PORT,dbname,sqlcontent))
    return output
