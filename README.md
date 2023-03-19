# Aether ROC CLI tool to manage an Aether Deployment.

This is a simple command line tool that I created to help me manage my Aether-In-a-Box deployment. It is still very early stages and I've only implemented 
the API calls that I use the most.
Since this was initially for AiaB, if you wish to use it for a standalone environment you have to change the base API URL:
```
roc_api_url = "http://localhost:31194/aether-roc-api/aether/v2.1.x/"
```

To add new subscribers to the Core we have to communicate with a different [API](https://docs.sd-core.opennetworking.org/master/configuration/config_rest.html).
This requires that we grab the config service IP address that's located on the omec namespace and note the _webui_ service IP address:
```
kubectl get svc -n omec
```

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
  add-sim              Add a subscriber to Aether's core.
  assign-device-group  Assign a device to a device group.
  create-slice         Create a new Slice.
  create-upf           Create a new UPF.
  get-site             Get a description of all the sites of an enterprise.
  setup-sim            Add a new sim card and device associated to it.
```
All the commands require you to provide a enterprise and site name, as all API calls require it.
Ex:
```
python3 mngmt.py ename sname setup-sim newsim newdevice 208930000000000
```

This is an example of a command which provides optional arguments. The help page for this specific command is in the Help section below.
```
python3 mngmt.py a a create-slice --sn "Slice 4" --sd "New Slice" --mbr_dl 1000000 --mbr_dl_bs 250000 --mbr_ul 1000000 --mbr_ul_bs 250000 slice4 dg4 040404 4 upf4
```

## Help

You can bring up the definition and help documentation of any command by doing:

```
python3 mngmt.py ename sname COMMAND --help
```

Example output of command _python3 mngmt.py ename sname create-slice --help_
```
Usage: mngmt.py ENTERPRISE SITE create-slice [OPTIONS] SLICE_ID DEVICE_GROUP
                                             SERVICE_DIFFERENTIATOR
                                             SLICE_SERVICE_TYPE UPF_ID

  Create a new Slice. Each Slice must be in only one site and must only have
  one UPF. Multiple device groups  may be added to the slice, but this version
  does not yet support this.

  SLICE_ID is a unique indentifier for the slice. ex: "slice4"

  DEVICE_GROUP is the device group ID associated to this slice. ex: "dg4"

  SERVICE_DIFFERENTIATOR is a 6 HEX characters value for the slice. ex:
  "040404"

  SLICE_SERVICE_TYPE is SST value between 1-255. ex: "4"

  UPF_ID is the UPF ID associated to this slice. ex: "upf4"

Options:
  --sn TEXT            Slice Name  [default: Slice]
  --sd TEXT            Slice Description  [default: Network Slice]
  --mbr_dl INTEGER     Slice Maximum Bit Rate Downlink  [default: 100000000]
  --mbr_dl_bs INTEGER  Slice MBR Downlink Burst Size  [default: 625000]
  --mbr_ul INTEGER     Slice Maximum Bit Rate Uplink  [default: 100000000]
  --mbr_ul_bs INTEGER  Slice MBR Uplink Burst Size  [default: 625000]
  --help               Show this message and exit.
```