import time
import os
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from utils import print_log,analysis_basic_info
from selenium.webdriver.common.action_chains import ActionChains,ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

def init_driver(server_config, cap):
    driver1 = None
    server = f"{server_config['protocol']}://{server_config['host']}:{server_config['port']}{server_config['path']}"
    try:
        driver1 = webdriver.Remote(server, cap)
        driver1.implicitly_wait(3)  # 设置隐式等待时间为3秒.定位控件时间超过3秒 则报错
        print_log("appium服务连接成功")
    except:
        print_log("!e!appium服务启动失败,请检查appium服务是否启动")
    
    time.sleep(5)  # 等待手机响应,跳过广告
    swipe_chuanda(driver1)
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


def auto(driver,resource_id, info_id,info_list,known_xhs_id,max_fresh_num=8,wait_time=0.5):
    """自动化主要流程"""

    fresh_num = 0  # 刷新次数
    while contain_video(driver,resource_id,wait_time=wait_time):
        #如果包含了视频,直接fresh
        print_log("发现视频", end="-->")
        if fresh_page(driver,resource_id):
            fresh_num += 1
            if fresh_num > max_fresh_num:
                print_log("刷新次数过多仍未获取到信息,退出程序")
                return False,[],known_xhs_id
        else:
            return False,[],known_xhs_id

    print_log("未发现视频,开始获取信息")
    for index in range(4):
        # 每个阶段获取四个博主信息
        try:
            wrong_step = "获取并点击文章"  # 出现异常的阶段
            articles = driver.find_elements(
                by=AppiumBy.ID, value=resource_id["article"])
            articles[index].click()
            print_log(f"进入第{index+1}篇文章", end="-->")
            time.sleep(wait_time)
            
            wrong_step = "点击头像"
            e2 = driver.find_element(
                by=AppiumBy.ID, value=resource_id['avatar'])
            e2.click()
            print_log("进入个人主页", end="-->")
            time.sleep(wait_time)
            
            wrong_step = "点击更多,保存基本信息"
            try:
                e3 = driver.find_element(
                    by=AppiumBy.ID, value=info_id['des']) # 点击更多
                e3.click()
                print_log("点击更多",end='-->')
            except:
                # 没有更多选项 直接保存
                pass
            time.sleep(wait_time)
            get_xml(driver)

     
            # 分析基本信息
            info,known_xhs_id = analysis_basic_info(info_id,known_xhs_id) #分析xml代码
            if info is not None:
                info_list.append(info)  # 信息添加
                
                wrong_step = "向下滑动,获取文章点赞数量"
                # try:
                #     swipe_get_article(driver)
                #     get_xml(driver)
                # except:
                #     pass
                    
                # time.sleep(wait_time)
                # get_xml(driver)
                
                
                # info,known_xhs_id = analysis_basic_info(info_id) #分析xml代码
                # if info == None:
                #     return False,[],known_xhs_id
                # info_list.append(info)  # 信息添加
        
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
            return False,[],known_xhs_id

    if fresh_page(driver,resource_id):
        return True,info_list,known_xhs_id
    
    return False,[],known_xhs_id

def swipe_chuanda(driver):
    """滑动获取穿搭模块"""
    
    
    x1 = 370
    y1 = 410
    # 向下滑动获取action_bar
    get_action_bar_actions = ActionChains(driver)
    get_action_bar_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"))
    get_action_bar_actions.w3c_actions.pointer_action.move_to_location(x1,y1)
    get_action_bar_actions.w3c_actions.pointer_action.pointer_down()
    get_action_bar_actions.w3c_actions.pointer_action.move_to_location(x1,y1+100)
    get_action_bar_actions.w3c_actions.pointer_action.release()
    get_action_bar_actions.perform()
    
    x2 = 840
    y2 = 280
    # 向左滑动
    left_swipe_actions = ActionChains(driver)
    left_swipe_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"))
    left_swipe_actions.w3c_actions.pointer_action.move_to_location(x2,y2)
    left_swipe_actions.w3c_actions.pointer_action.pointer_down()
    left_swipe_actions.w3c_actions.pointer_action.move_to_location(x2-500,y2)
    left_swipe_actions.w3c_actions.pointer_action.release()
    
    
    # 检测action_bar中是否包含穿搭模块
    # androidx.appcompat.app.ActionBar$Tab
    x = 0
    while x < 2:
        try:
            actionbar = driver.find_element(
                        by=AppiumBy.XPATH, value="//android.widget.TextView[@text='穿搭']")
            actionbar.click()
            print_log("点击穿搭bar成功",end="-->")
        except:
            if x == 1:
                print_log("!w!不存在穿搭bar")
            else:
                left_swipe_actions.perform()
                
        x += 1
            

def swipe_get_article(driver):
    """滑动获取穿搭模块"""
    
    
    x1 = 370
    y1 = 410
    # 向下滑动获取action_bar
    get_action_bar_actions = ActionChains(driver)
    get_action_bar_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"))
    get_action_bar_actions.w3c_actions.pointer_action.move_to_location(x1,y1)
    get_action_bar_actions.w3c_actions.pointer_action.pointer_down()
    get_action_bar_actions.w3c_actions.pointer_action.move_to_location(x1,y1+100)
    get_action_bar_actions.w3c_actions.pointer_action.release()
    get_action_bar_actions.perform()
    
    x2 = 840
    y2 = 280
    # 向左滑动
    left_swipe_actions = ActionChains(driver)
    left_swipe_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"))
    left_swipe_actions.w3c_actions.pointer_action.move_to_location(x2,y2)
    left_swipe_actions.w3c_actions.pointer_action.pointer_down()
    left_swipe_actions.w3c_actions.pointer_action.move_to_location(x2-500,y2)
    left_swipe_actions.w3c_actions.pointer_action.release()
    
    
    # 检测action_bar中是否包含穿搭模块
    # androidx.appcompat.app.ActionBar$Tab
    x = 0
    while x < 2:
        try:
            actionbar = driver.find_element(
                        by=AppiumBy.XPATH, value="//android.widget.TextView[@text='穿搭']")
            actionbar.click()
            print_log("点击穿搭bar成功",end="-->")
        except:
            if x == 1:
                print_log("!w!不存在穿搭bar")
            else:
                left_swipe_actions.perform()
                
        x += 1  

if __name__ == "__main__":
    # swipe
    pass
