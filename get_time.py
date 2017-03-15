#!/usr/bin/python
import urllib
import httplib
import re
import json
import time
import sys
from datetime import datetime
from datetime import date
from datetime import timedelta

def getServerTime():
    conn = httplib.HTTPSConnection("shop.48.cn", 443)
    #conn = httplib.HTTPConnection("115.231.96.204")
    client_time1 = time.time()
    conn.request("GET", "/pai/GetTime")
    client_time2 = time.time()
    res = conn.getresponse()
    if res.status == 200:
        data = res.read()
        server_time_str = int(re.search('\d+', data).group(0))
        server_time = float(server_time_str) / 1000.0
        return (client_time1, server_time, client_time2)
    return None

def getCookie(path):
    cookie = ''
    with open(path, 'r') as f:
        cookie = f.readline().strip()
    return cookie

def getHeaders(ticket_id, seat_type):
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
            'Cookie': getCookie("./cookie/haibo2.cookie")
            }
    return headers


def ticketCheck(ticket_id, seat_type, headers):
    headers = getHeaders(ticket_id, seat_type)
    params_dict = {'id': ticket_id, 'r':0.5651687378367096}
    params = urllib.urlencode(params_dict)
    url = '/TOrder/tickCheck'
    conn = httplib.HTTPConnection('shop.48.cn')
    conn.request('POST', url, params, headers)
    resp = conn.getresponse()
    print resp.status, resp.reason
    return resp

def addTicket(ticket_id, seat_type, headers):
    params_dict = {
            'id': ticket_id,
            'r': 0.5651687378367096,
            'num': 1,
            'seattype': seat_type,
            'brand_id': 1 # 1: snh48, 2: bej48, 3:gnz48
            }
    params = urllib.urlencode(params_dict)
    url = '/TOrder/add'
    conn = httplib.HTTPConnection('shop.48.cn')
    conn.request('POST', url, params, headers)
    resp = conn.getresponse()
    print resp.status, resp.reason
    return resp

def ticktack(hh, MM = 0, ss = 0):
    if hh == 0:
        return
    today = date.today()
    due_date = datetime(today.year, today.month, today.day,
            hh, MM, ss)
    due_date = time.mktime(due_date.timetuple())
    if due_date < time.time():
        return None;
    max_dlt = 0.0
    avg_rtt = 0.0
    check_time = 15
    rate = 0.7
    for i in range(0, check_time):
        while time.time() < due_date - (check_time + 1 - i) * 5:
            time.sleep(0.1)
        t1, server_time, t2 = getServerTime()
        dlt = server_time - (t1 + t2) / 2.0
        rtt = t2 - t1
        print "rtt = ", rtt, ", delta_t = ", dlt, "server time = ", datetime.fromtimestamp(server_time)
        #if abs(dlt) > abs(max_dlt):
        #    max_dlt = dlt
        if i == 0:
            max_dlt = dlt
        max_dlt = max_dlt * (1 - rate) + dlt * rate
        avg_rtt = avg_rtt * (1 - rate) + (t2 - t1) * rate
    # avg_rtt = avg_rtt / check_time
    while time.time() + max_dlt + avg_rtt / 2.0  < due_date:
        time.sleep(0.1)

    time.sleep(0.1) # magic number, avoid estimate time > server time
    t1, t2, t3 = getServerTime()
    # print "%.6f, %.6f, %.6f" % (t1, dlt, rtt)
    print max_dlt, avg_rtt
    dt1 = datetime.fromtimestamp(due_date)
    dt2 = datetime.fromtimestamp(t2)
    print "due date: ", dt1
    print "server time: ", dt2
    print "delta: ", t2 - due_date
    return None

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage:", sys.argv[0], "hour minute second."
        exit(1)
    ticktack(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
