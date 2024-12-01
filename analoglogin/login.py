# -*- coding: utf-8 -*-
import getpass

import requests
import time
import sys



class Loginer:
    def __init__(self):
        self.sessions = requests.Session()
        self.cookie = None

    def manual_login(self):
        """手动登录并输入 Cookie"""
        print('请手动登录到系统，并将浏览器中的 Cookie 粘贴到此处：')
        cookie_str = input('请输入 Cookie: ')
        try:
            self.cookie = {k: v for k, v in (x.split('=') for x in cookie_str.split('; '))}
            # 将 cookie 设置到 session 中
            self.sessions.cookies.update(self.cookie)
            print('Cookie 已保存。')
        except Exception as e:
            print('Cookie 格式错误，请检查输入...')
            sys.exit()

    def test_login(self):
        """测试是否登录成功"""
        try:
            url = 'http://202.119.206.41/jwglxt/xtgl/index_initMenu.html'
            response = self.sessions.get(url)

            # 检查登录状态
            if '用户登录' in response.text or '登录超时' in response.text:
                print('登录失败，请检查 Cookie 是否正确或已过期...')
                sys.exit()
            else:
                print('登录成功！')
                return True
        except Exception as e:
            print('登录失败，请检查网络连接...')
            sys.exit()

    def get_session(self):
        return self.sessions

    def get_cookie(self):
        return self.cookie

def logtime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def logging(foo):
    def wrapper(*args, **kwargs):
        print('[+]'+logtime()+' 尝试登录中...')
        start = time.time()
        foo(*args, **kwargs)
        end = time.time()
        duration = end - start
        q = "Good" if duration < 2 else "Normal" if duration < 10 else "Bad"
        print('[+]'+logtime()+' 登录成功!')
        print('[+]'+logtime()+' 登录用时: '+str(duration)[:6]+'s, 网络质量: '+q)
        print('[+]'+logtime()+' 启动线程中...')
    return wrapper

class Grades(Loginer):

    def __init__(self, user, passwd, year="none", term="none"):
        super().__init__(user, passwd)
        self.year = year
        self.term = term
        self.url1 = 'http://202.119.206.41/jwglxt/cjcx/cjcx_cxDgXscj.html?gnmkdm=N305005&layout=default&su='+user        
        self.url2 = 'http://202.119.206.41/jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005'

    def welcome(self):
        try:
            stu_name = self.req_2['items'][0]['xm']
            sch_stu = self.req_2['items'][0]['xslb']
            institute = self.req_2['items'][0]['jgmc']
            classss = self.req_2['items'][0]['bj']
            print('')
            print('')
            print(stu_name+'同学,欢迎您!!!')
            print('')
            print('姓名:{}\t学历:{}\t\t学院:{}\t班级:{}'.format(stu_name,sch_stu,institute,classss))
            print('')
            time.sleep(1)
        except:
            print('无当前学期,请重试')
    def post_gradedata(self):
        try:
            data = {'_search':'false',
                    'nd':int(time.time()),
                    'queryModel.currentPage':'1',
                    'queryModel.showCount':'15',
                    'queryModel.sortName':'',	
                    'queryModel.sortOrder':'asc',
                    'time':'0',
                    'xnm':self.year,
                    'xqm':self.term
                    }
            req_1 = self.sessions.post(self.url1, data = data, headers = self.header)
            req_2 = self.sessions.post(self.url2, data = data, headers = self.header)
            self.req_2 = req_2.json()
        except:
            print('获取失败,请重试...')
            sys.exit()

    def print_geades(self):
        try:
            plt = '{0:{4}<15}\t{1:{4}<6}\t{2:{4}<6}\t{3:{4}<4}' 
            gk = 0
            zkm = 0
            print('')
            print('--------------------------------------------------------------------------------')
            print(plt.format('课程','成绩','绩点','教师',chr(12288)))
            print('--------------------------------------------------------------------------------')
            for i in self.req_2['items']:
                print(plt.format(i['kcmc'], i['bfzcj'], i['jd'], i['jsxm'], chr(12288)))
                if i['bfzcj'] < 60:
                    gk +=1
                zkm += 1
            print('--------------------------------------------------------------------------------')
            print('')
            print('通过科目数:{}{}'.format(zkm-gk, '门'))
            print('挂科科目数:'+str(gk)+'门')
            print('')
            print('')
        except:
            print('无当前学期,请重试')
if __name__ == '__main__':
    print('')
    print('*************************************************************************************')
    print('                            CUMT成绩查询')
    print('')
    print('')
    print('                                                       ————Made By Eddie_Ivan')
    print('*************************************************************************************')
    user = 1
    passwd = 1
    while type(user)!=str or type(passwd)!=str: 
        user = input('请输入学号:').strip()
        passwd = getpass.getpass('请输入密码(密码不回显,输入完回车即可):') .strip()
    cumt_grades = Grades(str(user), str(passwd))
    cumt_grades.get_public()
    cumt_grades.get_csrftoken()
    cumt_grades.post_data()
    while True:
        year = 1
        term = 1        
        while type(year)!=str or type(term)!=str:
            year = input('请输入查询年份(2016-2017即输入2016):').strip()
            term = input('请输入学期(1或2):').strip()
        if term == '1':
            term = '3'
        elif term == '2':
            term = '12'
        else:
            print('输入有误,请重试...')
            sys.exit()
        cumt_grades.year = year
        cumt_grades.term = term
        cumt_grades.post_gradedata()
        cumt_grades.welcome()
        cumt_grades.print_geades()
        status = input('输入c继续查询,输入e退出程序:')
        if status == 'c':
            continue
        elif status == 'e':
            sys.exit()
        else:
            print('输入有误,退出...')
            sys.exit()

