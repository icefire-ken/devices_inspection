#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import time
import pandas
import threading
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException
from netmiko.exceptions import AuthenticationException

INFO_PATH = os.path.join(os.path.dirname(__file__), 'info.xlsx')  # 给定info文件
LOCAL_TIME = time.strftime('%Y.%m.%d', time.localtime())  # 读取当前日期
LOCK = threading.Lock()  # 线程锁实例化


def get_devices_info(info_file):  # 获取info文件中的设备登录信息
    try:
        devices_dataframe = pandas.read_excel(info_file, sheet_name=0, dtype=str)  # 读取Excel文件第一张工作表的数据生成DataFrame
    except FileNotFoundError as get_devices_error:  # 如果没有配置info文件或info文件名称错误
        print(f'没有找到info文件！')
        sys.exit(1)
    else:
        devices_dict = devices_dataframe.to_dict('records')  # 将DataFrame转换成字典
        # "records"参数规定外层为列表，内层以列标题为key，以此列的行内容为value的字典
        # 若有多列，代表字典内有多个key:value对；若有多行，每行为一个字典
        return devices_dict


def get_cmds_info(info_file):  # 获取info文件中的巡检命令
    try:
        cmds_dataframe = pandas.read_excel(info_file, sheet_name=1, dtype=str)  # 读取Excel文件第二张工作表的数据生成DataFrame
    except Exception as get_cmds_error:
        match type(get_cmds_error).__name__:
            case 'FileNotFoundError':
                print(f'没有找到info文件！')
                sys.exit(1)
            case 'ValueError':
                print(f'info文件缺失子表格信息！')
                sys.exit(1)
    else:
        cmds_dict = cmds_dataframe.to_dict('list')  # 将DataFrame转换成字典
        # "list"参数规定外层为字典，列标题为key，列下所有行内容以list形式为value的字典
        # 若有多列，代表字典内有多个key:value对
        return cmds_dict


def inspection(login_info, cmds_dict):
    # 使用传入的设备登录信息和巡检命令，登录设备依次输入巡检命令，如果设备登录出现异常，生成01log文件记录。
    t11 = time.time()  # 子线程执行计时起始点
    ssh = None  # 初始化ssh对象

    try:  # 尝试登录设备
        ssh = ConnectHandler(**login_info)  # 使用设备登录信息，SSH登录设备
        ssh.enable()  # 进入设备Enable模式
    except AttributeError:  # 登录信息中缺失IP地址
        with LOCK:  # 线程锁
            print(f'设备 {login_info["host"]} 登录信息错误！')  # 打印提示该设备登录错误信息
            with open(os.path.join(os.getcwd(), LOCAL_TIME, '01log.log'), 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' 登录信息错误！\n')  # 保存巡检报错的信息
    except NetMikoTimeoutException:  # 登录信息中IP地址不可达
        with LOCK:
            print(f'设备 {login_info["host"]} 管理地址或端口不可达！')
            with open(os.path.join(os.getcwd(), LOCAL_TIME, '01log.log'), 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' 管理地址或端口不可达！\n')
    except AuthenticationException:  # 登录信息中用户名或密码错误
        with LOCK:
            print(f'设备 {login_info["host"]} 登录认证失败！')
            with open(os.path.join(os.getcwd(), LOCAL_TIME, '01log.log'), 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' 登录认证失败！\n')
    except ValueError:  # 登录信息中的Enable密码错误
        with LOCK:
            print(f'设备 {login_info["host"]} Enable密码错误！')
            with open(os.path.join(os.getcwd(), LOCAL_TIME, '01log.log'), 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' Enable密码错误！\n')
    except TimeoutError:  # Telnet登录超时
        with LOCK:
            print(f'设备 {login_info["host"]} Telnet连接超时！')
            with open(os.path.join(os.getcwd(), LOCAL_TIME, '01log.log'), 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' Telnet连接超时！\n')
    else:  # 如果登录正常，开始巡检
        with open(os.path.join(os.getcwd(), LOCAL_TIME, login_info['host'] + '.log'), 'w', encoding='utf-8') as device_log_file:
            # 创建当前设备的巡检信息记录文件
            print(f'设备 {login_info["host"]} 正在巡检...')  # 打印当前设备正在巡检提示信息
            for cmd in cmds_dict[login_info['device_type']]:  # 从所有设备类型巡检命令中找到与当前设备类型匹配的命令列表，遍历所有巡检命令
                if type(cmd) is str:  # 判断读取的命令是否为字符串
                    device_log_file.write('=' * 10 + ' ' + cmd + ' ' + '=' * 10 + '\n\n')  # 写入当前巡检命令分行符，至巡检信息记录文件
                    show = ssh.send_command(cmd, read_timeout=30)  # 执行当前巡检命令，并获取结果，最长等待30s
                    device_log_file.write(show + '\n\n')  # 写入当前巡检命令的结果，至巡检信息记录文件
        t12 = time.time()  # 子线程执行计时结束点
        print(f'设备 {login_info["host"]} 巡检完成，用时 {round(t12 - t11, 1)} 秒。')  # 打印子线程执行时长
    finally:  # 最后结束SSH连接释放线程
        if ssh is not None:  # 判断ssh对象有没有被正确赋值，没有正确赋值代表发生了异常
            ssh.disconnect()  # 关闭SSH连接
        pool.release()  # 最大线程限制，释放一个线程


