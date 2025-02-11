import logging
import argparse

from scapy.all import *
from iot_header import *

iot_pkt_num = 43 # 43 pkt bundle to one agg pkt
data_unit_num = 8 # there are 8 data unit in each pkt 
unit_size = 4 # bytes
agg_len = iot_pkt_num * data_unit_num

def main(iface, dur_time):
    pkt = Ether(src="11:22:33:44:55:66")/\
            IP()/\
            UDP(sport=1,dport=2)/\
            Flag(spec=0xfa, num=iot_pkt_num, len=agg_len)

    for _ in range(0, iot_pkt_num):
        pkt = pkt / Len(len=data_unit_num)
        pkt = pkt / ("".join([chr(x % 256) for x in xrange(unit_size*data_unit_num)]))

    logging.info('The aggregated packet format')
    pkt.show2()
    print(len(pkt))
    logging.info('Start')
    pkt_count = 0
    sec_count = 1
    start_time = time.time()
    while True:
        try:
            sendp(pkt, iface=iface, verbose=False)
            pkt_count += 1
            if(time.time() - start_time > sec_count):
                logging.info('Sent aggregated packets: {0}'.format(pkt_count)) 
                sec_count += 1
            if(time.time() - start_time > dur_time):
                logging.info('Total sent aggregated packets: {0}'.format(pkt_count))
                logging.info('Total spent Time: {0:.2f}s'.format(time.time() - start_time))
                break
        except KeyboardInterrupt:
            logging.info('Total sent aggregated packets: {0}'.format(pkt_count))
            logging.info('Total spent Time: {0:.2f}s'.format(time.time() - start_time))
            break
'''
    sudo python send_disagg.py -i [interface] -t [Time]
'''

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', help='which interface card to send packet')
    parser.add_argument('-t', '--time', help='how long the program run (sec)', type=int)

    args = parser.parse_args()
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    if not args.interface:
        logging.error('Usage: python send_disagg.py -i [Interface] -t [Time]')
    else:
        main(args.interface, args.time)
