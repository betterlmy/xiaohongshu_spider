import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import os
from utils import print_log,analysis_info



def init_driver(server_config, cap):
    driver1 = None
    server = f"{server_config['protocol']}://{server_config['host']}:{server_config['port']}{server_config['path']}"
    try:
        driver1 = webdriver.Remote(server, cap)
        driver1.implicitly_wait(3)  # 设置隐式等待时间为3秒.定位控件时间超过3秒 则报错
        print_log("appium服务连接成功")
    except:
        print_log("!e!appium服务启动失败,请检查appium服务是否启动")

    time.sleep(3)  # 等待手机响应
    return driver1

def pass_ad(driver,resource_id,wait_time=0.5):
    """跳过广告"""

    try:
        driver.find_element(by=AppiumBy.ID, value=resource_id["pass"]).click()
        time.sleep(wait_time)
        print_log("跳过广告成功", end="-->")
    except:
        print_log("不存在广告", end="-->")


def get_xml(driver, xml="xml/info.xml"):
    """将页面资源写入到xml文件中"""

    if not os.path.exists("xml/"):
        os.mkdir("xml")
        print_log("xml文件夹不存在,已自动创建")

    if driver is None:
        print_log(f"!e!Driver不存在")
    else:
        with open(xml, "w", encoding="utf-8") as f:
            f.writelines(driver.page_source)
            print_log(f"xml文件成功保存到{xml}", end="-->")


def contain_video(driver,resource_id,wait_time=0.5):
    """判断是否存在视频,存在返回True,不存在返回False"""

    try:
        driver.find_element(by=AppiumBy.ID, value=resource_id["video"])
        time.sleep(wait_time)
        return True
    except:
        return False


def fresh_page(driver,resource_id):
    """刷新页面"""

    try:
        driver.find_element(by=AppiumBy.ID, value=resource_id['fresh']).click()
        print_log("页面刷新成功", end="-->")
        return True
    except:
        print_log("不存在刷新按钮,刷新失败")
        return False


def auto(driver,resource_id, info_id,info_list,max_fresh_num=8,wait_time=0.5):
    """自动化主要流程"""

    fresh_num = 0  # 刷新次数
    while contain_video(driver,resource_id,wait_time=wait_time):
        #如果包含了视频,直接fresh
        print_log("发现视频", end="-->")
        if fresh_page(driver,resource_id):
            fresh_num += 1
            if fresh_num > max_fresh_num:
                print_log("刷新次数过多仍未获取到信息,退出程序")
                return False,[]
        else:
            return False,[]

    print_log("未发现视频,开始获取信息")
    for index in range(4):
        # 每个阶段获取四个博主信息
        try:
            wrong_step = "获取文章控件"  # 出现异常的阶段
            articles = driver.find_elements(
                by=AppiumBy.ID, value=resource_id["article"])
            articles[index].click()

            wrong_step = "点击文章控件"
            print_log(f"进入第{len(info_list)+1}篇文章", end="-->")
            time.sleep(wait_time)
            e2 = driver.find_element(
                by=AppiumBy.ID, value=resource_id['avatar'])
            e2.click()

            wrong_step = "点击头像控件"
            print_log("进入个人主页", end="-->")
            time.sleep(wait_time)
            
            
            
            e3 = driver.find_element(
                by=AppiumBy.ID, value=info_id['des']) # 点击更多
            e3.click()
            time.sleep(wait_time)
            get_xml(driver)
             
            info = analysis_info(info_id)
            if info == None:
                return False,[]
            info_list.append(info)  # 信息添加

            wrong_step = "从个人主页返回文章"
            driver.find_element(
                by=AppiumBy.ID, value=resource_id['back1']).click()
            time.sleep(wait_time)

            wrong_step = "从文章返回首页"
            driver.find_element(
                by=AppiumBy.ID, value=resource_id['back2']).click()
            time.sleep(wait_time)
            print_log("退回主页")

        except:
            print_log(f"!e!某个控件不存在或页面出现其他异常,错误阶段{wrong_step}")
            get_xml(driver, "xml/wrong.xml")
            return False,[]

    if fresh_page(driver,resource_id):
        return True,info_list
    
    return False,[]
