import sys
import time
import socket
import random
import argparse

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP, ARP

def main(iface):

    none_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src='00:22:22:22:22:22')/IP()/TCP()
    none_pkt.show()
    
    start_time = time.time()
    pkt_count = 0
    sec_count = 0
    
    while True:
        sendp(none_pkt, iface=iface, verbose=False)
        pkt_count += 1
        
        if(time.time() - start_time > sec_count):
            sec_count += 1
            print('Send packet: {}'.format(pkt_count)) 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', help='which interface card to send packet')
    args = parser.parse_args()

    main(args.interface)


