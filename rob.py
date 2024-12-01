import threading
import json
import time
import requests
import datetime
import re

from analoglogin.login import Loginer
from bs4 import BeautifulSoup
from os import _exit


THREAD_FLAG = True
MAX_PROCESS = 4

def logging(foo):
    def wrapper(*args, **kwargs):
        print('[+]'+logtime()+' 尝试登录中...')
        start = time.time()
        foo(*args, **kwargs)
        end = time.time()
        duration = end - start
        q = ""
        if duration < 2:
            q = "Good"
        elif duration > 2 and duration < 10:
            q = "Normal"
        else:
            q = "Bad"
        print('[+]'+logtime()+' 登录成功!')
        print('[+]'+logtime()+' 登录用时: '+str(duration)[:6]+'s, 网络质量: '+q)
        print('[+]'+logtime()+' 启动线程中...')
    return wrapper

logtime = lambda: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())    

current_month = lambda: datetime.datetime.now().month


class Rob_Lessons(Loginer):
    def __init__(self, lesson_id=None):
        super().__init__()
        self.lesson_id = lesson_id
        self.user = None
        self.kcmc = None
        self.rob_data = None
        self.thread = []

        # 初始化基础请求头
        self.header_1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': '202.119.206.41',
            'Referer': 'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'
        }

        # 执行登录
        self.manual_login()
        if self.test_login():
            self.get_user_from_cookie()

    def get_user_from_cookie(self):
        """从 cookie 中获取用户 ID"""
        if self.cookie:
            # 从cookie中提取用户ID，根据实际cookie结构调整
            for key, value in self.cookie.items():
                if 'user' in key.lower():
                    self.user = value
                    return
        if not self.user:
            print('[!]' + logtime() + ' 未能从cookie中获取用户ID')
            _exit(-1)

    def lessons_info(self):
        if not self.user:
            print('[!]' + logtime() + ' 用户未登录')
            _exit(-1)

        self.header_2 = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'jwxt.cumt.edu.cn',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Referer': f'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su={self.user}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'X-Requested-With': 'XMLHttpRequest'
        }

        print('[+]' + logtime() + ' 尝试获取课程信息...')

        # 构建URL
        base_url = 'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb'
        urls = {
            'index': f'{base_url}_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su={self.user}',
            'search': f'{base_url}_cxZzxkYzbPartDisplay.html?gnmkdm=N253512&su={self.user}',
            'choose': f'{base_url}_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512&su={self.user}',
            'rob': f'{base_url}_xkBcZyZzxkYzb.html?gnmkdm=N253512&su={self.user}'
        }

        response = self.sessions.get(urls['index'], headers=self.header_1)

        if "当前不属于选课阶段" in response.text:
            print('[!]' + logtime() + ' 未到选课时间')
            _exit(-1)

        # 使用原始字符串避免转义问题
        try:
            pattern = r'onclick="queryCourse\(this,\'10\',\'([0-9A-F]{32})\'\)" role="tab" data-toggle="tab">通识选修课'
            xkkz = re.findall(pattern, response.text)[0]
        except:
            soup = BeautifulSoup(response.text, "html.parser")
            xkkz_elem = soup.find('input', {
                'type': "hidden",
                'name': "firstXkkzId",
                'id': "firstXkkzId"
            })
            if not xkkz_elem:
                print('[!]' + logtime() + ' 未能获取选课控制码')
                _exit(-1)
            xkkz = xkkz_elem['value']

        # 构建查询数据
        data = {
            'bh_id': '161031108',
            'bklx_id': '0',
            'ccdm': '3',
            'filter_list[0]': self.lesson_id,
            'jg_id': '03',
            'jspage': '10',
            'kkbk': '0',
            'kkbkdj': '0',
            'kklxdm': '10',
            'kspage': '1',
            'njdm_id': '2016',
            'njdmzyh': ' ',
            'rwlx': '2',
            'sfkcfx': '0',
            'sfkgbcx': '0',
            'sfkknj': '0',
            'sfkkzy': '0',
            'sfkxq': '0',
            'sfrxtgkcxd': '1',
            'sfznkx': '0',
            'tykczgxdcs': '10',
            'xbm': '1',
            'xh_id': self.user,
            'xkly': '0',
            'xkxnm': '2018',
            'xkxqm': '3' if current_month() > 5 and current_month() < 8 else '12',
            'xqh_id': '2',
            'xsbj': '4294967296',
            'xslbdm': '421',
            'zdkxms': '0',
            'zyfx_id': 'wfx',
            'zyh_id': '0311'
        }

        # 获取课程信息
        search_result = self.sessions.post(urls['search'], data=data, headers=self.header_2).json()

        try:
            course = search_result['tmpList'][0]
            self.kcmc = course['kcmc']

            # 构建抢课数据
            self.rob_data = {
                'cxbj': '0',
                'jxb_ids': course['jxb_id'],
                'kch_id': course['kch_id'],
                'kcmc': f'({self.lesson_id}){course["kcmc"]}+-+{course["xf"]}学分',
                'kklxdm': '10',
                'njdm_id': '2016',
                'qz': '0',
                'rlkz': '1',
                'rlzlkz': '0',
                'rwlx': '2',
                'sxbj': '1',
                'xkkz_id': xkkz,
                'xklc': '1',
                'xkxnm': '2018',
                'xkxqm': '3' if current_month() > 5 and current_month() < 8 else '12',
                'xsbxfs': '0',
                'xxkbj': '0',
                'zyh_id': '0311'
            }
            print('[+]' + logtime() + ' 课程信息获取成功!')
        except (KeyError, IndexError):
            print('[!]' + logtime() + ' 未找到课程信息')
            _exit(-1)

    def lessons(self, no):
        global THREAD_FLAG
        url = f'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_xkBcZyZzxkYzb.html?gnmkdm=N253512&su={self.user}'
        print('[+]' + logtime() + f' Thread-{no} Start')

        while THREAD_FLAG:
            try:
                response = self.sessions.post(url, data=self.rob_data, headers=self.header_2, timeout=5)

                if len(response.text) > 10000:
                    print('[!]' + logtime() + ' 会话已过期，正在重新登录...')
                    with open('relogin.txt', 'a') as logger:
                        logger.write(logtime() + ' relogin\n')
                    self.manual_login()
                    continue

                print('[*]' + logtime() + f' Thread-{no} 请求成功')

                result = response.json()
                if result.get('flag') != '1':
                    print('[*]' + logtime() + f' 异常状态码: {result.get("msg", "未知错误")}')
                    continue

                print(f'[*]{logtime()} Thread-{no} Success!')
                print(f'[*]{logtime()} {self.kcmc} 抢课成功!')
                print(f'[+]{logtime()} 程序即将退出...')
                THREAD_FLAG = False
                break

            except KeyboardInterrupt:
                os._exit(-1)
            except Exception as e:
                print(f'[*]{logtime()} Thread-{no} Fail: {str(e)}')

        print(f'[+]{logtime()} Thread-{no} Close')

    def generate_thread(self, count):
        self.thread = [
            threading.Thread(target=self.lessons, args=(str(i + 1),))
            for i in range(count)
        ]

    def rob_it(self, count):
        """开始抢课"""
        self.lessons_info()  # 获取课程信息
        self.generate_thread(count)  # 生成线程

        # 启动所有线程
        for thread in self.thread:
            thread.start()

        # 等待所有线程结束
        for thread in self.thread:
            thread.join()
def get_config():
    try:
        with open('config.json', 'r') as conf:
            data = json.load(conf)
            # 只需要课程ID
            return data.get('lesson_id', '').strip()
    except FileNotFoundError:
        print('[*]Error')
        print('[*]请检查配置文件config.json')
        _exit(-1)

def banner():
    print('')
    print(" _                                                 _              _             ___          ")
    print("|_)   _   |_     |    _    _   _   _   ._    _    |_   _   ._    /   | |  |\/|   |    _   ._ ")
    print("| \  (_)  |_)    |_  (/_  _>  _>  (_)  | |  _>    |   (_)  |     \_  |_|  |  |   |   (/_  |  ")
    print('')
    print('')
    print('[+]Made By EddieIvan，Improved By yuebaiv ')
    print('[+]Github: https://github.com/yuebaiv')
    print('')

if __name__ == '__main__':
    MAX_PROCESS = 5  # 可以根据需要修改线程数

    banner()
    lesson_id = get_config()

    # 创建抢课实例，只传入课程ID
    Robber = Rob_Lessons(lesson_id=lesson_id)

    # 开始抢课
    Robber.rob_it(MAX_PROCESS)
