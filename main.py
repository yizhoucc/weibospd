# _*_ coding: utf-8 _*_

import re
import rsa
import time
import json
import base64
import logging
import binascii
import requests
import urllib.parse
from lxml import etree
from bs4 import BeautifulSoup
import os
import urllib
import urllib3
import base64
import requests
import re
import rsa
import binascii
from urllib.request import urlopen


class WeiBoLogin(object):
    """
    class of WeiBoLogin, to login weibo.com
    """

    def __init__(self):
        """
        constructor
        """
        self.user_name = None
        self.pass_word = None
        self.user_uniqueid = None
        self.user_nick = None

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"})
        self.session.get("http://weibo.com/login.php")
        return

    def login(self, user_name, pass_word):
        """
        login weibo.com, return True or False
        """
        self.user_name = user_name
        self.pass_word = pass_word
        self.user_uniqueid = None
        self.user_nick = None

        # get json data
        s_user_name = self.get_username()
        json_data = self.get_json_data(su_value=s_user_name)
        if not json_data:
            return False
        s_pass_word = self.get_password(json_data["servertime"], json_data["nonce"], json_data["pubkey"])

        # make post_data
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "userticket": "1",
            "vsnf": "1",
            "service": "miniblog",
            "encoding": "UTF-8",
            "pwencode": "rsa2",
            "sr": "1280*800",
            "prelt": "529",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "rsakv": json_data["rsakv"],
            "servertime": json_data["servertime"],
            "nonce": json_data["nonce"],
            "su": s_user_name,
            "sp": s_pass_word,
            "returntype": "TEXT",
        }

        # get captcha code
        if json_data["showpin"] == 1:
            url = "http://login.sina.com.cn/cgi/pin.php?r=%d&s=0&p=%s" % (int(time.time()), json_data["pcid"])
            with open("captcha.jpeg", "wb") as file_out:
                file_out.write(self.session.get(url).content)
            code = input("请输入验证码:")
            post_data["pcid"] = json_data["pcid"]
            post_data["door"] = code

        # login weibo.com
        login_url_1 = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)&_=%d" % int(time.time())
        json_data_1 = self.session.post(login_url_1, data=post_data).json()
        if json_data_1["retcode"] == "0":
            params = {
                "callback": "sinaSSOController.callbackLoginStatus",
                "client": "ssologin.js(v1.4.18)",
                "ticket": json_data_1["ticket"],
                "ssosavestate": int(time.time()),
                "_": int(time.time()*1000),
            }
            response = self.session.get("https://passport.weibo.com/wbsso/login", params=params)
            json_data_2 = json.loads(re.search(r"\((?P<result>.*)\)", response.text).group("result"))
            if json_data_2["result"] is True:
                self.user_uniqueid = json_data_2["userinfo"]["uniqueid"]
                self.user_nick = json_data_2["userinfo"]["displayname"]
                logging.warning("WeiBoLogin succeed: %s", json_data_2)
            else:
                logging.warning("WeiBoLogin failed: %s", json_data_2)
        else:
            logging.warning("WeiBoLogin failed: %s", json_data_1)
        return True if self.user_uniqueid and self.user_nick else False

    def get_username(self):
        """
        get legal username
        """
        username_quote = urllib.parse.quote_plus(self.user_name)
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))
        return username_base64.decode("utf-8")

    def get_json_data(self, su_value):
        """
        get the value of "servertime", "nonce", "pubkey", "rsakv" and "showpin", etc
        """
        params = {
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallBack",
            "rsakt": "mod",
            "checkpin": "1",
            "client": "ssologin.js(v1.4.18)",
            "su": su_value,
            "_": int(time.time()*1000),
        }
        try:
            response = self.session.get("http://login.sina.com.cn/sso/prelogin.php", params=params)
            json_data = json.loads(re.search(r"\((?P<data>.*)\)", response.text).group("data"))
        except Exception as excep:
            json_data = {}
            logging.error("WeiBoLogin get_json_data error: %s", excep)

        logging.debug("WeiBoLogin get_json_data: %s", json_data)
        return json_data

    def get_password(self, servertime, nonce, pubkey):
        """
        get legal password
        """
        string = (str(servertime) + "\t" + str(nonce) + "\n" + str(self.pass_word)).encode("utf-8")
        public_key = rsa.PublicKey(int(pubkey, 16), int("10001", 16))
        password = rsa.encrypt(string, public_key)
        password = binascii.b2a_hex(password)
        return password.decode()

    cookies = []

    cookies = []

    def getCookies(weibo):
        """ 获取Cookies """

        loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        for elem in weibo:
            account = elem['no']
            password = elem['psw']
            username = base64.b64encode(account.encode('utf-8')).decode('utf-8')
            postData = {
                "entry": "sso",
                "gateway": "1",
                "from": "null",
                "savestate": "30",
                "useticket": "0",
                "pagerefer": "",
                "vsnf": "1",
                "su": username,
                "service": "sso",
                "sp": password,
                "sr": "1440*900",
                "encoding": "UTF-8",
                "cdult": "3",
                "domain": "sina.com.cn",
                "prelt": "0",
                "returntype": "TEXT",
            }
            session = requests.Session()
            r = session.post(loginURL, data=postData)
            jsonStr = r.content.decode('gbk')
            # print 'jsonStr=',jsonStr
            info = json.loads(jsonStr)
            # print 'info=',info
            if info["retcode"] == "0":
                print
                "Get Cookie Success!( Account:%s )" % account
                cookie = session.cookies.get_dict()
                cookies.append(cookie)
            else:
                print
                "Failed!( Reason:%s )" % info['reason']
        return cookies


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s\t%(message)s")
    weibo = WeiBoLogin()
    a=weibo.login("244551766@qq.com", "Apple123123")
    cookie={'Cookie':"_s_tentry=-; Apache=7615506666458.845.1528531819767; SINAGLOBAL=7615506666458.845.1528531819767; ULV=1528531819793:1:1:1:7615506666458.845.1528531819767:; login_sid_t=7b940ebf39b779804c6d479b34dc6f50; cross_origin_proto=SSL; UM_distinctid=164124342fd316-061f7901efbca3-47e1137-1fa400-164124342ff864; UOR=,,login.sina.com.cn; SSOLoginState=1531548085; wvr=6; USRANIME=usrmdinst_19; ALF=1566029059; SCF=AsMkHBLL9rpUO3tScCK0o8vALSWmymyIo1nbszn8YUlr5OqCOH40Fpye_2l-jbB3-oFLt9CiDIBdS2XcyiaJjqw.; SUB=_2A252cvHcDeRhGeVL4loS-S7FwjmIHXVVBmQUrDV8PUNbmtBeLXX7kW9NT-ByOn0Gb6cW1qOoG9Bq3qYJ4SV3paRJ; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5hxHCBzc_jbo0AkCE60Mg95JpX5KzhUgL.Foef1Kn01K541K-2dJLoIEXLxKqL1K-L1K.LxK-L122LBK2LxKnLBoMLB-qLxKML1h.L12eLxKML1-eL12zt; SUHB=0gHyaqpsCMTGLd"}
