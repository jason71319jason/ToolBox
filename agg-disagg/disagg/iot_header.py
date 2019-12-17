from scapy.all import *

class Flag(Packet):
    name = "Flag"
    fields_desc = [ BitField("spec",0,8),
                    BitField("num",0,16),
                    BitField("len",0,16),
                    BitField("agg",0,1),
                    BitField("pass",0,1),
                    BitField("cnter",0,4),
                    BitField("padding",0,2),
                    BitField("cnt2",0,32)]

class Len(Packet):
    name = "Len"
    fields_desc = [ BitField("len",0,8)]


bind_layers(UDP, Flag)
bind_layers(Flag, Len)


