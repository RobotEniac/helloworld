import datetime
import urllib
import httplib
import time
import re
import json

def getServerTime():
    conn = httplib.HTTPConnection("shop.48.cn")
    #conn = httplib.HTTPConnection("115.231.96.204")
    client_dt1 = datetime.datetime.now()
    conn.request("GET", "/pai/GetTime")
    client_dt2 = datetime.datetime.now()
    res = conn.getresponse()
    if res.status == 200:
        data = res.read()
        server_time = int(re.search('\d+', data).group(0))
        server_dt = datetime.datetime.fromtimestamp(server_time / 1000.0)
        return (client_dt1, server_dt, client_dt2)

def getCookie(path):
    cookie = ''
    with open(path, 'r') as f:
        cookie = f.readline().strip()
    return cookie

def ticketCheck(ticket_id, seat_type):
    header_ref = 'http://shop.48.cn/tickets/item/' + str(ticket_id) + '?seat_type=' + str(seat_type)
    headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'http://shop.48.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': header_ref,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Cookie': getCookie("./haibo.cookie")
            }
    params_dict = {'id': ticket_id, 'r':0.5651687378367096}
    params = urllib.urlencode(params_dict)
    url = '/TOrder/tickCheck'
    conn = httplib.HTTPConnection('shop.48.cn')
    conn.request('POST', url, params, headers)
    resp = conn.getresponse()
    print resp.status, resp.reason
    return resp

def getCheck(ticket_id, seat_type):
    header_ref = 'http://shop.48.cn/tickets/item/' + str(ticket_id) + '?seat_type=' + str(seat_type)
    headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'http://shop.48.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': header_ref,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Cookie': getCookie("./haibo.cookie")
            }
    params_dict = {'id': ticket_id, 'r':0.5651687378367096}
    params = urllib.urlencode(params_dict)
    url = '/TOrder/add'
    conn = httplib.HTTPConnection('shop.48.cn')
    conn.request('POST', url, params, headers)
    resp = conn.getresponse()
    print resp.status, resp.reason
    return resp


if __name__ == '__main__':
    for i in range(10):
        res = json.load(ticketCheck(464, 2))
        print res[u'Message']
        time.sleep(5)