#     header={Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
# Accept-Encoding: gzip, deflate, br
# Accept-Language: en-US,en;q=0.9,zh;q=0.8
# Connection: keep-alive
# Cookie: WEIBOCN_WM=3333_2001; _T_WM=d4ae212bf38827f4f4cc1dab1ac91feb; ALF=1537085064; SCF=AsMkHBLL9rpUO3tScCK0o8vALSWmymyIo1nbszn8YUlrV__CUjMeDIfhB3mRLu9bV02CbqcL7ZVLd9EJuZ5vO8Q.; SUB=_2A252cvGXDeRhGeVL4loS-S7FwjmIHXVVnJ_frDV6PUJbktAKLW_skW1NT-ByOn_QZJabyGCB8xoGvEMtkm_HUqit; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5hxHCBzc_jbo0AkCE60Mg95JpX5K-hUgL.Foef1Kn01K541K-2dJLoIEXLxKqL1K-L1K.LxK-L122LBK2LxKnLBoMLB-qLxKML1h.L12eLxKML1-eL12zt; SUHB=06ZVKvLMkWrng4; SSOLoginState=1534493127
# Host: weibo.cn
# Referer: https://weibo.cn/comment/GsDFCfRhi?uid=6315899738&rl=0
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36}

    urllist_set = []
    word_count = 1
    image_count = 1
    print(u'ready, run!')


    url="https://weibo.cn/comment/GsDFCfRhi?uid=6315899738&rl=0&page=1"
    html = requests.get(url,cookies=cookie).content
    # selector = etree.HTML(html)
    # pageNum = (int)(selector.xpath(u'//input[@name="mp"]')[0].attrib['value'])
    # result = ""  # 储存数据备用


