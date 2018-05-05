# coding:utf-8
import logging
import logging.config


def getLogger(name='root'):
    logfile = "./logging.conf"
    logging.config.fileConfig(logfile)

    return logging.getLogger(name)
