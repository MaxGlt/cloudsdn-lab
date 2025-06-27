from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3


class Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Switch, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.info(">> Switch connected (features)")

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        actions1 = [parser.OFPActionOutput(2)]
        match1 = parser.OFPMatch(in_port=1)
        inst1 = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions1)]
        mod1 = parser.OFPFlowMod(datapath=datapath, priority=10, match=match1, instructions=inst1)
        datapath.send_msg(mod1)

        actions2 = [parser.OFPActionOutput(1)]
        match2 = parser.OFPMatch(in_port=2)
        inst2 = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions2)]
        mod2 = parser.OFPFlowMod(datapath=datapath, priority=10, match=match2, instructions=inst2)
        datapath.send_msg(mod2)

        self.logger.info(">> Static forwarding rules installed")