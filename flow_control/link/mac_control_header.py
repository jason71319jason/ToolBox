from scapy.all import *

class MACControlPause(Packet):
    name = 'MACControlPause'
    fields_desc = [ BitField('op_code',0,16),
                    BitField('pause_time',0,16)]

bind_layers(Ether, MACControlPause)
