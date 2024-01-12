#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import time
import pandas
import threading
from netmiko import ConnectHandler
# from netmiko.ssh_exception import AuthenticationException, NetmikoTimeoutException
from netmiko.exceptions import NetMikoTimeoutException
from netmiko.exceptions import AuthenticationException
# from netmiko.exceptions import SSHException

INFO_PATH = os.path.dirname(__file__) + '\\info.xlsx'  # 给定信息文件
LOCAL_TIME = time.strftime('%Y.%m.%d', time.localtime())  # 读取当前日期
LOCK = threading.Lock()  # 线程锁实例化


def get_devices_info(info_file):  # 获取信息文件中的设备登录信息
    try:
        devices_dataframe = pandas.read_excel(info_file, sheet_name=0, dtype=str)  # 读取excel文件第一张表格的数据生成DataFrame
        devices_dict = devices_dataframe.to_dict('records')  # 将DataFrame转换成字典
        # "records"参数规定外层为列表，内层以列标题为key，以此列的行内容为value的字典
        # 若有多列，代表字典内有多个key:value对；若有多行，每行为一个字典
        return devices_dict
    except FileNotFoundError:  # 如果没有配置信息文件或信息文件名称错误
        print('没有找到info文件！')


def get_cmds_info(info_file):  # 获取信息文件中的巡检命令
    try:
        cmds_dataframe = pandas.read_excel(info_file, sheet_name=1, dtype=str)  # 读取excel文件第二张表格的数据
        cmds_dict = cmds_dataframe.to_dict('list')  # 将DataFrame转换成字典
        # "list"参数规定外层为字典，列标题为key，列下所有行内容以list形式为value的字典
        # 若有多列，代表字典内有多个key:value对
        return cmds_dict
    except FileNotFoundError:  # 如果没有配置信息文件或信息文件名称错误
        print('没有找到info文件！')
    except ValueError:  # 信息文件缺少子表格信息
        print('info文件缺失子表格信息！')


def inspection(login_info, cmds_dict):
    # 使用传入的参数设备登录信息和巡检命令，登录设备依次输入巡检命令，如果设备登录出现问题，生成log文件。
    t11 = time.time()  # 子线程执行计时起始点

    try:  # 尝试登录设备
        ssh = ConnectHandler(**login_info)  # 使用当前设备登录信息，SSH登录设备
        ssh.enable()  # 进入设备Enable模式
    except AttributeError:  # 登录信息中缺失IP地址
        with LOCK:  # 线程锁
            print(f'设备 {login_info["host"]} 登录信息错误！')  # 打印提示该设备登录错误信息
            with open(os.getcwd() + '\\' + LOCAL_TIME + '\\' + '01log.log', 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' 登录信息错误！\n')  # 保存巡检报错的信息
    except NetMikoTimeoutException:  # 登录信息中IP地址不可达
        with LOCK:
            print(f'设备 {login_info["host"]} 管理地址或端口不可达！')
            with open(os.getcwd() + '\\' + LOCAL_TIME + '\\' + '01log.log', 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' 管理地址或端口不可达！\n')
    except AuthenticationException:  # 登录信息中用户名或密码错误
        with LOCK:
            print(f'设备 {login_info["host"]} 登录认证失败！')
            with open(os.getcwd() + '\\' + LOCAL_TIME + '\\' + '01log.log', 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' 登录认证失败！\n')
    except ValueError:  # 登录信息中的Enable密码错误
        with LOCK:
            print(f'设备 {login_info["host"]} Enable密码错误！')
            with open(os.getcwd() + '\\' + LOCAL_TIME + '\\' + '01log.log', 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' Enable密码错误！\n')
    except TimeoutError:  # Telnet登录超时
        with LOCK:
            print(f'设备 {login_info["host"]} Telnet连接超时！')
            with open(os.getcwd() + '\\' + LOCAL_TIME + '\\' + '01log.log', 'a', encoding='utf-8') as log:
                log.write('设备 ' + login_info['host'] + ' Telnet连接超时！\n')
    else:  # 如果登录正常，开始巡检
        with open(os.getcwd() + '\\' + LOCAL_TIME + '\\' + login_info['host'] + '.log', 'w', encoding='utf-8') as device_log_file:
            # 创建当前设备的log文件
            print('设备', login_info['host'], '正在巡检...')  # 打印当前线程正在巡检的设备名称
            for cmd in cmds_dict[login_info['device_type']]:  # 从cmds_dict中找到与当前设备类型匹配的命令列表，遍历所有巡检命令
                if type(cmd) == str:  # 判断读取的名字是否正确
                    device_log_file.write('=' * 10 + ' ' + cmd + ' ' + '=' * 10 + '\n\n')  # 写入当前巡检命令分行符，至log文件
                    show = ssh.send_command(cmd, read_timeout=30)  # 执行当前巡检命令，并获取结果，最长等待30s
                    # time.sleep(1)  # 等待1s
                    device_log_file.write(show + '\n\n')  # 写入当前巡检命令的结果，至log文件
        ssh.disconnect()  # 关闭SSH连接
        t12 = time.time()  # 子线程执行计时结束点
        print('设备', login_info['host'], '巡检完成，用时', round(t12 - t11, 1), '秒。')  # 打印子线程执行共用时长
        pool.release()  # 最大线程限制，释放一个线程


