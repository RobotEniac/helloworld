#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import requests
import sys

def getHeaders():
    header_ref = 'http://user.snh48.com/Index/index.html'
    headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'http://shop.48.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': header_ref,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': ""
            }
    return headers

def simpleHeader():
    headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Upgrade-Insecure-Requests': '1',
    }
    return headers

def getCode(session):
    r = random.random()
    url = 'http://user.snh48.com/Authcode/getcode?' + str(r)
    resp = session.get(url)
    filename = './code.png'
    with open(filename, 'wb') as f:
        f.write(resp.content)
    code = input('code in ' + filename + ':')
    return code

def login(connection, code):
    params_dict = {
            'username': 'roboteniac',
            'password': '92xlztljdr',
            'code': code,
    }
    url = 'http://user.snh48.com/Login/dologin.html'
    headers = simpleHeader()
    resp = connection.post(url, data = params_dict, headers = headers)
    print("headers:", resp.headers)
    print("cookie:", resp.cookies)
    print("body:", resp.text)

def main():
    session = requests.session()
    session.headers.update(simpleHeader())
    code = getCode(session)
    print(code)
    login(session, code)

if __name__ == '__main__':
    main()

