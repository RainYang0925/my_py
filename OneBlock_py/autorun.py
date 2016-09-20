#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'among',lifeng29@163.com

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from time import sleep, strftime
import os


class autorun(object):
	def __init__(self, url='http://127.0.0.1:4444/wd/hub', enable_png=True, png_path='C:/pngdir'):
		self.flag = 'PASS'
		if enable_png == True:
			self.enable_png = True
			self.pngdir = os.path.join(png_path, strftime('%Y%m%d%H%M%S'))
			if not os.path.exists(self.pngdir):
				os.makedirs(self.pngdir)
		try:
			cap = DesiredCapabilities.CHROME.copy()
			# self.dr = webdriver.Remote(command_executor=url, desired_capabilities=cap)
			self.dr = webdriver.Chrome(executable_path='C:/chromedriver.exe', desired_capabilities=cap)
		except Exception as ex:
			self.flag = 'FAIL'

	def run(self, action, **attrs):
		if action == 'InitStep':
			self.InitStep(**attrs)
		elif action == 'EditStep':
			self.EditStep(**attrs)
		elif action == 'ClickStep':
			self.ClickStep(**attrs)
		elif action == 'CheckStep':
			self.CheckStep(**attrs)
		else:
			print('action %s not find' % action)
			self.flag = 'FAIL'

	def InitStep(self, **attrs):
		url = attrs['url']
		tm = attrs['implicitlyWait']
		try:
			self.dr.get(url=url)
			self.dr.implicitly_wait(time_to_wait=tm)
			self.getpng()
		except Exception as ex:
			self.flag = 'FAIL'
			print('启动浏览器:执行失败', ex)
		else:
			print('启动浏览器:执行成功')

	def EditStep(self, **attrs):
		try:
			elem = self.dr.find_element_by_name(attrs['name'])
			elem.clear()
			elem.send_keys(attrs['inputText'])
			if attrs['pressEnter'] == 'true':
				elem.send_keys(Keys.ENTER)
			self.getpng()
		except Exception as ex:
			self.flag = 'FAIL'
			print('输入:执行失败', ex)
		else:
			print('输入:执行成功')

	def ClickStep(self, **attrs):
		try:
			elem = self.dr.find_element_by_link_text(attrs['text'])
			elem.click()
			self.getpng()
		except Exception as ex:
			self.flag = 'FAIL'
			print('点击:执行失败', ex)
		else:
			print('点击:执行成功')

	def CheckStep(self, **attrs):
		try:
			elem = self.dr.find_element_by_xpath(attrs['xpath'])
			self.getpng()
		except Exception as ex:
			self.flag = 'FAIL'
			print('检查点:执行失败', ex)
		else:
			print('检查点:执行成功')

	# 获取屏幕截图
	def getpng(self):
		if self.enable_png is True:
			pngname = os.path.join(self.pngdir, strftime('%Y%m%d%H%M%S') + '.png')
			try:
				self.dr.get_screenshot_as_file(pngname)
			except Exception as ex:
				print('截图错误：%s' % ex)

	def quit(self):
		self.dr.quit()
