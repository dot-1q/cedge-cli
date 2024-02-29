"""
Monitoring process that will be responsible for detecting 
and act upon the network changes, more specifically, 
subscribers uplink and downlink network throughput.
"""

import requests
import time
from collections import deque

def get_sub_ul(ip_addr):
    url = "http://cedge-api:8080/get_sub_ul/{ip}".format(ip=ip_addr)
    response = requests.get(url)

    try:
        # Convert from bps to mbps
        value = float(response.content.decode('utf-8')) / 10**6
    except:
        # If the above code fails, i.e, no values are given, we return 0
        value = 0
    return value


def get_subs(slice):
    url = "http://cedge-api:8080/get_subscribers/{s}".format(s=slice)
    response = requests.get(url).json()
    # Return the IP addresses of the subscribers
    return [a['ip'] for a in response]

subs = get_subs('slice1')
print('Sub:' , subs[0])

while 1:
    val = get_sub_ul(subs[0])
    print("Sub {s} has bw: {b}".format(s=subs[0],b=val))
    time.sleep(3)
