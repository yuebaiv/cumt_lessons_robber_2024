"""
Asynchronous versions
Use `asyncio` and `aiohttp` libs
It has better performance with fewer system resource
"""

import json
import time
import requests
import asyncio
import aiohttp
import re
import datetime

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
    
    def __init__(self, user, passwd, lesson_id):
        super().__init__(user, passwd)
        self.lesson_id = lesson_id
        self.header_1 = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',	
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded',
            'Host':'202.119.206.62',
            'Referer':'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su='+self.user,
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'	
        }        
               
    def lessons_info(self):
        self.header_2 = {
            'Accept':'application/json, text/javascript, */*; q=0.01',	
            'Accept-Encoding':'gzip, deflate',
            'Host':'jwxt.cumt.edu.cn',
            'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded;charset=utf-8',
            'Referer':'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su='+self.user,
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'X-Requested-With':	'XMLHttpRequest',
            'Cookie':self.cookie
        }                 
        print('[+]'+logtime()+' 尝试获取课程信息...')
        try:
            index_url = 'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su='+self.user
            search_url = 'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512&su='+self.user
            choose_url = 'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512&su='+self.user
            rob_url = 'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_xkBcZyZzxkYzb.html?gnmkdm=N253512&su='+self.user
            response = self.sessions.get(index_url, headers=self.header_1)
            if "当前不属于选课阶段" in response.text:
                print('[!]'+logtime()+' 未到选课时间')
                _exit(-1)
            try:
                xkkz = re.findall("onclick=\"queryCourse\(this,'10','([0-9A-F]{32})'\)\" role=\"tab\" data-toggle=\"tab\">通识选修课", 
                    response.text)[0]
            except:
                text = BeautifulSoup(response.text, "html.parser")
                xkkz = text.findAll(name='input', 
                        attrs={
                            'type':"hidden",
                            'name':"firstXkkzId",
                             'id':"firstXkkzId"
                        })[0].attrs['value']
            data = {
                'bh_id':'151084001',  
                'bklx_id':'0',
                'ccdm':'3',
                'filter_list[0]':self.lesson_id,
                'jg_id':'08', 
                'jspage':'10',
                'kkbk':'0',
                'kkbkdj':'0',
                'kklxdm':'10',
                'kspage':'1',
                'njdm_id':'2015', 
                'njdmzyh':' ',
                'rwlx':'2',
                'sfkcfx':'0',
                'sfkgbcx':'0',
                'sfkknj':'0',
                'sfkkzy':'0',
                'sfkxq':'0',
                'sfrxtgkcxd':'1',
                'sfznkx':'0',
                'tykczgxdcs':'10',
                'xbm':'1',
                'xh_id':self.user,
                'xkly':'0',
                'xkxnm':'2018',
                'xkxqm':'3' if current_month() > 5 and current_month() < 8 else '12',
                'xqh_id':'2',
                'xsbj':'4294967296',
                'xslbdm':'421',
                'zdkxms':'0',
                'zyfx_id':'wfx',
                'zyh_id':'0311'         
            }
            search_result = requests.post(search_url, data=data, 
                                          headers=self.header_2).json()
            kch = search_result['tmpList'][0]['kch_id']
            jxb = search_result['tmpList'][0]['jxb_id']
            kcmc = search_result['tmpList'][0]['kcmc']
            self.kcmc = kcmc
            xf = search_result['tmpList'][0]['xf']
            self.rob_data = {
                'cxbj':'0',
                'jxb_ids':jxb,
                'kch_id':kch,
                'kcmc':'('+self.lesson_id+')'+kcmc+'+-+'+xf+'学分',
                'kklxdm':'10',
                'njdm_id':'2017',
                'qz':'0',
                'rlkz':'1',
                'rlzlkz':'0',
                'rwlx':'2',
                'sxbj':'1',
                'xkkz_id':xkkz,
                'xklc':'1',
                'xkxnm':'2018',
                'xkxqm':'3' if current_month() > 5 and current_month() < 8 else '12',
                'xsbxfs':'0',
                'xxkbj':'0',
                'zyh_id':'0311'        
            }
            print('[+]'+logtime()+' 课程信息获取成功!')
        except:
            print('[+]'+logtime()+' 获取失败，请查验课程代号')
            _exit(-1)
                    
    def _get_csrftoken(self):                   
        url = 'http://202.119.206.62/jwglxt/xtgl/login_slogin.html?language=zh_CN&_t=' + str(self.time)
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        self.token = soup.find('input', attrs={'id':'csrftoken'}).attrs['value'] 
             
    async def lessons(self, no):
        global THREAD_FLAG
        url = 'http://jwxt.cumt.edu.cn/jwglxt/xsxk/zzxkyzb_xkBcZyZzxkYzb.html?gnmkdm=N253512&su=' + self.user
        print('[+]'+logtime()+' Coroutine-'+no+' Start')
        async with aiohttp.ClientSession(headers=self.header_2, 
                                         cookies=self.login_cookies) as session:
            while THREAD_FLAG:
                try:
                    async with session.post(url, data=self.rob_data, 
                                            timeout=5) as resp:
                        data = await resp.json()
                        print('[*]'+logtime()+' Coroutine-'+no+'  请求成功')
                        if data['flag'] != '1':
                            #print('[*]'+logtime()+' Coroutine-'+no+'  异常!')
                            print('[*]'+logtime()+' 异常状态码: '+data['msg'])
                            raise Exception
                        print('[*]'+logtime()+' Coroutine-'+no+'  Success!')
                        print('[*]'+logtime()+' '+self.kcmc+'  抢课成功!')
                        print('[+]'+logtime()+' 程序即将退出...')
                        THREAD_FLAG = False
                except KeyboardInterrupt:
                    os._exit(-1)
                except aiohttp.client_exceptions.ContentTypeError as e:
                    with open('relogin.txt', 'a') as logger:
                        logger.write(logtime()+' relogin\n')
                    self.login_us()                    
                except:
                    print('[*]'+logtime()+' Coroutine-'+no+'  Fail')
        print('[+]'+logtime()+' Coroutine-'+no+' Close')
      
    @logging
    def login_us(self):
        self.reflush_time()
        self.get_public()
        self.get_csrftoken()
        self.post_data()
        self.login_cookies = dict(self.sessions.cookies.items())
        
    def init(self):
        self.login_us()
        self.lessons_info()


def get_config():
    try:
        with open('config.json', 'r') as conf:
            data = json.load(conf)
            return (data['user'].strip(), data['passwd'].strip(), 
                    data['lesson_id'].strip())
    except FileNotFoundError:
        print('[*]Error')
        print('[*]请检查配置文件config.json')
        _exit()

def banner():
    print('')
    print(" _                                                 _              _             ___          ")
    print("|_)   _   |_     |    _    _   _   _   ._    _    |_   _   ._    /   | |  |\/|   |    _   ._ ")
    print("| \  (_)  |_)    |_  (/_  _>  _>  (_)  | |  _>    |   (_)  |     \_  |_|  |  |   |   (/_  |  ")
    print('')
    print('')
    print('[+]Made By EddieIvan')
    print('[+]Github: http://github.com/eddieivan01')
    print('')
    
    
if __name__ == '__main__':
    banner()
    user_config = get_config()
    Robber = Rob_Lessons(*user_config)
    Robber.init()
    loop = asyncio.get_event_loop()
    tasks = []
    for i in range(MAX_PROCESS):
        tasks.append(asyncio.ensure_future(Robber.lessons(str(i))))
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()
