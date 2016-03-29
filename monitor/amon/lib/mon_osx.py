#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20160224'
__license__ = 'copy left'

import subprocess
from time import sleep, time
from bottle import template

# init
interval = 5


# result page
def mon_page():
	cpu_Total = None
	# cpu
	cpu_res = ex_cmd('/usr/sbin/iostat 1 2')
	if cpu_res != 'error':
		cpu_Total = 100 - float(cpu_res[3].split()[5])
	# memory
	# to do
	return template('osx', cpu_Total=cpu_Total)


# mon start
def mon_init():
	pass


# ex_cmd
def ex_cmd(cmd):
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
		# print(ex)
		res.append('error')
	return res


if __name__ == '__main__':
	mon_init()
	while True:
		result = mon_page()
		print(result)
		sleep(interval)
