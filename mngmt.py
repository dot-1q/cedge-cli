import requests
import click
import os
import json

# Base API URL
# This if or Aether-in-a-Box and is meant to be run on the same VM that it is deployed, this means
# that on an Aether Standalone deployment the API port will be different.
roc_api_url = "http://localhost:31194/aether-roc-api/aether/v2.1.x/"


@click.group()
@click.argument("enterprise", nargs=1, type=click.STRING)
@click.argument("site", nargs=1, type=click.STRING)
@click.pass_context
def aether_cli(ctx, enterprise, site):
    """
    Command line tool to manage Aether's ROC.

    An enterprise and site name need to be passed as all API endpoints require it.
    """
    ctx.ensure_object(dict)

    # Pass the enterprise and site to all the sub commands. We need them for the API endpoint
    ctx.obj["ENTERPRISE"] = enterprise
    ctx.obj["SITE"] = site


@aether_cli.command()
@click.argument("imsi", nargs=1, type=click.STRING)
@click.argument("plmn", nargs=1, type=click.STRING)
@click.argument("address", nargs=1, type=click.STRING)
@click.option(
    "--port",
    default=5000,
    type=click.INT,
    help="Subscriber config service Port",
    show_default=True,
)
@click.option(
    "--opc",
    default="981d464c7c52eb6e5036234984ad0bcf",
    type=click.STRING,
    help="OPC code",
    show_default=True,
)
@click.option(
    "--key",
    default="5122250214c33e723a5dd523fc145fc0",
    type=click.STRING,
    help="Key code",
    show_default=True,
)
@click.option(
    "--sqn",
    default="16f3b3f70fc2",
    type=click.STRING,
    help="Sequence number",
    show_default=True,
)
def add_sim(imsi, plmn, address, port, opc, key, sqn):
    """
    Add a subscriber to Aether's core. An imsi sim card number should be provided.

    You can find the address of the config server by running 'kubectl get svc -n omec' and noting
    the 'webui' IP address.

    IMSI is a 15 digit sim card number. ex: '208930000000000'

    PLMN is the PLMN code. ex: '20893'

    ADDRESS is the address of the subscriber config server.
    """
    # SD-Core subscriber's provisioning api endpoint.
    url = "http://{a}:{p}/api/subscriber/imsi-{i}".format(a=address, p=port, i=imsi)

    req_body = {
        "UeId": imsi,
        "plmnId": plmn,
        "opc": opc,
        "key": key,
        "sequenceNumber": sqn,
    }

    # Send POST
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument("sim-id", nargs=1, type=click.STRING)
@click.argument("imsi", nargs=1, type=click.STRING)
@click.argument("device-id", nargs=1, type=click.STRING)
@click.argument("device-group", nargs=1, type=click.STRING)
@click.option(
    "--sd",
    default="New Sim Card",
    type=click.STRING,
    help="Sim card description",
    show_default=True,
)
@click.option(
    "--sn",
    default="New UE Sim",
    type=click.STRING,
    help="Sim card name",
    show_default=True,
)
@click.option(
    "--dn",
    default="New Device",
    type=click.STRING,
    help="Device name",
    show_default=True,
)
@click.option(
    "--dd",
    default="UE Device",
    type=click.STRING,
    help="Device description",
    show_default=True,
)
def setup_ue(ctx, sim_id, imsi, device_id, device_group, sd, sn, dn, dd):
    """
    Add a new sim card, device and assign it to device group.
    This can only be done to sim card numbers that have been previously added to the ROC Core.
    Sim card name, description and device name values all have default values but they can be passed
    as optional arguments.

    SIM_ID is a unique sim identifier. ex: 'sim-12345'

    IMSI is the sim card number. ex: '208930000000000'

    DEVICE_ID is a unique device identifier. ex: 'device-12345'

    DEVICE_GROUP is the device-group identifier. ex: 'dg4'.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/sim-card/{sim}".format(
        e=enterprise, s=site, sim=sim_id
    )

    req_body = {
        "description": sd,
        "display-name": sn,
        "enable": True,
        # "iccid": "string", # Not using this at the moment.
        "imsi": imsi,
        "sim-id": sim_id,
    }

    # Create SIM
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)

    ###################################################################

    url = roc_api_url + "{e}/site/{s}/device/{device}".format(
        e=enterprise, s=site, device=device_id
    )

    req_body = {
        "description": dd,
        "device-id": device_id,
        "display-name": dn,
        # "imei": "string", # Not using this at the moment.
        "sim-card": sim_id,
    }

    # Create Device
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)

    # 3

    url = roc_api_url + "{e}/site/{s}/device-group/{dg}/device/{d}".format(
        e=enterprise, s=site, dg=device_group, d=device_id
    )

    req_body = {"device-id": device_id, "enable": True}

    # Assign to device group
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument("upf-id", nargs=1, type=click.STRING)
@click.argument("address", nargs=1, type=click.STRING)
@click.argument("config_endpoint", nargs=1, type=click.STRING)
@click.argument("repo", nargs=1, type=click.STRING)
@click.argument("path", nargs=1, type=click.STRING)
@click.argument("cluster", nargs=1, type=click.STRING)
@click.argument("values", nargs=1, type=click.STRING)
@click.argument("app_name", nargs=1, type=click.STRING)
@click.option(
    "--un", default="UPF", type=click.STRING, help="UPF Name", show_default=True
)
@click.option(
    "--ud",
    default="User Plane Function",
    type=click.STRING,
    help="UPF Description",
    show_default=True,
)
@click.option("--up", default=8805, type=click.INT, help="UPF Port", show_default=True)
@click.option(
    "--ap",
    default="default",
    type=click.STRING,
    help="App deployment project",
    show_default=True,
)
def create_upf(
    ctx,
    upf_id,
    address,
    config_endpoint,
    repo,
    path,
    cluster,
    values,
    app_name,
    un,
    ud,
    up,
    ap,
):
    """
    Create a new UPF. Each UPF can only be associated with a single site and slice.

    UPF_ID is a unique identifies for the new UPF. ex: "upf4"

    ADDRESS is the address of the UPF. ex: "10.10.1.4"

    CONFIG_ENDPOINT is the address of the config endpoint of the UPF. ex: "http://10.10.1.4:8080"

    REPO is the address of the github repo where the upf helm chart is. ex: "https://github.com/dot-1q/5g_connected_edge.git"

    PATH is the path of the folder where the helm chart is. ex: "site3/upf4_helm"

    CLUSTER is IP address of the cluster. Could be local or external. ex: "https://10.0.30.154:6443"

    VALUES is the name of the override helm chart values file. ex: "values_upf4.yaml"

    APP_NAME is the name of the deployment name for ArgoCD. ex: "site3-upf4"
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/upf/{u}".format(e=enterprise, s=site, u=upf_id)
    url_argocd = "https://localhost:30001/api/v1/applications"

    req_body = {
        "address": address,
        "config-endpoint": config_endpoint,
        "description": ud,
        "display-name": un,
        "port": up,
        "upf-id": upf_id,
    }

    # Send POST
    response = requests.post(url, json=req_body)
    print(response)

    # Use the Argocd API to create the upf app deployment
    token = get_argocd_token()
    headers = {
        'Authorization': 'Bearer '+ token,
    }

    req_body = {
        "metadata":{
                "name": app_name,
        },
        "spec": {
            "destination": {
                "namespace": upf_id,
                "server": cluster
            },
            "project": ap,
            "source": {
                "repoURL": repo,
                "path": path,
                "helm": {
                    "valueFiles": [values]
                }
            },
            "syncPolicy": {
                "automated": {"selfHeal": True},
                "syncOptions": ["CreateNamespace=true"]
            },
        }
    }

    # Send POST
    response = requests.post(url_argocd, json=req_body, headers=headers, verify=False)
    print(response)
    print("Created UPF deployment")


