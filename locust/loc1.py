#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'among,lifeng29@163.com'

from locust import *


class mytest(TaskSet):
	@task(weight=1)
	def transaction_1(self):
		with self.client.get(name='get', url='/transaction_1', catch_response=True) as response:
			if 'xxx' in response.content:
				response.success()
			else:
				response.failure('error')

	@task(weight=1)
	def transaction_2(self):
		dt = {
			'parm1': '123',
			'parm2': 'abc'
		}

		with self.client.post(name='post', url='/transaction_2', data=dt, catch_response=True) as response:
			if 'yyy' in response.content:
				response.success()
			else:
				response.failure('error')


class myrun(HttpLocust):
	task_set = mytest
	host = 'http://10.0.244.108:7070'
	min_wait = 0
	max_wait = 0
