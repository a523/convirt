#!/usr/bin/env python
#
#   ConVirt   -  Copyright (c) 2008 Convirture Corp.
#   ======
#
# ConVirt is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at:
#
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# 
#
# author : Jd <jd_jedi@users.sourceforge.net>
#


# All classes in thse files are required Interfaces for managing
# machines/host/nodes with virtualization technology.

import sys,os,re,types, traceback
import pprint
        
from convirt.core.utils.utils import constants, search_tree,Poller
from convirt.core.utils.utils import to_unicode,to_str
from convirt.model.ManagedNode import ManagedNode

from convirt.model.VM import VM
from convirt.model.VNode import VNode

from KVMDomain import *
from KVMProxy import KVMProxy
from kvm_constants import *

from convirt.core.utils.phelper import PHelper
from convirt.core.utils.phelper import HostValidationException,\
     AuthenticationException, CommunicationException

from sqlalchemy import  Column
from sqlalchemy.types import *
from sqlalchemy import orm
from convirt.model.DBHelper import DBHelper
from convirt.model.NodeInformation import Category,Component,Instance

import logging
LOGGER = logging.getLogger("convirt.core.platforms.kvm")
class KVMNode(VNode):
    """
    Interface that represents a node being managed.It defines useful APIs
    for clients to be able to do Management for a virtualized Node
    """                
    #migration_port=Column(Integer,default=8002)

    __mapper_args__ = {'polymorphic_identity': u'kvm'}

    def __init__(self,
                 hostname = None,
                 username= Node.DEFAULT_USER,
                 password=None,
                 isRemote=False,
                 ssh_port = 22,
                 migration_port = 8002,
                 helper = None,
                 #store = None,
                 use_keys = False,
                 address = None):

        VNode.__init__(self,
                       to_unicode("kvm"),
                       #store,
                       hostname,
                       username, password,
                       isRemote,
                       ssh_port,
                       helper,
                       use_keys,
                       address)


        self.migration_port = migration_port 

    @orm.reconstructor
    def init_on_load(self):
        VNode.init_on_load(self)

    def get_auto_config_dir(self):
        return "/etc/kvm/auto"

    #def get_config_dir(self):
    #    return '/etc/kvm'


    def is_HVM(self):
        return True

    def is_image_compatible(self, image):
        if image:
            # can run all hvm images and
            #can not run non-hvm images (at least for now)
            return image.is_hvm()
        return False

    # Factory method to create vm
    def new_config(self, filename):
        return KVMConfig(self, filename)

    def new_vm_from_config(self, config):
        return KVMDomain(self, config=config)

    def new_vm_from_info(self, info):
        return KVMDomain(self, vm_info=info)


    def get_running_vms(self):
        current_dict = {}
        vm_info_list = self.get_vmm().get_vms()
        for k, vm_info in vm_info_list.iteritems():
            vm = self.new_vm_from_info(vm_info)
            current_dict[k] = vm

        return current_dict


    def _init_vmm(self):
        return KVMProxy(self)

    def get_metric_snapshot(self,filter=False):
        # do top -b -p pids to get the info and stuff it here.
        # use std names
        pid_name_list = [(vm["pid"],vm["name"]) for vm in self.get_doms() \
                        if vm["pid"] != None ]

        pid_name_map = dict(pid_name_list)
        pids = pid_name_map.keys()

        """returns a dictionary containing metrics for all running domains
        in a frame"""

        # construct the frame: Map
        # Top level / node level metrics : frame[toplevel] = value
        # followed by each domain
        #   frame [domain_name] = metrics map

        #
        frame = {} # the output metric frame (dict of dict's)
        frame['RUNNING_VMs'] = 0
        frame['PAUSED_VMs']  = 0
        frame['CRASHED_VMs'] = 0
        frame['TOTAL_VMs'] = 0

        frame['VM_TOTAL_CPU'] = 0.0  # not normalized cpu %
        frame['VM_TOTAL_MEM'] = 0.0  # memory used (not %)
        frame['VM_TOTAL_CPU(%)'] = 0.0
        frame['VM_TOTAL_MEM(%)'] = 0.0

        ###added on 25/11/09
        ###to consider only the convirt created vms
        dom_names,vm_dict=self.get_all_dom_names()
        frame['TOTAL_VMs'] = len(dom_names)

        cpu_info = self.get_cpu_info()
        nr_cpus = int(cpu_info.get(key_cpu_count,1))
        outside_vms=[]
        
        max_pid_len = 20
        pid_len = 0
        if pids :
            pid_len = len(pids)
        else :
            pids = ["99999999999"]
            pid_len = len(pids)

        #set to -1 so that loop runs atleast once
        #print "pid_len=======",pid_len
        while len(pids) > 0:
            tmp_pids = pids[0:max_pid_len]
            pids = pids[max_pid_len:]

            pid_string = to_str(tmp_pids).replace("[", "").replace("]","")
            #print "pid_string=======",pid_string,"\n"

            FRAME_CMD = 'top -b -n 3 -d 1'
            if pid_string:
                FRAME_CMD = FRAME_CMD + " -p " + pid_string

            (retbuf, retcode) = self.node_proxy.exec_cmd(FRAME_CMD,
                                                         self.exec_path)
            if retcode:
                LOGGER.error("metrics Command error on Server:"+self.hostname)
                LOGGER.error("command = "+FRAME_CMD)
                err = "retcode :%s, error :%s" % (retcode,retbuf)
                LOGGER.error(err)
                raise Exception(err)

            # process and fill frame buffer
            frame_buffers = re.split("top -.*\n", retbuf)
            if len(frame_buffers) < 3:
                return None

            fbuffer = frame_buffers[2]

            #print  retbuf, FRAME_CMD, pids, pid_string
            m = re.search("Cpu\\(s\\):.*\n", fbuffer)
            line = m.group()
            # Sanitize the line
            line = line.replace(':',',')
            line = line.replace(' ','')
            line = line.replace('\t' ,'')
            tokens = line.split(',')
    #        total_cpu = reduce(lambda x,y: x + y,
    #                           [ float(tokens[ndx].split('%')[0]) for ndx in range(1,4)])

            #total_cpu =  float(tokens[0].split(',')[1].split('%')[0])
            total_cpu = 0.0
            for ndx in range(1,3):
                value = float(tokens[ndx].split('%')[0])
                total_cpu = total_cpu + value

            #print "TOTAL = ",self.hostname, total_cpu

            mem =  re.search("Mem:[ \t]+(\d+)k total,[ \t]+(\d+)k used,[ \t]+(\d+)k free,[ \t]+(\d+).*\n", fbuffer)
            if mem:
                total_mem = int(mem.group(1))/1024  # in MB
                used_mem = int(mem.group(2))/1024   # in MB
                buffer_mem= int(mem.group(4))/1024   # in MB
            else:
                mem =  re.search("Mem:[ \t]+(\d+)M total,[ \t]+(\d+)M used,[ \t]+(\d+)M free,[ \t]+(\d+).*\n", fbuffer)
                total_mem = int(mem.group(1))  # Already in MB
                used_mem = int(mem.group(2))   # Already in MB
                buffer_mem= int(mem.group(4))  # Already in MB

            swap =  re.search("Swap:[ \t]+(\d+)k total,[ \t]+(\d+)k used,[ \t]+(\d+)k free,[ \t]+(\d+).*\n", fbuffer)
            if swap:
               cached_mem= int(swap.group(4))/1024   # in MB
            else:
               swap =  re.search("Swap:[ \t]+(\d+)M total,[ \t]+(\d+)M used,[ \t]+(\d+)M free,[ \t]+(\d+).*\n", fbuffer)
               cached_mem= int(swap.group(4))   # Already in MB

            ###host_memory for kvm is calculated as
            ###memUsed-(memBuffer+memCcached)
            host_memory=used_mem-(buffer_mem+cached_mem)
            host_mem=(float(host_memory)/float(total_mem))*100
            #print "Total CPU %f , mem %f" % (total_cpu, (float(used) * 100 /total))



            lines = fbuffer.split("\n")
            ndx = 0
            for line in lines:
                ndx += 1
                if re.search("PID USER", line):
                    break

            for line in lines[ndx:]:
                d_frame = {}
                if line:
                    #print line
                    elem = line.split()

                    if pid_name_map.get(elem[0]) not in dom_names:
                        outside_vms.append(dict(name=pid_name_map.get(elem[0]),status=VM.RUNNING))
                        continue
                    ###end

                    cpu_pct = float(elem[8])
                    mem_pct = float(elem[9])
                    #print "VM CPU %f MEM %f"% (cpu_pct, mem_pct)

                    d_frame["CPU(%)"] = cpu_pct
                    d_frame["MEM(%)"] = mem_pct
                    d_frame["NAME"] = pid_name_map.get(elem[0])
                    d_frame["PID"] = elem[0]
                    d_frame['STATE'] = VM.RUNNING
                    dom = vm_dict[d_frame["NAME"]]
                    if dom.status==constants.PAUSED:
                        d_frame['STATE'] = VM.PAUSED
                        frame['PAUSED_VMs'] += 1
                    else:
                        frame['RUNNING_VMs'] += 1

                    vcpus = float(dom.getVCPUs())
                    d_frame['VM_CPU(%)'] = d_frame['CPU(%)']
                    if vcpus > 1: # adjust the utilization to 100%
                        #print d_frame["NAME"],"===",d_frame['CPU(%)'],"New::::::::::::",to_str(float(d_frame['CPU(%)']) / (vcpus))
                        d_frame['VM_CPU(%)'] = to_str(float(d_frame['CPU(%)']) / vcpus)

                    if nr_cpus > 1: # adjust the utilization to 100%
                        d_frame['CPU(%)'] = to_str(float(d_frame['CPU(%)']) / nr_cpus)


                    d_frame['NETRX(k)'] = 0
                    d_frame['NETS'] = 0
                    d_frame['NETTX(k)'] = 0


                    d_frame['VBDS'] = 0
                    d_frame['VBD_OO'] = 0
                    d_frame['VBD_RD'] = 0
                    d_frame['VBD_WR'] = 0

                    self.augment_storage_stats(d_frame["NAME"], d_frame)
                    # runnung counts
                    #frame['RUNNING_VMs'] += 1

                    frame['VM_TOTAL_CPU'] += cpu_pct  # not normalized cpu %
                    frame['VM_TOTAL_MEM'] += (mem_pct * total_mem)/100 # memory used (not %)
                    frame['VM_TOTAL_CPU(%)'] += float(d_frame['CPU(%)'])
                    frame['VM_TOTAL_MEM(%)'] += mem_pct

                    frame[d_frame["NAME"]] = d_frame

        if filter:
            self.insert_outside_vms(outside_vms)

        # build info from node info
        cpu_str = to_str(cpu_info.get(key_cpu_count,1)) + " @ " + \
                  to_str(cpu_info.get(key_cpu_mhz,0)) + "MHz"
        frame['SERVER_CPUs'] = cpu_str
                
        frame['SERVER_MEM'] =  to_str(self.get_memory_info().get(key_memory_total,0)) + "M"

        frame['HOST_MEM(%)']=host_mem
        frame['HOST_CPU(%)']=total_cpu

        info = self.get_platform_info()
        if info and info.get(key_version):
            frame['VER'] = info[key_version]

        self.update_storage_totals(frame)
        #pprint.pprint(frame)
        return frame
        
    
