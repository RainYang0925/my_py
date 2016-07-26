#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '[1.0,20150901],[2.0,20160111],[3.0,20160317]'
__license__ = 'copy left'

import json
import codecs
import logging
from logging.handlers import RotatingFileHandler
import platform
import socket
import uuid
from configparser import ConfigParser
from lib import *
from prep import ins

# check env
if sys.version_info < (3, 4):
	raise RuntimeError('At least Python 3.4 is required.')
pt_name = platform.platform()
if pt_name.startswith('Windows'):
	pt_name = 'Windows'
	sfind = 'findstr'
elif pt_name.startswith('Darwin'):
	pt_name = 'macOS'
	sfind = 'grep'
else:
	print("not support on %s" % pt_name)
	quit()


# global setting
cf = ConfigParser()
# cf.read('config.ini')
cf.readfp(codecs.open('config.ini', 'r', 'utf-8-sig'))
port = cf.getint('system', 'port')
static_path = cf.get('system', 'static_dir')
upload_path = cf.get('system', 'upload_dir')
selenium_flag = cf.getboolean('system', 'selenium')
appium_flag = cf.getboolean('system', 'appium')
log_path = cf.get('system', 'logfile')
device_ginfo = dict()


# init
socket.setdefaulttimeout(10)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(log_path, mode='a', maxBytes=10 * 1000 * 1000, backupCount=1)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d][%(funcName)s] %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Bottle()
logger.info('...........................')
logger.info('sf server starting up ...')

pt_system = platform.system()
pt_node = platform.node()
pt_version = platform.version()
pt_machine = platform.machine()

# selenium,appium setting
if appium_flag is True:
	appium_port = cf.getint(pt_name, 'appium_port')
	appium_start = cf.get(pt_name, 'appium_cmd')
	appium_logpath = cf.get(pt_name, 'appium_log')
	if not os.path.isdir(upload_path):
		os.makedirs(upload_path)
	if not os.path.isdir(appium_logpath):
		os.makedirs(appium_logpath)
if selenium_flag is True:
	selenium_port = cf.get(pt_name, 'selenium_port')
	selenium_cmd = cf.get(pt_name, 'selenium_cmd')
	selenium_arg = cf.get(pt_name, 'selenium_arg')
	selenium_log = cf.get(pt_name, 'selenium_log')
	ie_driver = cf.get(pt_name, 'webdriver.ie.driver')
	chrome_driver = cf.get(pt_name, 'webdriver.chrome.driver')
	sm_start = 'java -jar %s -port %s %s -log %s' % (selenium_cmd, selenium_port, selenium_arg, selenium_log)
	if chrome_driver.strip() != '':
		sm_start = '%s -Dwebdriver.chrome.driver=%s' % (sm_start, chrome_driver)
	if ie_driver.strip() != '':
		sm_start = '%s -Dwebdriver.ie.driver=%s' % (sm_start, ie_driver)
	logger.info('start selenium server: %s' % sm_start)
	ex_cmd2(sm_start)


