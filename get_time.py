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

def getServerTime(conn):
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
        #if abs(dlt) > abs(max_dlt):
        #    max_dlt = dlt
        if i == 0:
            max_dlt = dlt
            avg_rtt = rtt
        else:
            max_dlt = max_dlt * (1 - rate) + dlt * rate
            avg_rtt = avg_rtt * (1 - rate) + rtt * rate
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

    # time.sleep(0.009) # magic number, avoid estimate time > server time
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
        print "Usage:", sys.argv[0], "hour minute second."
        exit(1)
    conn = httplib.HTTPSConnection("shop.48.cn", 443)
    ticktack(conn, int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
