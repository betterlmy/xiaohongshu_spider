from GUI import GUI_start,GUI_running
from utils import print_log,save_excel
from automation import init_driver, pass_ad, fresh_page, auto
import threading
"""
    1. 小红书的控件id竟然会变化!!!!
    2. 真恶心
    3. !w! 表示warning. 出现提示
    4. !e! 表示error.   出现程序错误
    5. 仍需要完成的任务: 邮箱过滤
"""

class autoThread(threading.Thread):
    def __init__(self,driver,config,known_xhs_id):
        threading.Thread.__init__(self)
        self.stopped = False
        self.driver = driver
        self.config = config
        self.known_xhs_id = known_xhs_id

        
    def stop(self):
        self.stopped = True
        
    def run(self):
        resource_id = self.config['resource_id']
        info_id = self.config['info_id']
        info_list=[]
        error_num = 0
        max_erreor_num = 1
        plan_num = 400  # 计划获取的轮数
        times = 0  # 当前已经查询的数据量

        while times < plan_num:
            if self.stopped:
                print_log(f"程序手动停止",end="")
                break
            success,info_list = auto(self.driver, resource_id=resource_id, info_id=info_id, info_list=info_list,max_fresh_num=8, wait_time=wait_time)
            if not success:
                print_log(f"!e!程序出现异常,连续异常次数{error_num},重新开始执行")
                error_num += 1
                if error_num >= max_erreor_num:
                    print_log("!e!程序连续多次出现异常,退出程序")
                    break
                self.driver = init_driver(config['appium_server_config'], config['cap'])

            else:
                error_num = 0
                times += 1  
                if len(info_list) > 0:  # 每四次写入excel一次
                    self.known_xhs_id = save_excel(info_list,self.known_xhs_id)
                    info_list = []
                else:
                    print_log("!e!无新数据可以保存")

            try:
                with open("output/known_id.txt", "w", encoding="utf-8") as f:
                    for id in self.known_xhs_id:
                        f.write(str(id)+"\n")
                print_log("known_id.txt已更新",end="-->")
            except:
                print_log("!e! known_id.txt写入失败")

        print_log(f"程序运行结束,时间:")
        


if __name__ == '__main__':
    now_time, config, wait_time = GUI_start()  # GUI界面参数配置

    with open('output/known_id.txt', "r", encoding='utf-8') as f:
        known_xhs_id = [line.strip("\n") for line in f.readlines()]

    driver = init_driver(config['appium_server_config'], config['cap'])

    t1 = autoThread(driver,config,known_xhs_id)
    t1.start()
    GUI_running(t1)
    
    

    
    
