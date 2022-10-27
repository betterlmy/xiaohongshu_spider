from GUI import GUI_start, GUI_running, GUI_warning
from utils import load_count, print_log, load_known_id, update_count, update_known_id, load_count
from automation import init_driver, auto, fresh_page, swipe_chuanda
import threading
import sys
"""
    1. 小红书的控件id竟然会变化!!!!
    2. 真恶心
    3. !w! 表示warning. 出现提示
    4. !e! 表示error.   出现程序错误
"""


class State():
    """状态类 绑定进程,判断程序状态"""

    def __init__(self):
        self.stopped = False

    def stop(self):
        self.stopped = True

    def start(self):
        self.stopped = False

    def get_state(self):
        return self.stopped


class AutoThread(threading.Thread):
    def __init__(self, driver, config, max_erreor_num, wait_time, res, chuanda, state):
        threading.Thread.__init__(self)
        self.driver = driver
        self.config = config
        self.max_erreor_num = max_erreor_num
        self.res = res
        self.wait_time = wait_time
        self.chuanda = chuanda
        self.state = state

    def run(self):
        # 运行的主程序
        resource_id = self.config['resource_id']
        info_id = self.config['info_id']
        error_num = 0
        plan_num = 9999999  # 计划获取的轮数
        times = 0  # 当前已经查询的数据量
        all_count, valid_count = load_count()

        if self.chuanda:
            print_log("进入穿搭模式", end="-->")
            resource_id['article'] = resource_id['chuanda_article']
            swipe_chuanda(self.driver, self.res)
        else:
            print_log("进入推荐模式", end="-->")
            resource_id['article'] = resource_id['tuijian_article']

        print_log(resource_id['article'])

        while times < plan_num:
            known_xhs_id = load_known_id()
            success, new_valid_num = auto(self.driver, resource_id=resource_id, info_id=info_id,
                                                        known_xhs_id=known_xhs_id, res=self.res, state=self.state, max_fresh_num=8, wait_time=self.wait_time)
            if not success:
                error_num += 1
                if self.state.get_state():
                    print_log(f"程序手动停止", end="-->")
                    break
                elif error_num >= self.max_erreor_num:
                    print_log("!e!程序连续多次出现异常,退出程序")
                    GUI_warning("error", "程序连续多次出现异常,请检查网络或其他配置后重启")
                    break
                print_log(f"!w!程序出现异常,连续异常次数{error_num},重新开始执行")
                self.driver = init_driver(
                    config['appium_server_config'], config['cap'])
                
                if self.chuanda:
                    print_log("进入穿搭模式", end="-->")
                    resource_id['article'] = resource_id['chuanda_article']
                    swipe_chuanda(self.driver, self.res)
            else:
                error_num = 0
                times += 1
                all_count += 4
                valid_count += new_valid_num
                # if len(info_list) > 0:  # 每四次写入excel一次
                #     save_excel(info_list)
                #     valid_count += len(info_list)
                #     info_list = [] # 清空info_list
                # else:
                #     print_log("!e!无新数据可以保存")

                print_log(
                    f"本次运行已获取{times*4}次数据,总数据量{all_count},有效数据量{valid_count}")
                update_count(all_count, valid_count)
                fresh_page(self.driver, self.res, self.wait_time)

        print_log(f"程序运行结束,时间:")


if __name__ == '__main__':
    now_time, config, running_config, final_window = GUI_start()  # GUI界面参数配置

    driver = init_driver(config['appium_server_config'], config['cap'])
    if driver is None:
        GUI_warning("error", "检查appium服务是否启动(Appium Server GUI)")
        sys.exit()
    state = State()
    t1 = AutoThread(driver, config, running_config['max_error_time'],
                    running_config['wait_time'], running_config['res'], running_config['chuanda'], state)

    t1.start()

    GUI_running(t1, final_window, state)