@aether_cli.command()
@click.pass_context
@click.argument("slice-id", nargs=1, type=click.STRING)
@click.argument("device-group", nargs=1, type=click.STRING)
@click.argument("service-differentiator", nargs=1, type=click.STRING)
@click.argument("slice-service-type", nargs=1, type=click.STRING)
@click.argument("upf_id", nargs=1, type=click.STRING)
@click.option(
    "--sn", default="Slice", type=click.STRING, help="Slice Name", show_default=True
)
@click.option(
    "--sd",
    default="Network Slice",
    type=click.STRING,
    help="Slice Description",
    show_default=True,
)
@click.option(
    "--mbr_dl",
    default=100000000,
    type=click.INT,
    help="Slice Maximum Bit Rate Downlink",
    show_default=True,
)
@click.option(
    "--mbr_dl_bs",
    default=625000,
    type=click.INT,
    help="Slice MBR Downlink Burst Size",
    show_default=True,
)
@click.option(
    "--mbr_ul",
    default=100000000,
    type=click.INT,
    help="Slice Maximum Bit Rate Uplink",
    show_default=True,
)
@click.option(
    "--mbr_ul_bs",
    default=625000,
    type=click.INT,
    help="Slice MBR Uplink Burst Size",
    show_default=True,
)
# TODO: Add multiple device groups to a slice
def create_slice(
    ctx,
    slice_id,
    device_group,
    service_differentiator,
    slice_service_type,
    upf_id,
    sn,
    sd,
    mbr_dl,
    mbr_dl_bs,
    mbr_ul,
    mbr_ul_bs,
):
    """
    Create a new Slice. Each Slice must be in only one site and must only have one UPF. Multiple device groups
    may be added to the slice, but this version does not yet support this.

    SLICE_ID is a unique indentifier for the slice. ex: "slice4"

    DEVICE_GROUP is the device group ID associated to this slice. ex: "dg4"

    SERVICE_DIFFERENTIATOR is a 6 HEX characters value for the slice. ex: "040404"

    SLICE_SERVICE_TYPE is SST value between 1-255. ex: "4"

    UPF_ID is the UPF ID associated to this slice. ex: "upf4"
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/slice/{sl}".format(
        e=enterprise, s=site, sl=slice_id
    )

    req_body = {
        "connectivity-service": "5g",
        "default-behavior": "ALLOW-ALL",
        "description": sd,
        "device-group": [
            {"device-group": device_group, "enable": True}
            # TODO: Multiple device groups go here
        ],
        "display-name": sn,
        "mbr": {
            "downlink": mbr_dl,
            "downlink-burst-size": mbr_dl_bs,
            "uplink": mbr_ul,
            "uplink-burst-size": mbr_ul_bs,
        },
        "sd": service_differentiator,
        "slice-id": slice_id,
        "sst": slice_service_type,
        "upf": upf_id,
    }

    # Send POST
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument("device_group_id", nargs=1, type=click.STRING)
@click.argument("traffic_class", nargs=1, type=click.STRING)
@click.argument("ip_domain", nargs=1, type=click.STRING)
@click.argument("device-id", nargs=1, type=click.STRING)
@click.option(
    "--dgn",
    default="Device Group",
    type=click.STRING,
    help="Device Group Name",
    show_default=True,
)
@click.option(
    "--dgd",
    default="Device Group for UE's",
    type=click.STRING,
    help="Device Group Description",
    show_default=True,
)
@click.option(
    "--mbr_dl",
    default=20000000,
    type=click.INT,
    help="Device Group MBR Dowlink",
    show_default=True,
)
@click.option(
    "--mbr_ul",
    default=20000000,
    type=click.INT,
    help="Device Group MBR Uplink",
    show_default=True,
)
# TODO: Allow passing multiple device id's
def create_device_group(
    ctx, device_group_id, traffic_class, ip_domain, device_id, dgn, dgd, mbr_dl, mbr_ul
):
    """
    Create a new device group.

    DEVICE_GROUP_ID must be an unique idenfitifer. ex: "devgroup1"

    TRAFFIC_CLASS is the ID of the traffic class this group belongs to. ex: "class-1"

    IP_DOMAIN is the ID of the IP pool from where these devices get their addresses from. ex: "pool5"

    DEVICE_ID is the ID of a device that belongs to this group.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/device-group/{dg}".format(
        e=enterprise, s=site, dg=device_group_id
    )

    req_body = {
        "description": dgd,
        "device": [
            {"device-id": device_id, "enable": True}
            # TODO: Multiple device id's go here
        ],
        "device-group-id": device_group_id,
        "display-name": dgn,
        "ip-domain": ip_domain,
        "mbr": {
            "downlink": mbr_dl,
            "uplink": mbr_ul,
        },
        "traffic-class": traffic_class,
    }

    # Send POST
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument("ip-pool-id", nargs=1, type=click.STRING)
@click.argument("dnn", nargs=1, type=click.STRING)
@click.argument("subnet", nargs=1, type=click.STRING)
@click.argument("mtu", nargs=1, type=click.INT)
@click.option(
    "--ipn",
    default="IP pool",
    type=click.STRING,
    help="IP pool name",
    show_default=True,
)
@click.option(
    "--ipd",
    default="IP addresses for UE's",
    type=click.STRING,
    help="IP pool description",
    show_default=True,
)
@click.option(
    "--dnsp",
    default="1.1.1.1",
    type=click.STRING,
    help="Primary DNS server",
    show_default=True,
)
@click.option(
    "--dnss",
    default="1.0.0.1",
    type=click.STRING,
    help="Secondary DNS server",
    show_default=True,
)
def create_ip_pool(ctx, ip_pool_id, dnn, subnet, mtu, ipn, ipd, dnsp, dnss):
    """
    Create a new IP pool of addresses for UE's.

    IP_POOL_ID is a unique identifier for this IP pool. ex: "pool5"

    DNN is  the Data Network Name for this pool. ex: "internet"

    SUBNET is the range of IP addresses. ex: "172.5.0.0/16"

    MTU is the maximum transmission unit value. ex: 1450
    """
    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/ip-domain/{id}".format(
        e=enterprise, s=site, id=ip_pool_id
    )

    req_body = {
        "admin-status": "ENABLE",
        "description": ipd,
        "display-name": ipn,
        "dnn": dnn,
        "dns-primary": dnsp,
        "dns-secondary": dnss,
        "ip-domain-id": ip_pool_id,
        "mtu": mtu,
        "subnet": subnet,
    }

    # Send POST
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
def get_site(ctx):
    """
    Get a description of all the sites of an enterprise.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]

    url = roc_api_url + "{e}/site".format(e=enterprise)
    response = requests.get(url)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
def list_devices(ctx):
    """
    List all devices of a given device group.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_device_groups(ctx):
    """
    List all device groups
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_sim_cards(ctx):
    """
    List all sim cards of a given Enterprise and site.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_slices(ctx):
    """
    List all slices.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_upfs(ctx):
    """
    List all upfs.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_ip_pools(ctx):
    """
    List all IP pools.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def get_apps(ctx):
    """
    List all the deployed apps on all clusters
    """
    os.system("argocd app list")


@aether_cli.command()
@click.pass_context
@click.argument("name", nargs=1, type=click.STRING)
@click.argument("repo", nargs=1, type=click.STRING)
@click.argument("path", nargs=1, type=click.STRING)
@click.argument("cluster", nargs=1, type=click.STRING)
@click.option(
    "--ap",
    default="default",
    type=click.STRING,
    help="Application deployment project",
    show_default=True,
)
@click.option(
    "--dns",
    default="default",
    type=click.STRING,
    help="Application deployment namespace",
    show_default=True,
)
def deploy_app(ctx, name, repo, path, cluster, ap, dns):
    """
    Create a new ArgoCD application deployemnt. This command can be used to deploy the router needed for the k8s cluster,
    as well as deployment the edge services on any remote cluster

    NAME is the name of the deployment. ex: "site3-router"

    REPO is the address of the github repo that manages this deployment. ex: "https://github.com/dot-1q/5g_connected_edge.git"

    PATH is the path of the folder where the k8s deployment file is. ex: "site3/router"

    CLUSTER is IP address of the cluster. Could be local or external. ex: "https://10.0.30.154:6443"
    """

    url = "https://localhost:30001/api/v1/applications"
    token = get_argocd_token()
    headers = {
        'Authorization': 'Bearer '+ token,
    }

    req_body = {
        "metadata":{
                "name": name
        },
        "spec": {
            "destination": {
                "namespace": dns,
                "server": cluster,
            },
            "project": ap,
            "source": {
                "repoURL": repo,
                "path": path,
            },
            "syncPolicy": {
                "automated": {"selfHeal": True},
                "syncOptions": ["CreateNamespace=true"]
            },
        }
    }

    # Send POST
    response = requests.post(url, json=req_body, headers=headers, verify=False)
    print(response)
    

def get_argocd_token():
    """
    Get Bearer ArgoCD API token
    """

    url = "https://localhost:30001/api/v1/session"

    # This loads the file that contains the ArgoCD secrets
    # You should create a file with the same name that has your 
    # Username and password
    import argocd_secrets
    req_body = {
        "username": argocd_secrets.username,
        "password": argocd_secrets.password
    }

    response = requests.post(url,json=req_body,verify=False)

    # Return the token value
    return json.loads(response.text)['token']


if __name__ == "__main__":
    aether_cli()
