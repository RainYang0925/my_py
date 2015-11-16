#!/usr/bin/env python
# _*_ coding: utf-8 _*_

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20150901'
__license__ = 'copy left'

import os, subprocess, platform, json, re, socket, urllib
import threading
from bottle import *

pt_name = platform.platform()

if pt_name.startswith('Windows'):
	pt_name = 'Windows'
	appium_start = r'"C:/Program Files/Appium/node.exe" "C:/Program Files/Appium/node_modules/appium/lib/server/main.js" --command-timeout 7200 --session-override --local-timezone'
	appium_logpath = r'C:\appium_log'
	nul = 'NUL'
elif pt_name.startswith('Darwin'):
	pt_name = 'Mac OS X'
	appium_start = '/Applications/Appium.app/Contents/Resources/node/bin/node /Applications/Appium.app/Contents/Resources/node_modules/appium/lib/server/main.js --command-timeout 7200 --session-override --local-timezone'
	appium_logpath = '/tmp'
	nul = '/dev/null'
else:
	print "not support on %s" % pt_name
	quit()

# init
socket.setdefaulttimeout(5)
socket.socket._bind = socket.socket.bind


def my_socket_bind(self, *args, **kwargs):
	self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	return socket.socket._bind(self, *args, **kwargs)


socket.socket.bind = my_socket_bind

app = Bottle()


# 测试用方法
@app.route('/status', method='GET')
def status():
	# return template('{"status": 0,"test": "{{name}}"}', name=name)
	resp = dict()
	resp['status'] = 0
	resp['version'] = '1.0'
	resp['platform'] = pt_name
	return resp


