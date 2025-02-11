import sys
import time
import socket
import random
import argparse
import logging 

from scapy.all import *
from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump, bind_layers
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP, ARP
from scapy.config import conf
from iot_header import *

data_unit_num = 8
unit_size = 4 # bytes

def main(iface, dur_time):
    pkt = Ether(src="11:22:33:44:55:66")/\
            IP()/\
            UDP(sport=1,dport=2)/\
            Flag(spec=0xfa)/\
            Len(len=data_unit_num)
   
    pkt = pkt / ("".join([chr(x % 256) for x in xrange(data_unit_num*unit_size)]))
    
    s = conf.L2socket(iface=iface)
    logging.info('The packet is to be sent')
    pkt.show2()
    logging.info('Start')
    pkt_count = 0
    sec_count = 1
    start_time = time.time()
    while True:
        try:
            #sendp(pkt, iface=iface, verbose=False)
            s.send(pkt)
            pkt_count += 1
            if(time.time() - start_time > sec_count):
                logging.info('Sent iot packets: {0}'.format(pkt_count)) 
                sec_count += 1
            if(time.time() - start_time > dur_time):
                logging.info('Total sent iot packets: {0}'.format(pkt_count))
                logging.info('Total spent Time: {0:.2f}s'.format(time.time() - start_time))
                break
        except KeyboardInterrupt:
            logging.info('Total sent iot packets: {0}'.format(pkt_count))
            logging.info('Total spent Time: {0:.2f}s'.format(time.time() - start_time))
            break
'''
    sudo python sender.py -i [Interface] -t [Time]
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', help='which interface card to send packet')
    parser.add_argument('-t', '--time', help='how long the program run (sec)', type=int)
    args = parser.parse_args()

    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    if not args.interface:
        logging.error('Usage: python sender.py -i [Interface -t [Time]')
    else:
        main(args.interface, args.time)
        
