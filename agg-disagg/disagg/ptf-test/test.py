import pd_base_tests

from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *
from pltfm_pm_rpc.ttypes import *
from port_mapping import *
from pal_rpc.ttypes import *
from var_disagg.p4_pd_rpc.ttypes import *
from res_pd_rpc.ttypes import *
from mirror_pd_rpc.ttypes import *


def mirror_session(mir_type, mir_dir, sid, egr_port=0, egr_port_v=False,
                   egr_port_queue=0, packet_color=0, mcast_grp_a=0,
                   mcast_grp_a_v=False, mcast_grp_b=0, mcast_grp_b_v=False,
                   max_pkt_len = 0, level1_mcast_hash=0, level2_mcast_hash=0,
                   cos=0, c2c=0, extract_len=0, timeout=0, int_hdr=[]):
  return MirrorSessionInfo_t(mir_type,
                             mir_dir,
                             sid,
                             egr_port,
                             egr_port_v,
                             egr_port_queue,
                             packet_color,
                             mcast_grp_a,
                             mcast_grp_a_v,
                             mcast_grp_b,
                             mcast_grp_b_v,
                             max_pkt_len,
                             level1_mcast_hash,
                             level2_mcast_hash,
                             cos,
                             c2c,
                             extract_len,
                             timeout,
                             int_hdr,
                             len(int_hdr))


class Flag(Packet):
    name = "Flag"
    fields_desc = [ BitField("spec",0,8) , BitField("num",0,16), BitField("padding",0,56)]

class Len(Packet):
    name = "Len"
    fields_desc = [ BitField("len",0,8)]


#fp_ports = ["23/0" , "29/0"]
fp_ports = []
# egress port 2/1
fp_ports_10G = ["2/2", "2/0"]
# 1 : 10G
use_100G_or_10G = 1
mirror_index = 0 
egress_index = 0

