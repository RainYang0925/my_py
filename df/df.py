#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '[3.0,20160425]'
__license__ = 'copy left'

import codecs
import logging
import socket
from configparser import ConfigParser
from lib import *

# check env
if sys.version_info < (3, 4):
	raise RuntimeError('At least Python 3.4 is required.')

# global setting
cf = ConfigParser()
# cf.read('config.ini')
cf.readfp(codecs.open('config.ini', 'r', 'utf-8-sig'))
port = cf.getint('system', 'port')
data_file = cf.get('system', 'data_file')
sf_host_str = cf.get('system', 'sf_host')
log_path = cf.get('system', 'logfile')

sf_hosts = list()
for x in sf_host_str.split(','):
	sf_hosts.append(x.strip())

# init
socket.setdefaulttimeout(10)
logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(filename)s[line:%(lineno)d][%(funcName)s] %(levelname)s %(message)s',
					filename=log_path, filemode='a')
app = Bottle()
logging.info('...........................')
logging.info('df server starting up ...')

t1 = threading.Thread(target=ref_info, args=(data_file, sf_hosts))
t1.setDaemon(True)
t1.start()


# 测试用方法
@app.route('/status', method='GET')
def status():
	resp = dict()
	resp['status'] = 0
	resp['version'] = '3.0'
	logging.info(resp)
	return resp


# 获取执行机
@app.route('/list_runner', method='GET')
def list_runner():
	resp = dict()
	sql = "select * from runner"
	res = fetchall(data_file, sql)
	if res is not None:
		resp['status'] = 0
		resp['value'] = res
	else:
		resp['status'] = 500
		resp['value'] = 'ERROR'
	logging.info(resp)
	return resp


# 获取某个执行机器的详细信息
@app.route('/list_runner/<ip>', method='GET')
def list_runner_ip(ip):
	for x in sf_hosts:
		if ip == x.split(':')[0]:
			redirect('http://%s/status' % x)
	resp = dict()
	resp['status'] = 500
	resp['value'] = 'host not find'
	logging.info(resp)
	return resp


# 列出所有的移动设备
@app.route('/list_devices', method='GET')
def list_devices():
	resp = dict()
	sql = "select * from devices where state <> 'offline'"
	res = fetchall(data_file, sql)
	if res is not None:
		resp['status'] = 0
		resp['value'] = res
	else:
		resp['status'] = 500
		resp['value'] = 'ERROR'
	logging.info(resp)
	return resp


# 列出所有的appium
@app.route('/list_appium', method='GET')
def list_appium():
	resp = dict()
	sql = "select * from appium"
	res = fetchall(data_file, sql)
	if res is not None:
		resp['status'] = 0
		resp['value'] = res
	else:
		resp['status'] = 500
		resp['value'] = 'ERROR'
	logging.info(resp)
	return resp


# 刷新devices，仅适用于安卓设备
@app.route('/reset_devices', method='GET')
def reset_devices():
	def reset_devices_sub(sf_adv):
		url1 = "http://%s/reset_devices" % sf_adv
		http_get(url1)

	thrs = list()
	for sf_adv in sf_hosts:
		t = threading.Thread(target=reset_devices_sub, args=(sf_adv,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()
	resp = dict()
	resp['status'] = 0
	return resp


# 刷新appium，根据已经连接的设备，重新启动对应数量的appium
@app.route('/reset_appium', method='GET')
def reset_appium():
	def reset_appium_sub(sf_adv):
		url1 = "http://%s/reset_appium" % sf_adv
		http_get(url1)

	thrs = list()
	for sf_adv in sf_hosts:
		t = threading.Thread(target=reset_appium_sub, args=(sf_adv,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()
	resp = dict()
	resp['status'] = 0
	return resp


# 获取短信验证码
@app.route('/sms/<phone>', method='GET')
def df_sms(phone):
	return sms(phone)


run(app=app, server='cherrypy', host='0.0.0.0', port=port, reloader=False, debug=True)
