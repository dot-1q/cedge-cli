import requests
import time

req_body = {
     "enterprise": "ua",
     "site": "site1",
     "imsi": "208990000000010",
     "plmn": "20899",
     "opc": "28a182edf3c70667a90a66c619cec91f",
     "key": "fd4b1e644a2dd4d2c8c03cf5fe12238d",
     "sqn": "16f3b3f70fc2",
     "sim_id": "ua-sim-10",
     "sd": "Sim Card desc.",
     "sn": "Sim Card 10",
     "device_id": "ua-ue-10",
     "dd": "Device Desc.",
     "dn": "UE 10",
     "device_group": "device-group-1",
}

for i in range (10,50):
    req_body["imsi"] = "2089900000000" + str(i)
    req_body["sim_id"] = "ua-sim-" + str(i)
    req_body["sn"] = "Sim Card " + str(i)
    req_body["device_id"] = "ua-ue-" + str(i)
    req_body["dn"] = "UE " + str(i)

    url = "http://cedge-api:8080/add_subscriber"
    response = requests.post(url, json=req_body)
    print("Added:", response.content)
    time.sleep(1)
