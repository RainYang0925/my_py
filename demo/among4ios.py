#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = among,lifeng29@163.com
# 20150801
# for ios test

# import unittest
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from time import sleep, strftime
import threading
import os
import codecs


# class Mytc(unittest.TestCase):
class Mytc():
	# testcase 初始化
	def setUp(self):
		pass

	# testcase down
	def tearDown(self):
		pass

	# main pass
	def main(self):
		pass

	# init
	def __init__(self, url, cap, enable_png=False, png_tktm=10):
		self.dr = webdriver.Remote(command_executor=url, desired_capabilities=cap)
		# print cap
		# self.dr.wait_activity()
		wdsize = self.getwinsz()
		self.width = wdsize['width']
		self.height = wdsize['height']
		self.enable_png = enable_png
		self.png_tktm = png_tktm
		self.pngdir = 'C:/png/'

		self.tmp_png_file = 'C:/ios.png'
		self.tmp_source_file = 'C:/page_source.xml'

		# # 截图开启
		if self.enable_png is True:
			self.pgth = threading.Thread(target=self.getpng, args=())
			self.pgth.setDaemon(True)
			self.pgth.start()

	# return None

	# 退出程序
	def quit(self):
		if self.enable_png is True:
			sleep(3)
			self.enable_png = False
			sleep(self.png_tktm * 2)
		self.dr.close_app()
		self.dr.quit()

	# 获取屏幕大小
	def getwinsz(self):
		size = self.dr.get_window_size()
		return size

	# 获取屏幕截图
	def getpng(self):
		if self.enable_png is True:
			newpngdir = os.path.join(self.pngdir, strftime('%Y%m%d%H%M%S'))
			if not os.path.exists(newpngdir):
				os.makedirs(newpngdir)
		while self.enable_png:
			pngname = os.path.join(newpngdir, strftime('%Y%m%d%H%M%S') + '.png')
			try:
				self.dr.get_screenshot_as_file(pngname)
			except Exception as ex:
				pass
			sleep(self.png_tktm)

	# 公共函数部分开始：

	# 获取屏幕文字,未完成,todo
	def get_statictext(self, elname):
		# 重试三次
		for x in range(0, 3):
			try:
				# el = self.dr.find_element_by_name(elname)
				el = self.dr.find_element_by_xpath("//UIAStaticText[@name='%s']" % elname)

				text = el.text()
				break
			except Exception as ex:
				sleep(3)
				text = ex.message
		return text

	# 根据element的名字点击元素
	def click_element(self, elname, tk=2):
		el = self.dr.find_element_by_name(elname)
		el.click()
		sleep(tk)

	# 点击button
	def click_button(self, elname, tk=2):
		el = self.dr.find_element_by_xpath("//UIAButton[@name='%s']" % elname)
		el.click()
		tk = int(tk)
		sleep(tk)

	# 点击button
	def click_button2(self, **dictArg):
		if 'elname' in dictArg:
			elname = dictArg['elname']
		else:
			print("error")
		if 'tk' in dictArg:
			tk = dictArg['tk']
		else:
			tk = 10

		el = self.dr.find_element_by_xpath("//UIAButton[@name='%s']" % elname)
		el.click()
		tk = int(tk)
		sleep(tk)

	# 根据element的名称点击坐标，
	def click_element_xy(self, elname, tk=2):
		# 重试三次
		for x in range(0, 3):
			try:
				el = self.dr.find_element_by_name(elname)
				self.touchxy(el)
				break
			except Exception as ex:
				print(ex)
			sleep(tk)

	def click_element_xy2(self, **dictArg):
		if 'elname' in dictArg:
			elname = dictArg['elname']
		else:
			print("error")
		if 'tk' in dictArg:
			tk = dictArg['tk']
		else:
			tk = 2
		# 重试三次
		print
		"think time : %s" % (tk)
		for x in range(0, 3):
			try:
				el = self.dr.find_element_by_name(elname)
				self.touchxy(el)
				break
			except Exception as ex:
				print(ex)
			sleep(int(tk))

	# 根据elname或elname1点击元素的坐标
	def click_elements_xy(self, elname1, elname2, tk=2):
		# 重试三次
		for x in range(3):
			try:
				print("xy ing")
				el = self.dr.find_element_by_xpath("//[@name='%s' or @name='%s']" % elname1, elname2)
				print(el)
				self.touchxy(el)
				sleep(tk)
				break
			except Exception as ex:
				sleep(tk)

	# 已有账户登录
	def login(self, id, ps, tk=10):
		# 输入手机号码
		el = self.dr.find_element_by_xpath(
			'//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIAScrollView[1]/UIAScrollView[1]/UIATableView[1]/UIATableCell[1]/UIATextField[1]')
		# print dir(el)
		el.clear()
		el.send_keys("%s" % id)
		sleep(1)

		# 输入登录密码
		el2 = self.dr.find_element_by_xpath(
			'//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIAScrollView[1]/UIAScrollView[1]/UIATableView[1]/UIATableCell[2]')
		el2.click()
		sleep(1)
		self.click_passwd(ps)

		el3 = self.dr.find_element_by_xpath("//UIAButton[@name='登录']")
		el3.click()
		sleep(1)
		sleep(tk)

	# 签约需要，卡号，密码，开户行，开户省份，城市，支行
	def signzjb(self, khh, khsf, khcs, khfh, kh, ps):
		# 第一个行名
		el1 = self.dr.find_element_by_xpath(
			'//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIAScrollView[2]/UIATableView[1]/UIATableCell[2]/UIAStaticText[1]')
		el1.click()
		sleep(1)
		self.chose_text(khh)

		# 第二个省份
		el2 = self.dr.find_element_by_xpath(
			'//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIAScrollView[2]/UIATableView[1]/UIATableCell[3]/UIAStaticText[1]')
		el2.click()
		sleep(1)
		self.chose_text(khsf)

		# 第三个城市
		el2 = self.dr.find_element_by_xpath(
			'//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIAScrollView[2]/UIATableView[1]/UIATableCell[4]/UIAStaticText[1]')
		el2.click()
		sleep(1)
		self.chose_text(khcs)

		# 第四个分行
		el2 = self.dr.find_element_by_xpath(
			'//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIAScrollView[2]/UIATableView[1]/UIATableCell[5]/UIAStaticText[1]')
		el2.click()
		sleep(1)
		self.chose_text(khfh)

		# 输入账号
		# print "input zhanghao"
		self.input_text_by_idx(0, kh)
		self.input_text_by_idx(1, kh)

		sleep(2)
		# 输入密码
		self.input_passwd_by_idx(0, ps)
		self.input_passwd_by_idx(1, ps)

	# 点击元素中间的坐标，如图片的坐标位置
	def touchxy(self, el):
		p = el.location
		s = el.size
		p_x = int(p['x'] + s['width'] / 2)
		p_y = int(p['y'] + s['height'] / 2)
		# print p_x,p_y
		# self.dr.tap([(p_x, p_y)],10)
		action = TouchAction(self.dr)
		action.press(x=p_x, y=p_y)
		action.perform()
		sleep(2)

	# 往上滑动，选择文字
	def chose_text(self, value):
		p1 = int(self.width / 2)
		p2 = int(self.height * 0.770833)
		p3 = p1
		p4 = int(self.height * (0.770833 - 0.095))
		while True:
			self.dr.swipe(p1, p2, p3, p4)  # 滑动的位置
			el_value = self.dr.find_element_by_xpath(
				'//UIAApplication[1]/UIAWindow[1]/UIAPicker[1]/UIAPickerWheel[1]').text.encode("utf-8")
			if el_value.startswith(value):
				el2 = self.dr.find_element_by_name('确认')
				el2.click()
				sleep(2)
				break

	# 选择文本框，index为序列，第几个文本框，输入文本
	def input_text_by_idx(self, index, value):
		el = self.dr.find_elements_by_class_name('UIATextField')[index]
		try:
			el.click()
		except Exception as ex:
			print("error:", ex)
			self.touchxy(el)
			self.input_method(value)
		else:
			print("input ", value)
			el.clear()
			el.send_keys(value)

	# 选择文本框，按照class 和 name来，最后输入文本，输入文本
	def input_text_by_name(self, eltype, prop_name, prop_value, value):
		if eltype == 'UIASecureTextField':
			el = self.dr.find_element_by_xpath("//UIASecureTextField[@%s='%s']" % (prop_name, prop_value))
			try:
				el.click()
			except Exception as ex:
				print('input_passwd_by_idx error: ', ex)
				self.touchxy(el)
				self.click_passwd(value)
			else:
				print('input passwd: ', value)
				self.click_passwd(value)
		elif eltype == 'UIATextField':
			el = self.dr.find_element_by_xpath("//UIATextField[@%s='%s']" % (prop_name, prop_value))
			try:
				el.click()
			except Exception as ex:
				print("error:", ex)
				self.touchxy(el)
				self.input_method(value)
			else:
				print("input ", value)
				el.clear()
				el.send_keys(value)
		else:
			print("unknow eltype :", eltype)

	# 选择密码框，输入密码
	def input_passwd_by_idx(self, index, value):
		el = self.dr.find_elements_by_class_name('UIASecureTextField')[index]
		try:
			el.click()
		except Exception as ex:
			print('input_passwd_by_idx error: ', ex)
			self.touchxy(el)
			self.click_passwd(value)
		else:
			print('input passwd: ', value)
			self.click_passwd(value)

	# # 选择密码，按照name，输入密码
	# def input_passwd_by_name(self, name, value):
	# 	el = self.dr.find_element_by_xpath("//UIASecureTextField[@name='%s']" % name)
	# 	el.click()
	# 	sleep(1)
	# 	self.click_passwd(value)

	# 点击数字密码，123
	def click_passwd_123(self, ps):
		for mm in ps:
			if mm.isalpha():
				print("Error，click_passwd123 error")
			else:
				self.dr.find_element_by_xpath("//UIAButton[@name='%s']" % mm).click()
		self.dr.find_element_by_xpath("//UIAButton[@name='return']").click()

	# 点击密码，abc，123
	def click_passwd_abc(self, ps):
		for mm in ps:
			# print mm
			if mm.isalpha():
				if mm.islower():
					mm = mm.upper()
					self.dr.find_element_by_xpath("//UIAButton[@name='%s']" % mm).click()
				else:
					print("click_passwd to do: 大写字母")
			else:
				self.dr.find_element_by_xpath("//UIAButton[@name='123']").click()
				self.dr.find_element_by_xpath("//UIAButton[@name='%s']" % mm).click()
				self.dr.find_element_by_xpath("//UIAButton[@name='ABC']").click()
		self.dr.find_element_by_xpath("//UIAButton[@name='return']").click()

	# 保存pagesource到文件
	# 使用时要小心，会导致bug发生。可能为父类中的方法。要小心使用
	def tmp_page(self):
		temp = self.dr.page_source
		fh = codecs.open(self.tmp_source_file, "w", "utf-8")
		fh.write(temp)
		fh.close()

	def tmp_png(self):
		self.dr.get_screenshot_as_file(self.tmp_png_file)
		sleep(2)

	# 输入法
	def input_method(self, value):
		for mm in value:
			# print "mima value: ", mm
			# 重试2次，换键盘
			for x in range(2):
				try:
					el = self.dr.find_element_by_xpath("//UIAKey[@name='%s']" % mm)
				except Exception as ex:
					if mm.isalpha():
						print("is alpha")
						self.dr.find_element_by_xpath("//UIAKey[@name='更多，字母']").click()
					else:
						self.dr.find_element_by_xpath("//UIAKey[@name='更多，数字']").click()
				else:
					# print "find to click"
					el.click()
					break
		self.dr.hide_keyboard()

	# 点击密码，不区分abc，123，只考虑大写
	# 　软输入法
	def click_passwd(self, ps):
		for mm in ps:
			if mm.isalpha():
				if mm.islower():
					mm = mm.upper()
					for x in range(2):
						try:
							el = self.dr.find_element_by_xpath("//UIAButton[@name='%s']" % mm)
						except Exception as ex:
							self.dr.find_element_by_xpath("//UIAButton[@name='ABC']").click()
						else:
							el.click()
							break
			else:
				for x in range(2):
					try:
						el = self.dr.find_element_by_xpath("//UIAButton[@name='%s']" % mm)
					except Exception as ex:
						self.dr.find_element_by_xpath("//UIAButton[@name='123']").click()
					else:
						el.click()
						break
		self.dr.find_element_by_xpath("//UIAButton[@name='return']").click()
