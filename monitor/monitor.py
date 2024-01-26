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
    # Return the bps values in Mbps
    return float(response.content.decode('utf-8')) / 10**6


def get_subs(slice):
    url = "http://cedge-api:8080/get_subscribers/{s}".format(s=slice)
    response = requests.get(url).json()
    # Return the IP addresses of the subscribers
    return [a['ip'] for a in response]

subs = get_subs('slice1')

values = deque(maxlen=10)
while 1:
    print(values)
    values.append(get_sub_ul(subs[0]))
    print("Max in deque: ", max(values))
    time.sleep(3)
