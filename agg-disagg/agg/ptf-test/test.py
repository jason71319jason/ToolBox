import pd_base_tests

from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *
from pltfm_pm_rpc.ttypes import *
from port_mapping import *
from pal_rpc.ttypes import *
from var_agg.p4_pd_rpc.ttypes import *
from res_pd_rpc.ttypes import *


class Flag(Packet):
    name = "Flag"
    fields_desc = [ BitField("spec",0,8) ,BitField("padding",0,40)]

class Len(Packet):
    name = "Len"
    fields_desc = [ BitField("len",0,8)]


#fp_ports = ["23/0","25/0","27/0","19/0","20/0","21/0","22/0","26/0","28/0"]
fp_ports = ["2/2", "2/0", "2/1", "2/3"]
N = 43
flaglen = 2
payloadsize = 1+flaglen*4
nPacketSize = (N - 2) * payloadsize

class Test(pd_base_tests.ThriftInterfaceDataPlane):
    def __init__(self):
        pd_base_tests.ThriftInterfaceDataPlane.__init__(self, ["var_agg"])

    def write_result(self,data):
        filename = "/root/variable_agg/TestResult"
        myfile = open(filename, 'a')
        myfile.write(data)
        myfile.close()


    def set_worker(self,N):
        need_clean = ["set_mutex_limit"]
        for table in need_clean:
            delete_func = "self.client." + table + "_table_delete"
            for entry in self.entries[table]:
                exec delete_func + "(self.sess_hdl, self.dev, entry)"
        self.conn_mgr.complete_operations(self.sess_hdl)
        N = N-1
        self.entries["set_mutex_limit"].append(
        self.client.set_mutex_limit_table_add_with_set_mutex_number(
            self.sess_hdl, self.dev_tgt,
            var_agg_set_mutex_limit_match_spec_t(0),
            var_agg_set_mutex_number_action_spec_t( N )
        ))
        self.conn_mgr.complete_operations(self.sess_hdl)
        time.sleep(1)

    def cleanSwitch(self,nPacketSize):

        print("[Info] Clearing table entries")
        need_clean = ["table_start_agg","table_continue_agg","table_continue_agg2"]
        for table in need_clean:
            delete_func = "self.client." + table + "_table_delete"
            for entry in self.entries[table]:
                exec delete_func + "(self.sess_hdl, self.dev, entry)"
        self.conn_mgr.complete_operations(self.sess_hdl)
        time.sleep(1)
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

        self.client.register_write_all_cnt(self.sess_hdl, self.dev_tgt, 0)
        self.client.register_write_all_cnt2(self.sess_hdl, self.dev_tgt, 0)
        self.client.register_write_all_box_bitmap(self.sess_hdl, self.dev_tgt, 0)
        self.client.register_write_all_reg_mutex(self.sess_hdl, self.dev_tgt, 0)
        self.client.register_write_all_total_msg(self.sess_hdl, self.dev_tgt, 0)
        self.client.register_write_all_flag_number_counter(self.sess_hdl, self.dev_tgt, 0)

        #recir_port = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        recir_port = [68,68,68,68,68,68,68,68,68,68,68,68,68,68]
        #recir_port = [0]
        numberOfPort = 1
        #recir_port[0] = 68
        #recir_port[1] = 64
        #for x in range(2,10):
        #    recir_port[x] = self.devPorts[x-1]
       
        payloadsize = 1+flaglen*4
        #nPacketSize = (N - 2) * payloadsize
        #nPacketSize = 1500-52-45

        self.entries["table_start_agg"] = []
        self.entries["table_start_agg"].append(
        self.client.table_start_agg_table_add_with_action_start_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_start_agg_match_spec_t(1,0),
            var_agg_action_start_agg_action_spec_t( recir_port[0] )
        ))

        self.entries["table_start_agg"].append(
        self.client.table_start_agg_table_add_with_action_start_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_start_agg_match_spec_t(1,1),
            var_agg_action_start_agg_action_spec_t( recir_port[0] )))


        self.entries["table_continue_agg"] = []
        for x in range(0,numberOfPort-1):
            self.entries["table_continue_agg"].append(
            self.client.table_continue_agg_table_add_with_action_continue_agg(
                self.sess_hdl, self.dev_tgt,
                var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, x),0,
                var_agg_action_continue_agg_action_spec_t(recir_port[x], x+1)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, numberOfPort-1),0,
            var_agg_action_continue_agg_action_spec_t(recir_port[numberOfPort-1], 0)))


        """
        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 1),0,
            var_agg_action_continue_agg_action_spec_t(recir_port2, 2)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 2),0,
            var_agg_action_continue_agg_action_spec_t(recir_port3, 3)))


        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 3),0,
            var_agg_action_continue_agg_action_spec_t(recir_port4, 4)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 4),0,
            var_agg_action_continue_agg_action_spec_t(recir_port5, 5)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 5),0,
            var_agg_action_continue_agg_action_spec_t(recir_port6, 6)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 6),0,
            var_agg_action_continue_agg_action_spec_t(recir_port7, 7)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 7),0,
            var_agg_action_continue_agg_action_spec_t(recir_port8, 8)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 8),0,
            var_agg_action_continue_agg_action_spec_t(recir_port8, 8)))
        """


        self.entries["table_continue_agg2"] = []
        for x in range(0,numberOfPort-1):
            self.entries["table_continue_agg2"].append(
            self.client.table_continue_agg2_table_add_with_action_continue_agg2(
                self.sess_hdl, self.dev_tgt,
                var_agg_table_continue_agg2_match_spec_t(x),
                var_agg_action_continue_agg2_action_spec_t(recir_port[x], x+1)))

        self.entries["table_continue_agg2"].append(
        self.client.table_continue_agg2_table_add_with_action_continue_agg2(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg2_match_spec_t(numberOfPort-1),
            var_agg_action_continue_agg2_action_spec_t(recir_port[numberOfPort-1], 0)))
        """
        self.entries["table_continue_agg2"].append(
        self.client.table_continue_agg2_table_add_with_action_continue_agg2(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg2_match_spec_t(2),
            var_agg_action_continue_agg2_action_spec_t(recir_port3, 3)))
 
        self.entries["table_continue_agg2"].append(
        self.client.table_continue_agg2_table_add_with_action_continue_agg2(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg2_match_spec_t(3),
            var_agg_action_continue_agg2_action_spec_t(recir_port4, 0)))
        """
        self.conn_mgr.complete_operations(self.sess_hdl)
        time.sleep(1)

    def setUp(self):
        pd_base_tests.ThriftInterfaceDataPlane.setUp(self)
        self.dev = 0
        self.dev_tgt = DevTarget_t(self.dev, hex_to_i16(0xFFFF))
        self.sess_hdl = self.conn_mgr.client_init()
        self.devPorts = []
        self.entries={}
        #port-add
        self.platform_type = "mavericks"
        board_type = self.pltfm_pm.pltfm_pm_board_type_get()
        if re.search("0x0234|0x1234|0x4234|0x5234", hex(board_type)):
            self.platform_type = "mavericks"
        elif re.search("0x2234|0x3234", hex(board_type)):
            self.platform_type = "montara"

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

        recir_port1 = 68  #self.devPorts[0] # 68
        recir_port2 = 196 #self.devPorts[0] # 196
        recir_port3 = 324 #self.devPorts[0] # 324
        recir_port4 = 452 #self.devPorts[0] # 452
       
        worker_num = 60 # 59
        self.entries["set_mutex_limit"] = []
        self.entries["set_mutex_limit"].append(
        self.client.set_mutex_limit_table_add_with_set_mutex_number(
            self.sess_hdl, self.dev_tgt,
            var_agg_set_mutex_limit_match_spec_t(0),
            var_agg_set_mutex_number_action_spec_t( worker_num )
        ))
        # comment-start 
        self.entries["table_start_agg"] = []
        self.entries["table_start_agg"].append(
        self.client.table_start_agg_table_add_with_action_start_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_start_agg_match_spec_t(1,0),
            var_agg_action_start_agg_action_spec_t( recir_port1 )
        ))

        self.entries["table_start_agg"].append(
        self.client.table_start_agg_table_add_with_action_start_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_start_agg_match_spec_t(1,1),
            var_agg_action_start_agg_action_spec_t( recir_port2 )))

        self.entries["table_continue_agg"] = []
        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 0),0,
            var_agg_action_continue_agg_action_spec_t(recir_port1, 1)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 1),0,
            var_agg_action_continue_agg_action_spec_t(recir_port2, 2)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 2),0,
            var_agg_action_continue_agg_action_spec_t(recir_port3, 3)))

        self.entries["table_continue_agg"].append(
        self.client.table_continue_agg_table_add_with_action_continue_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg_match_spec_t(0,nPacketSize,0, 3),0,
            var_agg_action_continue_agg_action_spec_t(recir_port4, 0)))

        self.entries["table_continue_agg2"] = []
        self.entries["table_continue_agg2"].append(
        self.client.table_continue_agg2_table_add_with_action_continue_agg2(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg2_match_spec_t(0),
            var_agg_action_continue_agg2_action_spec_t(recir_port1, 1)))

        self.entries["table_continue_agg2"].append(
        self.client.table_continue_agg2_table_add_with_action_continue_agg2(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg2_match_spec_t(1),
            var_agg_action_continue_agg2_action_spec_t(recir_port2, 2)))

        self.entries["table_continue_agg2"].append(
        self.client.table_continue_agg2_table_add_with_action_continue_agg2(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg2_match_spec_t(2),
            var_agg_action_continue_agg2_action_spec_t(recir_port3, 3)))
 
        self.entries["table_continue_agg2"].append(
        self.client.table_continue_agg2_table_add_with_action_continue_agg2(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_continue_agg2_match_spec_t(3),
            var_agg_action_continue_agg2_action_spec_t(recir_port4, 0)))

        # comment-end
        self.egress_port = self.devPorts[0]
        print("[Info] Egress port {}".format(self.egress_port))
        #self.egress_port = 185
        # add default entry
        self.entries["forward"] = []
        self.entries["forward"].append(
        self.client.forward_table_add_with_set_egr(
            self.sess_hdl, self.dev_tgt,
            var_agg_forward_match_spec_t(2,
                ethernet_srcAddr=macAddr_to_string("11:22:33:44:55:66")),
            var_agg_set_egr_action_spec_t(
                action_egress_spec=self.egress_port)))

        self.entries["count_unit"] = []
        self.entries["count_unit"].append(
        self.client.count_unit_table_add_with_get_cntr(
            self.sess_hdl, self.dev_tgt,
            var_agg_count_unit_match_spec_t(flag_agg=0,flag_pass=0)))

        self.entries["count_unit"].append(
        self.client.count_unit_table_add_with_flag_cnt2_move_to_metadata_when_pass_1(
            self.sess_hdl, self.dev_tgt,
            var_agg_count_unit_match_spec_t(flag_agg=0,flag_pass=1)))

        self.entries["count_unit2"] = []

        self.entries["count_unit2"].append(
        self.client.count_unit2_table_add_with_get_cntr2(
            self.sess_hdl, self.dev_tgt,
            var_agg_count_unit2_match_spec_t(flag_agg=1,flag_pass=0)))

        self.entries["count_unit2"].append(
        self.client.count_unit2_table_add_with_flag_cnt2_move_to_metadata_when_pass_1(
            self.sess_hdl, self.dev_tgt,
            var_agg_count_unit2_match_spec_t(flag_agg=1,flag_pass=1)))

        self.entries["bitmap"] = []
        self.entries["bitmap"].append(
        self.client.bitmap_table_add_with_bitmap_save(
            self.sess_hdl, self.dev_tgt,
            var_agg_bitmap_match_spec_t(flag_agg=0)))

        self.entries["bitmap"].append(
        self.client.bitmap_table_add_with_bitmap_agg(
            self.sess_hdl, self.dev_tgt,
            var_agg_bitmap_match_spec_t(flag_agg=1)))

        self.entries["number_of_save_msg"] = []
        self.entries["number_of_save_msg"].append(
        self.client.number_of_save_msg_table_add_with_total_add(
            self.sess_hdl, self.dev_tgt,
            var_agg_number_of_save_msg_match_spec_t(flag_agg=0)))

        self.entries["number_of_save_msg"].append(
        self.client.number_of_save_msg_table_add_with_total_sub(
            self.sess_hdl, self.dev_tgt,
            var_agg_number_of_save_msg_match_spec_t(flag_agg=1)))

        self.entries["table_mutex"] = []
        self.entries["table_mutex"].append(
        self.client.table_mutex_table_add_with_action_mutex(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_mutex_match_spec_t(0,0,43,32767),
            0))

        self.entries["table_mutex"].append(
        self.client.table_mutex_table_add_with_action_mutex_set_zero(
            self.sess_hdl, self.dev_tgt,
            var_agg_table_mutex_match_spec_t(1,2,0,32767),
            0))


        self.add_pool()
 
        self.entries["count_N_packet_number"] = []
        self.entries["count_N_packet_number"].append(
        self.client.count_N_packet_number_table_add_with_count_flag_number(
            self.sess_hdl, self.dev_tgt,
            var_agg_count_N_packet_number_match_spec_t(self.egress_port)))


        self.add_add_agg_header()

    def printAndWriteRecord(self,printString):
        filename = "/root/variable_agg/TestRecord"
        testRecord = open(filename, 'a')
        print printString
        testRecord.write(printString+"\n")
        testRecord.close()

    # This method install all default functions for tables
    def add_pool(self):
        print("[Info] Add entry to agg-table")
        #### for table pool_00
        self.entries["pool_0"] = []
        self.entries["pool_1"] = []
        self.entries["pool_2"] = []
        self.entries["pool_3"] = []
        self.entries["pool_4"] = []
        self.entries["pool_5"] = []
        self.entries["pool_6"] = []
        self.entries["pool_7"] = []
        self.entries["pool_8"] = []
        self.entries["pool_9"] = []
        self.entries["pool_10"] = []
        self.entries["pool_11"] = []
        self.entries["pool_12"] = []
        self.entries["pool_13"] = []
        self.entries["pool_14"] = []
        self.entries["pool_15"] = []
        self.entries["pool_len"] = []

        self.entries["pool_len"].append(
            self.client.pool_len_table_add_with_push_box_len(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_len_match_spec_t(flag_agg=0)))

        self.entries["pool_len"].append(
            self.client.pool_len_table_add_with_pop_box_len(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_len_match_spec_t(flag_agg=1)))

        self.entries["pool_0"].append(
            self.client.pool_0_table_add_with_push_box0(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_0_match_spec_t(flag_agg=0)))

        self.entries["pool_0"].append(
            self.client.pool_0_table_add_with_pop_box0(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_0_match_spec_t(flag_agg=1)))

        self.entries["pool_1"].append(
            self.client.pool_1_table_add_with_push_box1(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_1_match_spec_t(flag_agg=0)))

        self.entries["pool_1"].append(
            self.client.pool_1_table_add_with_pop_box1(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_1_match_spec_t(flag_agg=1)))

        self.entries["pool_2"].append(
            self.client.pool_2_table_add_with_push_box2(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_2_match_spec_t(flag_agg=0)))

        self.entries["pool_2"].append(
            self.client.pool_2_table_add_with_pop_box2(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_2_match_spec_t(flag_agg=1)))

        self.entries["pool_3"].append(
            self.client.pool_3_table_add_with_push_box3(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_3_match_spec_t(flag_agg=0)))

        self.entries["pool_3"].append(
            self.client.pool_3_table_add_with_pop_box3(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_3_match_spec_t(flag_agg=1)))

        self.entries["pool_4"].append(
            self.client.pool_4_table_add_with_push_box4(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_4_match_spec_t(flag_agg=0)))

        self.entries["pool_4"].append(
            self.client.pool_4_table_add_with_pop_box4(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_4_match_spec_t(flag_agg=1)))

        self.entries["pool_5"].append(
            self.client.pool_5_table_add_with_push_box5(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_5_match_spec_t(flag_agg=0)))

        self.entries["pool_5"].append(
            self.client.pool_5_table_add_with_pop_box5(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_5_match_spec_t(flag_agg=1)))

        self.entries["pool_6"].append(
            self.client.pool_6_table_add_with_push_box6(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_6_match_spec_t(flag_agg=0)))

        self.entries["pool_6"].append(
            self.client.pool_6_table_add_with_pop_box6(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_6_match_spec_t(flag_agg=1)))

        self.entries["pool_7"].append(
            self.client.pool_7_table_add_with_push_box7(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_7_match_spec_t(flag_agg=0)))

        self.entries["pool_7"].append(
            self.client.pool_7_table_add_with_pop_box7(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_7_match_spec_t(flag_agg=1)))

        self.entries["pool_8"].append(
            self.client.pool_8_table_add_with_push_box8(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_8_match_spec_t(flag_agg=0)))

        self.entries["pool_8"].append(
            self.client.pool_8_table_add_with_pop_box8(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_8_match_spec_t(flag_agg=1)))

        self.entries["pool_9"].append(
            self.client.pool_9_table_add_with_push_box9(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_9_match_spec_t(flag_agg=0)))

        self.entries["pool_9"].append(
            self.client.pool_9_table_add_with_pop_box9(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_9_match_spec_t(flag_agg=1)))

        self.entries["pool_10"].append(
            self.client.pool_10_table_add_with_push_box10(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_10_match_spec_t(flag_agg=0)))

        self.entries["pool_10"].append(
            self.client.pool_10_table_add_with_pop_box10(
            self.sess_hdl, self.dev_tgt,
            var_agg_pool_10_match_spec_t(flag_agg=1)))
        self.conn_mgr.complete_operations(self.sess_hdl)

    def add_add_agg_header(self):
        print("[Info] add_add_agg_header")
        self.entries["add_agg_header"] = []
        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len1(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,1)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len2(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,2)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len3(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,3)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len4(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,4)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len5(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,5)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len6(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,6)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len7(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,7)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len8(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,8)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len9(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,9)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len10(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,10)))

        self.entries["add_agg_header"].append(
            self.client.add_agg_header_table_add_with_add_agg_header_len11(
            self.sess_hdl, self.dev_tgt,
            var_agg_add_agg_header_match_spec_t(1,11)))

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

        global flaglen
        #flaglen = raw_input("Flaglen init:")
        #flaglen= int(flaglen)
        flaglen= 8
        nPacketSize = 1500-52-45
        self.worker_number_limit = 200
        #self.cleanSwitch(nPacketSize)
        #self.set_worker(self.worker_number_limit)
        """
        hw_sync_flag = var_agg_register_flags_t(read_hw_sync = True)
        pipe = 0
        x = 0
        endN = 0
        maxWorker = 1
        avWorker = 0
        i = 0
        testTime = 0
        testResult = [0,0,0,0,0,0,0,0,0,0]
        #self.N = raw_input("N init:")
        #self.N = int(self.N)
        self.N = 43
        global flaglen
        #flaglen = raw_input("Flaglen init:")
        #flaglen= int(flaglen)
        flaglen= 8
        #self.timer = raw_input("Timer init:")
        #self.timer = int(self.timer)
        self.timer = 1000
        #self.worker_number_limit = raw_input("Worker init:")
        #self.worker_number_limit = int(self.worker_number_limit)
        self.worker_number_limit = 200
        payloadsize = 1+flaglen*4
        nPacketSize = 1500-52-45

        print "N = %d" % ((nPacketSize / payloadsize)+2)

        #socket create
        import socket
        host = '192.168.132.101'
        mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (host,5555)
        mysock.connect(addr)
        print "\n\nConnect to pktgen"

        success_flag = 0
        top = self.timer*2
        down = 0
        maxworker = 0

        reset = 1
        while True:
                if reset == 1:
                    payloadsize = 1+flaglen*4
                    nPacketSize = 1500-52-45
                    self.cleanSwitch(nPacketSize)
                    self.set_worker(self.worker_number_limit)
                    self.printAndWriteRecord("Test worker :%d..." % (self.worker_number_limit))
                    self.printAndWriteRecord("nPacketSize :%d..." % (nPacketSize))
                    self.printAndWriteRecord("\tflaglen :%d..." % (flaglen))
                    data = 'Worker: %d\n' %(self.worker_number_limit)
                    data = data + 'nPacketSize: %d\n' %(nPacketSize)
                    data = data + 'Flaglen: %d\n' %(flaglen)
                    self.write_result(data)
                    reset = 0

                N = nPacketSize / payloadsize + 2
                self.printAndWriteRecord("Test, Timer = %d...\nN = %d\n" % (self.timer,N))

                mysock.sendall(str(1))
                a = mysock.recv(512)
                mysock.sendall(str(flaglen))
                a = mysock.recv(512)
                mysock.sendall(str(self.timer))
                timeout = 0
                time.sleep(3) 
		while endN < 6:
                    worker = self.client.register_read_reg_mutex(self.sess_hdl, self.dev_tgt, 0, hw_sync_flag) 
                    b = self.pal.pal_port_all_stats_get( 0, self.devPorts[0])
                    #print ("flag_number_counter:%d" % flag_counts[pipe])
                    if x == b.entry[32] and x != 0:
                        endN += 1
                    else:
                        endN = 0
                        timeout+=1
                    x = b.entry[32]
                    if maxWorker < worker[pipe]:
			maxWorker = worker[pipe]
                    time.sleep(0.2)
                    if timeout == 100:
                        print "timeout"
                        timeout = 0
                        break
		endN = 0

                b = self.pal.pal_port_all_stats_get( 0, self.devPorts[0])
                numberOfIoTMsgSend = self.client.register_read_flag_number_counter(self.sess_hdl, self.dev_tgt, 0, hw_sync_flag)[pipe]
                self.printAndWriteRecord("\tReceive IoT packet Msg: %d" % (b.entry[0]))
                self.printAndWriteRecord("\tSend N packet: %d" % b.entry[32])
                self.printAndWriteRecord("\tSend IoT Msg packet: %d" % numberOfIoTMsgSend)
                self.printAndWriteRecord("\tIn Worker and still recir: %d" % (b.entry[0]- numberOfIoTMsgSend))
                endN = 0
                print "\tmaxWorker: %d" %maxWorker
                if maxWorker > 1000:
                    maxWorker = 1000
                #if (b.entry[0] - b.entry[32] * self.N <= maxWorker* self.N):
                if (b.entry[0] - numberOfIoTMsgSend <= self.worker_number_limit* 200):
                    self.printAndWriteRecord("\t... OK\n")
                    success_flag = 1
                    if (top - down) == 1 or top == down:
                        self.printAndWriteRecord("Write result to file")
                        data = '%d %d %d\n' %(N, self.worker_number_limit, self.timer)
                        self.write_result(data)
                        
                        if self.worker_number_limit == 30000:
                            reset = 1
                            flaglen+=1
                            return
                        self.timer = 1000
                        top = self.timer *2
                        down = 0
                        #nPacketSize -= payloadsize
                        reset = 1
                        if self.worker_number_limit >= 10 or self.worker_number_limit == 1 or self.worker_number_limit == 5:
                            self.worker_number_limit*=2
                        elif self.worker_number_limit == 2:
                            self.worker_number_limit = 5
                        self.cleanSwitch(nPacketSize)
                    else :
                        top = self.timer
                        self.timer = top - (top - down)/2
                        self.cleanSwitch(nPacketSize)
                else:
                    self.printAndWriteRecord("\tLoss: %d \n\t... Fail\n" % (b.entry[0]- numberOfIoTMsgSend))
                    if (top - down) == 1 or top == down:
                        self.printAndWriteRecord("Write result to file")
                        data = '%d %d %d\n' %(N, self.worker_number_limit, self.timer)
                        self.write_result(data)
                        #self.N -= 1
                        nPacketSize -= payloadsize
                        if self.worker_number_limit == 30000:
                            reset = 1
                            flaglen+=1
                            return
                        self.timer = 1000
                        top = self.timer *2
                        down = 0
                        #nPacketSize -= payloadsize
                        reset = 1
                        if self.worker_number_limit >= 10 or self.worker_number_limit == 1 or self.worker_number_limit == 5:
                            self.worker_number_limit*=2
                        elif self.worker_number_limit == 2:
                            self.worker_number_limit = 5
                    else :
                        down = self.timer
                        self.timer =top - (top - down)/2

                    #clean switch
                    self.cleanSwitch(nPacketSize)
        """    
        return

    def tearDown(self):
        try:
            flag = raw_input("[Info] end? (Press Any)")
            if flag == '1' or flag == '':
                print("[Info] Clearing table entries")
                for table in self.entries.keys():
                    delete_func = "self.client." + table + "_table_delete"
                    for entry in self.entries[table]:
                        exec delete_func + "(self.sess_hdl, self.dev, entry)"
                #for sid in self.sids:
                #    self.mirror.mirror_session_disable(self.sess_hdl,Direction_e.PD_DIR_INGRESS, self.dev_tgt, sid)
        except Exception, e:
            print("[Error] " + str(e))
            print("[Error] Error while cleaning up. ")
            print("[Error] You might need to restart the driver")
        finally:
            self.conn_mgr.complete_operations(self.sess_hdl)
            self.conn_mgr.client_cleanup(self.sess_hdl)
            print("[Info] Closed Session %d" % self.sess_hdl)
            pd_base_tests.ThriftInterfaceDataPlane.tearDown(self)

