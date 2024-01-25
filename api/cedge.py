from flask import Flask, request
import requests
import json
from ipaddress import IPv4Address as ip

app = Flask(__name__)
#roc_api_url = "http://"+spec['amp']+":31194/aether-roc-api/aether/v2.1.x/"
#webui_url = "http://"+spec['amp']+":30002/api/subscriber/"
#url_argocd = "https://"+spec['amp']+":30001/api/v1/"

@app.route("/")
def hello_world():
    return "<p>Hello, World! OK</p>"

@app.route("/add_subscriber", methods=["POST"])
def add_subscriber():
    if requests.method == 'POST':
        pass
    else:
        return 'Only POST method, no subscriber added'


@app.route("/create_upf", methods=["POST"])
def create_upf():
    if request.method == 'POST':
        # Get the request JSON data
        data = request.json

        roc_api_url = "http://"+data['amp']+":31194/aether-roc-api/aether/v2.1.x/"
        url_argocd = "https://"+data['amp']+":30001/api/v1/"
        enterprise = data['enterprise']
        site = data['site']
        
        url = roc_api_url + \
            "{e}/site/{s}/upf/{u}".format(e=enterprise, s=site, u=data['upf_id'])

        req_body = {
            "address": data['address'],
            "config-endpoint": data['config-endpoint'],
            "description": data['description'],
            "display-name": data['display-name'],
            "port": data['port'],
            "upf-id": data['upf_id'],
        }

        # Send POST
        response = requests.post(url, json=req_body)

        print(response)
        print(response.content)

        # Use the Argocd API to create the upf app deployment
        token = _get_argocd_token(data['amp'])
        headers = {
            'Authorization': 'Bearer ' + token,
        }

        req_body = {
            "metadata": {
                "name": site+"-"+data['upf_id'],
            },
            "spec": {
                "destination": {
                    "namespace": data['upf_id'],
                    "server": data['location']
                },
                "project": data['project'],
                "source": {
                    "repoURL": data['repository'],
                    "path": data['path'],
                    "helm": {
                        "valueFiles": data['values']
                    }
                },
                "syncPolicy": {
                    "automated": {"selfHeal": True},
                    "syncOptions": ["CreateNamespace=true"]
                },
            }
        }

        # Send POST
        response = requests.post(url_argocd+"applications", json=req_body,
                                headers=headers, verify=False)
    else:
        return 'Only POST method, no UPF created'

@app.route("/get_sub_ul/<sub>", methods=["GET"])
def get_sub_ul(sub):
    # Send POST
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = '8 * irate(upf_session_tx_bytes{{namespace="upf1",pdr=~".*[13579]", ue_ip="{s}"}}[15s])'.format(s=sub)

    response = requests.get(url+query, verify=False).json()
    try:
        data = response['data']['result'][0]['value'][1]
        return data
    except:
        return 'no_value'

@app.route("/get_sub_dl/<sub>", methods=["GET"])
def get_sub_dl(sub):
    # Send POST
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = '8 * irate(upf_session_tx_bytes{{namespace="upf1",pdr=~".*[02468]", ue_ip="{s}"}}[15s])'.format(s=sub)

    response = requests.get(url+query, verify=False).json()
    try:
        data = response['data']['result'][0]['value'][1]
        return data
    except:
        return 'no_value'

@app.route("/get_subscribers/", methods=["GET"])
def get_subscribers():
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = 'count (smf_pdu_session_profile) by (id,ip, enterprise)'

    response = requests.get(url+query, verify=False).json()

    data = []
    for values in response['data']['result']:
        # Check if said IMSI (id) is present in the data array
        if not any(a['id'] == values['metric']['id'] for a in data):
            data.append(values['metric'])
        else:
        # If yes, update its IP address only if its bigger then the one currently saved.
            for index, metric in enumerate(data):
                if (metric['id'] == values['metric']['id']) and (ip(values['metric']['ip']) > ip(metric['ip'])):
                    data[index] = values['metric']
    try:
        return data
    except:
        return 'no_value'

@app.route("/get_subscribers/<slice>", methods=["GET"])
def get_subscribers_by_slice(slice):
    url = "http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/api/v1/query?query="
    query = 'count (smf_pdu_session_profile{{enterprise="{e}"}}) by (id,ip)'.format(e=slice)

    response = requests.get(url+query, verify=False).json()

    data = []
    for values in response['data']['result']:
        # Check if said IMSI (id) is present in the data array
        if not any(a['id'] == values['metric']['id'] for a in data):
            data.append(values['metric'])
        else:
        # If yes, update its IP address only if its bigger then the one currently saved.
            for index, metric in enumerate(data):
                if (metric['id'] == values['metric']['id']) and (ip(values['metric']['ip']) > ip(metric['ip'])):
                    data[index] = values['metric']
    try:
        return data
    except:
        return 'no_value'

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
        "password": argocd_secrets.password
    }

    url_argocd = "https://"+amp+":30001/api/v1/"
    response = requests.post(url_argocd + "session", json=req_body, verify=False)

    # Return the token value
    return json.loads(response.text)['token']

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5000"), debug=True)