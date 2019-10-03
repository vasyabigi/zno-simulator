# Logging should be configured before any other imports and usage
import logging


logging.config.fileConfig('log.conf')


def getLogger(name):
    return logging.getLogger(name)
