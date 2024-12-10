# -*- coding: utf-8 -*-

import logging
import sys
import os
import time
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler

def init_logger(logdir, logger_name):
	if not os.path.exists(logdir):
		os.makedirs(logdir)

	if logger_name not in Logger.manager.loggerDict:
		logger = logging.getLogger(logger_name)
		logger.setLevel(logging.DEBUG)
		datefmt = "%Y-%m-%d %H:%M:%S"
		format_str = "[%(asctime)s]: PID:%(process)d file:%(filename)s line:%(lineno)s func:%(funcName)s %(levelname)s %(message)s"
		formatter = logging.Formatter(format_str, datefmt)
		
		# screen handler of level info
		handler = StreamHandler()
		handler.setFormatter(formatter)
		handler.setLevel(logging.INFO)
		logger.addHandler(handler)

		# file handler of level info
		handler = TimedRotatingFileHandler(os.path.join(logdir, "info.log"), when='midnight',backupCount=30)
		handler.setFormatter(formatter)
		handler.setLevel(logging.INFO)
		logger.addHandler(handler)
		
		# file handler of level error
		handler = TimedRotatingFileHandler(os.path.join(logdir, 'error.log'), when='midnight',backupCount=30)
		handler.setFormatter(formatter)
		handler.setLevel(logging.ERROR)
		logger.addHandler(handler)


	logger = logging.getLogger(logger_name)
	return logger

logger = init_logger("./log", "")


if __name__ == '__main__':
	logger = init_logger("./log", 'dataservice')
	logger.error("test-error")
	logger.info("test-info")
	logger.warn("test-warn")