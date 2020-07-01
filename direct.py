#!/usr/bin/python3
# -*- coding: utf-8 -*-
import http.client
import json
import time
import sys
import get_ticket
from datetime import datetime

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage:", sys.argv[0], "ticket_id seat_type count.")
        exit(1)
    conn = http.client.HTTPSConnection('shop.48.cn', 443, timeout=2)
    ticket_id = int(sys.argv[1])
    seat_type = int(sys.argv[2])
    count = int(sys.argv[3])

    seat_map = {1: "svip", 2: "vip", 3: "seat", 4: "stand"}
    headers = get_ticket.getHeaders(ticket_id, seat_type)
    for i in range(0, count):
        print("seat_type is %s" % (seat_map[seat_type]))
        res_str = get_ticket.addTicket(conn, ticket_id, seat_type, headers)
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
            res = get_ticket.ticketCheck(conn, ticket_id, seat_type, headers)
            if res and res.status == 200:
                res_json = json.load(res)
                print(json.dumps(res_json, ensure_ascii=False, sort_keys=True, indent=4))
