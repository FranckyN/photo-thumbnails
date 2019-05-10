"""
    apps_logger
    ~~~~~~~~~~~~~
    Helper module to configure the logging
    copyright: ©2019 by Franck Nassé
"""
import logging
import sys


def configure_logger(current_logger):
    logger = current_logger
    handler = logging.StreamHandler(stream=sys.stdout)
    # handler = RotatingFileHandler(path here, maxBytes=1000000,
    #                              backupCount=2)
    logger.setLevel(logging.DEBUG)
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    print("configure_logger {}".format(current_logger))
