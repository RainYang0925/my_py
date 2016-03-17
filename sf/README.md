# 说明 #

版本：3.0 20160317

lifeng29@163.com

----------
##安装方法：##

1. 系统需求: Windows或mac os x，Python3.4及以上版本；
2. 需安装配置好java，appium，安卓SDK环境；
3. Python依赖包：CherryPy，请使用pip install CherryPy 来安装；
4. mac中支持iOS设备的第三方运行环境，使用brew install --HEAD ideviceinstaller 进行安装（需翻墙）；
5. 在config.ini中按照运行环境信息修改配置信息；
6. Windows通过bat执行，mac通过sh文件执行。

## 主要功能 ##
提供json wire protocol形式的接口，用于管理selenium, appium和安卓、iOS移动设备。

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

## 6：获取设备在线状态 ##
 	查询设备是否在线。
	http方法：get
 	url: http://ip:port/device/<udid>/state

## 7：获取设备属性信息 ##
 	查询设备的属性信息
	http方法：get
 	url: http://ip:port/device/<udid>/<prop>
	prop为属性名称，安卓中使用adb shell getprop prop来获取，iOS中使用ideviceinfo -k prop来获取。

## 8：获取设备实时截图 ##
 	查询设备的实时截图
	http方法：get
 	url: http://ip:port/device/<udid>/png/<prop>
	prop为refresh，则实时刷新，否则使用缓存图片，实时安卓和iOS。

## 9：上传apk和ipa文件 ##
 	用于推送apk和ipa文件
	http方法：get，post
 	url: http://ip:port/upload
	get请求会返回一个页面，可手工调试。
	post请求，请把文件放到pkg_data字段中。
	post请求后，会返回保存的路径和文件的md5值。后续可调用install_app进行apk和ipa的安装。


## 10：安装app ##
 	http方法：get和post，可安装apk和ipa
 	url: http://ip:port/install_app
	get方法，为手动的方式，可以通过浏览器页面，点击提交apk。
	post方式，直接发送apk的路径信息，可指定apk和udid信息
 	提交的参数：
	app_path：可使用upload文件返回的路径信息
	package：com.xxx.xxxx
	udid：可空

## 11：获取selenium的状态信息 ##
 	获取selenium的端口号，当前运行的capabilities信息
	http方法：get
 	url: http://ip:port/list_selenium


# 其他 #
	目前完成了后端接口的开发，还需要有好的前端进行调用。。。