#    def get_platform_info(self):
#        platform_dict =self.environ['platform_info']
#        if platform_dict is None:
#            platform_dict={}
#            platform_dict = self.get_vmm_info()
#            self.environ['platform_info']=platform_dict
#            self.save_platform_info(platform_dict)
#        return platform_dict

    def get_platform_info_display_names(self):
        return { key_version : display_version }


    def migrate_dom(self, name, dest_node, live):
        """
        destroy dom
        """
        dom = self.get_dom(name)
        if dom.isDom0():
            return Exception(name + " can not be migrated.")
        migration_port=self.get_unused_port(dest_node.migration_port,dest_node.migration_port+10)
        if migration_port < 0:
            raise Exception("Migration : No port availabile in range on " + dest_node.hostname)
        self.get_dom(name)._migrate(dest_node, live,
                                    port=migration_port)

        self.refresh()

    

# Test code
if __name__ == "__main__":
    test_domu = "test"
    host = "localhost"
    dom_file = '/etc/kvm/test'
    dom_2b_started = 'test'
    dom_2b_shutdown = 'test'

    username = 'root'
    print "Enter password "
    passwd = sys.stdin.readline().strip()

    
    # basic connectivity
    remote = True
    if not remote:
        host = "localhost"
    else:
        host = '192.168.12.101'
        test_domu = "test"
        dom_file = '/etc/kvm/test'
        dom_2b_started = 'test'
        dom_2b_shutdown = 'test'
        
    managed_node = KVMNode(hostname=host,
                           username = username,
                           password = passwd,
                           isRemote=remote)

    ## list doms, knows and running
    names = managed_node.get_dom_names()

    
    for dom_name in names:
        print dom_name, managed_node.get_state(dom_name)

#    managed_node.start_dom("ubuntu_vm")

    for dom_name in names:
        print dom_name, managed_node.get_state(dom_name)

    ## create/destroy dom
    
    

    
    