if __name__ == '__main__':
    t1 = time.time()  # 程序执行计时起始点
    threading_list = []  # 创建一个列表，准备存放所有线程
    pool = threading.BoundedSemaphore(100)  # 最大巡检线程控制
    devices_info = get_devices_info(INFO_PATH)  # 读取所有设备信息
    cmds_info = get_cmds_info(INFO_PATH)  # 读取所有设备类型的巡检命令

    print('\n巡检开始...')  # 提示巡检开始
    print('\n' + '>' * 40 + '\n')  # 打印一行“>”，隔开巡检提示信息

    if not os.path.exists(LOCAL_TIME):  # 检查是否有同日期命名的相同文件夹
        os.makedirs(LOCAL_TIME)  # 如果没有，创建日期文件夹
    else:  # 如果有
        try:  # 尝试删除巡检故障设备报错的log文件
            os.remove(os.getcwd() + '\\' + LOCAL_TIME + '\\' + '01log.log')  # 删除log文件
        except FileNotFoundError:  # 如果没有log文件
            pass  # 跳过，不做处理

    for device_info in devices_info:  # 遍历所有设备登录信息
        pre_device = threading.Thread(target=inspection, args=(device_info, cmds_info))
        # 创建一个线程，执行inspection函数，传入当前遍历的设备登录信息和巡检命令字典
        threading_list.append(pre_device)  # 将当前创建的线程追加进列表
        pool.acquire()  # 最大线程限制，获取一个线程
        pre_device.start()  # 开启这个线程

    for i in threading_list:  # 遍历所有创建的线程
        i.join()  # 等待所有线程的结束

    try:  # 尝试打开巡检log文件
        with open(os.getcwd() + '\\' + LOCAL_TIME + '\\' + '01log.log', 'r', encoding='utf-8') as log_file:
            file_lines = len(log_file.readlines())  # 读取巡检log文件共有多少行，有多少行，代表出现了多少个设备登录异常
    except FileNotFoundError:  # 如果找不到巡检log文件
        file_lines = 0  # 证明没有出现巡检登录异常情况
    t2 = time.time()  # 程序执行计时结束点
    print('\n' + '<' * 40 + '\n')  # 打印一行“<”，隔开巡检报告信息
    print(f'巡检结束，共巡检 {len(threading_list)} 台设备， {file_lines} 台异常，共用时 {round(t2 - t1, 1)} 秒。')  # 打印巡检报告

