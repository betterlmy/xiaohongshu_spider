import time
import os
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from utils import print_log,analysis_basic_info,analysis_likes
from selenium.webdriver.common.action_chains import ActionChains,ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from utils import save_info
import traceback



def init_driver(server_config, cap):
    driver1 = None
    server = f"{server_config['protocol']}://{server_config['host']}:{server_config['port']}{server_config['path']}"
    try:
        cap["appium:newCommandTimeout"] = 10000
        driver1 = webdriver.Remote(server, cap)
        driver1.implicitly_wait(3)  # 设置隐式等待时间为3秒.定位控件时间超过3秒 则报错
        print_log("appium服务连接成功")
    except:
        
        print_log("!e!appium服务启动失败,请检查appium服务是否启动")

    
    time.sleep(5)  # 等待手机响应,跳过广告
    return driver1



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

def contain_video(driver,resource_id,wait_time=0.5):
    """判断是否存在视频,存在返回True,不存在返回False"""

    try:
        driver.find_element(by=AppiumBy.ID, value=resource_id["video"])
        time.sleep(wait_time)
        return True
    except:
        return False


def fresh_page(driver,res,wait_time=0.5):
    """刷新页面"""

    height = res[0]
    width = res[1]
    
    x1 = int(width*0.4)
    y1 = int(height*0.3)
    y2 = int(height*0.6)

    # driver.swipe(x1,y1,x1,y2,duration=1)
    # driver.get_window_size()

    fresh_actions = ActionChains(driver)
    fresh_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"),duration=500)
    fresh_actions.w3c_actions.pointer_action.move_to_location(x1,y1)
    fresh_actions.w3c_actions.pointer_action.pointer_down()
    fresh_actions.w3c_actions.pointer_action.move_to_location(x1,y2)
    fresh_actions.w3c_actions.pointer_action.release()
    fresh_actions.perform()
    time.sleep(wait_time)
    print_log("下拉刷新页面",end="-->")
    


def auto(driver,resource_id, info_id,known_xhs_id,res,state,max_fresh_num=8,wait_time=0.5):
    """自动化主要流程"""
    new_valid_num = 0
        
 
    for index in range(4):
        # 每个阶段获取四个博主信息
        if state.get_state():
            # 判断是否被终止
            return False,new_valid_num
        try:
            wrong_step = "获取并点击文章"  # 出现异常的阶段
            articles = driver.find_elements(
                by=AppiumBy.ID, value=resource_id["article"])
            if index >= len(articles):  
                print_log("!w! index>len 可能出现异常")  
                continue
            articles[index].click()
            print_log(f"进入第{index+1}篇文章", end="-->")
            time.sleep(wait_time*2)
            
            
            wrong_step = "滑动进入个人主页"
            swipe_info(driver,res)
            # e2 = driver.find_element(
            #     by=AppiumBy.ID, value=resource_id['avatar'])
            # e2.click()
            time.sleep(wait_time)
            
            wrong_step = "点击更多,保存基本信息"
            try:
                e3 = driver.find_element(
                    by=AppiumBy.ID, value=info_id['des']) # 点击更多
                
                if "更多" in e3.text:
                    rect = e3.rect
                    height = rect['height']
                    width = rect['width']
                    x = rect['x']
                    y = rect['y']
                    locx = x + width / 2
                    locy = y + height - 10
                    locx2 = x + width - 20
                    click_actions = ActionChains(driver)
                    click_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"))
                    click_actions.w3c_actions.pointer_action.move_to_location(locx,locy)
                    click_actions.w3c_actions.pointer_action.click()
                    click_actions.perform()
                    
                    click_actions1 = ActionChains(driver)
                    click_actions1.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"))
                    click_actions1.w3c_actions.pointer_action.move_to_location(locx2,locy)
                    click_actions1.w3c_actions.pointer_action.click()
                    click_actions1.perform()
                    
                    
                    print_log("点击更多",end='-->')
            except:
                print_log("无个人简介",end="-->")

            time.sleep(wait_time)
            get_xml(driver)

     
            # 分析基本信息
            info = analysis_basic_info(info_id,known_xhs_id) #分析xml代码
            if info is not None:
                # 向info添加新的信息
                wrong_step = "向下滑动,获取文章点赞数量"
                likes = [] # 点赞数量的list
                get_xml(driver)
                likes = analysis_likes(likes,info_id['ave'])
                for i in range(2):
                    # 向上滑动两次获取文章点赞量
                    wrong_step = f"滑动第{str(i)}次"
                    swipe_get_article_likes(driver,res)
                    get_xml(driver)
                    likes = analysis_likes(likes,info_id['ave'])
                if len(likes) == 0:
                    print_log("!e! 未获取到点赞数量,检查ID配置")
                    return False,new_valid_num
                ave = int(sum(likes)/len(likes))
                print_log(f'点赞均值{ave}',end="-->")
                info['ave']=ave  # 添加点赞数量的均值

                if save_info(info):
                    # 信息添加
                    new_valid_num += 1
            time.sleep(wait_time)
            wrong_step = "从个人主页返回"
            
            driver.find_element(
                by=AppiumBy.ID, value=resource_id['back1']).click()
            time.sleep(wait_time)
            print_log("返回文章或视频",end="-->")
            wrong_step = "从文章返回首页"
            try:
                driver.find_element(
                    by=AppiumBy.ID, value=resource_id['back2']).click()
            except:
                driver.find_element(
                    by=AppiumBy.ID, value=resource_id['back21']).click()
            print_log("退回主页")
            time.sleep(wait_time)

        except Exception as e:
            
            print_log(f"!w!页面出现异常,错误阶段{wrong_step}")
            print_log(str(e))
            traceback.print_exc()
            get_xml(driver, "xml/wrong.xml")
            return False,new_valid_num

    # if fresh_page(driver,resource_id):
    return True,new_valid_num
    