if __name__ == '__main__':
    t1 = time.time()  # 程序执行计时起始点
    threading_list = []  # 创建一个线程列表，准备存放所有线程
    pool = threading.BoundedSemaphore(100)  # 最大线程控制，当前100个线程可以同时运行
    devices_info = get_devices_info(INFO_PATH)  # 读取所有设备的登录信息
    cmds_info = get_cmds_info(INFO_PATH)  # 读取所有设备类型的巡检命令

    print(f'\n巡检开始...')  # 提示巡检开始
    print(f'\n' + '>' * 40 + '\n')  # 打印一行“>”，隔开巡检提示信息

    if not os.path.exists(LOCAL_TIME):  # 判断是否存在有同日期的文件夹（判断当天是否执行过巡检）
        os.makedirs(LOCAL_TIME)  # 如果没有，创建当天日期文件夹
    else:  # 如果有
        try:  # 尝试删除记录巡检设备异常的记录文件，即01log文件
            os.remove(os.path.join(os.getcwd(), LOCAL_TIME, '01log.log'))  # 删除01log文件
        except FileNotFoundError:  # 如果没有01log文件（之前执行巡检没有发生异常）
            pass  # 跳过，不做处理

    for device_info in devices_info:  # 遍历所有设备登录信息
        pre_device = threading.Thread(target=inspection, args=(device_info, cmds_info))
        # 创建一个线程，执行inspection函数，传入当前遍历的设备登录信息和所有设备类型巡检命令
        threading_list.append(pre_device)  # 将当前创建的线程追加进线程列表
        pool.acquire()  # 从最大线程限制，获取一个线程令牌
        pre_device.start()  # 开启这个线程

    for i in threading_list:  # 遍历所有创建的线程
        i.join()  # 等待所有线程的结束

    try:  # 尝试打开01log文件
        with open(os.path.join(os.getcwd(), LOCAL_TIME, '01log.log'), 'r', encoding='utf-8') as log_file:
            file_lines = len(log_file.readlines())  # 读取01log文件共有多少行（有多少行，代表出现了多少个设备登录异常）
    except FileNotFoundError:  # 如果找不到01log文件
        file_lines = 0  # 证明本次巡检没有出现巡检异常情况
    t2 = time.time()  # 程序执行计时结束点
    print(f'\n' + '<' * 40 + '\n')  # 打印一行“<”，隔开巡检报告信息
    print(f'巡检结束，共巡检 {len(threading_list)} 台设备， {file_lines} 台异常，共用时 {round(t2 - t1, 1)} 秒。')  # 打印巡检报告
    time.sleep(3)  # 等待3秒退出程序，方便使用者查看CMD中的输出信息

