#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '[1.0,20150901],[2.0,20160111]'
__license__ = 'copy left'

import hashlib
import json
import logging
import platform
import socket
import urllib.request
import uuid

from bottle import *

if sys.version_info < (3, 4):
	raise RuntimeError('At least Python 3.4 is required.')

pt_name = platform.platform()
static_path = os.path.join(sys.path[0], 'static')
upload_path = os.path.join(sys.path[0], 'pkg')
log_path = os.path.join(sys.path[0], 'run.log')

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
	print("not support on %s" % pt_name)
	quit()

# init
if not os.path.isdir(static_path):
	os.makedirs(static_path)
if not os.path.isdir(upload_path):
	os.makedirs(upload_path)

socket.setdefaulttimeout(10)
logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(filename)s[line:%(lineno)d][%(funcName)s] %(levelname)s %(message)s',
					filename=log_path, filemode='a')
app = Bottle()
logging.info('sf server starting up ...')


# 测试用方法
@app.route('/status', method='GET')
def status():
	# return template('{"status": 0,"test": "{{name}}"}', name=name)
	resp = dict()
	resp['status'] = 0
	resp['version'] = '2.0'
	resp['platform'] = pt_name
	logging.info(resp)
	return resp


# favicon图标
@app.route('/favicon.ico')
def favicon():
	return static_file(filename='favicon.ico', root=static_path, mimetype='image/x-icon')


