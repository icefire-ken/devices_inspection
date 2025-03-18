# 简介

- 作为网络工程师工作中经常遇到需要对网络设备进行巡检的情况，此前都是用SecureCRT软件开启记录Log Session，依次登录每台设备，依次输入命令收集巡检信息。
  
- 现在利用Python实现自动登录网络设备，自动输入命令收集巡检信息；并且使用多线程技术，缩减巡检时间。
  
- 在登录出现故障时，能够记录Log提醒工程师，待排查故障后可再次进行巡检。

- 执行巡检能够在.py脚本所在目录下生成当前日期的巡检信息存放目录，其中每台设备的巡检信息文件以设备名称命名。

- .py脚本已经封装为.exe程序，配合info文件可以方便的在没有Python环境的PC上使用。（可在Releases中下载）

# 使用方法

## Step-1、执行准备

- 准备info.xlsx文件，与.exe程序或.py脚本存放于同一目录，文件里应存有需要巡检设备的登录信息和巡检命令。

info文件内sheet1存放被巡检网络设备的登录信息，如下：

![sheet1.png](https://github.com/icefire-ken/devices_inspection/blob/main/images/sheet1.png?raw=true)

info文件内sheet2存放用于网络设备巡检输入的命令，如下：

![sheet2.png](https://github.com/icefire-ken/devices_inspection/blob/main/images/sheet2.png?raw=true)

## Step-2、exe程序执行（Step-2与Step-3任选其一）

- 在Releases中下载.exe程序。
- 运行.exe程序，开始巡检。

![exe.png](https://github.com/icefire-ken/devices_inspection/blob/main/images/exe.png?raw=true)

## Step-3、py脚本执行（Step-2与Step-3任选其一）

- py脚本执行需要先安装python环境与依赖的第三方库，利用requirements.txt文件，使用下面的命令安装依赖的第三方库。

```python
pip install -r requirements.txt
```

- 在脚本文件目录下，使用下面的命令运行脚本，开始巡检。

```python
python devices_inspection.py
```

# 关于info文件中的Secret密码！

- 如果人工登录设备没有要求输入Enable Password，info文件中的Secret字段为空（无需填写）。
- ~~A10设备默认是没有Enable Password的，但进入Enable模式时，仍然会提示要求输入Enable Password，人工操作时可以直接Enter进入；使用脚本时需要在info文件的Secret字段中填入空格即可。~~
  - 不再需要，2024.02.02更新解决。

# 为info文件添加需要的设备类型

## Step-1、首先确认Netmiko支持的设备类型

- 访问[Netmiko PLATFORMS](https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md)，查看支持的设备类型。

## Step-2、添加设备类型进info文件

- 在info文件内sheet1的Device Type列，添加需要的设备类型，并填写正确的登录信息。
![add_device_type.png](https://github.com/icefire-ken/devices_inspection/blob/main/images/add_device_type.png?raw=true)
- 在info文件内sheet2添加该设备类型对应的巡检命令。
![add_command.png](https://github.com/icefire-ken/devices_inspection/blob/main/images/add_command.png?raw=true)

# 关于使用Telnet方式登录设备

- Netmiko使用deivce_type后缀的方式来识别使用Telnet方式登录的设备，比如：cisco_ios_telnet，有此后缀的设备Netmiko会自动使用Telnet方式登录。
- 但Netmiko目前支持Telnet方式登录的设备类型有限，具体可参考[Netmiko PLATFORMS](https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md)官方说明。
- 使用Telnet方式巡检时，在info文件内sheet1的deivce_type列中，添加带有Telnet后缀标识的device_type，如：cisco_ios_telnet。（方法与**为info文件添加需要的设备类型**相同）
- 相应的，sheet2中也需要使用带有Telnet后缀的device_type，如：cisco_ios_telnet，来标识来用巡检此类型设备的巡检命令。（方法与**为info文件添加需要的设备类型**相同）

# 关于加密info文件的方式

- 想要为info文件加密，请参照下面的方法。
- 依次点击文件-信息-保护工作薄-用密码进行加密。
- 输入密码，并再次确认密码即可。。.

<img src="https://github.com/icefire-ken/devices_inspection/blob/main/images/encrypt_1.png" width="400" />

<img src="https://github.com/icefire-ken/devices_inspection/blob/main/images/encrypt_2.png" width="400" />

<img src="https://github.com/icefire-ken/devices_inspection/blob/main/images/encrypt_3.png" width="400" />

# 更新日志

详见[UPDATE.md](https://github.com/icefire-ken/devices_inspection/blob/main/UPDATE.md)。