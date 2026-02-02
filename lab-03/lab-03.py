import logging as log
import snappi
from datetime import datetime
import time

   
def Test():
    test_const = {
        "p1_location": "p1_location",
        "p2_location": "p2_location",
        "pktRate": 500,
        "pktCount": 1000,
        "pktSize": 128,
        "trafficDuration": 20,
        "txMac": "00:00:01:01:01:01",
        "txIp": "192.168.1.100",
        "txGateway": "192.168.1.101",
        "txPrefix": 24,
        "rxMac": "00:00:01:01:01:02",
        "rxIp": "192.168.1.101",
        "rxGateway": "192.168.1.100",
        "rxPrefix": 24,
    }

    api = snappi.api(location="https://127.0.0.1:8443", verify=False)

    c = otg_config(api, test_const)

    api.set_config(c)

    start_protocols(api)

    # start_capture(api)

    start_transmit(api)

    wait_for(lambda: flow_metrics_ok(api, test_const), "flow metrics",2,90)

    # stop_capture(api)

    # get_capture(api, "p2", "p2.pcap")


def otg_config(api, tc):

    c = api.config()
    c.options.port_options.location_preemption = True

    p1 = c.ports.add(name="p1", location=tc["p1_location"])
    p2 = c.ports.add(name="p2", location=tc["p2_location"])
    
    # capture configuration

    # p2_capture = c.captures.add(name="p2_capture")
    # p2_capture.set(port_names=["p2"],format="pcap",overwrite=True)
    

    d1 = c.devices.add(name="d1")
    d2 = c.devices.add(name="d2")

    d1_eth = d1.ethernets.add(name="d1_eth")
    d1_eth.connection.port_name = p1.name
    d1_eth.mac = tc["txMac"]
    d1_eth.mtu = 1500

    d1_ip = d1_eth.ipv4_addresses.add(name="d1_ip")
    d1_ip.set(address=tc["txIp"], gateway=tc["txGateway"], prefix=tc["txPrefix"])


    d2_eth = d2.ethernets.add(name="d2_eth")
    d2_eth.connection.port_name = p2.name
    d2_eth.mac = tc["rxMac"]
    d2_eth.mtu = 1500

    d2_ip = d2_eth.ipv4_addresses.add(name="d2_ip")
    d2_ip.set(address=tc["rxIp"], gateway=tc["rxGateway"], prefix=tc["rxPrefix"])


    for i in range(0, 2):
        f = c.flows.add()
        f.duration.fixed_seconds.seconds = tc["trafficDuration"]
        f.rate.pps = tc["pktRate"]
        f.size.fixed = tc["pktSize"]
        f.metrics.enable = True

    ftx_v4 = c.flows[0]
    ftx_v4.name = "p1-p2"
    ftx_v4.tx_rx.port.set(
        tx_name=p1.name, rx_names=[p2.name]
    )

    ftx_v4_eth, ftx_v4_ip, ftx_v4_udp = ftx_v4.packet.ethernet().ipv4().udp()
    ftx_v4_ip.src.value = tc["txIp"]
    ftx_v4_ip.dst.value = tc["rxIp"]
    ftx_v4_ip.priority.raw.increment.start = 0
    ftx_v4_ip.priority.raw.increment.count = 256
    ftx_v4_udp.src_port.value = 5000
    ftx_v4_udp.dst_port.value = 6000

    frx_v4 = c.flows[1]
    frx_v4.name = "p2-p1"
    frx_v4.tx_rx.port.set(
        tx_name=p2.name, rx_names=[p1.name]
    )

    frx_v4_eth, frx_v4_ip, frx_v4_udp = frx_v4.packet.ethernet().ipv4().udp()
    frx_v4_ip.src.value = tc["rxIp"]
    frx_v4_ip.dst.value = tc["txIp"]
    ftx_v4_ip.priority.raw.increment.start = 0
    ftx_v4_ip.priority.raw.increment.count = 256
    frx_v4_udp.src_port.value = 5000
    frx_v4_udp.dst_port.value = 6000

    # print("Config:\n%s", c)
    return c


def flow_metrics_ok(api, tc):
    for m in get_flow_metrics(api):
        if (
            m.transmit != m.STOPPED
            # or m.frames_tx != tc["pktCount"]
            # or m.frames_rx != tc["pktCount"]
        ):
            return False
    return True


