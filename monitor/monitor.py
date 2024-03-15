"""
Monitoring process that will be responsible for detecting 
and act upon the network changes, more specifically, 
subscribers uplink and downlink network throughput.
"""

import requests
import time

def get_sub_ul(ip_addr):
    url = "http://cedge-api:8080/get_sub_ul/{ip}".format(ip=ip_addr)
    response = requests.get(url)

    try:
        # Convert from bps to mbps
        value = float(response.content.decode('utf-8')) / 10**6
    except:
        # If the above code fails, i.e, no values are given, we return 0
        value = None
    return value


def get_subs(slice):
    url = "http://cedge-api:8080/get_subscribers/{s}".format(s=slice)
    response = requests.get(url).json()
    # Return the IP addresses of the subscribers
    return [a['ip'] for a in response]


# Analyze subs from slice 1
is_first = True
while 1:
    time.sleep(3)
    subs = get_subs('slice1')
    val = get_sub_ul(subs[0])
    # If there's no values for the subs
    if val == None:
        print("No one connected")
        continue
    print("Sub {s} has bw: {b}".format(s=subs[0],b=val))
   
    # If the bw is less than 50Mbps, edit the slice
    if val < 60:
        # First value is always too low
        if is_first:
            is_first = False
            continue

        url = "http://cedge-api:8080/edit_slice/"
        req_body = {
            "enterprise":"ua",
            "site":"site1",
            "slice":"slice3",
            "download":2000000000,
            "mbr_dl_bs":12500000,
            "upload":10000000,
            "mbr_ul_bs":12500000,
        }
        response = requests.post(url, json=req_body)
        data = response
        print(data.content)
