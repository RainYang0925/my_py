# 说明 #

版本：3.0 20160317

lifeng29@163.com

----------
##安装方法：##

1. 系统需求: Windows或mac os x，Python3.4及以上版本；
2. Python依赖包：CherryPy，请使用pip install CherryPy 来安装；
3. 在config.ini中按照运行环境信息修改配置信息；
4. Windows通过bat执行，mac通过sh文件执行。

## 主要功能 ##
动态数据服务，目前实现了sf服务中设备和appium信息的聚合服务，短信验证码的查询接口。
后续可在这个接口上，继续增加RESTful api的调用接口。

## 功能列表 ##
**port**指sf启动后监听的端口，在congfig.ini文件中配置。
## 1：获取状态等信息 ##
	此方法可用于获取状态等信息，如操作系统、版本号、类型等。
 	http方法：get
 	url: http://ip:port/status

## 2：获取已连接上的设备 ##
	用于获取安卓和iOS设备的信息，iOS仅限mac平台
 	http方法：get
 	url: http://ip:port/list_devices
	
## 3：获取appium服务信息 ##
	用于获取appium的状态信息，包括端口，版本等
 	http方法：get
 	url: http://ip:port/list_appium

## 4：重置devices ##
	其实就是重启下adb...，仅适用于安卓
 	http方法：get
 	url: http://ip:port/reset_devices

## 5：重置appium ##
 	首先杀掉现在已有的appium服务，然后根据当前机器上连接的移动设备数量，自动启动appium服务。
	默认从4723开始，后续为4733，4743...
	用于并发执行
	http方法：get
 	url: http://ip:port/reset_appium

## 6：获取执行机器信息 ##
 	获取执行机器信息
	http方法：get
 	url: http://ip:port/list_runner/<ip>
	若ip存在，则重定向到对应机器的sf服务的接口中去,否则从数据库中获取。
	

## 7：获取短信验证码 ##
 	获取执行机器信息
	http方法：get
 	url: http://ip:port//sms/<phone>
	phone为手机号码，根据这个号码查询对应的手机验证码。

	
# 其他 #
	可根据需要增加接口。。。
