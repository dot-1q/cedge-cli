"""
Monitoring process that will be responsible for detecting 
and act upon the network changes, more specifically, 
subscribers uplink and downlink network throughput.
"""

import requests
import time

def get_sub_ul(ip_addr):
    pass

url = "http://cedge-api.omec:8080/get_sub_bw"


while 1:
    # Create SIM
    response = requests.get(url)
    print(response.content)
    time.sleep(2)