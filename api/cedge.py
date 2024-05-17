from flask import Flask, request
import requests
import json
from ipaddress import IPv4Address as ip

app = Flask(__name__)

roc_api_url = "http://aether-roc-umbrella-aether-roc-api.aether-roc:8181/aether/v2.1.x/"
webui_url = "http://webui.omec:5000/api/subscriber/"
# url_argocd = "https://"+spec['amp']+":30001/api/v1/"


@app.route("/add_subscriber", methods=["POST"])
def add_subscriber():
    if request.method == "POST":
        # Get the request JSON data
        data = request.get_json()
        # Grab the enterprise and site from the command line for the api endpoint
        enterprise = data["enterprise"]
        site = data["site"]

        # SD-Core subscriber's provisioning api endpoint.
        url = webui_url + "imsi-{i}".format(i=data["imsi"])

        req_body = {
            "UeId": data["imsi"],
            "plmnId": data["plmn"],
            "opc": data["opc"],
            "key": data["key"],
            "sequenceNumber": data["sqn"],
        }

        # Send POST
        # Add to SD-Core
        response = requests.post(url, json=req_body)
        print(response)

        ################## Aether ROC Phase #################################

        # Create SIM [Start]
        url = roc_api_url + "{e}/site/{s}/sim-card/{sim}".format(
            e=enterprise, s=site, sim=data["sim_id"]
        )

        req_body = {
            "description": data["sd"],
            "display-name": data["sn"],
            "enable": True,
            # "iccid": "string", # Not using this at the moment.
            "imsi": data["imsi"],
            "sim-id": data["sim_id"],
        }

        response = requests.post(url, json=req_body)
        print(response)
        # Create SIM [End]

        # Create Device [Start]
        url = roc_api_url + "{e}/site/{s}/device/{device}".format(
            e=enterprise, s=site, device=data["device_id"]
        )

        req_body = {
            "description": data["dd"],
            "device-id": data["device_id"],
            "display-name": data["dn"],
            # "imei": "string", # Not using this at the moment.
            "sim-card": data["sim_id"],
        }

        response = requests.post(url, json=req_body)
        print(response)
        # Create Device [End]

        # Add Device to device group [Start]
        url = roc_api_url + "{e}/site/{s}/device-group/{dg}/device/{d}".format(
            e=enterprise, s=site, dg=data["device_group"], d=data["device_id"]
        )

        req_body = {"device-id": data["device_id"], "enable": True}

        response = requests.post(url, json=req_body)
        # Add Device to device group [End]
        return response.content
    else:
        return "Only POST method, no subscriber added"


# Assign a device group to a slice, so that the subscribers can have connectivity.
@app.route("/assign_slice", methods=["POST"])
def assign_slice():
    if request.method == "POST":
        # Get the request JSON data
        data = request.get_json()

        # Grab the enterprise and site from the command line for the api endpoint
        enterprise = data["enterprise"]
        site = data["site"]

        url = roc_api_url + "{e}/site/{s}/slice/{sl}/device-group/{dg}".format(
            e=enterprise, s=site, sl=data["slice_id"], dg=data["device_group_id"]
        )

        req_body = {"device-group": data["device_group_id"], "enable": True}

        # Send POST
        response = requests.post(url, json=req_body)
        return response.content
    else:
        return "Only Post Method Allowed"


# TODO: Implement
# Returns all the UPFs from a given site.
def get_site_upfs():
    pass


# TODO: Implement
# Returns all the Sites from a given enterprise
def get_sites():
    pass


# TODO: Create an *EMPTY* device group, so we can add a subscriber
@app.route("/create_device_group", methods=["POST"])
def create_device_group():
    if request.method == "POST":
        # Get the request JSON data
        data = request.get_json()

        # Grab the enterprise and site from the command line for the api endpoint
        enterprise = data["enterprise"]
        site = data["site"]

        url = roc_api_url + "{e}/site/{s}/device-group/{dg}".format(
            e=enterprise, s=site, dg=data["device_group_id"]
        )

        req_body = {
            "description": data["dgd"],
            "device-group-id": data["device_group_id"],
            "display-name": data["dgn"],
            "ip-domain": data["ip_domain"],
            "mbr": {
                "downlink": data["mbr_dl"],
                "uplink": data["mbr_ul"],
            },
            "traffic-class": data["traffic_class"],
        }

        # Send POST
        response = requests.post(url, json=req_body)
        return response.content
    else:
        return "Only POST method, no Device Group created"


