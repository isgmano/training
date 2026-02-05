<p align="center">
  <img src="images/banner_evpn.png" width="100%">
</p>

<h1 align="center">EVPN VXLAN IP Aliasing</h1>

## Table of Contents
- [Add Base Controls](#add-base-controls)
- [Configure Connectivity](#configure-connectivity)
- [Learned Information](#learned-information)
- [Traffic Configuration](#traffic-configuration)

---

## Add Base Controls
- Add 2 ports in the new configuration.
- From **New Topology** add **EVPN VXLAN** on first port.

![Figure 1 Add EVPN](images/figure-01-add-evpn.png)

- Rename the topology as **“Egress”** and device group as **“PE1-PE2”**.
- Also, set the device multiplier to **1**.

![Figure 2 Adjust Device Multiplier](images/figure-02-adjust-device-multiplier.png)

- Similarly, add EVPN VXLAN device group on other port.
- Rename the topology as **“Ingress”** and device group as **“PE3”**.
- Also, set the device multiplier to **1**.

![Figure 3 Base Topology](images/figure-03-base-topology.png)

> At this moment, if you are asking, where are two PEs in Egress, you are following **well**.

- Now add an IPv4 prefix to the EVPN VXLAN of Egress Topology.

![Figure 4 Choose Network Group](images/figure-04-choose-network-group.png)
![Figure 5 Select IPv4 Address Pools](images/figure-05-select-ipv4-address-pools.png)

- Choose **IPv4 Address Pools** and click **Finish**.
- Rename the network group as **“MH T5”** to indicate this network group will generate type 5 routes and this prefix is multi-homed (MH).
- Set IP address to **12.12.12.12/32**.

> **NOTE:** So far, we did not trick the configuration for multi-homing.

![Figure 6 Type 5 attached to EVPN](images/figure-06-type5-attached-to-evpn.png)

- Add an IPv4 Address pool to Ingress Topology.
- Set the prefix as **24.24.24.24/32**.
- Rename the network group as **“SH T5”** to indicate that this prefix is associated with a single home ethernet segment.

> Honestly, naming this network group in such a way does not signify anything at large. Only interest of this prefix pool is that, once we create traffic, this is going to be our source.

![Figure 7 Enhanced Topology with Traffic Endpoints](images/figure-07-enhanced-topology-with-traffic-endpoints.png)

---

## Configure Connectivity
- From the left pane click on **IPv4**. It will open the view to configure IPv4 addresses. Set:
  - IP Address as **10.10.10.10** and gateway as **10.10.10.20** on port1.
  - IP Address as **10.10.10.20** and gateway as **10.10.10.10** on port2.

![Figure 8 IP Connectivity](images/figure-08-ip-connectivity.png)

- Select **BGP Peer** from left pane and set:
  - DUT IP as **10.10.10.20** for first peer.
  - DUT IP as **10.10.10.10** for second peer.

![Figure 9 Configure BGP Peership](images/figure-09-configure-bgp-peership.png)

- Also, from same **BGP Peer** view, choose **Learn Route Filters** tab and enable **EVPN Filters**.

![Figure 10 Set Learned Info Filter](images/figure-10-set-learned-info-filter.png)

---

## EVPN Configuration

### Traffic Direction / Target Topology
Before moving to configuration, let us review the topology we are trying to build here.

![Figure 11 Interfaceless IP-VRF-To-IP-VRF Model](images/figure-11-interfaceless-ipvrf-to-ipvrf-model.png)

Here **MH T5** is multihomed to **PE1** and **PE2** with **ESI** value **ABC**. In IxNetwork we shall configure this value.

- **PE1** will send **RT5** for **12.12.12.12/32** prefix with next hop being set to itself.
- In addition to this **PE1** will also send **L3 Auto Discovery (AD) per Ethernet Segment (ES)**.
- **PE2** will send **L3 AD per ES** and **L3 AD per EVI** route with next hop being set to **PE2**.

Normally traffic from **24.24.24.24/32** to **12.12.12.12/32** will follow **PE1** using label **L3**, however for failover scenario, traffic will contain **IP AD Label** and sent to **PE2**.

With this brief description, let us continue the configuration of EVPN VXLAN.

### Ethernet Segments & Multihoming
- Return to **BGP Peer** in left pane. Now choose **EVPN** tab. Set:
  - Number of Ethernet Segments = **2** for port 1.
  - Keep Number of Ethernet Segments = **1** for port 2.

> **NOTE:** This is a simulation with respect to PE1 that there are two Ethernet Segments. We shall set the values same to indicate that they are part of same Ethernet Segment, therefore MH T5 is simulated as multihomed.

- Change **IP-VRF-To-IP-VRF** to **Interface-less Multihoming** for both the ports.

![Figure 12 Creation of Ethernet Segments](images/figure-12-creation-of-ethernet-segments.png)

- Now, click on **BGP Ethernet Segment** tab. Set ESI value for Egress topology to:
  - `0x00 00 00 00 00 00 00 0A BC`
  - Leave the values for second port.

![Figure 13 Set ESI Value](images/figure-13-set-esi-value.png)

- Stay in the same tab and scroll towards right. Look for **Support L3 Fast Convergence** field. Enable for all ports.

![Figure 14 Enable L3 Fast Convergence](images/figure-14-enable-l3-fast-convergence.png)

- Enable **Advertise IP Aliasing automatically** only for **PE2**.

> Note in Ethernet segment **1.2**, it simulates our **PE2**.

![Figure 15 Advertise IP Aliasing Automatically](images/figure-15-advertise-ip-aliasing-automatically.png)

### Next-hop tweaks (essential trick)
- Come to **Advanced** tab. Now set next hop for **PE2 (1.2)** manually to **30.30.30.30**.

> Similar configuration is needed in EVI. We shall come back to this essential trick later (point 27). In general these configurations are required for constructing AD per ES route.

![Figure 16 Nexthop in Ethernet Segment](images/figure-16-nexthop-in-ethernet-segment.png)

- From left pane select **EVI VXLAN**, reach to **Advance** tab and modify the nexthop in similar fashion.

![Figure 17 Nexthop in EVI](images/figure-17-nexthop-in-evi.png)

### Route targets and labels
- From left pane select **EVI VXLAN** and stay in **Basic** sub tab of **EVI** tab.
- Enable **Enable L3 Target List** for both sides.
- Scroll towards right. Set **IP AD Route Label** to:
  - **6534** (PE1)
  - **7534** (PE2)
  - **8534** (PE3)

> Important is the configuration for **IP AD Route Label** for Egress only.

![Figure 18 L3 RT and IP AD Label](images/figure-18-l3-rt-and-ip-ad-label.png)

- Stay in the same tab. Scroll to find the following fields:
  - **Include L2 Attr Ext Comm**: set for all ports
  - **Primary PE**: enable only for **PE1** and **PE3**
  - **Backup Flag**: enable for **PE2** only

![Figure 19 Enable L2 Ext Comm, Primary PE, and Backup](images/figure-19-primary-backup-flags.png)

> **NOTE:** This mismatch in Route Target will cause issues in traffic generation. In customer scenario also we have seen misconfiguration in RT values of different route types.

- Set **L3 Export Route Target List**. Set the assigned number to **1** for **PE2**.

![Figure 20 Set L3 RT](images/figure-20-set-l3-rt.png)

- Set route label value for **Egress** and **Ingress** as **2001**.
  - Navigate: **EVI VXLAN → IPv4 Routes → Label Space / SRv6 SID** tab.

![Figure 21 Set Prefix Label](images/figure-21-set-prefix-label.png)

- The prefix from Egress side should be advertised only by **PE1** (primary PE).

> This is a trick we have used to simulate the route advertisement is only happening by PE1 (refer Figure 11). However, using traffic and ordinal number we shall simulate the failover situation.

![Figure 22 Advertise Prefix using PE1 only](images/figure-22-advertise-prefix-using-pe1-only.png)

- At point 19, we added an arbitrary next hop address **30.30.30.30** for PE2.
- Now we need to inform the DUT about this address.
  - Advertise this IP address using BGP router of Egress Topology.
  - Add an IPv4 Prefix Pool and set the address to **30.30.30.30/32**.
  - Rename the network group as **PE2 NH**.

![Figure 23 Advertise Nexthop PE2](images/figure-23-advertise-nexthop-pe2.png)

---

## Learned Information
At this stage, we are good to go to start the protocols.

- Start the protocols. Wait for all protocols to come up.

![Figure 24 All are Green!](images/figure-24-all-green.png)

- Select **BGP Peer** of **PE3**.
- Go to **BGP Peer Grid** at **Basic** subtab.
- Right click: **Get VPN Learned Info → Get EVPN Learned Info**.

- From the learned information we focus on:
  - **EVPN Ethernet AD**
  - **EVPN IP Prefix**

![Figure 26 EVPN Ethernet AD](images/figure-26-evpn-ethernet-ad.png)
![Figure 27 EVPN IP Prefix](images/figure-27-evpn-ip-prefix.png)

The images are not readable quite clearly. Hence, following two tables are extracted from these images. Important fields are discussed.

### EVPN Ethernet AD
![EVPN Ethernet AD Table](images/figure-27a-evpn-ethernet-ad-table.png)

- Check the next hop addresses for PE1 and PE2.
- Check the label value for AD per EVI from PE2 as **7534** (cross-check with Figure 18).
- Ethernet Tag for AD per ES is set to **MAX** always.

### EVPN IP Prefix

| Field | Entry #1 | Entry #2 |
|---|---|---|
| Route Type | RT 5 | RT 1: AD per EVI |
| IP Prefix | 12.12.12.12 | 12.12.12.12 |
| IP Prefix Length | 32 | 32 |
| ESI | 00 00 00 00 00 00 00 00 0A BC | 00 00 00 00 00 00 00 00 0A BC |
| Gateway IP Address | 0.0.0.0 | 0.0.0.0 |
| Remote Peer MAC Address | 00:01:01:00:00:01 | 00:01:01:00:00:01 |
| Negotiated Encapsulation type(s) | VXLAN | VXLAN |
| RD | 10.10.10.10:1 | 10.10.10.10:2 |
| MPLS Label | **2001** | **7534** |

- RT5 is sent by **PE1** (confirmed by label **2001**).
- RT1: AD per EVI is coming from **PE2** (confirmed by label **7534**). We enabled **Advertise IP Aliasing Automatically** for PE2 only.
- Note **Entry #1** will be **ordinal 0**, and **Entry #2** will be **ordinal 1**.
  - The order is not guaranteed when *Start All Protocols* happens.
  - Controlled start of EVI can get a predictable outcome of ordinal numbers.

---

## Traffic Configuration
- Add **L2-3 Traffic Items**. This opens endpoint selection.
- Create traffic from **Ingress** to **Egress**.
- Send traffic from **SH T5 (24.24.24.24/32)** to **MH T5 (12.12.12.12/32)**.

![Figure 28 Endpoint Selection](images/figure-28-endpoint-selection.png)

- MH T5 is multihomed to two PEs, so there should be a single endpoint.
- Click the ellipses (…) associated with MH T5 prefix to open the traffic rectangle.
- Set the count of route to **1** for this configuration.

![Figure 29 Traffic Rectangle](images/figure-29-traffic-rectangle.png)

- Click on the arrow to update the selected endpoint set.
- Check the encapsulations and click **Next**.

![Figure 30 Final Endpoint set](images/figure-30-final-endpoint-set.png)

- Proceed through Encapsulation → Flow Group → Frame Setup → Rate Setup → Flow Tracking.
- In **Flow tracking**, enable:
  - **Source/Dest Value Pair**
  - **VXLAN: VNI**

- Move to **Protocol Behaviors**.

![Figure 31 Protocol Behaviors](images/figure-31-protocol-behaviors.png)

- Ordinal value for next hop selection is important:
  - **Ordinal = 0** → VNI **2001**
  - **Ordinal = 1** → VNI **7534**

- In **Preview**, click **View Flow Groups/Packet**, select the flow group, and verify VNI.

**Ordinal Value = 0**

![Figure 32 Traffic Preview for Ordinal = 0](images/figure-32-traffic-preview-ordinal-0.png)

**Ordinal Value = 1**

![Figure 33 Traffic Preview for Ordinal = 1](images/figure-33-traffic-preview-ordinal-1.png)

- Finish to create the traffic item.

![Figure 34 Traffic Item](images/figure-34-traffic-item.png)

- Apply traffic.

![Figure 35 Apply Traffic](images/figure-35-apply-traffic.png)

- Start traffic.
- In the statistics, you should find the trackers in yellow (as defined earlier).

![Figure 36 Traffic Stats](images/figure-36-traffic-stats.png)
