#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20160322'
__license__ = 'copy left'

import platform
import socket
from time import sleep
from bottle import *

# android app and device info
PKG_NAME = 'com.czbank.mbank'
UDID = 'NX511J'

# init
interval = 5
port = 8888
socket.setdefaulttimeout(10)

# check env
if sys.version_info < (3, 4):
	raise RuntimeError('At least Python 3.4 is required.')
pt_name = platform.platform()
if pt_name.startswith('Windows'):
	GREP = 'findstr'
else:
	GREP = 'grep'

# start
cpu_temp = {"idle": None, "user": None, "system": None, "iowait": None, "total": None, "cpu_app": None}
cpu_result = {"cpu_Total": None, "cpu_User": None, "cpu_Sys": None, "cpu_iowait": None, "cpu_app": None}
mem_result = {"MemTotal": None, "MemUsage": None, "Buffers": None, "Cached": None, "MemUsage_pct": None}
other_result = {"Native_heap": None, "Dalvik_heap": None, "Mem_app": None, "Network_rx": None, "Network_tx": None,
				"Network_all": None}
pkg_info = {"pkg_name": PKG_NAME, "pid": None, "uid": None, "userId": None, "UDID": UDID}


# function start
# ex_cmd
def ex_cmd(cmd, timeout=8):
	res = list()
	try:
		fh = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		fh.wait(timeout=timeout)
		for line in fh.stdout.readlines():
			line = line.decode().strip()
			if line != '':
				res.append(line)
	except Exception as ex:
		# res.append('error:%s' % ex)
		fh.terminate()
	finally:
		fh.stdout.close()
	return res


# get package pid ...
def get_pkg():
	global pkg_info
	pid_file = ex_cmd('adb -s %s shell ps|%s %s' % (pkg_info['UDID'], GREP, pkg_info['pkg_name']))
	if len(pid_file) > 0:
		pkg_info['uid'], pkg_info['pid'] = pid_file[0].split()[0:2]
	else:
		pkg_info['pid'] = None
		pkg_info['uid'] = None
	# print(pkg_info)


# get proc file
def Read_Proc(file):
	proc_file = ex_cmd('adb -s %s shell cat /proc/%s' % (pkg_info['UDID'], file))
	return proc_file


# get memory
def And_Memory():
	global mem_result
	Proc_MemInfo = Read_Proc('meminfo')
	if len(Proc_MemInfo) == 0:
		for x in mem_result:
			mem_result[x] = None
		return None
	Memory = dict()
	for i in Proc_MemInfo:
		Memory[i.split()[0][0:-1]] = int(i.split()[1])
	MemTotal = Memory['MemTotal']
	MemFree = Memory['MemFree']
	Buffers = Memory['Buffers']
	Cached = Memory['Cached']
	# memusage calc
	MemUsage = MemTotal - MemFree - Buffers - Cached
	# result value
	mem_result['MemTotal'] = MemTotal
	mem_result['MemUsage'] = MemUsage
	mem_result['Buffers'] = Buffers
	mem_result['Cached'] = Cached
	mem_result['MemUsage_pct'] = ('%.3f' % (float(MemUsage) * 100 / MemTotal))


# get system cpu
def And_Cpu():
	global cpu_result
	global cpu_temp
	Cpu_data = Read_Proc('stat')
	if len(Cpu_data) == 0:
		for x in cpu_temp:
			cpu_temp[x] = None
		for x in cpu_result:
			cpu_result[x] = None
		return None
	Cpu_data = Cpu_data[0].split()
	app_cpu1 = None
	if pkg_info['pid'] is not None:
		Cpu_app_data = Read_Proc('%s/stat' % pkg_info['pid'])[0].split()
		if len(Cpu_app_data) > 20:
			app_cpu1 = float(Cpu_app_data[13]) + float(Cpu_app_data[14]) + float(Cpu_app_data[15]) + float(
				Cpu_app_data[16])
	idle = float(Cpu_data[4])
	user = float(Cpu_data[1]) + float(Cpu_data[2])
	system = float(Cpu_data[3]) + float(Cpu_data[6]) + float(Cpu_data[7])
	iowait = float(Cpu_data[5])
	total = idle + user + system + iowait
	if cpu_temp['idle'] is not None:
		cpu_result_temp = dict()
		cpu_per = total - cpu_temp['total']
		cpu_result_temp['cpu_User'] = str("%.3f" % ((user - cpu_temp['user']) / cpu_per * 100))
		cpu_result_temp['cpu_Sys'] = str("%.3f" % ((system - cpu_temp['system']) / cpu_per * 100))
		cpu_result_temp['cpu_iowait'] = str("%.3f" % ((iowait - cpu_temp['iowait']) / cpu_per * 100))
		cpu_result_temp['cpu_Total'] = str("%.3f" % ((cpu_per - idle + cpu_temp['idle']) / cpu_per * 100))
		if cpu_temp['cpu_app'] is not None and app_cpu1 is not None:
			cpu_result_temp['cpu_app'] = str("%.3f" % ((app_cpu1 - cpu_temp['cpu_app']) / cpu_per * 100))
			if float(cpu_result_temp['cpu_app']) < 0:
				cpu_result_temp['cpu_app'] = None
		else:
			cpu_result_temp['cpu_app'] = None
		if float(cpu_result_temp['cpu_Total']) < 0 or float(cpu_result_temp['cpu_User']) < 0 or float(
				cpu_result_temp['cpu_Sys']) < 0:
			# print('zero###############################')
			return None
		else:
			cpu_result = cpu_result_temp
	cpu_temp['idle'] = idle
	cpu_temp['user'] = user
	cpu_temp['system'] = system
	cpu_temp['iowait'] = iowait
	cpu_temp['total'] = total
	cpu_temp['cpu_app'] = app_cpu1


