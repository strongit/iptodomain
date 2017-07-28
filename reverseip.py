# -*- coding: utf-8 -*-

import json
import requests
import sys
import urllib
import re
import codecs
from bs4 import BeautifulSoup
from publicsuffix import PublicSuffixList, fetch

ip = sys.argv[1]


# content match func
def get_soup(domain):
    global body_text
    try:
        body_text = urllib.urlopen(domain).read()
    except:
        print "[*] Web Get Error:checking the Url"
    soup = body_text.decode('utf-8', 'ignore').encode('utf-8')
    with open('bs.txt', 'w') as f:
        f.write(soup)
    DMfile = codecs.open('bs.txt', 'rb', 'utf-8')
    fileread = DMfile.read()
    f.close()
    DMfile.close()
    strlist = re.compile(u'迷信|赌博|色情|暴力|扫描', re.S) # 将字符串编译成re.S[DOTALL]模式下正则表达式
    if re.findall(strlist, fileread):
        print "网站内容包含'迷信|赌博|色情|暴力|扫描'等字段"
    else:
        print "网站内容无敏感词汇"


# qcloud_image yellow detection fucn
def pic_yellow(picture):
    from qcloud_image import Client
    from qcloud_image import CIUrl, CIFile, CIBuffer, CIUrls, CIFiles, CIBuffers
    appid = '1254082689'
    secret_id = 'AKID663puGvZFsafr9FnFcWYeaeomAebD0Rj'
    secret_key = 'erAcykbYMH4cK7maDwmSB4zz5eJwmT08'
    bucket = 'ws01'

    client = Client(appid, secret_id, secret_key, bucket)
    client.use_http()
    client.set_timeout(30)
    #单个或多个图片Url
    # print (client.porn_detect(CIUrls(['http://jiangsu.china.com.cn/uploadfile/2015/1102/1446443026382534.jpg',
    # 'http://n.sinaimg.cn/fashion/transform/20160704/flgG-fxtspsa6612705.jpg'])))
    #单个或多个图片File
    print (client.porn_detect(CIFiles(picture)))

# list subdomain func
def sub_domain(domain):
    sys.path.append( "/root/xiaotest/Sublist3r/sublist3r.py" )
    # sys.path.append( "F:/\strongitpro/\CDN/\Sublist3r/\sublist3r.py" )
    from Sublist3r import sublist3r
    subdomains = sublist3r.main(domain, 40, 'subdomains.txt', ports= None, silent=False, verbose= False, enable_bruteforce= False, engines=None)


# ip2domain funcs
def yougetsignal(ip):
    url = 'http://domains.yougetsignal.com/domains.php'
    data = urllib.urlencode({'remoteAddress': ip})
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0",
                "Host": "domains.yougetsignal.com",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    response = requests.post(url, params=data, headers=headers)
    result = json.loads(response.text)
    domainlist = list()
    if result["status"] == "Fail" or result["domainCount"] == 0:
        print "not found"
        sys.exit(0)
    for x in result["domainArray"]:
        domainlist.append(x[0])
    return domainlist


def sameip(ip):
    url = 'http://www.sameip.org/'
    domain = {}
    headers = {"Host": "www.sameip.org",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate"}
    response = requests.get(url + ip, headers=headers)
    if response.text:
        soup = BeautifulSoup(response.text)
        domain[ip] = [str(a.text) for a in soup.select('div  ol  li')]
        return domain[ip]


def aizhan(ip):
    url = 'http://dns.aizhan.com/'
    domain = {}
    headers = { "Host": "dns.aizhan.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate"}
    response = requests.get(url + ip + '/', headers=headers)
    if response.text:
        soup = BeautifulSoup(response.text)
        domain[ip] = [str(a.text) for a in soup.select('tbody  tr  td  a')]
        return domain[ip]


def c7(ip):
    url = "http://dns.7c.com/hander/dnsServices.ashx"
    domain = {}
    data = urllib.urlencode( {'domain': ip , 'strdo': 'dnsquery' , 'strstartindex': '1'} )
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0" ,
               "Host": "dns.7c.com" ,
               "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3" ,
               "Accept-Encoding": "gzip, deflate" ,
               "Accept": "*/*",
               "X-Requested-With": "XMLHttpRequest",
               "Referer": "http://dns.7c.com/",
               "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url , params=data, headers=headers)
    if response.text:
        soup = BeautifulSoup(response.text)
        domain[ip] = [str(a.get("title")) for a in soup.select('td  a  span')]
        return domain[ip]



if __name__ == '__main__':
    reload( sys )
    sys.setdefaultencoding("utf-8")
    print("Usage: python " + sys.argv[0] + " IP")
    result = list(set(yougetsignal(ip) + sameip(ip) + aizhan(ip) + c7(ip)))
    domainurl = list()
    for x in result:
        psl_file = codecs.open('./public_suffix_list.dat', encoding='utf8')
        psl = PublicSuffixList(psl_file).get_public_suffix(x)
        print psl
        sub_domain(psl)
        subfile = codecs.open('subdomains.txt', 'r').readlines()
        for x in subfile:
            domainurl.append(x.strip())

    # domainurl = ['708.58souso.com', '718.58souso.com', 'www.58souso.com', 'www.aimochen.com', 'www.tenglongbizhi.com', '722.58souso.com', '702.58souso.com', '726.58souso.com', '714.58souso.com', 'zzz.hld360.com', 'www.lalacs.com', 'xz.azwy.cn', 'www.azwy.cn', 'www.hld360.com', 'ddd.58souso.com']
    print("%sIP %s  map these domains: %s%s%s" %('\033[93m', ip, '\033[91m', list(set(domainurl)), '\033[0m'))
    print("%sNow check the illegal word of content: %s" %('\033[91m','\033[0m'))
    for url in domainurl:
        get_soup("http://" + url)
    # picture = ['F:/strongitpro/CDN/img/full/3ccc7126e4d22c0ecfc87a8d15aa8d0287c74d7a.jpg',]
    # pic_yellow(picture)
