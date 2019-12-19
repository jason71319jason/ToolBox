import sys
import time
import socket
import random
import logging
import argparse

from scapy.all import sniff, sendp, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import Ether, IP, UDP, TCP, ARP
from iot_header import *

total_pkt_count = 0
start_time = 0
show_verf_per_n_pkt = 1000

def main(iface):

    # display filter
    def filter(pkt):
        if Flag in pkt:
            global total_pkt_count
            global start_time
            global show_verf_per_n_pkt
            total_pkt_count += 1

            logging.info('Received aggregated packets: {0}'.format(
                total_pkt_count))

            if total_pkt_count % show_verf_per_n_pkt == 0:
                logging.info('Packet verification')
                pkt.show2()
                logging.info('Packet Length: {}'.format(len(pkt)))

            sys.stdout.flush()

    # sniff
    logging.info('Sniffing on {}'.format(iface))
    sys.stdout.flush()
    sniff(iface=iface, prn=lambda x: filter(x))

'''
    sudo python receiver.py -i [Interface]
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', help='sniff interface')
    args = parser.parse_args()
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
 
    if not args.interface:
        logging.error('Usage: python receiver.py -i [Interface]')
    else:     
        main(args.interface)
