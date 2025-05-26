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
        self.port_map = {
            "router1-veth": 1,
            "router2-veth": 2
        }
        # Lancer une boucle de rafraîchissement des routes
        threading.Thread(target=self.route_sync_loop, daemon=True).start()

    def route_sync_loop(self):
        while True:
            if self.datapath:
                self.logger.info("Synchronisation des routes...")
                self.sync_routes(self.datapath)
            time.sleep(10)

    def sync_routes(self, dp):
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        routes = self.ipr.get_routes(family=2)  # IPv4

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
                self.logger.warning(f"Interface {iface} non mappée à un port OpenFlow")
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

        # Flow par défaut : tout envoyer au contrôleur
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        dp.send_msg(parser.OFPFlowMod(
            datapath=dp,
            priority=0,
            match=match,
            instructions=inst
        ))