class Test(pd_base_tests.ThriftInterfaceDataPlane):
    def __init__(self):
        pd_base_tests.ThriftInterfaceDataPlane.__init__(self, ["var_disagg"])

    def setUp(self):
        pd_base_tests.ThriftInterfaceDataPlane.setUp(self)
        self.dev = 0
        self.dev_tgt = DevTarget_t(self.dev, hex_to_i16(0xFFFF))
        self.sess_hdl = self.conn_mgr.client_init()
        self.devPorts = []
        self.devPorts_10G = []

        #port-add
        self.platform_type = "mavericks"
        board_type = self.pltfm_pm.pltfm_pm_board_type_get()
        if re.search("0x0234|0x1234|0x4234|0x5234", hex(board_type)):
            self.platform_type = "mavericks"
        elif re.search("0x2234|0x3234", hex(board_type)):
            self.platform_type = "montara"


        # get the device ports from front panel ports
        for fpPort in fp_ports_10G:
            port, chnl = fpPort.split("/")
            devPort = \
                self.pal.pal_port_front_panel_port_to_dev_port_get(0,
                                                                   int(port),
                                                                   int(chnl))
            self.devPorts_10G.append(devPort)

        if test_param_get('setup') == True or (test_param_get('setup') != True
            and test_param_get('cleanup') != True):

            # add and enable the platform ports
            for i in self.devPorts_10G:
               self.pal.pal_port_add(0, i,
                                     #pal_port_speed_t.BF_SPEED_100G,
                                     pal_port_speed_t.BF_SPEED_10G,
                                     #pal_fec_type_t.BF_FEC_TYP_REED_SOLOMON)
                                     pal_fec_type_t.BF_FEC_TYP_NONE)
               self.pal.pal_port_enable(0, i)



        # get the device ports from front panel ports
        for fpPort in fp_ports:
            port, chnl = fpPort.split("/")
            devPort = \
                self.pal.pal_port_front_panel_port_to_dev_port_get(0,
                                                                   int(port),
                                                                   int(chnl))
            self.devPorts.append(devPort)

        if test_param_get('setup') == True or (test_param_get('setup') != True
            and test_param_get('cleanup') != True):

            # add and enable the platform ports
            for i in self.devPorts:
               self.pal.pal_port_add(0, i,
                                     #pal_port_speed_t.BF_SPEED_100G,
                                     pal_port_speed_t.BF_SPEED_10G,
                                     #pal_fec_type_t.BF_FEC_TYP_REED_SOLOMON)
                                     pal_fec_type_t.BF_FEC_TYP_NONE)
               self.pal.pal_port_enable(0, i)

        #mirror session
        if use_100G_or_10G ==0:
            mirror_port = self.devPorts[mirror_index]
        else:
            mirror_port = self.devPorts_10G[mirror_index]

        self.sids = []
        # determine mirror sesion (iot_pkt_len = 8)
        for i in range(8,9):
            m_sid = i
            print ("[Info] m_sid = %d" % m_sid)
            pktlen = 53+4*i+1 
            info = mirror_session(mir_type=MirrorType_e.PD_MIRROR_TYPE_NORM,
                                  mir_dir=Direction_e.PD_DIR_INGRESS,
                                  sid=m_sid,
                                  egr_port=mirror_port,
                                  egr_port_v=True,
                                  max_pkt_len=pktlen)        
            self.mirror.mirror_session_create(self.sess_hdl, self.dev_tgt, info)
            self.sids.append(m_sid)

 
        recir_port1 = 68
        recir_port2 = 196
        recir_port3 = 324
        recir_port4 = 452
        if use_100G_or_10G ==0 :
            self.egress_port = self.devPorts[egress_index]
        else:
            self.egress_port = self.devPorts_10G[egress_index]
        # add default entry
        self.entries={}

        aspec = var_disagg_action_end_dis_agg_action_spec_t(self.egress_port)
        #self.client.table_end_dis_agg_set_default_action_action_end_dis_agg(self.sess_hdl, self.dev_tgt, aspec)

        self.entries["table_dis_agg"] = []
        self.entries["table_end_dis_agg"] = []
        
        for i in range(1,12):
            self.entries["table_dis_agg"].append(
            self.client.table_dis_agg_table_add_with_action_dis_agg(
                self.sess_hdl, self.dev_tgt,
                var_disagg_table_dis_agg_match_spec_t(i,0),
                var_disagg_action_dis_agg_action_spec_t(
                i, -i, recir_port1,1)))
            self.entries["table_dis_agg"].append(
            self.client.table_dis_agg_table_add_with_action_dis_agg(
                self.sess_hdl, self.dev_tgt,
                var_disagg_table_dis_agg_match_spec_t(i,1),
                var_disagg_action_dis_agg_action_spec_t(
                i, -i, recir_port1,2)))
            self.entries["table_dis_agg"].append(
            self.client.table_dis_agg_table_add_with_action_dis_agg(
                self.sess_hdl, self.dev_tgt,
                var_disagg_table_dis_agg_match_spec_t(i,2),
                var_disagg_action_dis_agg_action_spec_t(
                i, -i, recir_port1,3)))
            self.entries["table_dis_agg"].append(
            self.client.table_dis_agg_table_add_with_action_dis_agg(
                self.sess_hdl, self.dev_tgt,
                var_disagg_table_dis_agg_match_spec_t(i,3),
                var_disagg_action_dis_agg_action_spec_t(
                i, -i, recir_port1,0)))
        



        for i in range(1,12):
            self.entries["table_end_dis_agg"].append(
            self.client.table_end_dis_agg_table_add_with_action_end_dis_agg(
                self.sess_hdl, self.dev_tgt,
                var_disagg_table_end_dis_agg_match_spec_t(i),
                var_disagg_action_end_dis_agg_action_spec_t(
                i, -i, self.egress_port)))


        """
        self.client.test_time1_table_add_with_write_time1(
            self.sess_hdl, self.dev_tgt,
            var_disagg_test_time1_match_spec_t(4))

        self.client.test_time2_table_add_with_write_time2(
            self.sess_hdl, self.dev_tgt,
            var_disagg_test_time2_match_spec_t(3))
        """
        
        self.entries["dis_agg_update"] = []
        self.entries["dis_agg_update"].append(
        self.client.dis_agg_update_table_add_with_update_flag(
            self.sess_hdl, self.dev_tgt,
            var_disagg_dis_agg_update_match_spec_t(1)))
        
        """
        pkt = Ether(src="11:22:33:44:55:66")/ \
              IP(len=100)/\
              UDP(sport=100,dport=100)/\
              Flag(spec=0xfa,num=5)
        for i in range(0,5):
              pkt = pkt /Len(len=8)
              pkt = pkt/("".join([chr(x % 256) for x in xrange(32)]))
        send_packet(self, 1, pkt)
        """
    def cleanSwitch(self):
        for i in self.devPorts:
            self.pal.pal_port_del(0, i)        
        time.sleep(1)
        for i in self.devPorts:
	    self.pal.pal_port_add(0, i,
                #pal_port_speed_t.BF_SPEED_100G,
                pal_port_speed_t.BF_SPEED_10G,
                #pal_fec_type_t.BF_FEC_TYP_REED_SOLOMON)
                pal_fec_type_t.BF_FEC_TYP_NONE)
            self.pal.pal_port_enable(0, i)
        time.sleep(3)

    def printAndWriteRecord(self,printString):
        filename = "/root/variable_disagg/TestRecord"
        testRecord = open(filename, 'a')
	print printString
	testRecord.write(printString+"\n")
	testRecord.close()

    def runTest(self):
        #speed_100g = 64
        #dev_id = 0
        #recir_port = 64
        
        #self.devport_mgr.devport_mgr_remove_port(dev_id, recir_port)
        #self.conn_mgr.recirculation_enable(self.sess_hdl, dev_id, recir_port)
        #self.devport_mgr.devport_mgr_add_port(dev_id ,recir_port, speed_100g, 0)
        #self.conn_mgr.complete_operations(self.sess_hdl)
        #recir_port = 192
        #self.devport_mgr.devport_mgr_remove_port(dev_id, recir_port)
        #self.conn_mgr.recirculation_enable(self.sess_hdl, dev_id, recir_port)
        #self.devport_mgr.devport_mgr_add_port(dev_id ,recir_port, speed_100g, 0)
        #self.conn_mgr.complete_operations(self.sess_hdl)
        
        """ 
        hw_sync_flag = var_disagg_register_flags_t(read_hw_sync = True)
        pipe = 1
        oldFlag = 0
        x = 0
        endN = 0
        maxWorker = 0
        avWorker = 0
        i = 0

        testTime = 0
        
        testResult = [0,0,0,0,0,0,0,0,0,0]
        self.N = raw_input("N init:")
        self.N = int(self.N) 
        self.timer = raw_input("Timer init:")
        self.timer = int(self.timer) 

        #socket create
        import socket
        host = '192.168.132.101'
        mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (host,5555)
        mysock.connect(addr)
        print "\n\nConnect to pktgen"
        #mysock.sendall(msg)
        #data = mysock.recv(1000)

        success_flag = 0
        top = self.timer*2
        down = 0


        while True:
                self.printAndWriteRecord("Test, N = %d, Timer = %d..." % (self.N, self.timer))

                mysock.sendall(str(self.N))
                a = mysock.recv(512)
                mysock.sendall(str(self.timer))
                
		while endN < 10:
		    b = self.pal.pal_port_all_stats_get( 0, self.devPorts[0])
		    #print ("flag_number_counter:%d" % flag_counts[pipe])
		    if x == b.entry[32] and x != oldFlag:
			endN += 1
                    else:
                        endN = 0
		    x = b.entry[32]
		    time.sleep(0.5)

		#a = self.pal.pal_port_all_stats_get( 0, self.devPorts[1])
		b = self.pal.pal_port_all_stats_get( 0, self.devPorts[0])
		c = self.pal.pal_port_all_stats_get( 0, self.devPorts[1])
		self.printAndWriteRecord("\tReceive N packet Msg: %d" % (b.entry[0]))
		#print ("\tSend IoT Msg: %d" % flag_counts[pipe])
                #oldFlag = flag_counts[pipe]
		self.printAndWriteRecord("\tSend IoT Msg packet: %d" % b.entry[32])
                endN = 0
                if (b.entry[0] * self.N == b.entry[32]):
                    self.printAndWriteRecord("\t... OK\n")
                    success_flag = 1
                    if (top - down) == 1 or top == down:
                        self.printAndWriteRecord("Write result to file")
                        filename = "/root/variable_disagg/TestResult"
                        myfile = open(filename, 'a')
                        data = '%d %d\n' %(self.N, self.timer+1)
                        myfile.write(data)
                        myfile.close()
                        self.N -= 1
                        if self.N == 1:
                            return
                        top = self.timer *2
                        down = 0
                        self.cleanSwitch()
                    else :
                        top = self.timer
                        self.timer = top - (top - down)/2
                else:
                    self.printAndWriteRecord("\tLoss: %d \n\t... Fail\n" % (b.entry[0]*self.N - b.entry[32]))
                    #print ("\n\nTest Result:")
                    #print ("\tN = %d" % self.N)
                    #print ("\tSuccess Timer: %d" % (self.timer+1))
                    if (top - down) == 1 or top == down:
                        self.printAndWriteRecord("Write result to file")
                        filename = "/root/variable_disagg/TestResult"
                        myfile = open(filename, 'a')
                        data = '%d %d\n' %(self.N, self.timer+1)
                        myfile.write(data)
                        myfile.close()
                        self.N -= 1
                        if self.N == 1:
                            return
                        top = self.timer *2
                        down = 0
                    else :
                        down = self.timer
                        self.timer =top - (top - down)/2
                    #success_flag = 0

                    #clean switch
                    self.cleanSwitch()
                #self.timer -= 1
                mysock.recv(512)
        """
        return

    def tearDown(self):
        try:
            flag = raw_input("end?")
            if flag == '1' or flag == '':
                print("Clearing table entries")
                for table in self.entries.keys():
                    delete_func = "self.client." + table + "_table_delete"
                    for entry in self.entries[table]:
                        exec delete_func + "(self.sess_hdl, self.dev, entry)"
                for sid in self.sids:
                    self.mirror.mirror_session_disable(self.sess_hdl,Direction_e.PD_DIR_INGRESS, self.dev_tgt, sid)
        except:
            print("Error while cleaning up. ")
            print("You might need to restart the driver")
        finally:
            self.conn_mgr.complete_operations(self.sess_hdl)
            self.conn_mgr.client_cleanup(self.sess_hdl)
            print("Closed Session %d" % self.sess_hdl)
            pd_base_tests.ThriftInterfaceDataPlane.tearDown(self)

