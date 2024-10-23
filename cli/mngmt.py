import requests
import click
import os
import json
import yaml
from yaml.loader import SafeLoader
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Load the enterprise YAML description
with open("enterprise.yaml") as f:
    spec = yaml.load(f, Loader=SafeLoader)

# Base API URL
# This if or Aether-in-a-Box and is meant to be run on the same VM that it is deployed, this means
# that on an Aether Standalone deployment the API port will be different.
# The IP of the  Aether Management Platform is defined in the yaml
roc_api_url = "http://" + spec["amp"] + ":31194/aether-roc-api/aether/v2.1.x/"
webui_url = "http://" + spec["amp"] + ":30002/api/subscriber/"
url_argocd = "https://" + spec["amp"] + ":30001/api/v1/"


@click.group()
@click.argument("enterprise", nargs=1, type=click.STRING)
@click.argument("site", nargs=1, type=click.STRING)
@click.pass_context
def aether_cli(ctx, enterprise, site):
    """

    Args:
        ctx ():
        enterprise ():
        site ():
    """
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
@click.argument("sim-id", nargs=1, type=click.STRING)
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
@click.option(
    "--opc",
    default="28a182edf3c70667a90a66c619cec91f",
    type=click.STRING,
    help="OPC code",
    show_default=True,
)
@click.option(
    "--key",
    default="fd4b1e644a2dd4d2c8c03cf5fe12238d",
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
@click.pass_context
def add_subscriber(
    ctx, imsi, plmn, sim_id, device_id, device_group, opc, key, sqn, sd, sn, dn, dd
):
    """
    Add a subscriber to Aether's core. This command first introduces the new subscriber IMSI to
    the SD-Core database, and then configures the SIM-Card, Device and Device-Group in Aether ROC.
    Sim card name, description and device name values all have default values but they can be passed
    as optional arguments.

    IMSI is a 15 digit sim card number. ex: '208930000000000'

    PLMN is the PLMN code. ex: '20893'

    SIM_ID is a unique sim identifier. ex: 'sim-12345'

    IMSI is the sim card number. ex: '208930000000000'

    DEVICE_ID is a unique device identifier. ex: 'device-12345'

    DEVICE_GROUP is the device-group identifier. ex: 'dg4'.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    # SD-Core subscriber's provisioning api endpoint.
    url = webui_url + "imsi-{i}".format(i=imsi)

    req_body = {
        "UeId": imsi,
        "plmnId": plmn,
        "opc": opc,
        "key": key,
        "sequenceNumber": sqn,
    }

    # Send POST
    # Add to SD-Core
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)

    ################## Aether ROC Phase #################################

    # Create SIM [Start]
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

    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)
    # Create SIM [End]

    # Create Device [Start]
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

    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)
    # Create Device [End]

    # Add Device to device group [Start]
    url = roc_api_url + "{e}/site/{s}/device-group/{dg}/device/{d}".format(
        e=enterprise, s=site, dg=device_group, d=device_id
    )

    req_body = {"device-id": device_id, "enable": True}

    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)
    # Add Device to device group [End]


@aether_cli.command()
@click.pass_context
@click.argument("upf-id", nargs=1, type=click.STRING)
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
@click.option(
    "--ap",
    default="default",
    type=click.STRING,
    help="App deployment project",
    show_default=True,
)
def create_upf(ctx, upf_id, un, ud, ap):
    """
    Create a new UPF and deploy it. Each UPF can only be associated with a single site and slice.

    UPF_ID is a unique identifier for the new UPF. ex: "upf4"
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/upf/{u}".format(e=enterprise, s=site, u=upf_id)

    req_body = {
        "address": spec[enterprise]["upfs"][upf_id]["address"],
        "config-endpoint": spec[enterprise]["upfs"][upf_id]["endpoint"],
        "description": ud,
        "display-name": un,
        "port": spec[enterprise]["upfs"][upf_id]["port"],
        "upf-id": upf_id,
    }

    # Send POST
    response = requests.post(url, json=req_body)

    print(response)
    print(response.content)

    # Use the Argocd API to create the upf app deployment
    token = _get_argocd_token()
    headers = {
        "Authorization": "Bearer " + token,
    }

    req_body = {
        "metadata": {
            "name": site + "-" + upf_id,
        },
        "spec": {
            "destination": {
                "namespace": upf_id,
                "server": spec[enterprise]["locations"][site],
            },
            "project": ap,
            "source": {
                "repoURL": spec[enterprise]["repository"],
                "path": spec[enterprise]["upfs"][upf_id]["path"],
                "helm": {"valueFiles": [spec[enterprise]["upfs"][upf_id]["values"]]},
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
    default=200000000,
    type=click.INT,
    help="Slice Maximum Bit Rate Downlink",
    show_default=True,
)
@click.option(
    "--mbr_dl_bs",
    default=12500000,
    type=click.INT,
    help="Slice MBR Downlink Burst Size",
    show_default=True,
)
@click.option(
    "--mbr_ul",
    default=200000000,
    type=click.INT,
    help="Slice Maximum Bit Rate Uplink",
    show_default=True,
)
@click.option(
    "--mbr_ul_bs",
    default=12500000,
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
        Create a new Slice. Each Slice must be in only one site and must only have one UPF. Multiple device groups may be added to the slice, but this
    version only supports one yet. Additional device groups must be configured manually through Aether ROC GUI.

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
@click.argument("slice-id", nargs=1, type=click.STRING)
@click.option(
    "--download",
    default=2000000000,
    type=click.INT,
    help="Download bandwidth",
    show_default=True,
)
@click.option(
    "--upload",
    default=2000000000,
    type=click.INT,
    help="Upload bandwidth",
    show_default=True,
)
@click.option(
    "--mbr_dl_bs",
    default=12500000,
    type=click.INT,
    help="Slice MBR Downlink Burst Size",
    show_default=True,
)
@click.option(
    "--mbr_ul_bs",
    default=12500000,
    type=click.INT,
    help="Slice MBR Uplink Burst Size",
    show_default=True,
)
# TODO: Add multiple device groups to a slice
def edit_slice(ctx, slice_id, download, upload, mbr_dl_bs, mbr_ul_bs):
    """
    Edit the download and upload values of an existing slice.

    SLICE_ID is a unique identifier for the slice. ex: "slice4"

    DOWNLOAD is the value for the download limit in bps. ex: "2000000000"

    UPLOAD is the value for the UPLOAD limit in bps. ex: "2000000000"

    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/slice/{sl}/mbr".format(
        e=enterprise, s=site, sl=slice_id
    )

    req_body = {
        "downlink": download,
        "downlink-burst-size": mbr_dl_bs,
        "uplink": upload,
        "uplink-burst-size": mbr_ul_bs,
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
@click.argument("device_group", nargs=1, type=click.STRING)
@click.option(
    "--download",
    default=2000000000,
    type=click.INT,
    help="Download bandwidth",
    show_default=True,
)
@click.option(
    "--upload",
    default=2000000000,
    type=click.INT,
    help="Upload bandwidth",
    show_default=True,
)
def edit_device_group(ctx, device_group, download, upload):
    """
    Edit the download and upload values of an existing device group.

    DEVICE_GROUP is a unique indentifier for the device group. ex: "device-group-2"

    DOWNLOAD is the value for the download limit in bps. ex: "2000000000"

    UPLOAD is the value for the UPLOAD limit in bps. ex: "2000000000"

    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/device-group/{dg}/mbr".format(
        e=enterprise, s=site, dg=device_group
    )

    req_body = {
        "downlink": download,
        "uplink": upload,
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
    default="8.8.8.8",
    type=click.STRING,
    help="Primary DNS server",
    show_default=True,
)
@click.option(
    "--dnss",
    default="8.8.8.8",
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
@click.argument("device_id", nargs=1, type=click.STRING)
def get_device(ctx, device_id):
    """
    Check if device exists.

    DEVICE_ID is the unique indentifier of the device.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/device/{d}".format(
        e=enterprise, s=site, d=device_id
    )
    response = requests.get(url)
    print(response.status_code)


@aether_cli.command()
@click.pass_context
def get_site(ctx):
    """
    Get a description of all the sites of an enterprise.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]

    url = roc_api_url + "{e}/site/".format(e=enterprise)
    response = requests.get(url)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument("device_id", nargs=1, type=click.STRING)
@click.argument("device_group", nargs=1, type=click.STRING)
@click.argument("sim_id", nargs=1, type=click.STRING)
@click.argument("imsi", nargs=1, type=click.STRING)
def delete_device(ctx, device_id, device_group, sim_id, imsi):
    """
    Delete Device

    DEVICE_ID is a unique identifier of the device.
    DEVICE_GROOUP is a unique identifier of the device group.
    SIM_ID is a unique identifier of the sim card.
    IMSI is the imsi number of the device.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    # Delete from Device Group
    url = roc_api_url + "{e}/site/{s}/device-group/{dg}/device/{d}".format(
        e=enterprise, s=site, dg=device_group, d=device_id
    )
    response = requests.delete(url)
    print(response)
    print(response.content)

    # Delete from Device List
    url = roc_api_url + "{e}/site/{s}/device/{d}".format(
        e=enterprise, s=site, d=device_id
    )
    response = requests.delete(url)
    print(response)
    print(response.content)

    # Delete from SIM Cards
    url = roc_api_url + "{e}/site/{s}/sim-card/{sim}".format(
        e=enterprise, s=site, sim=sim_id
    )
    response = requests.delete(url)
    print(response)
    print(response.content)

    # Delete from SD-Core
    url = webui_url + "imsi-{i}".format(i=imsi)
    response = requests.delete(url)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
def list_devices(ctx):
    """
    List all devices of a device group [NOT YET IMPLEMENTED]
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_device_groups(ctx):
    """
    List all device groups [NOT YET IMPLEMENTED]
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_sim_cards(ctx):
    """
    List all sim cards of a given Enterprise and site [NOT YET IMPLEMENTED]
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_slices(ctx):
    """
    List all slices [NOT YET IMPLEMENTED]
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_upfs(ctx):
    """
    List all upfs [NOT YET IMPLEMENTED]
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
def list_ip_pools(ctx):
    """
    List all IP pools [NOT YET IMPLEMENTED]
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]


@aether_cli.command()
@click.pass_context
@click.argument("app_name", nargs=1, type=click.STRING)
def get_app_status(ctx, app_name):
    """
    Get health status of an app.

    APP_NAME is a unique identifier for the deployment of an application.
    """

    # Use the Argocd API to create the upf app deployment
    token = _get_argocd_token()
    headers = {
        "Authorization": "Bearer " + token,
    }

    # Send POST
    response = requests.get(
        url_argocd + "applications/" + app_name, headers=headers, verify=False
    )
    data = response.json()
    print(data["status"]["health"]["status"])


@aether_cli.command()
@click.pass_context
@click.argument("name", nargs=1, type=click.STRING)
@click.argument("path", nargs=1, type=click.STRING)
@click.option(
    "--helm",
    is_flag=True,
    default=False,
    help="Application is an Helm chart",
    show_default=True,
)
@click.option(
    "--values",
    default="values.yaml",
    type=click.STRING,
    help="Value file for Helm Chart",
    show_default=True,
)
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
def deploy_app(ctx, name, path, helm, values, ap, dns):
    """
    Create a new ArgoCD application deployemnt. This command can be used to deploy any Kubernetes application in any given cluster.

    NAME is the name of the deployment. ex: "site3-upf"

    PATH is the path of the folder where the k8s deployment file is. ex: "site3/upf"

    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    token = _get_argocd_token()
    headers = {
        "Authorization": "Bearer " + token,
    }

    req_body = {
        "metadata": {"name": name},
        "spec": {
            "destination": {
                "namespace": dns,
                "server": spec[enterprise]["locations"][site],
            },
            "project": ap,
            "source": {
                "repoURL": spec[enterprise]["repository"],
                "path": path,
                "helm" if helm is True else "": (
                    ({"valueFiles": [values]}) if helm is True else ""
                ),
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
    print(response)


@aether_cli.command()
@click.pass_context
@click.argument("app_name", nargs=1, type=click.STRING)
def delete_app(ctx, app_name):
    """
    Delete app deployment

    APP_NAME is a unique identifier for the deployment of an application.
    """

    # Use the Argocd API to create the upf app deployment
    token = _get_argocd_token()
    headers = {
        "Authorization": "Bearer " + token,
    }

    # Send POST
    response = requests.delete(
        url_argocd + "applications/" + app_name, headers=headers, verify=False
    )

    print(response)


@aether_cli.command()
@click.pass_context
@click.argument("slice_id", nargs=1, type=click.STRING)
def delete_slice(ctx, slice_id):
    """
    Delete a slice

    SLICE_ID is a unique identifier for the slice
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/slice/{sl}".format(
        e=enterprise, s=site, sl=slice_id
    )

    req_body = {
        "enterprise-id": enterprise,
        "site-id": site,
        "slice-id": slice_id,
    }

    # Send POST
    response = requests.delete(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument("upf_id", nargs=1, type=click.STRING)
def delete_upf(ctx, upf_id):
    """
    Delete a UPF

    UPF_ID is a unique identifier for the UPF
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj["ENTERPRISE"]
    site = ctx.obj["SITE"]

    url = roc_api_url + "{e}/site/{s}/upf/{u}".format(e=enterprise, s=site, u=upf_id)

    req_body = {
        "enterprise-id": enterprise,
        "site-id": site,
        "upf-id": upf_id,
    }

    # Send POST
    response = requests.delete(url, json=req_body)
    print(response)
    print(response.content)


def _get_argocd_token():
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

    response = requests.post(url_argocd + "session", json=req_body, verify=False)

    # Return the token value
    return json.loads(response.text)["token"]


if __name__ == "__main__":
    aether_cli()
