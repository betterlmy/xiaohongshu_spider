import time
import os
import json
import openpyxl

    
def print_log(x,end="\n"):  
    """将日志保存到log文件夹下

    Args:
        x (str): 要打印的字符串
        now_time (str): 以日期为文件名
        end (str, optional): 结尾符. Defaults to "\n".
    """
    with open("tmp/.nowtime","r") as f:
        global now_time
        now_time = f.read()
    
    end = "  "+time.strftime("%H:%M:%S", time.localtime()
                             ) + end if end == "\n" else end
    date = time.strftime('%m-%d', time.localtime())+"/"
    if not os.path.exists("log/"+date):
        os.makedirs("log/"+date)

    with open("log/"+date+now_time+".log", "a+", encoding="utf-8") as f:
        f.write(str(x)+end)

    print(str(x), end=end)

def load_config(file="config.json"):
    """加载配置文件"""
    
    if not os.path.exists(file):
        print_log("config文件不存在")
        return None
    try:
        with open(file, 'r') as f:
            config = json.load(f)
    except:
        print_log("!e! 转换错误")
        return None

    if 'appium:noReset' in config['cap'].keys():
        # boolean类型转换
        config['cap']['appium:noReset'] = True if config['cap']['appium:noReset'] == 'True' or 'true' else False
    return config

def analysis_info(info_id,xml="xml/info.xml"):
    """解析xml文件中的信息"""
    #因为数据量不大,采用逐行匹配,而非xml树形解析

    info: dict[str, str] = {
    }
    with open(xml, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        for info_name, ids in info_id.items():
            if ids in line:
                padding = 6 if ids != info_id['xhs_id'] else 11  # 小红书id字段特殊处理
                start_num = line.find("text=\"") + padding
                end_num = line.find("\"", start_num)
                para = line[start_num:end_num]
                info[info_name] = para
                break
    if len(info) < 2:
        print_log("!e!未获取到博主信息,建议检查config文件")
        return None
    else:
        print_log("个人信息解析完成", end="-->")
        return info

def save_excel(info_list,known_xhs_id, file="output/info.xlsx"):
    """将用户写入到excel中,并更新已知id"""
    columns_map = {
        'name_id': '用户名',
        'xhs_id': '小红书id',
        'des': '个人简介',
        'fans_num': '粉丝数',
        'all_likes_num': '点赞数',
        # 'article_likes_num': '前两篇点赞数',
    }
    if not os.path.exists("output/"):
        os.mkdir("output")
        print("output文件夹不存在,已自动创建")

    # 每日创建新的Sheet
    try:
        wb = openpyxl.load_workbook(file)
        print_log("已加载info.xlsx", end="-->")
    except:
        print_log("excel文件读取失败")

    date = time.strftime("%m-%d", time.localtime())
    if date not in wb.sheetnames:
        ws = wb.create_sheet(date, 0)
        print_log("新创建工作表", "-->")
        ws.append([v for _, v in columns_map.items()])

    # 激活当前的sheet
    wb.active = wb[date]
    ws = wb.active
    for info in info_list:
        meet = True  # 判断当前博主是否满足条件
        person_list = []  # 存放用户信息

        for k, _ in columns_map.items():
            if k in info.keys():
                # 添加异常判断
                person_list.append(info[k])
            else:
                meet = False
                break

        if not meet:
            continue

        try:
            fans_num = int(person_list[3]) # 粉丝数
            xhs_id = person_list[1] # 小红书id    
            if fans_num < 100:
                # 添加粉丝数等限制
                print_log("!w! 粉丝数不满足要求",end="")
                continue
            
            elif xhs_id in known_xhs_id:
                print_log("!w! 该用户已经存在",end="") 
            else:
                known_xhs_id.append(xhs_id)
                
        except:
            print_log("!w! 转换异常",end="")
            continue
        
        ws.append(person_list)

    wb.save("output/info.xlsx")
    print_log("新数据已保存至output/info.xlsx")
    return known_xhs_id