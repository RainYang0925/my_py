#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'among',lifeng29@163.com

from bottle import *
from autorun import *
import json
import threading

app = Bottle()


# 获取案例执行
@app.route('/testRun', method='POST')
def testRun():
	ref = request.get_header('Referer')
	info = request.body.read().decode()

	thr = threading.Thread(target=async, args=(ref, info,))
	thr.setDaemon(True)
	thr.start()

	response.headers['Access-Control-Allow-Origin'] = '*'
	return None


def async(ref, info):
	print("###########################################")
	print("执行案例：%s" % ref)
	req = json.loads(info, encoding='utf-8')
	steps = req['steps']
	run_instance = autorun()
	for step in steps:
		action = step['name']
		desc = step['describe']
		attrs = step['attrs']
		if run_instance.flag == 'PASS':
			run_instance.run(action, **attrs)
		sleep(2)
	print("案例执行结果：%s" % run_instance.flag)
	run_instance.quit()
	print("###########################################")


print("Listening on http://0.0.0.0:8500/")
run(app=app, host='0.0.0.0', port=8500, reloader=False, quiet=True, debug=True)