# Create a Slice
@app.route("/create_slice", methods=["POST"])
def create_slice():
    if request.method == "POST":
        # Get the request JSON data
        data = request.get_json()

        # Grab the enterprise and site from the command line for the api endpoint
        enterprise = data["enterprise"]
        site = data["site"]

        url = roc_api_url + "{e}/site/{s}/slice/{sl}".format(
            e=enterprise, s=site, sl=data["slice_id"]
        )

        req_body = {
            "connectivity-service": "5g",
            "default-behavior": "ALLOW-ALL",
            "description": data["sdesc"],
            "device-group": [
                {"device-group": data["device_group"], "enable": True}
                # TODO: Multiple device groups go here
            ],
            "display-name": data["sname"],
            "mbr": {
                "downlink": data["mbr_dl"],
                "downlink-burst-size": data["mbr_dl_bs"],
                "uplink": data["mbr_ul"],
                "uplink-burst-size": data["mbr_ul_bs"],
            },
            "sd": data["service_differentiator"],
            "slice-id": data["slice_id"],
            "sst": data["slice_service_type"],
            "upf": data["upf_id"],
        }
        # Send POST
        response = requests.post(url, json=req_body)
        # print(response.content)
        return response.content
    else:
        return "Only Post Method Allowed"


# Create an UPF
@app.route("/create_upf", methods=["POST"])
def create_upf():
    if request.method == "POST":
        # Get the request JSON data
        data = request.get_json()

        roc_api_url = "http://" + data["amp"] + ":31194/aether-roc-api/aether/v2.1.x/"
        url_argocd = "https://" + data["amp"] + ":30001/api/v1/"
        enterprise = data["enterprise"]
        site = data["site"]
        url = roc_api_url + "{e}/site/{s}/upf/{u}".format(
            e=enterprise, s=site, u=data["upf_id"]
        )

        req_body = {
            "address": data["address"],
            "config-endpoint": data["config-endpoint"],
            "description": data["description"],
            "display-name": data["display-name"],
            "port": data["port"],
            "upf-id": data["upf_id"],
        }

        # Send POST
        response = requests.post(url, json=req_body)

        print(response)
        print(response.content)

        # Use the Argocd API to create the upf app deployment
        token = _get_argocd_token(data["amp"])
        headers = {
            "Authorization": "Bearer " + token,
        }

        req_body = {
            "metadata": {
                "name": site + "-" + data["upf_id"],
            },
            "spec": {
                "destination": {
                    "namespace": data["upf_id"],
                    "server": data["location"],
                },
                "project": data["project"],
                "source": {
                    "repoURL": data["repository"],
                    "path": data["path"],
                    "helm": {"valueFiles": data["values"]},
                },
                "syncPolicy": {
                    "automated": {"selfHeal": True},
                    "syncOptions": ["CreateNamespace=true"],
                },
            },
        }

        # Send POST
        response = requests.post(
            url_argocd + "applications", json=req_body, headers=headers, verify=False
        )
        return "UPF created successfully"
    else:
        return "Only POST method, no UPF created"


# Get specific UE uplink value. IP required.
@app.route("/get_sub_ul/<sub>", methods=["GET"])
def get_sub_ul(sub):
    # Send POST
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = '8 * avg_over_time(upf_session_tx_bytes{{namespace="upf1",pdr=~".*[13579]", ue_ip="{s}"}}[5s])'.format(
        s=sub
    )

    response = requests.get(url + query, verify=False).json()
    try:
        data = response["data"]["result"][0]["value"][1]
        return data
    except:
        return "no_value"


# Get specific UE downlink value. IP required.
@app.route("/get_sub_dl/<sub>", methods=["GET"])
def get_sub_dl(sub):
    # Send POST
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = '8 * avg_over_time(upf_session_tx_bytes{{namespace="upf1",pdr=~".*[02468]", ue_ip="{s}"}}[5s])'.format(
        s=sub
    )

    response = requests.get(url + query, verify=False).json()
    try:
        data = response["data"]["result"][0]["value"][1]
        return data
    except:
        return "no_value"


# Get the IP and IMSI of ALL subscribers of ALL slices.
@app.route("/get_subscribers/", methods=["GET"])
def get_subscribers():
    url = "http://metricfunc:9301/nmetric-func/v1/subscriber/all"
    response = requests.get(url, verify=False).json()
    data = {}
    for values in response:
        if values != "":
            print(response)
            data[values] = get_ue_ip(values)
    try:
        return data
    except:
        return "", 404


