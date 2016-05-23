#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'

from bottle import *
from time import sleep

app = Bottle()


@app.route('/transaction_1', method='GET')
def tr1():
	sleep(0.2)
	resp = dict()
	resp['status'] = 0
	resp['value'] = 'xxx'
	return resp


@app.route('/transaction_2', method='POST')
def tr2():
	parm1 = request.forms.get('parm1')
	parm2 = request.forms.getunicode('parm2')
	sleep(0.5)
	resp = dict()
	resp['status'] = 0
	resp['value'] = 'yyy'
	resp['your_input'] = parm2
	return resp


run(app=app, server='cherrypy', host='0.0.0.0', port=7070, reloader=False, debug=False)
