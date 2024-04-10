"""
Monitoring process that will be responsible for detecting 
and act upon the network changes, more specifically, 
subscribers uplink and downlink network throughput.
"""

import requests
import time


# Create a UPF for the new subscribers
# This is for when we exhaust the current UPFs throughput.
def create_upf():
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
    listUpfs = get_site_upfs("ua", "site1")
    for upf in listUpfs:
        val = get_upf_ul(upf)
        # If there's no values for the UPF
        if val == None:
            continue
        print("{u} has bw: {b}".format(u=upf, b=val))
        if upf == "upf1" and val < 40:
            r = edit_slice("slice3", 10000000)
            print("Edited slice")
