import sys
import socket
import random
import argparse

from scapy.all import sniff, sendp, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import Ether, IP, UDP, TCP, ARP
from mac_control_header import *

def main(iface):
    # display filter
    def filter(pkt):
        if MACControlPause in pkt:
            pkt.show()
        if Ether in pkt and pkt[Ether].type == 0x8808:
            pkt.show()
        if Ether in pkt and pkt[Ether].src == '00:22:22:22:22:22':
            pkt.show()
            
        sys.stdout.flush()
    # sniff
    print('sniffing on {}'.format(iface))
    sys.stdout.flush()
    sniff(iface=iface, prn=lambda x: filter(x))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', help='sniff interface')
    args = parser.parse_args()
    main(args.interface)
