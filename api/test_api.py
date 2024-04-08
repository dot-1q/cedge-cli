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

req_body = {
    "enterprise": "ua",
    "site": "site1",
    "slice": "slice3",
    "download": 10000000,
    "mbr_dl_bs": 12500000,
    "upload": 2000000000,
    "mbr_ul_bs": 12500000,
}

url = "http://cedge-api:8080/get_upf_ul/upf1"

response = requests.get(url)
# Decode bytes to int, and then convert bps to Mbps
data = response
print("Uplink", data.content)

url = "http://cedge-api:8080/get_upf_dl/upf1"

response = requests.get(url)
# Decode bytes to int, and then convert bps to Mbps
data = response
print("Downlink", data.content)
