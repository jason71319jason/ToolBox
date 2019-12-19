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

unit_size = 4 # bytes

def main(iface, dur_time):
    pkt_8 = Ether(src="11:22:33:44:55:66")/\
            IP()/\
            UDP(sport=1,dport=2)/\
            Flag(spec=0xfa)/\
            Len(len=8)
   
    pkt_8 = pkt_8 / ("".join([chr(x % 256) for x in xrange(8*unit_size)]))

    pkt_6 = Ether(src="11:22:33:44:55:66")/\
            IP()/\
            UDP(sport=1,dport=2)/\
            Flag(spec=0xfa)/\
            Len(len=6)
   
    pkt_6 = pkt_6 / ("".join([chr(x % 256) for x in xrange(6*unit_size)]))

    pkt_4 = Ether(src="11:22:33:44:55:66")/\
            IP()/\
            UDP(sport=1,dport=2)/\
            Flag(spec=0xfa)/\
            Len(len=4)
   
    pkt_4 = pkt_4 / ("".join([chr(x % 256) for x in xrange(4*unit_size)]))

    s = conf.L2socket(iface=iface)
    logging.info('The packets are to be sent')
    pkt_8.show2()
    pkt_6.show2()
    pkt_4.show2()
    logging.info('Start')
    pkt_count = 0
    sec_count = 1
    start_time = time.time()
    while True:
        try:
            #sendp(pkt, iface=iface, verbose=False)
            s.send(pkt_8)
            s.send(pkt_6)
            s.send(pkt_4)
            pkt_count += 3
            if(time.time() - start_time > sec_count):
                logging.info('Sent iot packets: {0}'.format(pkt_count)) 
                sec_count += 1

            if(time.time() - start_time > dur_time):
                logging.info('Total sent iot packets: {0}'.format(pkt_count))
                logging.info('Total spent Time: {0:.2f}s'.format(time.time() - start_time))
                break

        except KeyboardInterrupt:
            s.close()
            logging.info('Total sent iot packets: {0}'.format(pkt_count))
            logging.info('Total spent Time: {0:.2f}s'.format(time.time() - start_time))
            break
'''
    sudo python sender.py -i [Interface] -t [Time]
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', help='which interface card to send packet')
    parser.add_argument('-t', '--time', help='how long the program run', type=int)
    args = parser.parse_args()
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    if not args.interface:
        logging.error('Usage: python sender.py -i [Interface] -t [Time]')
    else:
        main(args.interface, args.time)
        
