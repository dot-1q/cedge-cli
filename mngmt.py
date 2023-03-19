import requests
import click

# Base API URL
# This if or Aether-in-a-Box and is meant to be run on the same VM that it is deployed, this means
# that on an Aether Standalone deployment the API port will be different.
roc_api_url = "http://localhost:31194/aether-roc-api/aether/v2.1.x/"


@click.group()
@click.argument('enterprise', nargs=1, type=click.STRING)
@click.argument('site', nargs=1, type=click.STRING)
@click.pass_context
def aether_cli(ctx, enterprise, site):
    """
    Command line tool to manage Aether's ROC.

    An enterprise and site name need to be passed as all API endpoints require it.
    """
    ctx.ensure_object(dict)

    # Pass the enterprise and site to all the sub commands. We need them for the API endpoint
    ctx.obj['ENTERPRISE'] = enterprise
    ctx.obj['SITE'] = site


@aether_cli.command()
@click.argument('imsi', nargs=1, type=click.INT)
@click.argument('address', nargs=1, type=click.STRING)
@click.option('--port', default=5000, type=click.INT, help='Subscriber config service Port', show_default=True)
def add_sim(imsi, address, port):
    """
    Add a subscriber to Aether's core. An imsi sim card number should be provided.

    You can find the address of the config server by running 'kubectl get svc -n omec' and noting
    the 'webui' IP address.

    IMSI is a 15 digit sim card number. ex: '208930000000000'

    ADDRESS is the address of the subscriber config server.
    """
    # SD-Core subscriber's provisioning api endpoint.
    url = "http://{a}:{p}/api/subscriber/imsi-{i}".format(
        a=address, p=port, i=imsi)
    print(url)

    req_body = {
        "UeId": str(imsi),
        "plmnId": "20893",
        "opc": "981d464c7c52eb6e5036234984ad0bcf",
        "key": "5122250214c33e723a5dd523fc145fc0",
        "sequenceNumber": "16f3b3f70fc2"
    }

    # Send POST
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument('sim-id', nargs=1, type=click.STRING)
@click.argument('device-id', nargs=1, type=click.STRING)
@click.argument('imsi', nargs=1, type=click.STRING)
@click.option('--sd', default="New Sim Card", type=click.STRING, help='Sim card description', show_default=True)
@click.option('--sn', default="New UE Sim", type=click.STRING, help='Sim card name', show_default=True)
@click.option('--dn', default="New Device", type=click.STRING, help='Device name', show_default=True)
def setup_sim(ctx, sim_id, device_id, imsi, sd, sn, dn):
    """
    Add a new sim card and device associated to it.
    This can only be done to sim card numbers that have been previously added to the ROC Core.
    Sim card name, description and device name values all have default values but they can be passed
    as optional arguments.

    SIM_ID is a unique sim identifier. ex: 'sim-12345'

    DEVICE_ID is a unique device identifier. ex: 'device-12345'

    IMSI is the sim card number. ex: '208930000000000'
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj['ENTERPRISE']
    site = ctx.obj['SITE']

    url = roc_api_url + \
        "{e}/site/{s}/sim-card/{sim}".format(e=enterprise, s=site, sim=sim_id)

    req_body = {
        "description": sd,
        "display-name": sn,
        "enable": True,
        "imsi": imsi,
        "sim-id": sim_id
    }

    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)

    ###################################################################

    url = roc_api_url + \
        "{e}/site/{s}/device/{device}".format(e=enterprise,
                                              s=site, device=device_id)

    req_body = {
        "device-id": device_id,
        "display-name": dn,
        "sim-card": sim_id,
    }

    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument('device-group', nargs=1, type=click.STRING)
@click.argument('device-id', nargs=1, type=click.STRING)
def assign_device_group(ctx, device_group, device_id):
    """
    Assign a device to a device group.

    DEVICE_ID is the device identifier. ex: 'device-12345'.

    DEVICE_GROUP is the device-group identifier. ex: 'dg4'.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj['ENTERPRISE']
    site = ctx.obj['SITE']

    url = roc_api_url + "{e}/site/{s}/device-group/{dg}/device/{d}".format(
        e=enterprise, s=site, dg=device_group, d=device_id)

    req_body = {
        "device-id": device_id,
        "enable": True
    }

    # Send POST
    response = requests.post(url, json=req_body)
    print(response)
    print(response.content)


