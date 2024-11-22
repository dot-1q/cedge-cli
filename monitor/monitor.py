"""
Monitoring process that will be responsible for detecting
and act upon the network changes, more specifically,
subscribers uplink and downlink network throughput.
"""

import requests
import time


# Move ue
def move_ue(ue):
    req_body = {
        "enterprise": "ua",
        "site": "site1",
        "old-dg": "device-group-1",
        "new-dg": "device-group-3",
        "device-id": "ua-ue-" + ue,
    }
    url = "http://cedge-api:8080/move_ue"
    response = requests.post(url, json=req_body)
    print("Moved:", response.content)


# Create a UPF for the new subscribers
# This is for when we exhaust the current UPFs throughput.
def create_upf():
    pass


# Create a SLICE for the new subscribers
# Similarly to the UPF creation, this is to give connectivity to the new subscribers
def create_slice():
    pass


# From a given IMSI, get its IP, if its connected to the network.
def get_ue_ip(imsi):
    url = "http://cedge-api:8080/get_ue_ip/{imsi}".format(imsi=imsi)
    response = requests.get(url)

    return response.content.decode("utf-8")


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
        value = 0
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


below_threshold = 0
moved = False
while 1:
    imsi = "208990000000000"
    ue_ip = get_ue_ip(imsi)
    ue_bw = get_sub_ul(ue_ip)
    print(f"IMSI: {imsi} has IP: {ue_ip} and bandwidth value: {ue_bw}")

    if ue_bw < 40.0 and ue_bw > 0:
        print(f"IMSI: {imsi} Bandwidth value below threshold")
        # Check if this IMSI bw value has been below threshold for more than 3 consecutive seconds
        if below_threshold >= 2 and not moved:
            # print("Moving UE with least priority to another slice")
            # move_ue("2")

            print("Restricting slice 3 to lower bandwidth")
            edit_slice("slice3", 15000000)

            print("Adding the leftover to slice 1 ")
            edit_slice("slice1", 85000000)
            moved = True
        below_threshold += 1
    else:
        below_threshold = 0
    # ?????????????????????????????????????????
    # ?????????????????????????????????????????
    # ?????????????????????????????????????????
    # How to check if an IMSI is below threshold, i.e, in a congested environment,
    # or just utilizing less bandwidth because it doesnt require more?
    # I think the best way is to subtract the current Bandwidth utilized by the UE from the
    # Total free Bandwidth available. If a slice has 75Mbps capacity, the UE is using 15Mbps, and
    # there plenty (75-15)Mbps bandwidth available, that means it just
    # doesnt require more than that, not that it is congested
    # Conversely, if there's no more free bandwidth, the whole space is being utilized and
    # the bandwidth dips below the threshold, means its congested.

    # Sleep 1 second
    time.sleep(1)
