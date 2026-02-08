"""
Scaling DGs
Scaling Traffic
"""

import sys, os, time, traceback

# Import the RestPy module
from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.assistants.ports.portmapassistant import PortMapAssistant
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from ixnetwork_restpy import SessionAssistant, BatchAdd, Files

apiServerIp = '10.36.84.12'

# For Linux API server only
username = 'admin'
password = 'admin'

# For linux and connection_manager only. Set to True to leave the session alive for debugging.
debugMode = True

# Forcefully take port ownership if the portList are owned by other users.
forceTakePortOwnership = True

scale = 2

ixChassisIpList = ['10.36.84.12']
portList = [[ixChassisIpList[0], 12,1], [ixChassisIpList[0], 12, 2]]
try:
    testPlatform = TestPlatform(ip_address=apiServerIp, log_file_name='restpy.log')

    # Console output verbosity: none|info|warning|request|request_response|all
    testPlatform.Trace = 'info'

    testPlatform.Authenticate(username, password)
    session = testPlatform.Sessions.find(Name='Demo_Automation')
    ixNetwork = session.Ixnetwork

    ixNetwork.NewConfig()

    ixNetwork.info('Assign ports')
    portMap = PortMapAssistant(ixNetwork)
    vport = dict()
    for index,port in enumerate(portList):
        portName = 'Port_{}'.format(index+1)
        vport[portName] = portMap.Map(IpAddress=port[0], CardId=port[1], PortId=port[2], Name=portName)
        vport[portName].TxMode = 'interleaved'

    ixNetwork.info('Creating Topology Group 1')
    T1_start_time = time.time()
    with BatchAdd(ixNetwork) as ba:
        topology1 = ixNetwork.Topology.add(Name='Topo1', Ports=vport['Port_1'])
        for dgIndex in range(1,scale+1):
            deviceGroup1 = topology1.DeviceGroup.add(Name='T1DG'+str(dgIndex), Multiplier='1')
            ethernet1 = deviceGroup1.Ethernet.add(Name='T1Eth'+str(dgIndex))
            ethernet1.EnableVlans.Single(True)

            ixNetwork.info('Configuring IPv4')
            ipv4 = ethernet1.Ipv4.add(Name='T1Ipv4'+str(dgIndex))
            ipv4.Address.Increment(start_value='22.1.'+str(dgIndex)+'.1', step_value='0.0.0.1')
            ipv4.GatewayIp.Increment(start_value='22.1.'+str(dgIndex)+'.2', step_value='0.0.0.0')
            #ipv4.Prefix.Single(16)

            ixNetwork.info('Configuring IPv4 Network Group')
            networkGroup1 = deviceGroup1.NetworkGroup.add(Name='T1RoutesV4'+str(dgIndex), Multiplier='1')
            ipv4PrefixPool = networkGroup1.Ipv4PrefixPools.add(NumberOfAddresses='1')
            ipv4PrefixPool.NetworkAddress.Increment(start_value='100.1.'+str(dgIndex)+'.1', step_value='0.0.0.1')
            ipv4PrefixPool.PrefixLength.Single(24)
            
            ixNetwork.info('Configuring IPv6')
            ipv6 = ethernet1.Ipv6.add(Name='T1Ipv6'+str(dgIndex))
            ipv6.Address.Increment(start_value='22:'+str(hex(dgIndex)[2:])+'::1', step_value='0::1')
            ipv6.GatewayIp.Increment(start_value='22:'+str(hex(dgIndex)[2:])+'::2', step_value='0::0')
            ipv6.Prefix.Single(64)

            ixNetwork.info('Configuring IPv6 Network Group')
            networkGroup1 = deviceGroup1.NetworkGroup.add(Name='T1RoutesV6'+str(dgIndex), Multiplier='1')
            ipv6PrefixPool = networkGroup1.Ipv6PrefixPools.add(NumberOfAddresses='1')
            ipv6PrefixPool.NetworkAddress.Increment(start_value='100:1:'+str(dgIndex)+'::1', step_value='0::1')
            ipv6PrefixPool.PrefixLength.Single(64)
    T1_end_time = time.time()

    ixNetwork.info('Creating Topology Group 2')
    T2_start_time = time.time()
    with BatchAdd(ixNetwork) as ba:
        topology2 = ixNetwork.Topology.add(Name='Topo2', Ports=vport['Port_2'])
        deviceGroup2 = topology2.DeviceGroup.add(Name='T2DG', Multiplier=scale)

        ethernet2 = deviceGroup2.Ethernet.add(Name='T2Eth2')
        ethernet2.Mac.Increment(start_value='00:01:01:02:00:01', step_value='00:00:00:00:00:01')
        ethernet2.EnableVlans.Single(True)

        #ixNetwork.info('Configuring vlanID')
        #vlanObj = ethernet2.Vlan.find()[0].VlanId.Increment(start_value=101, step_value=1)

        ixNetwork.info('Configuring IPv4')
        ipv4 = ethernet2.Ipv4.add(Name='T2Ipv4')
        ipv4.Address.Increment(start_value='22.1.1.2', step_value='0.0.1.0')
        ipv4.GatewayIp.Increment(start_value='22.1.1.1', step_value='0.0.1.0')

        ixNetwork.info('Configuring IPv4 Network Group')
        networkGroup2 = deviceGroup2.NetworkGroup.add(Name='T2RoutesV4', Multiplier='1')
        ipv4PrefixPool = networkGroup2.Ipv4PrefixPools.add(NumberOfAddresses='1')
        ipv4PrefixPool.NetworkAddress.Increment(start_value='200.1.1.1', step_value='0.0.0.1')
        ipv4PrefixPool.PrefixLength.Single(24)
        
        ixNetwork.info('Configuring IPv6')
        ipv6 = ethernet2.Ipv6.add(Name='T2Ipv6')
        ipv6.Address.Increment(start_value='22:1::2', step_value='0:1::0')
        ipv6.GatewayIp.Increment(start_value='22:1::1', step_value='0:1::0')
        ipv6.Prefix.Single(64)

        ixNetwork.info('Configuring IPv6 Network Group')
        networkGroup2 = deviceGroup2.NetworkGroup.add(Name='T2RoutesV6', Multiplier='1')
        ipv6PrefixPool = networkGroup2.Ipv6PrefixPools.add(NumberOfAddresses='1')
        ipv6PrefixPool.NetworkAddress.Increment(start_value='100:1:'+str(dgIndex)+'::1', step_value='0::1')
        ipv6PrefixPool.PrefixLength.Single(64)
    T2_end_time = time.time()
    
    print(f"Topology 1 creation time:",+int(T1_end_time-T1_start_time)," seconds")
    print(f"Topology 2 creation time:",+int(T2_end_time-T2_start_time)," seconds")
    
    portMap.Connect(forceTakePortOwnership)
    ixNetwork.StartAllProtocols(Arg1='sync')

    ixNetwork.info('Verify protocol sessions\n')
    protocolsSummary = StatViewAssistant(ixNetwork, 'Protocols Summary')
    protocolsSummary.CheckCondition('Sessions Not Started', StatViewAssistant.EQUAL, 0)
    protocolsSummary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
    ixNetwork.info(protocolsSummary)
   
    if debugMode == False:
        # For linux and connection_manager only
        session.remove()

except Exception as errMsg:
    print('\n%s' % traceback.format_exc(None, errMsg))
    if debugMode == False and 'session' in locals():
        session.remove()