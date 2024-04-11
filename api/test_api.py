import requests

# Request body for UPF creation. Save for later
# req_body = {
#     "amp":"10.255.32.183",
#     "enterprise":"ua",
#     "site":"site3",
#     "upf_id":"upf4",
#     "address":"upf.upf4",
#     "config-endpoint":"http://upf-http.upf4:8080",
#     "description":"UPF 4 for Site 3",
#     "display-name":"UPF 4",
#     "port":8805,
#     # ArgoCD requirements
#     "location":"https://kubernetes.default.svc",
#     "project":"default",
#     "repository":"https://github.com/dot-1q/5g_connected_edge",
#     "path":"site3/upf",
#     "values":"values_upf4.yaml"
# }

# Request body for Slice edit. Save for later
# req_body = {
#     "enterprise": "ua",
#     "site": "site1",
#     "slice": "slice3",
#     "download": 10000000,
#     "mbr_dl_bs": 12500000,
#     "upload": 2000000000,
#     "mbr_ul_bs": 12500000,
# }

# Request body for Slice Creation. Save for later
# req_body = {
#     "enterprise": "ua",
#     "site": "site1",
#     "slice_id": "slice3",
#     "sdesc": "Slice 3 for site 1 TEST",
#     "device_group": "device-group-3",
#     "sname": "Slice 3",
#     "mbr_dl": 500000000,
#     "mbr_dl_bs": 12500000,
#     "mbr_ul": 50000000,
#     "mbr_ul_bs": 12500000,
#     "service_differentiator": "030303",
#     "slice_service_type": "3",
#     "upf_id": "upf3",
# }

# # Request body for Device Group Creation. Save for later
# req_body = {
#     "enterprise": "ua",
#     "site": "site1",
#     "device_group_id": "dg4",
#     "dgd": "test device group creation",
#     "dgn": "Device Group 4",
#     "ip_domain": "ua-pool3",
#     "mbr_dl": 200000000,
#     "mbr_ul": 200000000,
#     "traffic_class": "class-1",
# }

# Request body for the addition of a new subscriber. Save for later
# req_body = {
#     "enterprise": "ua",
#     "site": "site1",
#     "imsi": "208990000000099",
#     "plmn": "20899",
#     "opc": "28a182edf3c70667a90a66c619cec91f",
#     "key": "fd4b1e644a2dd4d2c8c03cf5fe12238d",
#     "sqn": "16f3b3f70fc2",
#     "sim_id": "ua-sim-099",
#     "sd": "Sim Card desc.",
#     "sn": "Sim Card 99",
#     "device_id": "ua-ue-99",
#     "dd": "Device Desc.",
#     "dn": "UE 99",
#     "device_group": "dg4",
# }

# Request body for the assignment of the newly created device group to a slice.
req_body = {
    "enterprise": "ua",
    "site": "site1",
    "slice_id": "slice3",
    "device_group_id": "dg4",
}


url = "http://cedge-api:8080/assign_slice"

response = requests.post(url, json=req_body)
# Decode bytes to int, and then convert bps to Mbps
data = response
print("Status:", data.content)