# 静态图片资源
@app.route('/static/<filename:re:.*\.png>')
def static_png(filename):
	return static_file(filename=filename, root=static_path, mimetype='image/png', download=False)


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
			except Exception as ex:
				logging.exception("adb shell error on udid %s: wm size error:%s" % (tps['udid'], fh2))
				wm_size = ''
			tps['screen size'] = wm_size
			# android version
			fh3 = ex_cmd('adb -s %s shell getprop ro.build.version.release' % tps['udid'])
			tps['version'] = fh3[0]
			#
			devices.append(tps)

	# thread def end
	fh = ex_cmd('adb devices -l')
	thrs = list()
	for line in fh:
		t = threading.Thread(target=list_devices_sub, args=(line,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()

	# mac
	if pt_name == 'Mac OS X':
		fh = ex_cmd('instruments -s devices')
		for line in fh:
			m = re.search(r'(.+)\s{1}\((\S+)\)\s{1}\[([a-z0-9]+)\]', line)
			if m:
				# print m.groups()
				tps = dict()
				tps['type'] = 'iOS'
				tps['model'], tps['version'], tps['udid'] = m.groups()
				devices.append(tps)
	resp['devices'] = devices
	logging.info(resp)
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
	logging.info(resp)
	return resp


# 安装，更新app，提供调试用页面
@app.route('/install_app', method='GET')
def install_show():
	return '''
<html>
<head>
<title>app install test page</title>
</head>
<body>
<form action="/install_app" method="post">
app_select: <input type="file" name="app_select" style="width:500px" value="Browse..." /><br>
copy text to : <br>
app_path: <input type="text" name="app_path" style="width:500px" /><br>
package:  <input name="package" style="width:500px" value="com.rytong.czfinancial" type="text" /><br>
udid: <input name="udid" style="width:500px" type="text" /><br>
<input value="install" type="submit" />
</form>
</body>
</html>
'''


# 安装，更新app的post方法
@app.route('/install_app', method='POST')
def install_app():
	app_path = request.forms.get('app_path')
	package = request.forms.get('package')
	udid = request.forms.get('udid')
	resp = dict()
	resp['status'] = 0
	global devices
	devices = list()

	# thread start
	def install_app_sub(ud, package, app_path):
		global devices
		flag = "Fail"
		if app_path.endswith('apk'):
			ex_cmd('adb -s %s uninstall %s' % (ud, package))
			res = ex_cmd('adb -s %s install -r %s' % (ud, app_path))
			for line in res:
				if line.endswith('Success'):
					flag = "Success"
					break
		else:
			ex_cmd('ideviceinstaller -u %s -U %s' % (ud, package))
			res = ex_cmd('ideviceinstaller -u %s -i %s' % (ud, app_path))
			for line in res:
				if line.endswith('Complete'):
					flag = "Success"
					break
		tps = dict()
		tps['udid'] = ud
		tps['flag'] = flag
		devices.append(tps)

	# thread end
	logging.debug('#' * 20)
	logging.debug('install debug message:')
	logging.debug("udid: %s, package: %s, app_path: %s" % (udid, package, app_path))
	logging.debug('#' * 20)
	if app_path and package:
		# print app_path
		if os.path.exists(app_path):
			# app_path = app_path.encode('utf-8')
			# get udid
			local_udids = list()
			if app_path.endswith('apk'):
				fh = ex_cmd('adb devices -l')
				for line in fh:
					m = re.search(r'(\S+)\s+device.*model:(\S+)', line)
					if m:
						local_udids.append(m.group(1))
			elif pt_name == 'Mac OS X' and app_path.endswith('ipa'):
				fh = ex_cmd('instruments -s devices')
				for line in fh:
					m = re.search(r'(.+)\s{1}\((\S+)\)\s{1}\[([a-z0-9]+)\]', line)
					if m:
						local_udids.append(m.group(3))
			else:
				resp['status'] = 500
				resp['comment'] = 'not support'
				return resp
			logging.debug("local devices: %s" % (local_udids))

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
				logging.debug("install app for %s " % ud)
				t = threading.Thread(target=install_app_sub, args=(ud, package, app_path))
				t.start()
				thrs.append(t)
			for t in thrs:
				t.join()

			resp['result'] = devices
		else:
			resp['status'] = 404
			resp['comment'] = 'app_path not exist'
	else:
		resp['status'] = 405
		resp['comment'] = 'apk path or package is null'
	logging.info(resp)
	return resp


# 刷新devices，仅适用于安卓设备
@app.route('/reset_devices', method='GET')
def reset_devices():
	ex_cmd2('adb kill-server')
	ex_cmd2('adb start-server')
	resp = dict()
	resp['status'] = 0
	logging.info(resp)
	return resp


# 刷新appium，根据已经连接的设备，重新启动对应数量的appium
@app.route('/reset_appium', method='GET')
def reset_appium():
	resp = dict()
	resp['status'] = 0
	all_apm = list_appium()['appium']
	for ap in all_apm:
		pid = int(ap['pid'])
		logging.debug('stop appium pid : %d ' % pid)
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
		logging.debug('start appium : ' + st_cmd)
		ex_cmd2(st_cmd)
		port += 10
	# return resp
	logging.info(resp)
	return resp


# 根据udid获取设备信息
@app.route('/device/<udid>/info/<prop>', method='GET')
def device_info(udid, prop):
	resp = dict()
	resp['status'] = 0
	resp['prop'] = prop
	if len(udid) == 40:
		if pt_name == 'Mac OS X':
			if prop != 'all':
				res = ex_cmd('ideviceinfo -u %s -k %s' % (udid, prop))
			else:
				res = ex_cmd('ideviceinfo -u %s -x' % (udid))
		else:
			res = 'not support idevices on other os'
	else:
		# to_do
		if prop != 'all':
			res = ex_cmd('adb -s %s shell getprop %s' % (udid, prop))
		else:
			res = ex_cmd('adb -s %s shell getprop' % (udid))
	resp['value'] = res
	logging.info(resp)
	return resp


# 根据udid获取设备实时截图
@app.route('/device/<udid>/png/<prop>', method='GET')
def device_png(udid, prop):
	fname = os.path.join(sys.path[0], 'static', udid)
	if prop != 'refresh' and os.path.exists('%s.png' % fname):
		logging.debug('use old png file: %s.png' % fname)
	else:
		if len(udid) == 40:
			if pt_name == 'Mac OS X':
				ex_cmd('idevicescreenshot -u %s %s.tiff' % (udid, fname))
				ex_cmd('sips -s format png %s.tiff --out %s.png' % (fname, fname))
			else:
				res = 'not support idevice on other os'
				return res
		# android support
		else:
			# if pt_name == 'Mac OS X':
			#	ex_cmd("adb -s %s shell screencap -p |perl -pe 's/\\x0D\\x0A/\\x0A/g' > %s.png" % (udid, fname))
			# else:
			ex_cmd('adb -s %s shell screencap -p /sdcard/screenshot.png' % udid)
			ex_cmd('adb -s %s pull /sdcard/screenshot.png %s.png' % (udid, fname))
		logging.debug('get new png file: %s.png' % fname)
	return static_file(filename='%s.png' % udid, root=static_path, mimetype='image/png')


@app.route('/upload', method='GET')
def sf_upload():
	return '''
<html>
<head>
<title>apk,ipa upload page</title>
</head>
<body>
<form action="upload" method="POST" enctype="multipart/form-data">
<input type="file" name="pkg_data" value='浏览...'/>
<input type="submit" value="上传"/>
</form>
</body>
</html>
'''


@app.route('/upload', method='POST')
def do_upload():
	resp = dict()
	uploadfile = request.files.get('pkg_data')
	if not isinstance(uploadfile, FileUpload):
		resp['status'] = 404
		resp['comment'] = 'File is null.'
		return resp
	upload_fn = uploadfile.filename.lower()
	if not (upload_fn.endswith('.apk') or upload_fn.endswith('.ipa')):
		resp['status'] = 403
		resp['comment'] = 'File extension not allowed.'
		return resp
	name, ext = os.path.splitext(upload_fn)
	save_file_name = os.path.join(upload_path, str(uuid.uuid1()) + ext)
	uploadfile.save(save_file_name, overwrite=True)
	md5_value = file_md5(save_file_name)
	logging.debug("upload success,save_path:%s,md5_value:%s" % (save_file_name, md5_value))
	resp['status'] = 0
	resp['save_path'] = save_file_name
	resp['md5_value'] = md5_value
	logging.info(resp)
	return resp


def http_get(url):
	try:
		logging.info("connect to url %s" % (url))
		gt = urllib.request.urlopen(url)
	except Exception as ex:
		logging.exception(ex)
		return "error"
	else:
		if gt.getcode() == 200:
			res = gt.read()
			res_str = res.decode('utf8')
			gt.close()
			logging.info("url response: %s" % (res_str))
			return res_str
		else:
			return "error"


def ex_cmd(cmd):
	logging.debug(cmd)
	res = list()
	try:
		fh = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		fh.wait()
		for line in fh.stdout.readlines():
			line = line.decode().strip()
			if line != '':
				res.append(line)
		fh.stdout.close()
	except Exception as ex:
		logging.exception(ex)
		res.append('error')
	# logging.info(res)
	return res


def ex_cmd2(cmd):
	logging.debug(cmd)
	subprocess.Popen(cmd, shell=True)


def file_md5(file):
	md5file = open(file, 'rb')
	md5_value = hashlib.md5(md5file.read()).hexdigest()
	md5file.close()
	return md5_value


run(app=app, server='cherrypy', host='0.0.0.0', port=8080, reloader=False, debug=True)
