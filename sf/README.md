# 说明 #


## 主要功能 ##
提供json wire protocol形式的接口，用于管理appium，和安卓、iOS移动设备。

## 部署方式 ##
适用于Windows和MAC平台，其他平台暂不支持。

基于python，请先安装python，无需安装其他第三方package。

可按需修改的地方：
sf.py 程序的 15，16行，表示你windows机器上appium的安装路径和nul的路径；20，21行，表示你mac机器上，appium的安装路径，nul不用修改。

默认监听8080端口，如需修改，请修改最后一行中的port。

启动方式：python sf.py

## 功能列表 ##

## 1：获取状态信息 ##
	此方法可用于接口调试，无其他用处。
 	http方法：get
 	url: http://ip:port/status
 	返回值:
	{
	"status": 0,
	"platform": "Windows",
	"version": "1.0"
	}


## 2：获取连接上的设备: ##
	此方法可获取安卓和iOS设备的信息
 	http方法：get
 	url: http://ip:port/list_devices
 	返回值:
	{
		"status": 0,
		"platform": "Windows",
		"devices": [{
			"udid": "5T2SQL1563015797",
			"screen size": "720x1280",
			"model": "HUAWEI_P7_L07",
			"version": "4.4.2",
			"type": "Android"
		}, {
			"udid": "750BBLE224M7",
			"screen size": "1152x1920",
			"model": "MX4",
			"version": "4.4.2",
			"type": "Android"
		}]
	}
	
## 3：获取已经开启的appium服务 ##
 	http方法：get
 	url: http://ip:port/list_appium
 	返回值:
 	#如果appium正在执行，也会返回执行的phone_type，udid，sessionid信息，如果不在运行，则只有pid，port等
	{
		"status": 0,
		"platform": "Windows",
		"appium": [{
			"phone_type": "Android",
			"udid": "5T2SQL1563015797",
			"pid": "2816",
			"sessionid": "a558cba3-5778-4847-9a2e-fa8c193f15b9",
			"version": "1.4.0",
			"port": "4723"
		}, {
			"version": "1.4.0",
			"pid": "1884",
			"port": "4733"
		}]
	}

## 4：重置devices ##
 	http方法：get
 	url: http://ip:port//reset_devices
	其实就是重启下adb...，仅适用于安卓
 	返回值:
	{"status": 0}
 	
## 5：重置appium ##
 	http方法：get
 	url: http://ip:port//reset_appium
	首先杀掉现在已有的appium服务，然后根据当前机器上连接的移动设备数量，自动启动appium服务，端口从4723开始，后续为4733，4743...
 	返回值:
	返回值都为0，请通过list_appium 方法重新获取appium的信息。
	{"status": 0}

## 6：安装apk ##
 	http方法：get和post，仅适用于安卓apk
 	url: http://ip:port/install_apk
	get方法，为手动的方式，可以通过浏览器页面，点击提交apk。
	post方式，直接发送apk的路径信息，可指定apk和udid信息

 	提交的参数：
	app_path	\\10.0.247.57\Share\apk_release\xxx-yz-1.0.52.apk
	package	    com.xxx.xxxx
	udid	
	以上信息，app_path为apk的路径，在mac上，路径为'/'格式，要求win和mac都要自己访问到，这里只发送路径。package 为卸载apk时用的，udid可选，如不填，就默认安装到所有的安卓设备上，如有值，则只安装到你指定的设备上。
	
 	返回值:
	{
		"status": 0,
		"result": [{
			"udid": "5T2SQL1563015797",
			"flag": "Success"
		}, {
			"udid": "750BBLE224M7",
			"flag": "Success"
		}]
	}


# 遗留问题 #
	py程序使用了基于bottle的web框架，在某些时候发现，如果使用ctrl + c的方式，停止py程序，则有可能造成占用的端口无法释放，通过netstat -ano|findstr 8080可以看到占用pid号，但实际的pid号已经不存在。
	此问题在windows上遇到过，也不是经常出现，在mac上暂未发现。
	如果出现了，只有通过注销或重启操作系统。。。 =_=
