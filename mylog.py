# coding:utf-8
import logging
import logging.config

def getLogger(name='root'):
    CONF_LOG = "./logging.conf"

    logging.config.fileConfig(CONF_LOG)

    return logging.getLogger(name)
