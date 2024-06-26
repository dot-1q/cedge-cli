"""
Monitoring process that will be responsible for detecting 
and act upon the network changes, more specifically,
subscribers uplink and downlink network throughput.
"""

import requests
import time

# Priorities 1 and 2. Rest are best effor
# Priority 1: 15Mbps
# Priority 2: 10Mbps
priority = {
    "1": ["upf1"],
}


# Move ue
def move_ue(imsi, slice):
    req_body = {
        "enterprise": "ua",
        "site": "site1",
        "old-dg": "device-group-1",
        "new-dg": "device-group-3",
        "device-id": "ua-ue-0",
    }
    url = "http://cedge-api:8080/move_ue"
    response = requests.post(url, json=req_body)
    print("Moved:", response.content)


# Create a UPF for the new subscribers
# This is for when we exhaust the current UPFs throughput.
def create_upf():
    pass


# Create a SLICE for the new subscribers
# Similarly to the UPF creation, this is to give connectivity to the new subcribers
def create_slice():
    pass


# From a given IMSI, get its IP, if its connected to the network.
def get_ue_ip(imsi):
    pass


def get_upf_ul(upf):
    url = "http://cedge-api:8080/get_upf_ul/{upf}".format(upf=upf)
    response = requests.get(url)

    try:
        # Convert from bps to mbps
        value = float(response.content.decode("utf-8")) / 10**6
    except:
        # If the above code fails, i.e, no values are given, we return 0
        value = None
    return value


# TODO: This method needs to be in the API module.
# Returns all the UPFs from a given site.
def get_site_upfs(enterprise, site):
    roc_api_url = (
        "http://aether-roc-umbrella-aether-roc-api.aether-roc:8181/aether/v2.1.x/"
    )
    query = "{e}/site/{s}/upf".format(e=enterprise, s=site)
    response = requests.get(roc_api_url + query).json()

    l = []
    # For each entry of upf details, just return their respective ids.
    for entry in response:
        l.append(entry["upf-id"])
    return l


def get_sub_ul(ip_addr):
    url = "http://cedge-api:8080/get_sub_ul/{ip}".format(ip=ip_addr)
    response = requests.get(url)

    try:
        # Convert from bps to mbps
        value = float(response.content.decode("utf-8")) / 10**6
    except:
        # If the above code fails, i.e, no values are given, we return 0
        value = None
    return value


def get_subs(slice):
    url = "http://cedge-api:8080/get_subscribers/{s}".format(s=slice)
    response = requests.get(url).json()
    # Return the IP addresses of the subscribers
    return [a["ip"] for a in response]


def edit_slice(slice, value):
    url = "http://cedge-api:8080/edit_slice/"
    req_body = {
        "enterprise": "ua",
        "site": "site1",
        "slice": slice,
        "download": 2000000000,
        "mbr_dl_bs": 12500000,
        "upload": value,
        "mbr_ul_bs": 12500000,
    }
    response = requests.post(url, json=req_body)
    return response


while 1:
    time.sleep(3)
    done = False
    # listUpfs = get_site_upfs("ua", "site1")
    # for upf in listUpfs:
    #     val = get_upf_ul(upf)
    #     # If there's no values for the UPF
    #     if val == None:
    #         continue
    #     print("{u} has bw: {b}".format(u=upf, b=val))
    #     if upf == "upf1" and val < 40:
    #         r = edit_slice("slice3", 10000000)
    #         print("Edited slice")
    if not done:
        done = True
        move_ue("imsi", "slice")