for page in range(1,4228+1):
    url=('https://weibo.cn/comment/GsDFCfRhi?uid=6315899738&rl=0&page=%d' % page)
    # lxml=requests.get(url).content
    time.sleep(1)
    a = weibo.login("244551766@qq.com", "Apple123123")
    time.sleep(1)
    # response = urlopen(url)
    # actual=response.geturl()  # 'http://stackoverflow.com/'
    # if actual != url:
    #     print('lost connection')
    #     time.sleep(2)
    #     a = weibo.login("244551766@qq.com", "Apple123123")
    #     print('reconnectiong')
    #     time.sleep(1)
    #     # code = requests.get(url, cookies=cookie).status_code
    #     # if code !=200:
    #     #     print ('fail for 2nd time, stop')
    #     #     break
    markup=requests.get(url,cookies=cookie).content
    cookie = requests.get(url,cookies=cookie).cookies
    # lhtml = html.fromstring(lxml)
    # selector = etree.HTML(lxml)
    # content = selector.xpath('//span[@class="ctt"]')

    # soup = BeautifulSoup(lxml, "lxml")
    soup = BeautifulSoup(markup, "html.parser")
    urllist = soup.find_all(href=re.compile("weibo.cn/sinaurl"))
    print('page',page,url)

    # response = urllib.request.urlopen(url)
    # if response.getcode() == 200:
    #     print('Bingo')
###
    # thislink = urllist[0].get('href', None)
    # print (thislink)
    # allpage = requests.get(thislink, cookies=cookie).content
    # soup = BeautifulSoup(allpage, "html.parser")
    # imglink = soup.find_all(href=re.compile("img"))
    # imag = imglink[0].get('href', None)
    #
    # temp = '1.jpg'
    # print(u'正在下载第%s张图片')
    # try:
    #     urllib.request.urlretrieve(urllib.request.urlopen(imag).geturl(), temp)
    # except:
    #     print(u'图片下载失败：%s')

####
    try:
        for x in range(len(urllist)):
            urllist_set.append(urllist[x])
            print('pic',x)
            if len(urllist)==0:
                time.sleep(1)

                print('no pic in this page')

    except:
        print('some error')
    time.sleep(3)
print('url list ready, to link list')

theset=set()

for imgurl in urllist_set:
    thislink=imgurl[0].get('href',None)

    # urllist_set.add(requests.get(imgurl[0]).url)
    theset.add(thislink)

    image_count += 1
    print(image_count)
# link = ""
# fo2 = open("/Users/wanghuan/AppData/Local/Programs/Python/Python35/爬虫/%s_imageurls" % user_id, "w")
# for eachlink in urllist_set:
#     link = link + eachlink + "\n"
# fo2.write(link)
# print(u'图片链接爬取完毕')
# fo2.close()

image_path = os.getcwd() + '\pics'
if os.path.exists(image_path) is False:
    os.mkdir(image_path)
x = 1
for imgurl in theset:

    allpage = requests.get(imgurl,cookies=cookie).content
    soup = BeautifulSoup(allpage, "html.parser")
    imglink = soup.find_all(href=re.compile("img"))
    imag=imglink[0].get('href', None)

    temp = image_path + '/%s.jpg' % x
    print(u'正在下载第%s张图片' % x)
    try:
        urllib.request.urlretrieve(urllib.request.urlopen(imag).geturl(), temp)
    except:
        print(u'图片下载失败：%s' % imgurl)
    x += 1
print(u'图片爬取完毕，共%d张，保存路径%s' % (image_count - 1, image_path))