#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '1.0,20160622'
__license__ = 'copy left'

import platform
from lib import *
import logging

logger = logging.getLogger('main.prep')
pt_name = platform.platform()
if pt_name.startswith('Windows'):
	sfind = 'findstr'
elif pt_name.startswith('Darwin'):
	sfind = 'grep'

# 文件所在路径
BASE = os.path.split(os.path.realpath(__file__))[0]
CAP_DIR = os.path.join(BASE, 'minix', 'minicap')
CAP_DIR_bin = os.path.join(CAP_DIR, 'bin')
CAP_DIR_share = os.path.join(CAP_DIR, 'shared')
TOUCH_DIR = os.path.join(BASE, 'minix', 'minitouch')
REV_DIR = os.path.join(BASE, 'minix', 'minirev')
SH_DIR = os.path.join(BASE, 'minix', 'sh')
ph_path = '/data/local/tmp'

# 获取路径下相应的文件夹
cap_version = os.listdir(CAP_DIR_bin)
andro_level = os.listdir(CAP_DIR_share)
andro_screen = os.listdir(SH_DIR)


def get_cpu_abi(udid):
	cpu_abi = ex_cmd('adb -s %s shell getprop ro.product.cpu.abi' % udid)
	return cpu_abi[0]


def get_andro_level(udid):
	andro_level = ex_cmd('adb -s %s shell getprop ro.build.version.sdk' % udid)
	return andro_level[0]


# 推送minicap(bin),minirev,minitouch
def push_minicap_minitouch(udid):
	cpu_abi = get_cpu_abi(udid)
	if cpu_abi in cap_version:
		path1 = os.path.join(CAP_DIR_bin, '%s') % (cpu_abi)
		path2 = os.path.join(TOUCH_DIR, '%s') % (cpu_abi)
		path3 = os.path.join(REV_DIR, '%s') % (cpu_abi)
		ex_cmd('adb -s %s shell mkdir %s' % (udid, ph_path))
		ex_cmd('adb -s %s push %s/%s %s' % (udid, path1, 'minicap', ph_path))
		ex_cmd('adb -s %s push %s/%s %s' % (udid, path1, 'minicap-nopie', ph_path))
		ex_cmd('adb -s %s push %s/%s %s' % (udid, path2, 'minitouch', ph_path))
		ex_cmd('adb -s %s push %s/%s %s' % (udid, path2, 'minitouch-nopie', ph_path))
		ex_cmd('adb -s %s push %s/%s %s' % (udid, path3, 'minirev', ph_path))
		ex_cmd('adb -s %s push %s/%s %s' % (udid, path3, 'minirev-nopie', ph_path))
	else:
		logger.debug('cpu_abi not found:%s' % udid)


# push_minicap_minitouch()

# 推送minicap(shared)
def push_minicap_shared(udid):
	level = get_andro_level(udid)
	levels = ('android-''%s''') % level
	if levels in andro_level:
		cpu_abi = get_cpu_abi(udid)
		path4 = os.path.join(CAP_DIR_share, '%s', '%s') % (levels, cpu_abi)
		# print(path4)
		ex_cmd('adb -s %s push %s/minicap.so %s' % (udid, path4, ph_path))
		ex_cmd('adb -s %s shell chmod -R 777 %s' % (udid, ph_path))
	else:
		logger.debug('levels not found: %s' % udid)


# push_minicap_shared()

# 推送sh
def push_sh(udid):
	sr = ex_cmd('adb -s %s shell dumpsys display|%s mDefaultViewport' % (udid, sfind))
	m = re.search(r'deviceWidth=(\d+),\s+deviceHeight=(\d+)', sr[0])
	if m:
		width, height = m.group(1, 2)
		# print(width,height)
		screen = ('%sx%s') % (height, width)
		# print(screen)
		if screen in andro_screen:
			path5 = os.path.join(SH_DIR, '%s') % (screen)
			# print(path5)
			ex_cmd('adb -s %s push %s/%s %s' % (udid, path5, 'cap.sh', ph_path))
			ex_cmd('adb -s %s push %s/%s %s' % (udid, path5, 'rec.sh', ph_path))
		else:
			logger.debug('screen:%s not found' % screen)
	else:
		logger.debug('screen not found: %s' % udid)


def ins(udid):
	push_minicap_minitouch(udid)
	push_minicap_shared(udid)
	push_sh(udid)


if __name__ == '__main__':
	ins('8LAIZ5LVSKORJNCU')
