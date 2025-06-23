from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from pyroute2 import IPRoute
import ipaddress
import time
import threading

class FRRInteropRouter(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FRRInteropRouter, self).__init__(*args, **kwargs)
        self.ipr = IPRoute()
        self.logger.info("List of visible interfaces:")
        for link in self.ipr.get_links():
            name = link.get_attr('IFLA_IFNAME')
            index = link['index']
            self.logger.info(f"Interface detected : {name}, index {index}")
        self.datapath = None
        self.port_map = {
            "r1-veth": 1,
            "r2-veth": 2
        }
        threading.Thread(target=self.route_sync_loop, daemon=True).start()

    def route_sync_loop(self):
        while True:
            if self.datapath:
                self.logger.info("Route synchronization...")
                self.sync_routes(self.datapath)
            time.sleep(10)

    def sync_routes(self, dp):
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        del_flows = parser.OFPFlowMod(
            datapath=dp,
            command=ofp.OFPFC_DELETE,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=10,
            match=parser.OFPMatch()
        )
        dp.send_msg(del_flows)

        routes = self.ipr.get_routes(family=2)

        for route in routes:
            dst_ip = "0.0.0.0/0"
            if 'dst' in route:
                dst_ip = f"{route.get_attr('RTA_DST')}/{route['dst_len']}"
            gateway = None
            for attr in route['attrs']:
                if attr[0] == 'RTA_GATEWAY':
                    gateway = attr[1]

            oif = route.get('oif')
            if not oif:
                continue
            iface = self.ipr.get_links(oif)[0].get_attr('IFLA_IFNAME')
            port_no = self.port_map.get(iface)
            if not port_no:
                self.logger.warning(f"Interface {iface} not mapped to an OpenFlow port")
                continue

            self.logger.info(f"Route {dst_ip} via {iface} (port {port_no})")
            net = ipaddress.IPv4Network(dst_ip, strict=False)

            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst=(str(net.network_address), str(net.netmask)))
            actions = [parser.OFPActionOutput(port_no)]
            inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
            mod = parser.OFPFlowMod(
                datapath=dp,
                priority=10,
                match=match,
                instructions=inst
            )
            dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        self.datapath = dp
        parser = dp.ofproto_parser
        ofp = dp.ofproto

        # Default flow: send everything to the controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        dp.send_msg(parser.OFPFlowMod(
            datapath=dp,
            priority=0,
            match=match,
            instructions=inst
        ))
