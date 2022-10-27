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
            # server_window.close()
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
        
    with open("tmp/.state", 'w') as f:
        f.write(str(0))  # 通过.state文件来判断是否终止了程序
        f.close()

    print_log(f"程序运行开始,时间:")

    config = load_config()  # 加载配置文件 用于读取和修改

    if config is None:
        # 配置文件出现异常
        sg.popup("发生错误","config文件不存在")
        sys.exit()

    resource_id = config['resource_id']
    info_id = config['info_id']

    serverLayout = [
        [sg.Text('Appium服务器ip:',size=(20,1)), sg.InputText(
            default_text=config['appium_server_config']['host'], key='host', size=(20, 1))],

        [sg.Text('设备名称(adb devices):',size=(20,1)), sg.InputText(
            default_text=config['cap']['appium:deviceName'], key='appium:deviceName', size=(20, 1))],

        [sg.Button('配置资源id'), sg.Button('使用默认配置直接开始运行')]

    ]

    resourceIDLayout = [
        [sg.Text('穿搭文章ID:',size=(13,1)), sg.InputText(
            default_text=resource_id['chuanda_article'], key='chuanda_article',size=(20,1))],
        [sg.Text('推荐文章ID:',size=(13,1)), sg.InputText(
            default_text=resource_id['tuijian_article'], key='tuijian_article',size=(20,1))],
        [sg.Text('信息页返回ID:',size=(13,1)), sg.InputText(
            default_text=resource_id['back1'], key='back1',size=(20,1))],
        [sg.Text('文章返回ID:',size=(13,1)), sg.InputText(
            default_text=resource_id['back2'], key='back2',size=(20,1))],
        [sg.Text('视频返回ID:',size=(13,1)), sg.InputText(
            default_text=resource_id['back21'], key='back21',size=(20,1))],
        [sg.Button('配置信息ID'), sg.Button('关闭')]
    ]

    infoIDLayout = [
        [sg.Text('账号名ID:',size=(13,1)), sg.InputText(
            default_text=info_id['name_id'], key='name_id',size=(20,1))],
        [sg.Text('小红书idID:',size=(13,1)), sg.InputText(
            default_text=info_id['xhs_id'], key='xhs_id',size=(20,1))],
        [sg.Text('个人简介ID:',size=(13,1)), sg.InputText(
            default_text=info_id['des'], key='des',size=(20,1))],
        [sg.Text('粉丝数ID:',size=(13,1)), sg.InputText(
            default_text=info_id['fans_num'], key='fans_num',size=(20,1))],
        [sg.Text('总获赞ID:',size=(13,1)), sg.InputText(
            default_text=info_id['all_likes_num'], key='all_likes_num',size=(20,1))],
        [sg.Text('均赞数ID:',size=(13,1)), sg.InputText(
            default_text=info_id['ave'], key='ave',size=(20,1))],
        [sg.Button('参数配置',size=(13,1)), sg.Button('关闭')]
    ]

    configLayout = [
        [sg.Text('默认等待时间(s):',size=(13,1)), sg.InputText(
            default_text='0.5', key='wait_time',size=(10,1))],
        [sg.Text('最大错误次数:',size=(13,1)), sg.InputText(
            default_text='10', key='max_error_time',size=(10,1))],
        [sg.Text('纵向分辨率:',size=(13,1)), sg.InputText(
            default_text='2310', key='VR',size=(10,1))],
        [sg.Text('横向分辨率:',size=(13,1)), sg.InputText(
            default_text='1080', key='LR',size=(10,1))],
        [sg.Text('进入模式:\n(1进入穿搭,0进入推荐)',size=(13,3)), sg.InputText(
            default_text='1', key='chuanda',size=(10,3))],
        [sg.Button('开始执行'), sg.Button('关闭')]
    ]

    margins = (100, 100)
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
                with open("config.json", 'w') as f:
                    json.dump(config, f)

            # 获取运行参数
            while True:
                event, values = setting_window.read()
                if event == sg.WIN_CLOSED or event == '关闭':
                    closed = True
                    break
                try:
                    wait_time = float(values['wait_time'])
                    max_error_time = int(values['max_error_time'])
                    VR = int(values['VR'])
                    LR = int(values['LR'])
                    chuanda = bool(int(values['chuanda']))
                    print(f"穿搭?{chuanda}")
                    running_config = {
                        'wait_time' : wait_time,
                        'max_error_time': max_error_time,
                        'res': [VR,LR],
                        'chuanda':chuanda,
                    }
                except:
                    sg.popup("发生错误","请检查参数配置")
                    print_log("!e! 前端格式转换错误")
                    sys.exit()
                break
            
        return now_time, config, running_config ,setting_window
    running_config = {
        'wait_time' : 0.5,
        'max_error_time': 8,
        'res': [2310,1080],
        'chuanda':True,
    }
    return now_time, config, running_config,server_window

def GUI_running(t,final_window,state):
    
    runningLayout = [
        [sg.Text('服务器连接成功,自动化脚本正在运行中...')],
        [sg.Button('关闭任务')]
    ]
    
    running_window = sg.Window("运行中", runningLayout,margins=(80, 80))
    final_window.close()
    x=0
    while t.is_alive():
        event, values = running_window.read(timeout=1000)# 每秒查询一次
        if event == sg.WIN_CLOSED or event == '关闭任务':
            state.stop()
            break

    running_window.close()
    

def GUI_warning(x1,x2):
    sg.popup(x1,x2)
    
    
if __name__ == '__main__':
    GUI_start()