# 列出所有的移动设备
@app.route('/list_devices', method='GET')
def list_devices():
	# res dict
	resp = dict()
	resp['status'] = 0
	resp['platform'] = pt_name

	global devices
	devices = list()

	# thread start
	def list_devices_sub(line):
		# print line
		# 5T2SQL1563015797       device product:P7-L07 model:HUAWEI_P7_L07 device:hwp7
		m = re.search(r'(\S+)\s+device.*model:(\S+)', line)
		if m:
			# print m.groups()
			global devices
			tps = dict()
			tps['type'] = 'Android'
			# udid
			tps['udid'], tps['model'] = m.groups()
			# wm size
			fh2 = ex_cmd('adb -s %s shell wm size' % tps['udid'])
			try:
				wm_name, wm_size = fh2[0].split(':')
				wm_size = wm_size.strip()
			except Exception, ex:
				print "adb shell wm size error:%s" % ex
				wm_size = ''
			tps['screen size'] = wm_size
			# android version
			fh3 = ex_cmd('adb -s %s shell getprop ro.build.version.release' % tps['udid'])
			tps['version'] = fh3[0]
			#
			devices.append(tps)

	# thread def end
	fh = ex_cmd('adb devices -l 2>NULL')
	thrs = list()
	for line in fh:
		t = threading.Thread(target=list_devices_sub, args=(line,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()

	# mac
	if pt_name == 'Mac OS X':
		fh = ex_cmd('instruments -s devices 2>NULL')
		for line in fh:
			m = re.search(r'(.+)\s{1}\((\S+)\)\s{1}\[([a-z0-9]+)\]', line)
			if m:
				# print m.groups()
				tps = dict()
				tps['type'] = 'iOS'
				tps['model'], tps['version'], tps['udid'] = m.groups()
				devices.append(tps)
	resp['devices'] = devices
	return resp


# 列出所有的appium执行机器
@app.route('/list_appium', method='GET')
def list_appium():
	resp = dict()
	resp['status'] = 0
	resp['platform'] = pt_name
	appium = list()

	if pt_name == 'Windows':
		fh1 = ex_cmd('wmic process where caption="node.exe" get handle')
		for line1 in fh1:
			pid = line1
			if pid.isdigit():
				fh2 = ex_cmd('wmic process where handle=%d get commandline' % int(pid))
				for line2 in fh2:
					# print 'test', line2
					m = re.search(r'--port (\d+)', line2)
					if m:
						port = m.group(1)
						tps = dict()
						tps['pid'] = pid
						tps['port'] = port
						# tps['cmd'] = line2
						url1 = "http://127.0.0.1:%d/wd/hub/status" % int(port)
						rstmp = http_get(url1)
						if rstmp != 'error':
							rstmp = json.loads(rstmp, encoding='utf-8')
							tps['version'] = rstmp['value']['build']['version']
							if 'sessionId' in rstmp:
								sessionid = rstmp['sessionId']
								tps['sessionid'] = sessionid
								url2 = "http://127.0.0.1:%d/wd/hub/session/%s" % (int(port), sessionid)
								rstmp2 = http_get(url2)
								if rstmp2 != 'error':
									rstmp2 = json.loads(rstmp2, encoding='utf-8')
									tps['udid'] = rstmp2['value']['deviceName']
									tps['app'] = rstmp2['value']['appPackage']
									tps['phone_type'] = rstmp2['value']['platformName']
						appium.append(tps)

	# mac 
	else:
		fh1 = ex_cmd('ps -ef|grep appium |grep -v /bin/sh')
		for line1 in fh1:
			m = re.search(r'^\s*\d+\s+(\d+).*--port (\d+)', line1)
			if m:
				tps = dict()
				# tps['cmd'] = line1
				tps['pid'], tps['port'] = m.groups()
				port = tps['port']
				# print m.groups()
				url = "http://127.0.0.1:%d/wd/hub/status" % int(port)
				rstmp = http_get(url)
				if rstmp != 'error':
					rstmp = json.loads(rstmp, encoding='utf-8')
					tps['version'] = rstmp['value']['build']['version']
					if 'sessionId' in rstmp:
						sessionid = rstmp['sessionId']
						tps['sessionid'] = sessionid
						url2 = "http://127.0.0.1:%d/wd/hub/session/%s" % (int(port), sessionid)
						rstmp2 = http_get(url2)
						if rstmp2 != 'error':
							rstmp2 = json.loads(rstmp2, encoding='utf-8')
							tps['phone_type'] = rstmp2['value']['platformName']
							if tps['phone_type'] == 'iOS':
								tps['app'] = rstmp2['value']['bundleId']
							else:
								tps['app'] = rstmp2['value']['appPackage']
							if 'udid' in rstmp2['value']:
								tps['udid'] = rstmp2['value']['udid']
							else:
								tps['udid'] = ''

				appium.append(tps)
	resp['appium'] = appium
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
	resp = dict()
	resp['status'] = 0

	global devices
	devices = list()

	# thread start
	def install_apk_sub(ud, package, app_path):
		global devices
		ex_cmd('adb -s %s uninstall %s' % (ud, package))
		res = ex_cmd('adb -s %s install -r %s' % (ud, app_path))
		tps = dict()
		tps['udid'] = ud
		tps['flag'] = res[-1]
		devices.append(tps)

	# thread end
	print '#' * 20
	print 'insatll apk debug message'
	print udid, package, app_path
	print '#' * 20
	if app_path and package:
		# print app_path
		if os.path.exists(app_path):
			# app_path = app_path.encode('utf-8')
			# get udid
			local_udids = list()
			fh = ex_cmd('adb devices -l')
			for line in fh:
				m = re.search(r'(\S+)\s+device.*model:(\S+)', line)
				if m:
					local_udids.append(m.group(1))
			# print local_udids

			# 判断udid的值
			if udid != '':
				if udid not in local_udids:
					resp['status'] = 403
					resp['comment'] = 'udid device not find'
					return resp
				else:
					local_udids = []
					local_udids.append(udid)
			# 全部安装。
			# print "install all"
			thrs = list()
			for ud in local_udids:
				print "install apk for %s " % ud
				t = threading.Thread(target=install_apk_sub, args=(ud, package, app_path))
				t.start()
				thrs.append(t)
			for t in thrs:
				t.join()

			resp['result'] = devices
		else:
			resp['status'] = 404
			resp['comment'] = 'apk path not exist'
	else:
		resp['status'] = 405
		resp['comment'] = 'apk path or package is null'
	return resp


# 刷新devices，仅适用于安卓设备
@app.route('/reset_devices', method='GET')
def reset_devices():
	ex_cmd('adb kill-server')
	ex_cmd('adb start-server')
	resp = dict()
	resp['status'] = 0
	return resp


# 刷新appium，根据已经连接的设备，重新启动对应数量的appium
@app.route('/reset_appium', method='GET')
def reset_appium():
	resp = dict()
	resp['status'] = 0
	all_apm = list_appium()['appium']
	for ap in all_apm:
		pid = int(ap['pid'])
		print 'stop appium pid : %d ' % pid
		if pt_name == 'Windows':
			ex_cmd('taskkill /T /F /PID %d' % pid)
		else:
			ex_cmd('kill -9 %d' % pid)
	# start appium
	all_dev = list_devices()['devices']
	# default appium server port
	port = 4723
	# print port
	for dev in all_dev:
		# for dev in range(4):
		logfile = os.path.join(appium_logpath, 'appium_%d.log' % port)
		st_cmd = appium_start + ' --port %d --log %s' % (port, logfile) + ' >%s' % nul
		print 'start appium : ' + st_cmd
		subprocess.Popen(st_cmd, shell=True)
		port += 10
	# return resp
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


def ex_cmd(cmd):
	fh = os.popen(cmd)
	res = list()
	for line in fh.readlines():
		line = line.strip()
		if line != '':
			res.append(line)
	return res


run(app, host='0.0.0.0', port=8080, debug=True)
