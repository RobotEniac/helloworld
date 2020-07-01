#!/usr/bin/python3
# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, urllib.error
import http.client
import json
import time
import sys
import socket
from datetime import datetime
import get_time


def getCookie(path):
    cookie = ''
    with open(path, 'r') as f:
        cookie = f.readline().strip()
    return cookie


def getHeaders(ticket_id, seat_type):
    header_ref = 'https://shop.48.cn/tickets/item/' + str(ticket_id) + '?seat_type=' + str(seat_type)
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://shop.48.cn',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/62.0.3202.94 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': header_ref,
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8u,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Upgrade-Insecure-Requests': '1',
        'Cookie': getCookie("./cookie/haibo.cookie")
    }
    return headers


def ticketCheck(connection, ticket_id, seat_type, headers):
    headers = getHeaders(ticket_id, seat_type)
    params_dict = {'id': ticket_id, 'r': 0.5651687378367096}
    params = urllib.parse.urlencode(params_dict)
    url = '/TOrder/tickCheck'
    try:
        connection.request('GET', url, params, headers)
        resp = connection.getresponse()
        print(resp.status, resp.reason)
        return resp
    except (http.client.HTTPException, socket.error) as ex:
        print("ticketCheck exception: %s" % ex)
        return None


def addTicket(connection, ticket_id, seat_type, headers):
    params_dict = {
        'id': ticket_id,
        'r': 0.5651687378367096,
        'num': 1,
        'seattype': seat_type,
        'brand_id': 3,  # 1: snh48, 2: bej48, 3:gnz48
        'choose_times_end': -1,
    }
    params = urllib.parse.urlencode(params_dict)
    url = '/TOrder/add'
    try:
        connection.request('POST', url, params, headers)
        resp = connection.getresponse()
        print(resp.status, resp.reason)
        return resp
    except (http.client.HTTPException, socket.error) as ex:
        print("addTicket exception: %s" % ex)
        return None


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage:", sys.argv[0], "ticket_id seat_type count [backup_seat_type].")
        exit(1)
    conn = http.client.HTTPSConnection('shop.48.cn', 443, timeout=2)
    get_time.ticktack(conn, 20)
    ticket_id = int(sys.argv[1])
    seat_type = int(sys.argv[2])
    count = int(sys.argv[3])
    backup_seat_type = -1
    if len(sys.argv) >= 5:
        backup_seat_type = int(sys.argv[4])

    seat_map = {1: "svip", 2: "vip", 3: "seat", 4: "stand"}
    start = datetime.now()
    for i in range(0, count):
        if backup_seat_type > 0:
            if (datetime.now() - start).seconds < 30:
                seat_type = backup_seat_type
        print("seat_type is %s" % (seat_map[seat_type]))
        headers = getHeaders(ticket_id, seat_type)
        res_str = addTicket(conn, ticket_id, seat_type, headers)
        if res_str is None:
            conn = http.client.HTTPSConnection('shop.48.cn', 443, timeout=1)
            print("i: %d, now: %s" % (i, datetime.now()))
            continue
        if res_str and res_str.status == 200:
            res = json.load(res_str)
            print(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=4))
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
                print(json.dumps(res_json, ensure_ascii=False, sort_keys=True, indent=4))