def swipe_chuanda(driver,res):
    """滑动获取穿搭模块"""
    # 点击一次穿搭模块就会刷新一次

    height = res[0]
    width = res[1]
    x1 = int(width*0.5)
    y1 = int(height*0.5)
    y2 = int(height*0.55)
    # 向下滑动获取action_bar
    get_action_bar_actions = ActionChains(driver)
    get_action_bar_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"),duration=500)
    get_action_bar_actions.w3c_actions.pointer_action.move_to_location(x1,y1)
    get_action_bar_actions.w3c_actions.pointer_action.pointer_down()
    get_action_bar_actions.w3c_actions.pointer_action.move_to_location(x1,y2)
    get_action_bar_actions.w3c_actions.pointer_action.release()
    get_action_bar_actions.perform()
    
    x2 = (width*0.8)
    x3 = (width*0.15)
    y3 = (height*0.12)
    # 向左滑动
    left_swipe_actions = ActionChains(driver)
    left_swipe_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"),duration=500)
    left_swipe_actions.w3c_actions.pointer_action.move_to_location(x2,y3)
    left_swipe_actions.w3c_actions.pointer_action.pointer_down()
    left_swipe_actions.w3c_actions.pointer_action.move_to_location(x3,y3)
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
            break
        except:
            if x == 1:
                print_log("!w!不存在穿搭bar")
            else:
                # get_action_bar_actions.perform()
                left_swipe_actions.perform()
        x += 1
            

def swipe_get_article_likes(driver,res):
    """向上滑动获取文章点赞数"""
    height = res[0]
    width = res[1]
    x1 = int(width*0.3)
    
    y1 = int(height*0.8)
    y2 = int(height*0.28)
    # driver.swipe(x1,y1,x1,y2,duration=1)
    # driver.get_window_size()

    up_actions = ActionChains(driver)
    up_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"),duration=600)
    up_actions.w3c_actions.pointer_action.move_to_location(x1,y1)
    up_actions.w3c_actions.pointer_action.pointer_down()
    up_actions.w3c_actions.pointer_action.move_to_location(x1,y2)
    up_actions.w3c_actions.pointer_action.release()
    up_actions.perform()
    print_log("向下滑动一次",end="-->")

def swipe_info(driver,res):
    """向左滑动进入博主主页"""
    height = res[0]
    width = res[1]
    
    x1 = int(width*0.85)
    x2 = int(width*0.2)
    y1 = int(height*0.09)

    # driver.swipe(x1,y1,x1,y2,duration=1)
    # driver.get_window_size()

    left_actions = ActionChains(driver)
    left_actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput('touch', "touch"),duration=100)
    left_actions.w3c_actions.pointer_action.move_to_location(x1,y1)
    left_actions.w3c_actions.pointer_action.pointer_down()
    left_actions.w3c_actions.pointer_action.move_to_location(x2,y1)
    left_actions.w3c_actions.pointer_action.release()
    left_actions.perform()
    print_log("左滑进入主页",end="-->")


if __name__ == "__main__":
    # swipe
    pass
