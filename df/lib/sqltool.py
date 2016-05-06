#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '[1.0,20160425]'
__license__ = 'copy left'

import sqlite3
import logging
import json
import threading
from time import sleep
from .tools import *


class sqltool():
	def __init__(self, path):
		self.conn = sqlite3.connect(path, timeout=3)
		self.dbpath = path

	def get_cursor(self):
		if self.conn is not None:
			return self.conn.cursor()
		else:
			self.conn = sqlite3.connect(self.dbpath, timeout=3)
			return self.conn.cursor()

	def drop_tb(self, table):
		sql = 'DROP TABLE IF EXISTS ' + table
		try:
			cu = self.get_cursor()
			cu.execute(sql)
			self.conn.commit()
		except Exception as ex:
			logging.debug("drop table %s error:%s" % (table, ex))

	def exec_sql(self, sql):
		if sql is not None and sql != '':
			try:
				cu = self.get_cursor()
				cu.execute(sql)
				self.conn.commit()
			except Exception as ex:
				logging.debug("exec sql:%s error:%s" % (sql, ex))
		else:
			logging.debug("exec sql error: %s" % sql)

	def exec_query(self, sql):
		try:
			cu = self.get_cursor()
			cu.execute(sql)
			collist = [tuple[0] for tuple in cu.description]
			resp = list()
			for res in cu.fetchall():
				row = dict()
				for i in range(len(collist)):
					row[collist[i]] = res[i]
				resp.append(row)
			return resp
		except Exception as ex:
			logging.debug("exec_query sql:%s error:%s" % (sql, ex))
			return None

	def init_db(self):
		self.drop_tb('devices')
		self.drop_tb('appium')
		sql1 = '''CREATE TABLE 'devices' (
								  'udid' VARCHAR(80) NOT NULL,
								  'model' varchar(80),
								  'type' varchar(40),
								  'version' varchar(40),
								  'screen size' varchar(40),
								  'address' varchar(80) NOT NULL,
								  'state' varchar(40) NOT NULL,
								  PRIMARY KEY ('udid'))
				'''
		sql2 = '''CREATE TABLE 'appium' (
								  'url' VARCHAR(200) NOT NULL,
								  'platform' varchar(80),
								  'version' varchar(40),
								  'address' varchar(80) NOT NULL,
								  'state' varchar(40) NOT NULL,
								  'udid' varchar(80),
								  'appName' varchar(100),
								  PRIMARY KEY ('url'))
				'''
		self.exec_sql(sql1)
		self.exec_sql(sql2)


def ref_devices(sqltk, sf_host):
	global dev_list
	dev_list = dict()
	resp = dict()
	resp['status'] = 0

	# thread start
	def ref_devices_sub(sf_adv):
		url1 = "http://%s/list_devices" % sf_adv
		# print url1
		rstmp1 = http_get(url1)
		if not rstmp1.startswith('error'):
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
	cur1 = sqltk.get_cursor()
	## for devices
	cur1.execute('select udid from devices')
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
			ip = dev_info['ip']
			sql = "update devices set state='%s',address='%s' where udid='%s'" % (
				'online', ip, udid)
		else:
			sql = "update devices set state='%s',address='%s' where udid='%s'" % (
				'offline', '', db_dev)
		# print sql
		sqltk.exec_sql(sql)

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
			sql = "insert into devices values ('%s','%s','%s','%s','%s','%s','%s')" % (
				udid, model, type, version, screen_size, ip, 'online')
			# print(sql)
			sqltk.exec_sql(sql)
	# conn.close()
	return resp


# 刷新所有的appium
def ref_appium(sqltk, sf_host):
	resp = dict()
	resp['status'] = 0
	global apm_list
	apm_list = dict()
	# appium list

	def ref_appium_sub(sf_adv):
		url1 = "http://%s/list_appium" % sf_adv
		ip = sf_adv.split(':')[0]
		rstmp1 = http_get(url1)
		if not rstmp1.startswith('error'):
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
	sql = "delete from appium"
	sqltk.exec_sql(sql)

	for apm in apm_list.keys():
		apm_info = apm_list[apm]
		# 在刚刚启动，未启动好的时候，异常处理
		platform = apm_info['platform']
		ip = apm_info['ip']
		try:
			version = apm_info['version']
			pid = apm_info['pid']
		except Exception as ex:
			version = ''
			pid = ''
		# to
		if 'udid' in apm_info:
			udid = apm_info['udid']
			isbusy = 'busy'
		else:
			udid = ''
			isbusy = 'idle'
		if 'app' in apm_info:
			app = apm_info['app']
		else:
			app = ''
		sql = "insert into appium values ('%s','%s','%s','%s','%s','%s','%s')" % (
			apm, platform, version, ip, isbusy, udid, app)
		sqltk.exec_sql(sql)
	# conn.close()
	return resp


def ref_runner(dbs, sf_host):
	sf_online = list()
	# thread start
	def list_runner_sub(sf_adv):
		url1 = "http://%s/status" % sf_adv
		rstmp1 = http_get(url1)
		if not rstmp1.startswith('error'):
			sf_online.append(sf_adv)

	# thread def end

	thrs = list()
	for sf_adv in sf_host:
		t = threading.Thread(target=list_runner_sub, args=(sf_adv,))
		t.start()
		thrs.append(t)
	for t in thrs:
		t.join()
	return sf_online


def ref_info(data_file, sf_host):
	dbs = sqltool(data_file)
	dbs.init_db()
	while True:
		sf_host_alive = ref_runner(dbs, sf_host)
		ref_devices(dbs, sf_host_alive)
		ref_appium(dbs, sf_host_alive)
		sleep(10)


def fetchall(data_file, sql):
	dbs = sqltool(data_file)
	res = dbs.exec_query(sql)
	return res


if __name__ == '__main__':
	xx = sqltool('C:\\xx.db')
	ips = ['10.1.38.76:8029', '10.1.38.98:8029', '192.168.1.1:8922']
	ref_devices(xx, ips)

	print(xx.dbpath)
	print(xx.conn)
