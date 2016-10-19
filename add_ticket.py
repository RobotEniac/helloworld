import os
import sys
import time
from datetime import datetime
import re

def getCookie(path):
    cookie = ''
    with open(path, 'r') as f:
        cookie = f.readline().strip()
    return cookie

t_yy = 2016
t_mm = 10
t_dd = 19
t_hh = 20
t_mi = 0
t_si = 0
aid = '480'
sid = '2'
if len(sys.argv) < 9:
    print("Usage: python [script] [time] [id] [sid]")
    print("Example: python set_time.py 2016 10 12 20 0 0 453 4")
    # sys.exit(0)
else :
    t_yy = int(sys.argv[1])
    t_mm = int(sys.argv[2])
    t_dd = int(sys.argv[3])
    t_hh = int(sys.argv[4])
    t_mi = int(sys.argv[5])
    t_si = int(sys.argv[6])
    aid = sys.argv[7]
    sid = sys.argv[8]

def getDelay():
    CMDLINE_TIME=r"""
    curl "http://shop.48.cn/pai/GetTime" """
    t1 = time.time()
    output = os.popen(CMDLINE_TIME)
    time_url = re.split('\\(|\\)',output.read())[1]
    t2 = float(time_url[:-3]+"."+time_url[-3:])
    return t2 - t1

#os.system(CMDLINE)

CMD_C0 = getCookie('./haibo.cookie') # Your cookie here

CMDT = r""" curl 'http://shop.48.cn/pai/GetTime' """
CMD0_0 = r"""curl 'http://shop.48.cn/TOrder/add' -H 'Cookie: """ + CMD_C0 + r"""' -H 'Origin: http://shop.48.cn' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en;q=0.6' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://shop.48.cn/tickets/item/"""

# 448?seat_type=4
CMD0_1 = r"""' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'id="""

# 448&num=1&seattype=4
CMD0_2 = r"""&brand_id=1&r=0.9775960921017517' --compressed"""

CMD0 = CMD0_0 + aid + "?seat_type=" + sid + CMD0_1 + aid + "&num=1&seattype=" + sid + CMD0_2;

# CMD0 buy ticket
print(CMD0)
#sys.exit()

CMD_C1 = getCookie('./haibo.cookie') # Your cookie here

CMD1_0 = r"""curl 'http://shop.48.cn/TOrder/tickCheck' -H 'Cookie: """ + CMD_C1 + r"""' -H 'Origin: http://shop.48.cn' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.8,en;q=0.6' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://shop.48.cn/tickets/item/"""

CMD1_1 = r"""' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'id="""

CMD1_2 = r"""&r=0.24410195595323092' --compressed """

CMD1 = CMD1_0 + aid + "?seat_type=" + sid + CMD1_1 + aid + CMD1_2;

# CMD1 get ticket status
print(CMD1)
#sys.exit()

t = time.mktime(datetime(t_yy, t_mm, t_dd, t_hh, t_mi, t_si).timetuple())
t_ep = 0.1
li = []
t_dl = 1000
while time.time() < ( t - 40):
    time.sleep(0.1)
getDelay()

for i in range(0,5):
    while time.time() < ( t - 30 + i * 5):
        time.sleep(0.1)
    t_t = getDelay()
    li.append(t_t)
    if t_dl > t_t:
        t_dl = t_t

while time.time() < t - t_dl + t_ep:
    time.sleep(0.1)

#do something here

os.system(CMD0)


t_str = re.split('\\(|\\)', os.popen(CMDT).read())[1]
t_ser = float(t_str[:-3]+'.'+t_str[-3:])
print(datetime.fromtimestamp(t_ser))
print(t_dl)
for i in li:
    print(i)

time.sleep(0.5)
for i in range(0,100):
    res = os.popen(CMD1).read()
    print(res)
    if res.find("ErrorCode\":\"wait") == -1:
        break;
    time.sleep(5)