# get other
def And_Other():
	global other_result
	if pkg_info['pid'] is None:
		for x in other_result:
			other_result[x] = None
	else:
		global mem_result
		# mem calc
		ad_mem_info = ex_cmd('adb -s %s shell dumpsys meminfo %s' % (pkg_info['UDID'], pkg_info['pkg_name']))
		if len(ad_mem_info) > 5:
			for info in ad_mem_info:
				info = info.split()
				if info[0] == 'Native':
					if info[1].isdigit():
						other_result['Native_heap'] = info[1]
					elif info[1] == 'Heap':
						other_result['Native_heap'] = info[2]
				elif info[0] == 'Dalvik':
					if info[1].isdigit():
						other_result['Dalvik_heap'] = info[1]
					elif info[1] == 'Heap':
						other_result['Dalvik_heap'] = info[2]
				elif info[0] == 'TOTAL':
					other_result['Mem_app'] = info[1]
					break
			# net user calc
			net_user_info = ex_cmd(
				'adb -s %s shell cat /proc/net/xt_qtaguid/stats |%s %s' % (pkg_info['UDID'], GREP, pkg_info["userId"]))
			if len(net_user_info) > 0:
				rx_b = 0
				tx_b = 0
				for xx in net_user_info:
					all_net = xx.split()
					rx_b += int(all_net[5])
					tx_b += int(all_net[7])
				rxtx = rx_b + tx_b
				other_result['Network_rx'] = rx_b
				other_result['Network_tx'] = tx_b
				other_result['Network_all'] = rxtx


def mon_run():
	while True:
		thrs = list()
		t0 = threading.Thread(target=get_pkg)
		t0.start()
		thrs.append(t0)
		t1 = threading.Thread(target=And_Memory)
		t1.start()
		thrs.append(t1)
		t2 = threading.Thread(target=And_Cpu)
		t2.start()
		thrs.append(t2)
		t3 = threading.Thread(target=And_Other)
		t3.start()
		thrs.append(t3)
		for t in thrs:
			t.join()
		sleep(interval)


def mon_page():
	return template('android', MemTotal=mem_result['MemTotal'], MemUsage=mem_result['MemUsage'],
					Buffers=mem_result['Buffers'], Cached=mem_result['Cached'],
					MemUsage_pct=mem_result['MemUsage_pct'], Native_heap=other_result['Native_heap'],
					Dalvik_heap=other_result['Dalvik_heap'], Mem_app=other_result['Mem_app'],
					cpu_Total=cpu_result['cpu_Total'], cpu_User=cpu_result['cpu_User'], cpu_Sys=cpu_result['cpu_Sys'],
					cpu_iowait=cpu_result['cpu_iowait'], cpu_app=cpu_result['cpu_app'],
					Network_rx=other_result['Network_rx'], Network_tx=other_result['Network_tx'],
					Network_all=other_result['Network_all'])


# get app userid

userid_info = ex_cmd('adb -s %s shell dumpsys package %s|%s userId' % (pkg_info['UDID'], PKG_NAME, GREP))

if len(userid_info) > 0:
	tpinfo = userid_info[0].split()
	pkg_info["userId"] = tpinfo[0].split('=')[1]

th_all = threading.Thread(target=mon_run)
th_all.setDaemon(True)
th_all.start()

app = Bottle()


# monitor
@app.route('/SiteScope/cgi/go.exe/SiteScope')
@app.route('/monitor')
def monitor():
	return mon_page()


run(app=app, host='0.0.0.0', port=port, reloader=False, quiet=True, debug=True)
