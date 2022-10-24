import PySimpleGUI as sg
import os
import sys
import json
from utils import load_config, print_log
import time

def check(type1, values, config, changed):
    """检查并修改配置变量"""
    for key, _ in config[type1].items():
        if key not in values.keys():
            continue
        if config[type1][key] != values[key]:
            print_log(f"修改了{key}")
            # 判断ip合法性
            config[type1][key] = values[key]
            changed = True
    return changed, config


def config_server(server_window, config, changed):
    """服务器配置界面"""
    closed = False  # 是否点击关闭
    direct = False
    while True:
        event, values = server_window.read()
        if event == sg.WIN_CLOSED:
            closed = True
            break

        changed = False
        if event == '使用默认配置直接开始运行':
            direct = True
            server_window.close()
            return changed, config, closed, direct
        if config['appium_server_config']['host'] != values['host']:
            print_log("修改了host")
            # 判断ip合法性
            config['appium_server_config']['host'] = values['host']
            changed = True

        if config['cap']['appium:deviceName'] != values['appium:deviceName']:
            print_log("修改了deviceName")
            # 判断ip合法性
            config['cap']['appium:deviceName'] = values['appium:deviceName']
            changed = True
        break
    server_window.close()
    return changed, config, closed, direct


def config_resourceID(resource_window, config, changed):
    """配置资源控件ID"""
    closed = False
    while True:
        event, values = resource_window.read()
        if event == sg.WIN_CLOSED or event == '关闭':
            closed = True
            break
        changed, config = check('resource_id', values, config, changed)
        resource_window.close()
        break
    return changed, config, closed


def config_infoID(info_window, config, changed):
    """配置info控件ID"""
    closed = False
    while True:
        event, values = info_window.read()
        if event == sg.WIN_CLOSED or event == '关闭':
            closed = True
            break

        changed, config = check('info_id', values, config, changed)
        info_window.close()
        break
    return changed, config, closed


def GUI_start():
    now_time = time.strftime("%H-%M-%S", time.localtime())

    if not os.path.exists("tmp/"):
        os.mkdir("tmp")

    with open("tmp/.nowtime", 'w') as f:
        f.write(now_time)  # 通过.nowtime文件来进行全局变量传递
        f.close()

    print_log(f"程序运行开始,时间:")

    config = load_config()  # 加载配置文件 用于读取和修改

    if config is None:
        # 配置文件出现异常
        sys.exit()

    resource_id = config['resource_id']
    info_id = config['info_id']

    serverLayout = [
        [sg.Text('Appium服务器ip:'), sg.InputText(
            default_text=config['appium_server_config']['host'], key='host')],

        [sg.Text('设备名称(adb devices):'), sg.InputText(
            default_text=config['cap']['appium:deviceName'], key='appium:deviceName')],

        [sg.Button('配置资源id'), sg.Button('使用默认配置直接开始运行')]

    ]

    resourceIDLayout = [
        [sg.Text('文章ID:'), sg.InputText(
            default_text=resource_id['article'], key='article')],
        [sg.Text('头像ID:'), sg.InputText(
            default_text=resource_id['avatar'], key='avatar')],
        [sg.Text('视频ID:'), sg.InputText(
            default_text=resource_id['video'], key='video')],
        [sg.Text('刷新ID:'), sg.InputText(
            default_text=resource_id['fresh'], key='fresh')],
        [sg.Text('返回1ID:'), sg.InputText(
            default_text=resource_id['back1'], key='back1')],
        [sg.Text('返回2ID:'), sg.InputText(
            default_text=resource_id['back2'], key='back2')],
        [sg.Button('配置信息ID'), sg.Button('关闭')]
    ]

    infoIDLayout = [
        [sg.Text('账号名ID:'), sg.InputText(
            default_text=info_id['name_id'], key='name_id')],
        [sg.Text('小红书idID:'), sg.InputText(
            default_text=info_id['xhs_id'], key='xhs_id')],
        [sg.Text('个人简介ID:'), sg.InputText(
            default_text=info_id['des'], key='des')],
        [sg.Text('粉丝数ID:'), sg.InputText(
            default_text=info_id['fans_num'], key='fans_num')],
        [sg.Text('总获赞ID:'), sg.InputText(
            default_text=info_id['all_likes_num'], key='all_likes_num')],
        [sg.Button('参数配置'), sg.Button('关闭')]
    ]

    configLayout = [
        [sg.Text('默认等待时间(s):'), sg.InputText(
            default_text='0.5', key='wait_time')],
        [sg.Button('开始执行'), sg.Button('关闭')]
    ]

    margins = (100, 200)
    server_window = sg.Window("服务器配置", serverLayout, margins=margins)  # 绑定布局
    resource_window = sg.Window("资源ID配置", resourceIDLayout, margins=margins)
    info_window = sg.Window("信息ID配置", infoIDLayout, margins=margins)
    setting_window = sg.Window("自动化参数配置", configLayout, margins=margins)

    changed = False
    # 服务器配置界面
    changed, config, closed, direct = config_server(
        server_window, config, changed)
    
    if not direct:
    # 控件ID配置界面
        if not closed:
            changed, config, closed = config_resourceID(
                resource_window, config, changed)
        # infoID配置界面
        if not closed:
            changed, config, closed = config_infoID(info_window, config, changed)

        if not closed:
            if changed:  # 修改config文件
                with open("confing2.json", 'w') as f:
                    json.dump(config, f)

            # 获取运行参数
            while True:
                event, values = setting_window.read()
                if event == sg.WIN_CLOSED or event == '关闭':
                    closed = True
                    break

                try:
                    wait_time = float(values['wait_time'])
                except:
                    print_log("!e! wait_time格式转换错误")
                info_window.close()
                break

        return now_time, config, wait_time
    return now_time, config, 0.5

def GUI_running(t):

    runningLayout = [
        [sg.Text('服务器连接成功,正在运行中...')],
        [sg.Button('关闭任务')]
    ]
    running_window = sg.Window("运行中", runningLayout)
    x=0
    while t.is_alive():
        event, values = running_window.read(timeout=1000)# 每秒查询一次
        if event == sg.WIN_CLOSED or event == '关闭任务':
            t.stop()
            break

    running_window.close()
    
    

if __name__ == '__main__':
    GUI_running()