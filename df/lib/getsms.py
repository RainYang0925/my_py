#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'yyh'

import urllib.request
import urllib.parse
import http.cookiejar
import re
import logging


def sms(ph):
	resp = dict()
	logger = logging.getLogger('main.getsms')
	# 保存cookie ，为登录访问其他页面做准备
	cookie = http.cookiejar.CookieJar()
	cjhdr = urllib.request.HTTPCookieProcessor(cookie)
	opener = urllib.request.build_opener(cjhdr)

	# url
	url2 = "http://10.0.240.158:9080/smsbs/vip/logon?trSubCode=chk "
	url4 = "http://10.0.240.158:9080/smsbs/vip/msgQry?trSubCode=now"

	# 登录用户名和密码
	post_data1 = {
		'target_screen': 'null',
		'userNo': 'lif',
		'password': '888888'
	}

	# 将用户名和密码转换为"userNo=lcl&password=111111"的形式
	data1 = urllib.parse.urlencode(post_data1).encode("gbk")
	req2 = urllib.request.Request(url2, data1)
	try:
		opener.open(req2, timeout=5)
	except Exception as ex:
		logger.debug("login %s error:%s" % (url2, ex))
		resp['status'] = 500
		resp['value'] = 'ERROR'
		return (resp)

	# 查询
	post_data2 = {
		'pageStart': '1',
		'lastItemNum': '0',
		'custno': '',
		'srvaccno': '',
		'mobile': ph,
		'tmsgcont': '',
		'tmsgchanno': '',
		'msgstat': '-1'
	}

	data2 = urllib.parse.urlencode(post_data2).encode("gbk")
	req3 = urllib.request.Request(url4, data2)

	try:
		response = opener.open(req3, timeout=5)
	except Exception as ex:
		logger.debug("search sms error:%s" % ex)
		resp['status'] = 500
		resp['value'] = 'ERROR'
		return (resp)

	# 截取验证码
	shuju = response.read().decode("gbk")
	m = re.search(r'动态密码是(\d+)', shuju)
	if m:
		resp['status'] = 0
		resp['value'] = m.group(1)
		logger.debug("phone: %s ,sms:%s" % (ph, resp['value']))
	else:
		resp['status'] = 500
		resp['value'] = 'ERROR'
		logger.debug("phone: %s ,sms not find" % ph)
	return resp


if __name__ == '__main__':
	result = sms(1771)
	print(result)
