#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'among',lifeng29@163.com
# 20150801


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep

cps = DesiredCapabilities.INTERNETEXPLORER.copy()

cps['ignoreProtectedModeSettings'] = True

dr = webdriver.Remote(command_executor='http://10.0.244.109:4444/wd/hub', desired_capabilities=cps)

dr.implicitly_wait(10)

dr.get('http://10.0.244.115:8080/xtest/login.jsp')

dr.maximize_window()

print(dr.title)
print(dr.get_window_size())

elem = WebDriverWait(dr, 20).until(EC.presence_of_element_located((By.ID, 'txtUid')))

elem.send_keys('admin')

dr.find_element_by_id('txtPwd').send_keys('Czbank806')
dr.find_element_by_id('ok').click()

WebDriverWait(dr, 20).until(EC.presence_of_all_elements_located)
dr.find_element_by_xpath("//*[@id='projectmanager']").click()

pngname = 'c:/test.png'
try:
	dr.get_screenshot_as_file(pngname)
except Exception as ex:
	pass

dr.quit()