# 获取全局信息
@app.route('/status', method='GET')
def status():
	resp = dict()
	resp['status'] = 0
	resp['platform'] = pt_system
	resp['hostname'] = pt_node
	resp['version'] = pt_version
	resp['machine'] = pt_machine
	resp['appium'] = appium_flag
	resp['selenium'] = selenium_flag
	logger.info(resp)
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
	resp = dict()
	resp['status'] = 0
	resp['platform'] = pt_name
	if appium_flag is False:
		logger.info(resp)
		return resp
	devices = list()
	global device_ginfo
	# thread start
	def list_devices_sub(line):
		m = re.search(r'(\S+)\s+device(.*model:(\S+))?', line)
		if m:
			tps = dict()
			tps['type'] = 'Android'
			# udid
			tps['udid'], tps['model'] = m.group(1, 3)
			# 判断是否在缓存中
			if tps['udid'] in device_ginfo:
				tps = device_ginfo[tps['udid']]
			else:
				if tps['model'] is None:
					fh1 = ex_cmd('adb -s %s shell getprop ro.product.model' % tps['udid'])[0]
					if fh1.startswith('error'):
						return None
					else:
						tps['model'] = fh1
				# wm size
				fh2 = ex_cmd('adb -s %s shell dumpsys display|%s mDefaultViewport' % (tps['udid'], sfind))[0]
				if fh2.startswith('error'):
					return None
				else:
					n = re.search(r'deviceWidth=(\d+),\s+deviceHeight=(\d+)', fh2)
					if n:
						width, height = n.group(1, 2)
						tps['screen size'] = '%sx%s' % (height, width)
					else:
						tps['screen size'] = ''
						logger.debug(
							"adb shell error on udid %s: dumpsys display|%s mDefaultViewport" % (tps['udid'], sfind))
				# android version
				fh3 = ex_cmd('adb -s %s shell getprop ro.build.version.release' % tps['udid'])[0]
				if fh3.startswith('error'):
					return None
				else:
					tps['version'] = fh3
				device_ginfo[tps['udid']] = tps
			devices.append(tps)

	# thread def end
	fh = ex_cmd('adb devices -l')
	thrs = list()
	for line in fh[1:]:
		t = threading.Thread(target=list_devices_sub, args=(line,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()

	# mac
	if pt_name == 'macOS':
		fh = ex_cmd('idevice_id -l')
		for line in fh:
			if len(line) == 40:
				tps = dict()
				tps['type'] = 'iOS'
				tps['udid'] = line
				if tps['udid'] in device_ginfo:
					tps = device_ginfo[tps['udid']]
				else:
					fh2 = ex_cmd('ideviceinfo -u %s -s' % line)
					for line2 in fh2:
						if line2.startswith('DeviceClass'):
							tps['model'] = line2.split()[1]
						elif line2.startswith('ProductVersion'):
							tps['version'] = line2.split()[1]
							break
					device_ginfo[tps['udid']] = tps
				devices.append(tps)
	resp['devices'] = devices
	logger.info(resp)
	return resp


# 列出所有的appium执行机器
@app.route('/list_appium', method='GET')
def list_appium():
	resp = dict()
	resp['status'] = 0
	resp['platform'] = pt_name
	if appium_flag is False:
		logger.info(resp)
		return resp
	appium = list()
	if pt_name == 'Windows':
		fh1 = ex_cmd('wmic process where caption="node.exe" get handle')
		for line1 in fh1:
			pid = line1
			if pid.isdigit():
				fh2 = ex_cmd('wmic process where handle=%d get commandline' % int(pid))
				for line2 in fh2:
					m = re.search(r'--port (\d+)', line2)
					if m:
						port = m.group(1)
						tps = dict()
						tps['pid'] = pid
						tps['port'] = port
						# tps['cmd'] = line2
						url1 = "http://127.0.0.1:%d/wd/hub/status" % int(port)
						rstmp = http_get(url1)
						if not rstmp.startswith('error'):
							rstmp = json.loads(rstmp, encoding='utf-8')
							tps['version'] = rstmp['value']['build']['version']
							if 'sessionId' in rstmp:
								sessionid = rstmp['sessionId']
								tps['sessionid'] = sessionid
								url2 = "http://127.0.0.1:%d/wd/hub/session/%s" % (int(port), sessionid)
								rstmp2 = http_get(url2)
								if not rstmp2.startswith('error'):
									rstmp2 = json.loads(rstmp2, encoding='utf-8')
									tps['udid'] = rstmp2['value']['deviceName']
									tps['app'] = rstmp2['value']['appPackage']
									tps['phone_type'] = rstmp2['value']['platformName']
								logger.info(rstmp2)
						logger.info(rstmp)
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
				url = "http://127.0.0.1:%d/wd/hub/status" % int(port)
				rstmp = http_get(url)
				if not rstmp.startswith('error'):
					rstmp = json.loads(rstmp, encoding='utf-8')
					tps['version'] = rstmp['value']['build']['version']
					if 'sessionId' in rstmp:
						sessionid = rstmp['sessionId']
						tps['sessionid'] = sessionid
						url2 = "http://127.0.0.1:%d/wd/hub/session/%s" % (int(port), sessionid)
						rstmp2 = http_get(url2)
						if not rstmp2.startswith('error'):
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
						logger.info(rstmp2)
				logger.info(rstmp)
				appium.append(tps)
	resp['appium'] = appium
	logger.info(resp)
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
	udid = request.forms.get('udid').strip()
	resp = dict()
	resp['status'] = 0
	devices_res = list()

	# thread start
	def install_app_sub(ud, package, app_path):
		flag = "Fail"
		if app_path.endswith('apk'):
			ex_cmd('adb -s %s uninstall %s' % (ud, package), 60)
			res = ex_cmd('adb -s %s install -r %s' % (ud, app_path), 120)
			for line in res:
				if line.endswith('Success'):
					flag = "Success"
					break
		else:
			ex_cmd('ideviceinstaller -u %s -U %s' % (ud, package), 60)
			res = ex_cmd('ideviceinstaller -u %s -i %s' % (ud, app_path), 120)
			for line in res:
				if line.endswith('Complete'):
					flag = "Success"
					break
		tps = dict()
		tps['udid'] = ud
		tps['flag'] = flag
		devices_res.append(tps)

	# thread end
	logger.debug('#' * 20)
	logger.debug('install debug message:')
	logger.debug("udid: %s, package: %s, app_path: %s" % (udid, package, app_path))
	logger.debug('#' * 20)
	if app_path and package:
		# print app_path
		if os.path.exists(app_path):
			local_udids = list()
			if app_path.endswith('apk'):
				fh = ex_cmd('adb devices -l')
				for line in fh[1:]:
					m = re.search(r'(\S+)\s+device(.*model:(\S+))?', line)
					if m:
						local_udids.append(m.group(1))
			elif pt_name == 'macOS' and app_path.endswith('ipa'):
				fh = ex_cmd('idevice_id -l')
				for line in fh:
					if len(line) == 40:
						local_udids.append(line)
			else:
				resp['status'] = 500
				resp['comment'] = 'not support'
				return resp
			logger.debug("local devices: %s" % (local_udids))

			# fix 20160525
			select_udids = list();
			for ud in udid.split(','):
				ud = ud.strip()
				if ud == '':
					continue
				elif ud not in local_udids:
					tps = dict()
					tps['udid'] = ud
					tps['flag'] = 'device not find'
					devices_res.append(tps)
				else:
					select_udids.append(ud)
			if udid == '':
				select_udids = local_udids
			# 全部安装。
			# print(select_udids)
			thrs = list()
			for ud in select_udids:
				logger.debug("install app for %s " % ud)
				t = threading.Thread(target=install_app_sub, args=(ud, package, app_path))
				t.start()
				thrs.append(t)
			for t in thrs:
				t.join()

			resp['result'] = devices_res
		else:
			resp['status'] = 404
			resp['comment'] = 'app_path not exist'
	else:
		resp['status'] = 405
		resp['comment'] = 'app_path or package is null'
	logger.info(resp)
	return resp


# 刷新devices，仅适用于安卓设备
@app.route('/reset_devices', method='GET')
def reset_devices():
	resp = dict()
	resp['status'] = 0
	if appium_flag is True:
		ex_cmd('adb kill-server')
		ex_cmd2('adb start-server')
	logger.info(resp)
	return resp


# 刷新appium，根据已经连接的设备，重新启动对应数量的appium
@app.route('/reset_appium/<cmd>', method='GET')
def reset_appium(cmd):
	resp = dict()
	resp['status'] = 0
	if appium_flag is False:
		logger.info(resp)
		return resp
	all_apm = list_appium()['appium']
	all_dev = list_devices()['devices']
	port = appium_port
	# reboot appium
	if cmd == 'reboot':
		for ap in all_apm:
			pid = int(ap['pid'])
			logger.debug('stop appium pid : %d ' % pid)
			if pt_name == 'Windows':
				ex_cmd2('taskkill /T /F /PID %d' % pid)
			else:
				ex_cmd2('kill -9 %d' % pid)
		# start appium
		# default appium server port
		for dev in all_dev:
			while port_isfree('127.0.0.1', port) is False:
				port += 10
			bpport = port + 3
			chport = port + 6
			logfile = os.path.join(appium_logpath, 'appium_%d.log' % port)
			st_cmd = '%s --port %d --bootstrap-port %d --chromedriver-port %d --log %s >%s' % (
				appium_start, port, bpport, chport, logfile, os.devnull)
			logger.debug('start appium : %s' % st_cmd)
			ex_cmd2(st_cmd)
			port += 10
	# start new appium
	else:
		ct = len(all_dev) - len(all_apm)
		port = port + len(all_apm) * 10
		while ct > 0:
			while port_isfree('127.0.0.1', port) is False:
				port += 10
			bpport = port + 3
			chport = port + 6
			logfile = os.path.join(appium_logpath, 'appium_%d.log' % port)
			st_cmd = '%s --port %d --bootstrap-port %d --chromedriver-port %d --log %s >%s' % (
				appium_start, port, bpport, chport, logfile, os.devnull)
			logger.debug('start appium : %s' % st_cmd)
			ex_cmd2(st_cmd)
			port += 10
			ct -= 1
	# return resp
	logger.info(resp)
	return resp


# 根据udid获取设备状态
@app.route('/device/<udid>/state', method='GET')
def device_state(udid):
	resp = dict()
	resp['status'] = 0
	if appium_flag is False:
		logger.info(resp)
		return resp
	if len(udid) == 40:
		if pt_name == 'macOS':
			res = ex_cmd('idevicename -u %s' % udid)
		else:
			res = 'ERROR: ideviceinfo not support on other os'
		if len(res) == 1:
			res = res[0]
			if res.startswith('ERROR'):
				resp['value'] = 'offline'
			else:
				resp['value'] = 'online'
		else:
			resp['value'] = 'unknown'
	else:
		res = ex_cmd('adb -s %s get-state' % udid)
		if len(res) == 1:
			res = res[0]
			if res == 'device':
				resp['value'] = 'online'
			else:
				resp['value'] = 'offline'
		else:
			resp['value'] = 'unknown'
	logger.info(resp)
	return resp


# 根据udid执行一些命令,only support android
@app.route('/device/<udid>/cmd/<cmd>', method='GET')
def device_cmd(udid, cmd):
	logger.debug('run cmd %s on device %s ' % (cmd, udid))
	resp = dict()
	resp['status'] = 0
	if cmd == 'wakeup':
		ex_cmd2('adb -s %s shell input keyevent 26' % (udid))
	elif cmd == 'reboot':
		ex_cmd2('adb -s %s reboot' % (udid))
	else:
		resp['status'] = 404
	logger.info(resp)
	return resp


# 根据udid获取设备信息
@app.route('/device/<udid>/info/<prop>', method='GET')
def device_info(udid, prop):
	resp = dict()
	resp['status'] = 0
	if appium_flag is False:
		logger.info(resp)
		return resp
	resp['prop'] = prop
	if len(udid) == 40:
		if pt_name == 'macOS':
			res = ex_cmd('ideviceinfo -u %s -k %s' % (udid, prop))
		else:
			res = 'error: ideviceinfo not support on other os'
	else:
		res = ex_cmd('adb -s %s shell getprop %s' % (udid, prop))
	if len(res) == 0:
		res = ''
		resp['status'] = 404
	elif len(res) == 1:
		res = res[0]
		if res.startswith('error'):
			resp['status'] = 500
	resp['value'] = res
	logger.info(resp)
	return resp


# 根据udid获取设备实时截图
@app.route('/device/<udid>/png/<prop>', method='GET')
def device_png(udid, prop):
	fname = os.path.join(static_path, udid)
	if prop == 'refresh':
		# iOS support
		if len(udid) == 40:
			if pt_name == 'macOS':
				ex_cmd('idevicescreenshot -u %s %s.tiff' % (udid, fname))
				ex_cmd('sips -s format png %s.tiff --out %s.png' % (fname, fname))
			else:
				logger.debug('error: not support idevicescreenshot on other os')
				return static_file(filename='404.png', root=static_path, mimetype='image/png')
		# android support
		else:
			res1 = ex_cmd('adb -s %s shell sh /data/local/tmp/cap.sh' % udid)
			if res1[0].startswith('PID'):
				res2 = ex_cmd('adb -s %s pull /data/local/tmp/tmpscreen.jpg %s.jpg' % (udid, fname))
				if len(res2) == 0 or not res2[0].startswith('remote'):
					if os.path.exists('%s.jpg' % fname) and os.path.getsize('%s.jpg' % fname) > 0:
						logger.debug('minicap get new img file: %s.jpg' % fname)
						return static_file(filename='%s.jpg' % udid, root=static_path, mimetype='image/jpg')
			ex_cmd('adb -s %s shell screencap -p /sdcard/screenshot.png' % udid)
			ex_cmd('adb -s %s pull /sdcard/screenshot.png %s.png' % (udid, fname))
			logger.debug('screencap get new img file: %s.png' % fname)
			return static_file(filename='%s.png' % udid, root=static_path, mimetype='image/png')
	else:
		logger.debug('use old image file: %s' % fname)
	# use old file
	if os.path.exists('%s.jpg' % fname) and os.path.getsize('%s.jpg' % fname) > 0:
		return static_file(filename='%s.jpg' % udid, root=static_path, mimetype='image/jpg')
	elif os.path.exists('%s.png' % fname) and os.path.getsize('%s.png' % fname) > 0:
		return static_file(filename='%s.png' % udid, root=static_path, mimetype='image/png')
	else:
		logger.debug('get 404 png file: %s' % os.path.join(static_path, '404.png'))
		return static_file(filename='404.png', root=static_path, mimetype='image/png')


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
	logger.debug("upload success,save_path:%s,md5_value:%s" % (save_file_name, md5_value))
	resp['status'] = 0
	resp['save_path'] = save_file_name
	resp['md5_value'] = md5_value
	logger.info(resp)
	return resp


# 获取selenium状态信息，正在执行的session信息等
@app.route('/list_selenium', method='GET')
def list_selenium():
	resp = dict()
	resp['status'] = 0
	if selenium_flag is True:
		url = 'http://127.0.0.1:%d/wd/hub/sessions' % int(selenium_port)
		rstmp = http_get(url)
		if not rstmp.startswith('error'):
			rstmp2 = json.loads(rstmp, encoding='utf-8')
			resp['selenium_port'] = selenium_port
			resp['value'] = rstmp2['value']
	logger.info(resp)
	return resp


# 为指定设备安装minicap等程序
@app.route('/install_minix/<udid>', method='GET')
def install_minix(udid):
	resp = dict()
	resp['status'] = 0
	ins(udid)
	logger.info('install minix for device : %s' % udid)
	return resp


reset_devices()
reset_appium('reboot')

run(app=app, server='cherrypy', host='0.0.0.0', port=port, reloader=False, debug=True)
