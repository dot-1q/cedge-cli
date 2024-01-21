import requests

req_body = {
    "amp":"10.255.32.183",
    "enterprise":"ua",
    "site":"site3",
    "upf_id":"upf4",
    "address":"upf.upf4",
    "config-endpoint":"http://upf-http.upf4:8080",
    "description":"UPF 4 for Site 3",
    "display-name":"UPF 4",
    "port":8805,
    # ArgoCD requirements
    "location":"https://kubernetes.default.svc",
    "project":"default",
    "repository":"https://github.com/dot-1q/5g_connected_edge",
    "path":"site3/upf",
    "values":"values_upf4.yaml"
}

url = "http://cedge-api:8080/get_sub_bw"

# Create SIM
response = requests.get(url, json=req_body)
print(response.content)
