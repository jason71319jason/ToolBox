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

pkt_count = 0
start_time = 0
last_time = 0

def main(iface):

    # display filter
    def filter(pkt):
        if Flag in pkt:
            global pkt_count
            global start_time
            global last_time

            pkt_count += 1
                        
            if pkt_count % 10000 == 0:
                logging.info('Received {0} bytes in {1:.2f} seconds'.format(
                    len(pkt)*pkt_count, time.time() - start_time))

            if time.time() - last_time > 1:
                logging.info('Received {0} iot packets'.format(pkt_count))
                last_time = time.time()

            sys.stdout.flush()

    # sniff
    logging.info('Sniffing on {}'.format(iface))
    sys.stdout.flush()
    global start_time
    start_time = time.time()
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
