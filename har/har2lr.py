#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'
__version__ = '(1.0,20160615)'
__license__ = 'copy left'

from optparse import OptionParser
import os
import sys
import json


# check env
if sys.version_info < (3, 4):
	raise RuntimeError('At least Python 3.4 is required.')

restype = ('js', 'css', 'jpg', 'gif', 'ico', 'png')


def list2dic(headers):
	header_dic = dict()
	for head in headers:
		if head['name'] in header_dic:
			header_dic[head['name']] = header_dic[head['name']] + ',' + head['value']
		else:
			header_dic[head['name']] = head['value']
	return header_dic


def dictoand(dct):
	res_list = list()
	for tp in dct:
		res_list.append('%s=%s' % (tp['name'], tp['value']))
	return '&'.join(res_list)


def dict2lr(lrsc):
	tmpl = '''
	web_custom_request("%(name)s",
		"URL=%(url)s",
		"Method=%(method)s",
		"Resource=%(res)s",
		"Referer=%(referer)s",
		"EncType=%(enctype)s",
		"Body=%(body)s",
		LAST);'''
	# url
	url = lrsc['url']
	method = lrsc['method']
	name = url.split('/')[-1]
	name = name.split('?')[0]
	suff = url.split('.')[-1]
	# Resource type
	global restype
	res = '0'
	if suff in restype:
		res = '1'

	# Content-Type
	enctype = ''
	if 'Content-Type' in lrsc:
		enctype = lrsc['Content-Type']
	# Referer
	referer = ''
	if 'Referer' in lrsc:
		referer = lrsc['Referer']

	# Body
	body = ''
	if 'posttext' in lrsc:
		body = lrsc['posttext']
	elif 'postparams' in lrsc:
		body = dictoand(lrsc['postparams'])
	body = body.replace('"', '\\"')
	res = tmpl % {'name': name, 'url': url, 'method': method, 'enctype': enctype, 'referer': referer, 'res': res,
				  'body': body}
	# Head
	if 'SOAPAction' in lrsc:
		res = ("\n" + '	web_add_header("SOAPAction", "%s")' + ";\n" + res) % lrsc['SOAPAction']
	return res


def parhar(harfile):
	res = list()
	try:
		FH = open(harfile, mode='r', encoding='utf-8', closefd=True)
		all = json.load(FH)
		FH.close()
	except Exception as ex:
		print('Open har file errr: %s' % ex)
		quit()

	har_ver = all['log']['version']
	creater = all['log']['creator']['name']
	entries = all['log']['entries']

	ct = len(entries)
	for et in entries:
		stm = et['startedDateTime']
		req = et['request']
		rsp = et['response']
		lrsc = dict()
		if '_charlesStatus' in rsp and rsp['_charlesStatus'] != 'Complete':
			continue
		lrsc['method'] = req['method']
		lrsc['url'] = req['url']
		headers = req['headers']
		# http head
		header_dic = list2dic(headers)
		if 'SOAPAction' in header_dic:
			lrsc['SOAPAction'] = header_dic['SOAPAction'].replace('"', '\\"')
		if 'Referer' in header_dic:
			lrsc['Referer'] = header_dic['Referer']
		if 'Content-Type' in header_dic:
			lrsc['Content-Type'] = header_dic['Content-Type']
		if lrsc['method'] == 'GET':
			pass
		elif lrsc['method'] == 'POST':
			if 'postData' in req:
				if 'text' in req['postData']:
					lrsc['posttext'] = req['postData']['text']
				if 'params' in req['postData']:
					lrsc['postparams'] = req['postData']['params']
				if 'mimeType' in req['postData']:
					lrsc['postmime'] = req['postData']['mimeType']
		else:
			continue
		res.append(dict2lr(lrsc))
	return res


if __name__ == '__main__':
	parse = OptionParser()
	parse.add_option("-f", action="store", dest="harfile", help='harfile path')
	parse.add_option("-o", action="store", dest="lrfile", help='action.c path')
	(options, args) = parse.parse_args()

	if options.harfile is None or options.lrfile is None:
		parse.print_help()
		quit()
	if not os.path.exists(options.harfile):
		print('Har file %s not exist' % options.harfile)
		quit()
	res = parhar(options.harfile)
	file = open(options.lrfile, mode='w', encoding='utf-8')
	for sc in res:
		file.write(sc)
		file.write("\n")
	file.close()
	print('Output to %s' % options.lrfile)
