#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20160122'
__license__ = 'copy left'

import threading
from time import sleep, time
from bottle import template

# init
interval = 5

cpu_temp = {"idle": None, "user": None, "system": None, "iowait": None, "total": None}
cpu_result = {"cpu_Total": None, "cpu_User": None, "cpu_Sys": None, "cpu_iowait": None}
mem_result = {"MemTotal": None, "MemUsage": None, "Buffers": None, "Cached": None, "SwapTotal": None,
			  "SwapUsage": None, "MemUsage_pct": None, "SwapUsage_pct": None}


# result page
def mon_page():
	return template('linux', MemTotal=mem_result['MemTotal'], MemUsage=mem_result['MemUsage'],
					Buffers=mem_result['Buffers'], Cached=mem_result['Cached'], SwapTotal=mem_result['SwapTotal'],
					SwapUsage=mem_result['SwapUsage'], MemUsage_pct=mem_result['MemUsage_pct'],
					SwapUsage_pct=mem_result['SwapUsage_pct'], cpu_Total=cpu_result['cpu_Total'],
					cpu_User=cpu_result['cpu_User'], cpu_Sys=cpu_result['cpu_Sys'], cpu_iowait=cpu_result['cpu_iowait'])


# mon start
def mon_init():
	t1 = threading.Thread(target=mon_run)
	t1.setDaemon(True)
	t1.start()


# mon
def mon_run():
	while True:
		thrs = list()
		t1 = threading.Thread(target=Memory)
		t1.start()
		thrs.append(t1)
		t2 = threading.Thread(target=Cpu)
		t2.start()
		thrs.append(t2)
		for t in thrs:
			t.join()
		# print(time())
		sleep(interval)


def Read_Proc(file):
	proc_file = '/proc/' + file
	# proc_file = file
	with open(proc_file, 'r') as proc_data:
		return proc_data.readlines()


def Memory_Info():
	Proc_MemInfo = Read_Proc('meminfo')
	MemInfo = dict()
	for i in Proc_MemInfo:
		MemInfo[i.split()[0][0:-1]] = int(i.split()[1])
	return MemInfo


def Cpu_Info():
	Proc_CpuInfo = Read_Proc('stat')
	CpuInfo = Proc_CpuInfo[0].split()
	return CpuInfo


def Memory():
	global mem_result
	Memory = Memory_Info()
	MemTotal = Memory['MemTotal']
	MemFree = Memory['MemFree']
	Buffers = Memory['Buffers']
	Cached = Memory['Cached']
	SwapTotal = Memory['SwapTotal']
	SwapFree = Memory['SwapFree']
	# memusage calc
	MemUsage = MemTotal - MemFree - Buffers - Cached
	SwapUsage = SwapTotal - SwapFree
	# result value
	mem_result['MemTotal'] = MemTotal
	mem_result['MemUsage'] = MemUsage
	mem_result['Buffers'] = Buffers
	mem_result['Cached'] = Cached
	mem_result['SwapTotal'] = SwapTotal
	mem_result['SwapUsage'] = SwapUsage
	mem_result['MemUsage_pct'] = ('%.3f' % (float(MemUsage) * 100 / MemTotal))
	mem_result['SwapUsage_pct'] = ('%.3f' % (float(SwapUsage) * 100 / SwapTotal))


def Cpu():
	Cpu_data = Cpu_Info()
	# sum
	idle = float(Cpu_data[4])
	user = float(Cpu_data[1]) + float(Cpu_data[2])
	system = float(Cpu_data[3]) + float(Cpu_data[6]) + float(Cpu_data[7])
	iowait = float(Cpu_data[5])
	total = idle + user + system + iowait
	global cpu_temp
	if cpu_temp['idle'] is not None:
		cpu_result_temp = dict()
		global cpu_result
		cpu_per = total - cpu_temp['total']
		cpu_result_temp['cpu_User'] = str("%.3f" % ((user - cpu_temp['user']) / cpu_per * 100))
		cpu_result_temp['cpu_Sys'] = str("%.3f" % ((system - cpu_temp['system']) / cpu_per * 100))
		cpu_result_temp['cpu_iowait'] = str("%.3f" % ((iowait - cpu_temp['iowait']) / cpu_per * 100))
		cpu_result_temp['cpu_Total'] = str("%.3f" % ((cpu_per - idle + cpu_temp['idle']) / cpu_per * 100))
		if float(cpu_result_temp['cpu_Total']) < 0:
			return None
		else:
			cpu_result = cpu_result_temp
	cpu_temp['idle'] = idle
	cpu_temp['user'] = user
	cpu_temp['system'] = system
	cpu_temp['iowait'] = iowait
	cpu_temp['total'] = total


if __name__ == '__main__':
	mon_init()
	while True:
		result = mon_page()
		print(result)
		sleep(interval)
