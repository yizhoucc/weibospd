import re
import requests
from bs4 import BeautifulSoup
def printHeaders(headers):
    for h in headers:
        print(h+" : "+headers[h] + '\r\n')

def printCookies(cookies):
    for h in cookies:
        print(h+" : "+cookies[h] + '\r\n')

def loginFw(id,password):
    url = "http://xxxxx/login.asp" 
    try:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                   'Host':'www.xxx.org',
                   'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept-Encoding':'gzip, deflate',
                   'Content-Type':'application/x-www-form-urlencoded',
                   'Referer':'http://xxx/login.asp',
                   'Connection':'keep-alive',
                   }
        params = {"Reglname":id,"reglpassword":password}
        r = requests.post(url,data=params,headers=headers)
        printHeaders(r.request.headers) #服务器返回的cookie需要用r.request里的headers来获取
        printHeaders(r.headers) #这里是获取不到服务器返回的cookie的

        r.encoding = 'utf-8'

        return r.text
    except Exception as e:
        print("登陆错误："+str(e))




ret = loginFw("244551766@qq.com","Apple123")
#print(ret)