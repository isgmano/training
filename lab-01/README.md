# Lab 01 Instructions

## Overview

This lab uses [snappi](https://github.com/open-traffic-generator/snappi) to control the free Ixia-c Community Edition (OTG Test Tool) which is deployed via vanilla Docker Engine commands and utilized to send raw traffic in a back-to-back topology. This lab consists of 1x Keng Controller and 2x Ixia-c Traffic Engine containers.
The test script has been already created before this lab. The test includes only raw traffic (no protocol emulation) and performs the following actions:
- Validates that total packet sent and received on both interfaces is as expected using the port metrics.
- Sends 2000 packets between the two ports at a rate of 100 packets per second for a total of 20 seconds.


We will only require 1 VM for this lab. Deployment and logical topology below.

![Deployment topology](../Docs/images/lab-01/lab1-1.png)


## Prerequisites

Install snappi

```Shell
python3 -m pip install --upgrade snappi
```

Clone this repo

```Shell
git clone https://github.com/isgmano/training.git
```


## Deployment

We need to pull the desired version of the Ixia-c Controller and Ixia-c Traffic Engine from the GitHub Container Registry

```Shell
docker pull ghcr.io/open-traffic-generator/keng-controller:1.40.0-15
docker pull ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.8.0.245

```

Check once again the list of images which are loaded in the local registry and the list of containers which are already running

```Shell
docker images
docker ps -a
```

A virtual interface pair must be created on the server. These will be sending and receiving traffic. Use the “ip link” command to see the newly created virtual interfaces 

```Shell
sudo ip link add name veth0 type veth peer name veth1 && sudo ip link set dev veth0 up && sudo ip link set dev veth1 up
ip link
```

One basic way to deploy the test tool is to start the containers one by one. During this process multiple parameters must be specified. Start the KENG Controller. 

```Shell
docker run -d --name controller --network=host ghcr.io/open-traffic-generator/keng-controller:1.40.0-15 --http-port 8443 -accept-eula
```
Continue the manual deployment process by starting two Ixia-c Traffic Engine containers. Analyze the parameters that have been used during the deployment. 

```Shell
docker run -d --name traffic-engine-1 --network=host -e ARG_IFACE_LIST=virtual@af_packet,veth0 -e OPT_NO_HUGEPAGES=Yes --privileged -e OPT_LISTEN_PORT=5551 ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.8.0.245
```


```Shell
docker run -d --name traffic-engine-2 --network=host -e ARG_IFACE_LIST=virtual@af_packet,veth1 -e OPT_NO_HUGEPAGES=Yes --privileged -e OPT_LISTEN_PORT=5552 ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.8.0.245
```

All the previous commands specify the names of the containers, and the name of the images used to boot these. All the containers are using host networking which is a type of network attachment that ensures direct connection between the container and the Linux host.  

Each container listens for connections on a default port (TCP 8443 for Ixia-c Controller and TCP 5555 for Ixia-c Traffic Engine). The default port can be overridden with a specific command parameter as seen for the two Ixia-c Traffic Engine containers. Please note that all containers sharing the same namespace must listen on different TCP ports. 

Furthermore, each Ixia-c Traffic Engine container must have one (or more) test interfaces. In this lab we are using virtual test interfaces veth0 and veth1. This means the test traffic stays inside the Linux host but in most cases, this type of test will probably use an existing interface which in turn gets connected to other network devices. 

Check the list of containers which are actively running on the host.  

```Shell
docker ps 
```

## Execution

```Shell
cd ~/training/lab-01 && vim lab-01.py
```

Observe the controller location and the two traffic engine locations used as otg ports.

![alt text](../Docs/images/lab-01/lab1-2.png)

Run the test script

```Shell
python3 lab-01.py
```

![alt text](../Docs/images/lab-01/lab1-3.png)

Check the interface counters and save it to a file to verify the amount of traffic that has been sent and received.

```Shell
cat /proc/net/dev
```

Get the statistics from the controller user REST API curl commands

```Shell
curl -k -d '{"choice":"flow"}' -X POST https://127.0.0.1:8443/monitor/metrics
curl -k -d '{"choice":"port"}' -X POST https://127.0.0.1:8443/monitor/metrics
```

See the entire configuration using the REST API

```Shell
curl -k https://127.0.0.1:8443/config
```

Edit the file with a text editor such as VIM to perform the changes below. Please use the [OTG model rendering](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/open-traffic-generator/models/master/artifacts/openapi.yaml#tag/Configuration/operation/set_config) for your reference. 


- Send traffic with a rate of 200 fps instead of 100 fps. 
- Send traffic with a duration of 5 seconds instead of 20 seconds. 
- Send traffic with a frame size of 512 bytes instead of 128 bytes in each direction. 
- Send traffic with ETH + IP packet structure instead of ETH + IP + UDP packet structure for one of the flows 
- Send traffic with both flows in the same direction instead of sending bidirectional traffic.

Check your changes with `git diff` command and re-run the test script.

![alt text](../Docs/images/lab-01/lab1-4.png)

![alt text](../Docs/images/lab-01/lab1-5.png)


## Cleanup

Stop and remove the previously created containers. 

```Shell
docker stop traffic-engine-1 traffic-engine-2 controller && docker rm traffic-engine-1 traffic-engine-2 controller
```

Remove the veth link. This command will also remove the veth interfaces. 

```Shell
sudo ip link delete veth0
```

