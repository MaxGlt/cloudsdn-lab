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
        self.datapath = None
        self.port_map = {}
        threading.Thread(target=self.route_sync_loop, daemon=True).start()

    def route_sync_loop(self):
        while True:
            if self.datapath:
                self.logger.info("[SYNC] Syncing routes with OpenFlow table...")
                self.sync_routes(self.datapath)
            time.sleep(10)

    def sync_routes(self, dp):
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # Clear previous flows (priority 10 only)
        del_flows = parser.OFPFlowMod(
            datapath=dp,
            command=ofp.OFPFC_DELETE,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=10,
            match=parser.OFPMatch()
        )
        dp.send_msg(del_flows)

        # Get system routes
        routes = self.ipr.get_routes(family=2)

        for route in routes:
            dst_ip = "0.0.0.0/0"
            if 'dst' in route:
                dst_ip = f"{route.get_attr('RTA_DST')}/{route['dst_len']}"
            else:
                continue  # skip routes without destination (e.g., local)

            oif = route.get('oif')
            if not oif:
                continue  # skip routes without interface
            iface = self.ipr.get_links(oif)[0].get_attr('IFLA_IFNAME')
            self.logger.info(f"[DEBUG] Route {dst_ip} via interface {iface}")
            self.logger.info(f"[DEBUG] Port map = {self.port_map}")
            port_no = self.port_map.get(iface)
            if not port_no:
                self.logger.warning(f"[SKIP] Interface {iface} not mapped to OpenFlow port")
                continue

            try:
                net = ipaddress.IPv4Network(dst_ip, strict=False)
            except ValueError:
                self.logger.warning(f"[SKIP] Invalid route: {dst_ip}")
                continue

            self.logger.info(f"[ADD] Route {dst_ip} via {iface} (port {port_no})")
            self.logger.info(f"[ROUTES] Current routes: {[r.get_attr('RTA_DST') for r in routes if 'dst' in r]}")

            match = parser.OFPMatch(
                eth_type=0x0800,  # IPv4
                ipv4_dst=(str(net.network_address), str(net.netmask))
            )
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

        req = parser.OFPPortDescStatsRequest(dp, 0)
        dp.send_msg(req)
        self.logger.info("[INIT] Sent port description request")

        # Default flow: send unmatched traffic to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=dp,
            priority=0,
            match=match,
            instructions=inst
        )
        dp.send_msg(mod)

        self.logger.info("[INIT] Waiting for port descriptions to build port_map...")

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_handler(self, ev):
        ports = ev.msg.body
        self.port_map = {p.name.decode(): p.port_no for p in ports}
        self.logger.info(f"[PORTS] Updated OpenFlow port mapping: {self.port_map}")
        if self.datapath:
            self.sync_routes(self.datapath)
