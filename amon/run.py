#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20160122'
__license__ = 'copy left'

import sys
import os
import platform
import socket

sys.path.insert(0, (os.path.join(sys.path[0], 'lib')))
pt_name = platform.platform()

if pt_name.startswith('Linux'):
	pt_name = 'Linux'
	from bottle import *
	from mon_linux import *
else:
	print("not support on %s" % pt_name)
	quit()

# init
mon_init()
socket.setdefaulttimeout(10)
port = 8888
app = Bottle()


# help page
@app.route('/help', method='GET')
def help():
	return "help page"


# monitor
@app.route('/SiteScope/cgi/go.exe/SiteScope')
@app.route('/monitor')
def monitor():
	return mon_page()


run(app=app, host='0.0.0.0', port=port, reloader=False, quiet=True, debug=True)