# Get the IP and IMSI of ALL subscribers of given SLICE.
@app.route("/get_subscribers/<slice>", methods=["GET"])
def get_subscribers_by_slice(slice):
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = 'count (smf_pdu_session_profile{{enterprise="{e}"}}) by (id,ip)'.format(
        e=slice
    )

    response = requests.get(url + query, verify=False).json()

    data = []
    for values in response["data"]["result"]:
        # Check if said IMSI (id) is present in the data array
        if not any(a["id"] == values["metric"]["id"] for a in data):
            data.append(values["metric"])
        else:
            # If yes, update its IP address only if its bigger then the one currently saved.
            for index, metric in enumerate(data):
                if (metric["id"] == values["metric"]["id"]) and (
                    ip(values["metric"]["ip"]) > ip(metric["ip"])
                ):
                    data[index] = values["metric"]
    try:
        return data
    except:
        return "no_value"


# Get the IP address of a given IMSI
@app.route("/get_ue_ip/<imsi>", methods=["GET"])
def get_ue_ip(imsi):
    url = "http://metricfunc:9301/nmetric-func/v1/subscriber/" + imsi
    data = requests.get(url).json()
    try:
        return data["ipaddress"]
    except:
        return "", 404


# Edit a slice
@app.route("/edit_slice/", methods=["POST"])
def edit_slice():
    data = []

    if request.method == "POST":
        data = request.get_json()

        url = roc_api_url + "{e}/site/{s}/slice/{sl}/mbr".format(
            e=data["enterprise"], s=data["site"], sl=data["slice"]
        )

        req_body = {
            "downlink": data["download"],
            "downlink-burst-size": data["mbr_dl_bs"],
            "uplink": data["upload"],
            "uplink-burst-size": data["mbr_ul_bs"],
        }

        response = requests.post(url, json=req_body)
        print(response)
        print(response.content)

        return "edited"

    return "Only POST requests allowed"


# Get specific UPF uplink value. UPF ID required
@app.route("/get_upf_ul/<upf>", methods=["GET"])
def get_upf_ul(upf):
    # Send POST
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = 'sum(8 * rate(upf_bytes_count{{dir="tx",iface="Core", namespace="{upf_id}"}}[5s]))'.format(
        upf_id=upf
    )
    response = requests.get(url + query, verify=False).json()
    try:
        data = response["data"]["result"][0]["value"][1]
        return data
    except:
        return "no_value"


# Get specific UPF downlin value. UPF ID required.
@app.route("/get_upf_dl/<upf>", methods=["GET"])
def get_upf_dl(upf):
    # Send POST
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = 'sum(8 * rate(upf_bytes_count{{dir="tx",iface="Access", namespace="{upf_id}"}}[5s]))'.format(
        upf_id=upf
    )
    response = requests.get(url + query, verify=False).json()
    try:
        data = response["data"]["result"][0]["value"][1]
        return data
    except:
        return "no_value"


# Move UE to another slice. Each slices has a device group associated,
# which is where the UE will be moved to.
@app.route("/move_ue/", methods=["POST"])
def move_ue():
    if request.method == "POST":
        data = request.get_json()
        url = roc_api_url + "{e}/site/{s}/device-group/{dg}/device/{id}".format(
            e=data["enterprise"],
            s=data["site"],
            dg=data["old-dg"],
            id=data["device-id"],
        )

        # REMOVE FROM OLD DEVICE-GROUP
        response = requests.delete(url)
        print(response)
        print(response.content)

        # ADD TO NEW DEVICE-GROUP
        url = roc_api_url + "{e}/site/{s}/device-group/{dg}/device/{id}".format(
            e=data["enterprise"],
            s=data["site"],
            dg=data["new-dg"],
            id=data["device-id"],
        )

        # HACK:
        # First disable this moved UE. Aether does not like when its enabled right away.
        req_body = {"device-id": data["device-id"], "enable": False}
        response = requests.post(url, json=req_body)
        print(response)
        print(response.content)

        # HACK:
        # Only then we enable it
        req_body = {"device-id": data["device-id"], "enable": True}
        response = requests.post(url, json=req_body)
        print(response)
        print(response.content)

        return "edited"

    return "Only POST requests allowed"


def _get_argocd_token(amp):
    """
    Get Bearer ArgoCD API token
    """

    # This loads the file that contains the ArgoCD secrets
    # You should create a file with the same name that has your
    # Username and password
    import argocd_secrets

    req_body = {
        "username": argocd_secrets.username,
        "password": argocd_secrets.password,
    }

    url_argocd = "https://" + amp + ":30001/api/v1/"
    response = requests.post(url_argocd + "session", json=req_body, verify=False)

    asdf = 0
    # Return the token value
    return json.loads(response.text)["token"]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
