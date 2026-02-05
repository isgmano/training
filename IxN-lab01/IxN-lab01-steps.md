# BGP Configuration using Wizard

This guide walks through configuring BGP (Border Gateway Protocol) using the IxNetwork Wizard.

## Table of Contents

- [Connect to IxNetworkWeb](#connect-to-ixnetworkweb)
- [Configure Base Configuration](#configure-base-configuration)
- [Configure Connectivity](#configure-connectivity)
- [Learned Information](#learned-information)
- [Traffic and Stats](#traffic-and-stats)

## Connect to IxNetworkWeb

1. Connect to `https://<chassis>/ixnetworkweb`
2. Use your credentials to enter
3. Click on **New Session** for IxNetwork
4. The landing page will open
![alt text](image.png)

## Configure Base Configuration

The landing page contains three main areas:

- **[1]** Controls to perform user operations (add protocol, add traffic, run wizard)
- **[2]** Options to create configurations quickly
- **[3]** Latest files saved on the system (click to open)
![alt text](image-1.png)

### Using the Wizard

1. Access the Wizard from the **File** menu or click **Run Wizard** on the landing page
2. Click on **Device Wizard**, then **New Wizard**

### Wizard Step 1

Since this is a fresh configuration:
- Choose **DeviceGroups to be added to new topologies**
- All other options will be disabled
- Click **Next**

### Wizard Step 2

Configure the following settings:

- **Number of Topologies**: 2
- **Topology Prefix Name**: AS100
- **Multiplier**: 1
- **DeviceGroup Prefix Name**: BGP

Click **Next** to proceed.

### Protocol Selection

1. Select **BGP** from the protocol list
2. Use the Filter text box to search for protocols if needed
3. Click **Next**

### Interface Configuration

1. Leave everything as default (or configure addresses based on connectivity requirements if auto-generation is off)
2. Click **Next**

### Summary

1. Enable **Summary** and review the configuration
2. Click **Finish** when satisfied

## Configure Connectivity

### IPv4 Layer Configuration

**For IPv4 1 Layer (Topology 1):**
- IP Address: `10.10.10.10`
- Gateway: `10.10.10.20`

**For IPv4 2 Layer (Topology 2):**
- IP Address: `10.10.10.20`
- Gateway: `10.10.10.10`

### BGP Peer Configuration

**BGP Peer 1:**
- DUT IP: `10.10.10.20`
- Enable **Filter IPv4 Unicast** in Learned Routes Filters

**BGP Peer 2:**
- DUT IP: `10.10.10.10`
- Enable **Filter IPv4 Unicast** in Learned Routes Filters

### Adding Network Groups

1. Select **BGP Peer 1** and use **Add** to add a network group
2. Choose **IPv4 Addresses** and select **Append**
3. Repeat for **BGP Peer 2**

### Starting the Test

1. Add ports to the topology using **Add/Remap ports**
2. Connect all ports
3. Start the test from **Test → Start**
4. Verify protocols come up (all green status)

## Learned Information

1. From the **Action** button, choose **BGP Peer Get Non-VPN Learned Info**
2. Review the learned information displayed

## Traffic and Stats

### Adding Traffic

1. Click on **Traffic** option
2. Choose **Add Traffic Item**
3. In the Add Traffic page:
   - Select **IPv4**
   - Choose source endpoint
   - Choose destination endpoint
   - Click **New Traffic Item**

### Viewing Statistics

1. Start traffic
2. Check **Port Statistics** to see frame transfer
3. Stop traffic

### Enabling Tracking

1. Go back to traffic item
2. Click **Statistics Tracking** column
3. Choose **Dest Endpoint**
4. Start traffic
5. From **Statistics** option, choose **Flow Statistics** to view detailed stats

---

## Notes

- This configuration creates a basic BGP setup with two topologies
- IP addresses use the `10.10.10.0/24` subnet
- Both BGP peers are configured to exchange IPv4 unicast routes
- Traffic flows between the configured network groups