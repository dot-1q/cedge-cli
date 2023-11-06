# C-Edge CLI
<p align="center">
  <img src="cedge.svg" />
</p>

#### CLI tool to manage a Connected Edge Setup, leveraging Aether/SD-Core & ArgoCD.

---
This CLI came to be because of my [own deployment](https://github.com/dot-1q/AiaB-UERANSIM), where i needed to quickly create new UPFs, Slices, add subscribers and so on, and doing so via GUI was tiresome and not enough.

As with [Aether-in-a-box](https://docs.aetherproject.org/master/developer/aiab.html) (now defunct) and [Aether OnRamp](https://github.com/opennetworkinglab/aether-onramp), the default port for both the GUI and API is *31194*, so this tool can be used with both deployments of Aether, with the exepction of the *create_upf* command, which needs ArgoCD to be installed.
```
roc_api_url = "http://localhost:31194/aether-roc-api/aether/v2.1.x/"
```

To add new subscribers to the Core we have to communicate with the SD-Core [API](https://docs.sd-core.opennetworking.org/master/configuration/config_rest.html).
This requires that we expose the *webui* pod, which is done via the SD-Core helm chart: `sd-core-5g-values.yaml`
```
...
    webui:
      serviceType: NodePort
      urlport:
        nodePort: 30002
...
```

The create_upf() method is deeply coupled with ArgoCD and how it manages helm chart deployments to a remote cluster, so it will only work if your setup is similar to mine.

### ArgoCD
The ArgoCD API enables the deployment of the UPF helm chart to any cluster that's [registered within it](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_cluster/).
These are the methods that rely on its installation:
- deploy_app()
- create_upf()

If you wish to install ArgoCD, it's API needs to be port-forwarded, so that the CLI can interact with it. In my case, I nodeport to 30001. You may need to change the base url in the `mngmt.py` file

mngmt.py file:
```
url_argocd = "https://"+spec['amp']+":30001/api/v1/"
```

NodePort ArgoCD:
```
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort", "ports": [{ "nodePort": 30001, "port": 80, "protocol": "TCP", "targetPort": 8080 }] }}'
```

## Enterprises Specification

In order to not clutter the arguments that we pass to the CLI, the enterprise(s) that will rely on the CLI need to be specified in the `enterprise.yaml` file.
The sample file provided is from my [own deployment](https://github.com/dot-1q/AiaB-UERANSIM), but can be adapted easily.

In this YAML, you should specify where the Core is (`amp`, which is where all the API reside), along with the `repository` where all the Helm Charts for the deployments are, and the cluster `locations`.

Additionally, you need to specify all the UPFs present in the network. If you add one later one, you should first update the YAML file, and only after run the `create-upf` command.

Note: The name of the sites in the `enterprise.yaml` need to be the same as the ones created upon the deployment of Aether, in the `roc-5g-models.json` file, or the ones created subsequently.

## Requirements
```
pip3 install -r requirements.txt
```

## Usage

As of now, these are all the commands available:

```
Usage: mngmt.py [OPTIONS] ENTERPRISE SITE COMMAND [ARGS]...

  Command line tool to manage Aether's ROC.

  An enterprise and site name need to be passed as all API endpoints require
  it.

Options:
  --help  Show this message and exit.

Commands:
  add-subscriber       Add a subscriber to Aether's core.
  create-device-group  Create a new device group.
  create-ip-pool       Create a new IP pool of addresses for UE's.
  create-slice         Create a new Slice.
  create-upf           Create a new UPF and deploy it.
  delete-app           Delete app deployment
  delete-device        Delete Device
  delete-slice         Delete a slice
  delete-upf           Delete a UPF
  deploy-app           Create a new ArgoCD application deployemnt.
  edit-device-group    Edit the download and upload values of an existing...
  edit-slice           Edit the download and upload values of an existing...
  get-app-status       Get health status of an app.
  get-device           Check if device exists.
  get-site             Get a description of all the sites of an enterprise.
  list-device-groups   List all device groups [NOT YET IMPLEMENTED]
  list-devices         List all devices of a device group [NOT YET...
  list-ip-pools        List all IP pools [NOT YET IMPLEMENTED]
  list-sim-cards       List all sim cards of a given Enterprise and site...
  list-slices          List all slices [NOT YET IMPLEMENTED]
  list-upfs            List all upfs [NOT YET IMPLEMENTED]
```
All the commands require you to provide a enterprise and site name, as all Aether API calls require it.

Ex:
```
python3 mngmt.py [e_name] [s_name] setup-ue newsim 208930000000000 newdevice devicegroup
```

This is an example of a command which provides optional arguments. The help page for this specific command is in the Help section below.
```
python3 mngmt.py [e_name] [s_name] create-slice --sn "Slice 4" --sd "New Slice" --mbr_dl 1000000 --mbr_dl_bs 250000 --mbr_ul 1000000 --mbr_ul_bs 250000 slice4 device-group-4 040404 4 upf4
```

To better understand this command, the next section goes over its help text.

## Help

You can bring up the definition and help documentation of any command by doing:

```
python3 mngmt.py [e_name] [s_name] create-slice --help
```

Output:
```
Usage: mngmt.py ENTERPRISE SITE create-slice [OPTIONS] SLICE_ID DEVICE_GROUP
                                             SERVICE_DIFFERENTIATOR
                                             SLICE_SERVICE_TYPE UPF_ID

      Create a new Slice. Each Slice must be in only one site and must only
      have one UPF. Multiple device groups may be added to the slice, but this
      version only supports one yet. Additional device groups must be
      configured manually through Aether ROC GUI.

      SLICE_ID is a unique indentifier for the slice. ex: "slice4"

      DEVICE_GROUP is the device group ID associated to this slice. ex: "dg4"

      SERVICE_DIFFERENTIATOR is a 6 HEX characters value for the slice. ex:
      "040404"

      SLICE_SERVICE_TYPE is SST value between 1-255. ex: "4"

      UPF_ID is the UPF ID associated to this slice. ex: "upf4"

Options:
  --sn TEXT            Slice Name  [default: Slice]
  --sd TEXT            Slice Description  [default: Network Slice]
  --mbr_dl INTEGER     Slice Maximum Bit Rate Downlink  [default: 200000000]
  --mbr_dl_bs INTEGER  Slice MBR Downlink Burst Size  [default: 12500000]
  --mbr_ul INTEGER     Slice Maximum Bit Rate Uplink  [default: 200000000]
  --mbr_ul_bs INTEGER  Slice MBR Uplink Burst Size  [default: 12500000]
  --help               Show this message and exit.
```

## TODO
As is stands, this tool does not yet do any sanity checks on input, meaning for example, if you were to create a sim card and add it to a device group that
doesn't exist, it wouldn't stop you from doing so. This is future work as well as adding more commands.
