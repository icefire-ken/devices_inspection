#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os, time, pandas, threading
from netmiko import ConnectHandler

info_path = 'info.xlsx'  # 给定信息文件
localtime = time.strftime('%Y.%m.%d', time.localtime())  # 读取当前日期


def get_devices_info(info_file):  # 获取信息文件中的设备登录信息
    try:
        devices_dataframe = pandas.read_excel(info_file, sheet_name=0)  # 读取excel文件第一张表格的数据生成DataFrame
        devices_dict = devices_dataframe.to_dict('records')  # 将DataFrame转换成字典
        # 'records'参数规定外层为列表，内层以列标题为key，一行内容为value的字典
        # 若有多列，代表字典内有多个key:value对；若有多行，每行为一个字典
        return devices_dict
    except (FileNotFoundError):
        print('没有找到info文件！')


def get_cmds_info(info_file):  # 获取信息文件中的巡检命令
    try:
        cmds_dataframe = pandas.read_excel(info_file, sheet_name=1)  # 读取excel文件第二张表格的数据
        cmds_dict = cmds_dataframe.to_dict('list')  # 将DataFrame转换成字典
        # 'list'参数规定外层为字典，列标题为key，列下所有行内容以list形式为value的字典
        # 若有多列，代表字典内有多个key:value对
        return cmds_dict
    except (FileNotFoundError):
        print('没有找到info文件！')
    except (ValueError):
        print('info文件缺失子表格信息！')


def inspection(device_info, cmds_dict):
    # 使用传入的参数设备登录信息和巡检命令，登录设备依次输入巡检命令，并生成log文件
    t11 = time.time()  # 子线程执行计时起始点
    ssh = ConnectHandler(**device_info)  # 使用当前设备登录信息，SSH登录设备
    ssh.enable()  # 进入设备Enable模式
    f = open(os.getcwd() + '\\' + localtime + '\\' + device_info['host'] + '.log', 'w')  # 创建当前设备的log文件
    print('设备', device_info['host'], '正在巡检...')  # 打印线程正在巡检的设备IP
    for c in cmds_dict[device_info['device_type']]:  # 从cmds_dict中找到与当前设备类型匹配的命令列表，遍历所有巡检命令
        f.write('=' * 10 + ' ' + c + ' ' + '=' * 10 + '\n\n')  # 写入当前巡检命令分行符，至log文件
        show = ssh.send_command(c)  # 执行当前巡检命令，并获取结果
        time.sleep(1)  # 等待1s
        f.write(show + '\n\n')  # 写入当前巡检命令的结果，至log文件
    f.close()  # 关闭创建的log文件
    ssh.disconnect()  # 关闭SSH连接
    t12 = time.time()  # 子线程执行计时结束点
    print('设备', device_info['host'], '巡检完成，用时', round(t12 - t11, 1), '秒。')  # 打印子线程执行共用时长
    pool.release()  # 最大线程限制，释放一个线程


if __name__ == '__main__':
    t1 = time.time()  # 程序执行计时起始点
    thread_list = []  # 创建一个列表，准备存放所有线程
    pool = threading.BoundedSemaphore(100)  # 最大巡检线程控制
    print('巡检开始...')
    if not os.path.exists(localtime):  # 检查是否有同日期命名的相同文件夹
        os.makedirs(localtime)  # 如果没有，创建日期文件夹
    for device_info in get_devices_info(info_path):  # 遍历所有设备登录信息
        pre_device = threading.Thread(target=inspection, args=(device_info, get_cmds_info(info_path)))
        # 创建一个线程，执行inspection函数，传入当前遍历的设备登录信息和巡检命令字典
        thread_list.append(pre_device)  # 将当前创建的线程追加进列表
        pool.acquire()  # 最大线程限制，获取一个线程
        pre_device.start()  # 开启这个线程
    for i in thread_list:  # 遍历所有创建的线程
        i.join()  # 等待所有线程的结束
    t2 = time.time()  # 程序执行计时结束点
    print('巡检结束，共用时', round(t2 - t1, 1), '秒。')  # 打印程序执行共用时长