def get_flow_metrics(api):

    print("%s Getting flow metrics    ..." % datetime.now())
    req = api.metrics_request()
    req.flow.flow_names = []

    metrics = api.get_metrics(req).flow_metrics

    tb = Table(
        "Flow Metrics",
        [
            "Name",
            "State",
            "Frames Tx",
            "Frames Rx",
            "FPS Tx",
            "FPS Rx",
            "Bytes Tx",
            "Bytes Rx",
        ],
    )

    for m in metrics:
        tb.append_row(
            [
                m.name,
                m.transmit,
                m.frames_tx,
                m.frames_rx,
                m.frames_tx_rate,
                m.frames_rx_rate,
                m.bytes_tx,
                m.bytes_rx,
            ]
        )
    print(tb)
    return metrics

def start_protocols(api):
    print("%s Starting protocols    ..." % datetime.now())
    cs = api.control_state()
    cs.choice = cs.PROTOCOL
    cs.protocol.choice = cs.protocol.ALL
    cs.protocol.all.state = cs.protocol.all.START
    api.set_control_state(cs)

def start_transmit(api):
    print("%s Starting transmit on all flows    ..." % datetime.now())
    cs = api.control_state()
    cs.choice = cs.TRAFFIC
    cs.traffic.choice = cs.traffic.FLOW_TRANSMIT
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
    api.set_control_state(cs)

def stop_transmit(api):
    print("%s Stopping transmit    ..." % datetime.now())
    cs = api.control_state()
    cs.choice = cs.TRAFFIC
    cs.traffic.choice = cs.traffic.FLOW_TRANSMIT
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
    api.set_control_state(cs)

def start_capture(api):
    print("%s Starting capture  ..." % datetime.now())
    cs = api.control_state()
    cs.choice = cs.PORT
    cs.port.choice = cs.port.CAPTURE
    cs.port.capture.set(port_names = [], state="start")
    api.set_control_state(cs)

def stop_capture(api):
    print("%s Stopping capture  ..." % datetime.now())
    cs = api.control_state()
    cs.choice = cs.PORT
    cs.port.choice = cs.port.CAPTURE
    cs.port.capture.set(port_names = [], state="stop")
    api.set_control_state(cs)

def get_capture(api,port_name,file_name):
    print('Fetching capture from port %s' % port_name)
    capture_req = api.capture_request()
    capture_req.port_name = port_name
    pcap = api.get_capture(capture_req)
    with open(file_name, 'wb') as out:
        out.write(pcap.read())

def get_capture_slice(api, port_name, file_name):
    print('Fetching capture from port %s' % port_name)
    capture_req = api.capture_request()
    capture_req.port_name = port_name
    capture_req.packets.choice = capture_req.packets.SLICE
    capture_req.packets.slice.initial.start=1
    capture_req.packets.slice.initial.count=2
    pcap = api.get_capture(capture_req)
    with open(file_name, 'wb') as out:
        out.write(pcap.read())

def wait_for(func, condition_str, interval_seconds=None, timeout_seconds=None):
    """
    Keeps calling the `func` until it returns true or `timeout_seconds` occurs
    every `interval_seconds`. `condition_str` should be a constant string
    implying the actual condition being tested.

    Usage
    -----
    If we wanted to poll for current seconds to be divisible by `n`, we would
    implement something similar to following:
    ```
    import time
    def wait_for_seconds(n, **kwargs):
        condition_str = 'seconds to be divisible by %d' % n

        def condition_satisfied():
            return int(time.time()) % n == 0

        poll_until(condition_satisfied, condition_str, **kwargs)
    ```
    """
    if interval_seconds is None:
        interval_seconds = 1
    if timeout_seconds is None:
        timeout_seconds = 60
    start_seconds = int(time.time())

    print('\n\nWaiting for %s ...' % condition_str)
    while True:
        if func():
            print('Done waiting for %s' % condition_str)
            break
        if (int(time.time()) - start_seconds) >= timeout_seconds:
            msg = 'Time out occurred while waiting for %s' % condition_str
            raise Exception(msg)

        time.sleep(interval_seconds)
    

class Table(object):
    def __init__(self, title, headers, col_width=15):
        self.title = title
        self.headers = headers
        self.col_width = col_width
        self.rows = []

    def append_row(self, row):
        diff = len(self.headers) - len(row)
        for i in range(0, diff):
            row.append("_")

        self.rows.append(row)

    def __str__(self):
        out = ""
        border = "-" * (len(self.headers) * self.col_width)

        out += "\n"
        out += border
        out += "\n%s\n" % self.title
        out += border
        out += "\n"

        for h in self.headers:
            out += ("%%-%ds" % self.col_width) % str(h)
        out += "\n"

        for row in self.rows:
            for r in row:
                out += ("%%-%ds" % self.col_width) % str(r)
            out += "\n"
        out += border
        out += "\n\n"

        return out


if __name__ == "__main__":
    Test()
