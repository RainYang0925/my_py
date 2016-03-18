#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20160301'
__license__ = 'copy left'

import hashlib
import urllib.request
import subprocess
import logging

logger = logging.getLogger('main.tools')


# 获取http响应
def http_get(url):
	try:
		gt = urllib.request.urlopen(url)
	except Exception as ex:
		logger.debug('Get url %s Exception:%s' % (url, ex))
		res = 'error:%s' % ex
	else:
		if gt.getcode() == 200:
			resp = gt.read()
			resp_str = resp.decode('utf8')
			res = resp_str
		else:
			res = 'error:%d' % gt.getcode()
		gt.close()
	return res


# 执行命令，有返回,返回内容有大小限制
def ex_cmd(cmd):
	res = list()
	try:
		fh = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		fh.wait()
		for line in fh.stdout.readlines():
			line = line.decode().strip()
			if line != '':
				res.append(line)
	except Exception as ex:
		logger.debug('Run cmd %s Exception:%s' % (cmd, ex))
		res.append('error:%s' % ex)
	finally:
		fh.stdout.close()
	return res


# 执行命令，无需返回
def ex_cmd2(cmd):
	subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# 获取文件md5值
def file_md5(file):
	md5file = open(file, 'rb')
	md5_value = hashlib.md5(md5file.read()).hexdigest()
	md5file.close()
	return md5_value
