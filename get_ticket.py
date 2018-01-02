#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import httplib
import re
import json
import time
import sys
from datetime import datetime
from datetime import date
from datetime import timedelta

def getServerTime(connection):
    try:
        client_time1 = time.time()
        connection.request("GET", "/pai/GetTime")
        client_time2 = time.time()
        res = connection.getresponse()
        if res.status == 200:
            data = res.read()
            server_time_str = int(re.search('\d+', data).group(0))
            server_time = float(server_time_str) / 1000.0
            return (client_time1, server_time, client_time2)
        return (None, None, None)
    except:
        print "getServertime exception"
        return (None, None, None)

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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': header_ref,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': getCookie("./cookie/haibo.cookie")
            }
    return headers


def ticketCheck(connection, ticket_id, seat_type, headers):
    headers = getHeaders(ticket_id, seat_type)
    params_dict = {'id': ticket_id, 'r':0.5651687378367096}
    params = urllib.urlencode(params_dict)
    url = '/TOrder/tickCheck'
    try:
        connection.request('GET', url, params, headers)
        resp = connection.getresponse()
        print resp.status, resp.reason
        return resp
    except:
        print "ticketCheck exception"
        return None

def addTicket(connection, ticket_id, seat_type, headers):
    params_dict = {
            'id': ticket_id,
            'r': 0.5651687378367096,
            'num': 1,
            'seattype': seat_type,
            'brand_id': 3, # 1: snh48, 2: bej48, 3:gnz48
            'choose_times_end': -1,
            }
    params = urllib.urlencode(params_dict)
    url = '/TOrder/add'
    try:
        connection.request('POST', url, params, headers)
        resp = connection.getresponse()
        print resp.status, resp.reason
        return resp
    except:
        print "addTicket exception"
        return None

def ticktack(connection, hh, MM = 0, ss = 0):
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
    rate = 0.9
    for i in range(0, check_time):
        while time.time() < due_date - (check_time - i) * 2:
            time.sleep(0.01)
        t1, server_time, t2 = getServerTime(connection)
        dlt = server_time - (t1 + t2) / 2.0
        rtt = t2 - t1
        print "rtt = ", rtt, ", delta_t = ", dlt, "server time = ", datetime.fromtimestamp(server_time),\
                "local_time = ", datetime.fromtimestamp((t1 + t2) / 2.0)
        if i == 0:
            max_dlt = dlt
            max_rtt = rtt
        max_dlt = max_dlt * (1 - rate) + dlt * rate
        avg_rtt = avg_rtt * (1 - rate) + (t2 - t1) * rate
    # avg_rtt = avg_rtt / check_time
    i = 0
    while time.time() + max_dlt + avg_rtt / 2.0  < due_date:
        time.sleep(0.01)
        i += 1
        if i % 100 == 0:
            t1, server_time, t2 = getServerTime(connection)
            dlt = server_time - (t1 + t2) / 2.0
            rtt = t2 - t1
            print "rtt = ", rtt, ", delta_t = ", dlt, "server time = ", datetime.fromtimestamp(server_time),\
                    "local_time = ", datetime.fromtimestamp((t1 + t2) / 2.0)
        if i > 10000000:
            i = 0

    time.sleep(0.008) # magic number, avoid estimate time > server time
    t1, t2, t3 = getServerTime(connection)
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
        print "Usage:", sys.argv[0], "ticket_id seat_type count [backup_seat_type]."
        exit(1)
    conn = httplib.HTTPSConnection('shop.48.cn', 443)
    ticktack(conn, 20)
    ticket_id = int(sys.argv[1])
    seat_type = int(sys.argv[2])
    count = int(sys.argv[3])
    backup_seat_type = -1
    if len(sys.argv) >= 5:
        backup_seat_type = int(sys.argv[4])

    seat_map = {1:"svip", 2:"vip", 3:"seat", 4:"stand"}
    for i in range(0, count):
        if backup_seat_type > 0:
            if i >= 3:
                seat_type = backup_seat_type
        print "seat_type is %s" % (seat_map[seat_type])
        headers = getHeaders(ticket_id, seat_type)
        res_str = addTicket(conn, ticket_id, seat_type, headers)
        if res_str and res_str.status == 200:
            res = json.load(res_str, 'utf8')
            print json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4)
        start_time = time.time()
        last_req = start_time - 2.5
        while True:
            time.sleep(0.1)
            end_time = time.time()
            if end_time - start_time > 10:
                break
            if end_time - last_req < 3:
                continue
            last_req = end_time
            res = ticketCheck(conn, ticket_id, seat_type, headers)
            if res and res.status == 200:
                res_json = json.load(res)
                print json.dumps(res_json, ensure_ascii=False, sort_keys=True, indent=4)
