#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'

import requests

proxy = {
	'http': 'http://127.0.0.1:8888',
}

postdata = {'parm1': '123', 'parm2': '中文'}

r = requests.post('http://127.0.0.1:7070/transaction_2', data=postdata, proxies=proxy)

print(r.text)

print(r.json())

print(r.json()['your_input'])
