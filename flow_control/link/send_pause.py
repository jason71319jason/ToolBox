import sys
import time
import socket
import random
import argparse

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP, ARP
from mac_control_header import * 

def main(iface):
    
    pause_pkt = Ether(dst='01:80:c2:00:00:01', src='00:00:00:00:00:00', type=0x8808) /\
            MACControlPause(op_code=0x0001, pause_time=0xffff)
    pause_pkt.show()
    sendp(pause_pkt, iface=iface)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', help='which interface card to send packet')
    args = parser.parse_args()

    main(args.interface)
