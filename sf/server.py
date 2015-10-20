#!/usr/bin/env python
# _*_ coding: utf-8 _*_

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20151010'
__license__ = 'copy left'

import pymssql, json, socket, urllib, urllib2
import threading
from bottle import *

dbhost = '10.0.247.57'
db_id = 'sa'
db_password = '123456'
db_name = 'DCTT'
# 设备表名：mobile
# appium表名：appium
# 执行机的地址配置，包括ip和端口号
sf_host = ('10.1.38.76:8080', '10.1.38.98:8080')

# init
socket.setdefaulttimeout(5)
socket.socket._bind = socket.socket.bind


def my_socket_bind(self, *args, **kwargs):
	self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	return socket.socket._bind(self, *args, **kwargs)


socket.socket.bind = my_socket_bind

app = Bottle()

# db connect
conn = pymssql.connect(host=dbhost, user=db_id, password=db_password, database=db_name, charset="utf8")


# 测试用方法
@app.route('/status', method='GET')
def status():
	# return template('{"status": 0,"test": "{{name}}"}', name=name)
	resp = dict()
	resp['status'] = 0
	resp['version'] = '1.0'
	return resp


# 获取appium的执行机
@app.route('/list_runner', method='GET')
def list_runner():
	resp = dict()
	resp['status'] = 0

	global sf_online
	sf_online = list()
	# thread start
	def list_runner_sub(sf_adv):
		url1 = "http://%s/status" % sf_adv
		# print url1
		rstmp1 = http_get(url1)
		if rstmp1 != 'error':
			global sf_online
			sf_online.append(sf_adv)
		# rstmp2 = json.loads(rstmp1, encoding='utf-8')
		# platform = rstmp2['platform']

	# thread def end

	thrs = list()
	for sf_adv in sf_host:
		t = threading.Thread(target=list_runner_sub, args=(sf_adv,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()

	resp['runner'] = sf_online
	return resp


# 刷新所有的移动设备
@app.route('/ref_devices', method='GET')
def ref_devices():
	# res dict
	global dev_list
	dev_list = dict()
	resp = dict()
	resp['status'] = 0

	# thread start
	def ref_devices_sub(sf_adv):
		url1 = "http://%s/list_devices" % sf_adv
		# print url1
		rstmp1 = http_get(url1)
		if rstmp1 != 'error':
			global dev_list
			rstmp2 = json.loads(rstmp1, encoding='utf-8')
			platform = rstmp2['platform']
			devs = rstmp2['devices']
			for dev in devs:
				dev['platform'] = platform
				dev['ip'] = sf_adv.split(':')[0]
				udid = dev['udid']
				dev_list[udid] = dev

	# thread def end

	thrs = list()
	for sf_adv in sf_host:
		t = threading.Thread(target=ref_devices_sub, args=(sf_adv,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()

	# sql connect
	# conn = pymssql.connect(host=dbhost, user=db_id, password=db_password, database=db_name, charset="utf8")
	cur1 = conn.cursor()

	## for devices
	cur1.execute('select MT_UDID from mobile')
	res_tmp = cur1.fetchall()
	db_devlist = list()

	for dev in res_tmp:
		db_devlist.append(dev[0])

	# device action
	for db_dev in db_devlist:
		# print "check udid", db_dev
		if db_dev in dev_list:
			dev_info = dev_list[db_dev]
			# print "find  it "
			udid = dev_info['udid']
			if 'screen size' in dev_info:
				screen_size = dev_info['screen size']
			else:
				screen_size = ''
			version = dev_info['version']
			ip = dev_info['ip']
			model = dev_info['model']
			type = dev_info['type']
			# print udid,screen_size
			sql = "update mobile set MT_ONLINE='%s',MT_OPREATION='%s',MT_IPADDRESS='%s',MT_UPDATEON=getDate() where MT_UDID='%s'" % (
				1, version, ip, udid)
		else:
			sql = "update mobile set MT_ONLINE='%s',MT_IPADDRESS='%s',MT_UPDATEON=getDate() where MT_UDID='%s'" % (
				0, '', db_dev)
		# print sql
		cur1.execute(sql)
		conn.commit()

	# 新增设备的处理
	for dev in dev_list.keys():
		if dev not in db_devlist:
			# print "not find"
			dev = dev_list[dev]
			udid = dev['udid']
			if 'screen size' in dev:
				screen_size = dev['screen size']
			else:
				screen_size = ''
			version = dev['version']
			ip = dev['ip']
			model = dev['model']
			type = dev['type']
			sql = "insert into mobile values ('%s','%s','%s','%s','%s','','','','','%s','%s','',getDate(),getDate())" % (
				model, udid, 1, type, screen_size, version, ip)
			# print sql
			cur1.execute(sql)
			conn.commit()
	# conn.close()
	return resp


# 刷新所有的appium
@app.route('/ref_appium', method='GET')
def ref_appium():
	resp = dict()
	resp['status'] = 0
	global apm_list
	apm_list = dict()
	# appium list

	def ref_appium_sub(sf_adv):
		url1 = "http://%s/list_appium" % sf_adv
		ip = sf_adv.split(':')[0]
		rstmp1 = http_get(url1)
		if rstmp1 != 'error':
			global apm_list
			rstmp2 = json.loads(rstmp1, encoding='utf-8')
			platform = rstmp2['platform']
			devs = rstmp2['appium']
			for dev in devs:
				dev['platform'] = platform
				dev['ip'] = ip
				url = 'http://%s:%s/wd/hub' % (ip, dev['port'])
				apm_list[url] = dev

	thrs = list()
	for sf_adv in sf_host:
		t = threading.Thread(target=ref_appium_sub, args=(sf_adv,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()

	# sql connect
	# conn = pymssql.connect(host=dbhost, user=db_id, password=db_password, database=db_name, charset="utf8")
	cur1 = conn.cursor()

	sql = "truncate table appium"
	cur1.execute(sql)
	conn.commit()

	for apm in apm_list.keys():
		apm_info = apm_list[apm]
		# 在刚刚启动，未启动好的时候，异常处理
		platform = apm_info['platform']
		ip = apm_info['ip']
		try:
			version = apm_info['version']
			pid = apm_info['pid']
		except Exception, ex:
			version = ''
			pid = ''
		# to
		if 'udid' in apm_info:
			udid = apm_info['udid']
			isbusy = '1'
		else:
			udid = ''
			isbusy = '0'
		if 'app' in apm_info:
			app = apm_info['app']
		else:
			app = ''
		sql = "insert into appium values ('%s','%s','%s','%s','%s','%s','%s','%s','%s',getDate())" % (
			apm, 1, isbusy, ip, platform, version, udid, pid, app)
		cur1.execute(sql)
		conn.commit()
	# conn.close()
	return resp


# 安装，更新apk，提供调试用页面
@app.route('/install_apk', method='GET')
def install_show():
	return '''
	<form action="/install_apk" method="post">
	app_select: <input type="file" name="app_select" style="width:500px" value="Browse..." /><br>
	copy text to : <br>
	app_path: <input type="text" name="app_path" style="width:500px" /><br>
	package:  <input name="package" style="width:500px" value="com.rytong.czfinancial" type="text" /><br>
	udid: <input name="udid" style="width:500px" type="text" /><br>
	<input value="install" type="submit" />
	</form>
	'''


# 安装，更新apk的post方法
@app.route('/install_apk', method='POST')
def install_apk():
	app_path = request.forms.get('app_path')
	package = request.forms.get('package')
	udid = request.forms.get('udid')

	data = {"app_path": app_path, "package": package, "udid": udid}

	resp = dict()
	# resp['status'] = 0

	if udid != '':
		# sql connect
		# conn = pymssql.connect(host=dbhost, user=db_id, password=db_password, database=db_name, charset="utf8")
		cur1 = conn.cursor()

		## for devices
		sql = "select MT_IPADDRESS from mobile where MT_UDID='%s'" % udid
		cur1.execute(sql)
		res_tmp = cur1.fetchall()
		if len(res_tmp) != 1:
			resp['status'] = 404
			resp['result'] = ({"udid": udid, "flag": "udid not find "},)
		else:
			ip = res_tmp[0][0]
			url = ''
			for sf_adv in sf_host:
				sf_ip = sf_adv.split(':')[0]
				# print ip, sf_ip, sf_adv
				if ip == sf_ip:
					url = 'http://%s/install_apk' % sf_adv
			if url != '':
				resp = http_post(url, data)
			else:
				resp['status'] = 505
				resp['comment'] = 'ip not find'
			# conn.close()
	else:
		resp['status'] = 500
		resp['comment'] = 'to do xxx'
	return resp


# 刷新devices，仅适用于安卓设备
@app.route('/reset_devices', method='GET')
def reset_devices():
	def reset_devices_sub(sf_adv):
		url1 = "http://%s/reset_devices" % sf_adv
		rstmp1 = http_get(url1)

	thrs = list()
	for sf_adv in sf_host:
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
		rstmp1 = http_get(url1)

	thrs = list()
	for sf_adv in sf_host:
		t = threading.Thread(target=reset_appium_sub, args=(sf_adv,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()

	resp = dict()
	resp['status'] = 0
	return resp


def http_get(url):
	try:
		gt = urllib.urlopen(url)
	except Exception, ex:
		print "get url %s failed" % url, ex
		return "error"
	else:
		if gt.getcode() == 200:
			res = gt.read()
			return res
		else:
			return "error"


def http_post(url, data):
	data = urllib.urlencode(data)
	req = urllib2.Request(url=url, data=data)
	try:
		gt = urllib2.urlopen(req)
	except Exception, ex:
		print "get url %s failed" % url, ex
		return "error"
	else:
		if gt.getcode() == 200:
			res = gt.read()
			return res
		else:
			return "error"


run(app, host='0.0.0.0', port=9090, debug=True)
