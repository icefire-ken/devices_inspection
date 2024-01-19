# 简介

- 作为网络工程师工作中经常遇到需要对网络设备进行巡检的情况，此前都是用SecureCRT软件开启记录Log Session，依次登录每台设备，依次输入命令收集巡检信息。
  
- 现在利用Python实现自动登录网络设备，自动输入命令收集巡检信息；并且使用多线程技术，缩减巡检时间。
  
- 在登录出现故障时，能够记录Log提醒工程师，待排查故障后可再次进行巡检。

- 执行巡检能够在.py脚本所在目录下生成当前日期的巡检信息存放目录，其中每台设备的巡检信息文件以设备名称命名。

- .py脚本已经封装为.exe程序，配合info文件可以方便的在没有Python环境的PC上使用。（可在Releases中下载）

# 使用方法

## P1、执行准备

- 准备info.xlsx文件，与.exe程序或.py脚本存放于同一目录，文件里应存有需要巡检设备的登录信息和巡检命令。

info文件内sheet1存放被巡检网络设备的登录信息，如下：

![OvzZfp.png](https://ooo.0x0.ooo/2024/01/19/OvzZfp.png)

info文件内sheet2存放用于网络设备巡检输入的命令，如下：

![OvzyBU.png](https://ooo.0x0.ooo/2024/01/19/OvzyBU.png)

## P2、exe程序执行（P2与P3任选其一）

- 在Releases中下载.exe程序。
- 运行.exe程序，开始巡检。

![OvzKpj.png](https://ooo.0x0.ooo/2024/01/19/OvzKpj.png)

## P3、py脚本执行（P2与P3任选其一）

- 脚本执行需要先安装依赖的第三方库，利用requirements.txt文件，使用下面的命令安装依赖的第三方库。

```python
pip install -r requirements.txt
```

- 在脚本文件目录下，使用下面的命令运行脚本，开始巡检。

```python
python devices_inspection.py
```

## 关于info文件中的Secret密码！

- 如果人工登录设备没有要求输入Enable Password，info文件中的Secret字段为空（无需填写）。
- A10设备默认是没有Enable Password的，但进入Enable模式时，仍然会提示要求输入Enable Password，人工操作时可以直接Enter进入；使用脚本时需要在info文件的Secret字段中填入空格即可。

# 更新日志

## 待更新

- 增加了对未知异常的处理。

## 2024.01.19

- 使用了更多的格式化字符串，使得输出信息更清晰，脚本可读性更高。
- 在info文件设备登录信息表项中添加了port字段，为某些修改了SSH和Telnet默认端口的场景提供使用。
- 增加了程序延迟结束，在使用.exe程序时为工程师留有充足的时间查看CMD中的输出信息。
- 修改了操作文件的路径获取方式。
- 修改了对巡检命令是否为字符串的判断。
- 修改了一些不够准确的注释。
- 修复了释放线程的结构，避免了异常退出时，可能无法释放线程的错误。
- 修复了读取info文件异常时，脚本仍然继续执行的错误。

## 2024.01.12

- 修改了获取info文件路径的方式。

## 2023.12.28

- info文件添加了部分锐捷类型设备的巡检命令。

## 2023.12.25

- 为了方便在没有Python环境的PC上使用，以将.py脚本打包成了.exe程序。
- EXE程序Release，想要直接使用的朋友可以在Releases下载EXE程序，配合info文件使用。

## 2023.06.19

- 修复了巡检命令输入等待结果时间过长的问题，大幅缩短巡检时间。
  
## 2022.11.07

- 修复了CMD窗口内巡检过程实时显示，有可能发生的多个设备信息在同一行显示的问题。

## 2022.08.12

- A10设备请注意，若Enable密码为空，则需要在info文件中的Secret列中填补空格，否则会报“登录信息错误”异常。

## 2022.06.21

- 增加了对Telnet连接超时的异常捕获，并记录到日志文件中。

## 2021.12.28

- 为项目添加requirements.txt文件，方便脚本移植。

## 2021.12.13

- 修复多线程对01log文件操作时可能出现的冲突问题。
- 修复保存的巡检文件和log文件打开时会出现乱码的问题。

## 2021.12.02

- 修复读取设备登录信息中的纯数字内容为数字类型，不能供给Netmiko使用的问题。

## 2021.11.04

- 为info文件添加需要使用telnet登录的标识。
- 为“设备管理地址不可达！”登录异常修改描述“设备管理地址或端口不可达！”。
- info文件添加了部分华三（hp_comware）类型设备的巡检命令。

## 2021.11.01

- 加入登录设备出现错误信息的记录功能，会在巡检目录下创建01log文件来记录设备登录时出现的异常。
- info文件添加了部分Cisco ASA（cisco_asa）类型设备的巡检命令。
- 修复读取巡检命令时，由于pandas出现的nan。

## 2021.10.02

- 为避免过多消耗设备性能，加入巡检最大线程限制，默认最大100个线程。
- info文件添加了部分华为（huawei）类型设备的巡检命令。

## 2021.09.17

- 初次上传脚本。
- 脚本已经实现基本功能，及多线程巡检功能。
- info文件中Sheet2只包含了cisco_ios、a10的巡检命令。
