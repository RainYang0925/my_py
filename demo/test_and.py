#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'among',lifeng29@163.com
# 20150801

from appium import webdriver
from among4ios import Mytc
from time import sleep

url = 'http://127.0.0.1:4723/wd/hub'

url = 'http://10.1.38.98:4723/wd/hub'

caps_ip4 = {'deviceName': 'Android emulator', 'platformVersion': '4.4', 'udid': '9SS4NFB65TAUCU5L',
			'platformName': 'Android',
			'appPackage': 'com.czbank.mbank', 'appActivity': 'com.zsbank.emp.activity.MainActivity'}

# caps_ip4 = {'deviceName': 'Android emulator', 'platformName': 'Android'}
# ispng = True
ispng = False
png_tm = 10


# dr = webdriver.Remote(command_executor=url, desired_capabilities=caps_ip4)
my = Mytc(url=url, cap=caps_ip4, enable_png=True)

sleep(20)

a = my.dr.find_element_by_xpath(
	'//android.widget.FrameLayout/android.widget.RelativeLayout/android.view.View/android.widget.LinearLayout/android.widget.FrameLayout/android.view.View/android.view.View[2]/android.view.View/android.view.View/android.view.View/android.view.View[2]/android.view.View/android.widget.ImageView')
# print cap

a.click()

while True:
	print('gen png')
	my.dr.get_screenshot_as_file('c:/4723.png')
	sleep(10)
