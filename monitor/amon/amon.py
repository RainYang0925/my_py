#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20160122'
__license__ = 'copy left'

import platform
import socket

pt_name = platform.platform()
from lib.bottle import *

if pt_name.startswith('Linux'):
	pt_name = 'Linux'
	from lib.mon_linux import *
elif pt_name.startswith('Darwin'):
	pt_name = 'Mac OS X'
	from lib.mon_osx import *
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