@aether_cli.command()
@click.pass_context
@click.argument('upf-id', nargs=1, type=click.STRING)
@click.argument('address', nargs=1, type=click.STRING)
@click.argument('config_endpoint', nargs=1, type=click.STRING)
@click.option('--un', default="UPF", type=click.STRING, help='UPF Name', show_default=True)
@click.option('--ud', default="User Plane Function", type=click.STRING, help='UPF Description', show_default=True)
@click.option('--up', default=8805, type=click.INT, help='UPF Port', show_default=True)
def create_upf(ctx, upf_id, address, config_endpoint, un, ud, up):
    """
    Create a new UPF. Each UPF can only be associated with a single site and slice.

    UPF_ID is a unique identifies for the new UPF. ex: "upf4"

    ADDRESS is the address of the UPF. ex: "10.10.1.4"

    CONFIG_ENDPOINT is the address of the config endpoint of the UPF. ex: "http://10.10.1.4:8080"
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj['ENTERPRISE']
    site = ctx.obj['SITE']

    url = roc_api_url + \
        "{e}/site/{s}/upf/{u}".format(e=enterprise, s=site, u=upf_id)

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
    print(respone)
    print(response.content)

# TODO: Add multiple device groups to a slice


@aether_cli.command()
@click.pass_context
@click.argument('slice-id', nargs=1, type=click.STRING)
@click.argument('device-group', nargs=1, type=click.STRING)
@click.argument('service-differentiator', nargs=1, type=click.STRING)
@click.argument('slice-service-type', nargs=1, type=click.STRING)
@click.argument('upf_id', nargs=1, type=click.STRING)
@click.option('--sn', default="Slice", type=click.STRING, help='Slice Name', show_default=True)
@click.option('--sd', default="Network Slice", type=click.STRING, help='Slice Description', show_default=True)
@click.option('--mbr_dl', default=100000000, type=click.INT, help='Slice Maximum Bit Rate Downlink', show_default=True)
@click.option('--mbr_dl_bs', default=625000, type=click.INT, help='Slice MBR Downlink Burst Size', show_default=True)
@click.option('--mbr_ul', default=100000000, type=click.INT, help='Slice Maximum Bit Rate Uplink', show_default=True)
@click.option('--mbr_ul_bs', default=625000, type=click.INT, help='Slice MBR Uplink Burst Size', show_default=True)
def create_slice(ctx, slice_id, device_group, service_differentiator, slice_service_type, upf_id, sn, sd, mbr_dl, mbr_dl_bs, mbr_ul, mbr_ul_bs):
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
    enterprise = ctx.obj['ENTERPRISE']
    site = ctx.obj['SITE']

    url = roc_api_url + \
        "{e}/site/{s}/slice/{sl}".format(e=enterprise, s=site, sl=slice_id)

    req_body = {
        "connectivity-service": "5g",
        "default-behavior": "ALLOW-ALL",
        "description": sd,
        "device-group": [
            {
                "device-group": device_group,
                "enable": True
            }
            # TODO: Multiple device groups go here
        ],
        "display-name": sn,
        "mbr": {
            "downlink": mbr_dl,
            "downlink-burst-size": mbr_dl_bs,
            "uplink": mbr_ul,
            "uplink-burst-size": mbr_ul_bs
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
def get_site(ctx):
    """
    Get a description of all the sites of an enterprise.
    """

    # Grab the enterprise and site from the command line for the api endpoint
    enterprise = ctx.obj['ENTERPRISE']

    url = roc_api_url + "{e}/site".format(e=enterprise)
    response = requests.get(url)
    print(response)
    print(response.content)


if __name__ == '__main__':
    aether_cli()
