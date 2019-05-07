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

# Represents ManagedNode with Xen

import sys,os,re,types, socket

from convirt.model.ManagedNode import ManagedNode

from convirt.core.utils.utils import constants, Poller
from convirt.core.utils.utils import to_unicode,to_str
from convirt.model.VM import VM
from convirt.model.VNode import VNode
from convirt.model.ManagedNode import NodeEnvHelper
from convirt.model import DBSession

from XenDomain import *

from xen_constants import *
import traceback

from sqlalchemy import  Column
from sqlalchemy.types import *
from sqlalchemy import orm
from convirt.model.DBHelper import DBHelper
from convirt.model.NodeInformation import Category,Component,Instance

import logging
LOGGER = logging.getLogger("convirt.core.platforms.xen")
class XenNode(VNode):
    """
    Interface that represents a node being managed.It defines useful APIs
    for clients to be able to do Management for a virtualized Node
    """

    tcp_port=Column(Integer,default=8006)
    #migration_port=Column(Integer,default=8002)
    protocol=Column(Unicode(255))

    __mapper_args__ = {'polymorphic_identity': u'xen'}

    def __init__(self,
                 hostname = None,
                 username= Node.DEFAULT_USER,
                 password=None,
                 isRemote=False,
                 protocol = "tcp",
                 tcp_port = 8006,
                 ssh_port = 22,
                 migration_port = 8002,
                 helper = None,
                 #store = None,
                 use_keys = False,
                 address = None):

        VNode.__init__(self,
                       to_unicode("xen"), #platform, I'm xen node
                       #store,
                       hostname,
                       username, password,
                       isRemote,
                       ssh_port,
                       helper,
                       use_keys,
                       address)
        self._dom0     = None

        self.metrics_helper = MetricsHelper(self)

        self.tcp_port = tcp_port
        self.migration_port = migration_port
        self.protocol = protocol

    @orm.reconstructor
    def init_on_load(self):
        VNode.init_on_load(self)
        self._dom0 = None
        self.metrics_helper = MetricsHelper(self)
        
    def get_auto_config_dir(self):
        return '/etc/xen/auto'

    #def get_config_dir(self):
    #    return '/etc/xen'


        
    # Factory method to create vm
    def new_config(self, filename):
        return XenConfig(self, filename)

    def new_vm_from_config(self, config):
        return XenDomain(self, config=config)

    def new_vm_from_info(self, info):
        return XenDomain(self, vm_info=info)

    # return a list of running VMs
    def get_running_vms(self):
        current_dict = {}
        vm_list_info = self.get_vmm().get_vms()
        for vm_info in vm_list_info:
            vm = XenDomain(self,vm_info=vm_info)
            if vm.pid == 0:
                self._set_dom0(vm)
            #else
            #ALLOW Dom 0 to be in the list too
            #This would allow twaking mem and cpus
            # The xend-managed returns non-running vms too. ignore id = None 
            if vm.pid is not None:
                current_dict[vm.name] = vm
            
        return current_dict

    def _init_vmm(self):
        from XenVMM import XenVMM
        return XenVMM(self.protocol, self.hostname, self.tcp_port,
                      self.isRemote,
                      self.node_proxy.transport,
                      self.ssh_port, self.username, self.password,
                      self.use_keys, self)
    

    #def __getattr__(self, name):
    #    if name == 'node_info':
    #        return self.get_vmm().info()
    #    else:
    #        return VNode.__getattr__(self, name)

    # encapsulate the host and dom0 information here.        
    def __getitem__(self, param):
        node_info = self.node_info
        val = node_info[param]
        #val = VNode.__getitem__(self, param)
        if  val == None:
            # try the dom0            
            return self._dom0[param]
        else:
            return val


    def _set_dom0(self,dom):
        self._dom0 = dom

    # provide the snapshot to the base class
    def get_metric_snapshot(self,filter=False):
       return self.metrics_helper.getFrame(filter=filter)

    def get_connection_port(self):
        return self.tcp_port

    # can Server run hvm image?
    def is_HVM(self):
        if self["xen_caps"] and self["xen_caps"].find("hvm") > -1:
           return True
        else:
           return False

    def is_image_compatible(self, image):
        if image:
            if image.is_hvm() and self.is_hvm():
		return True
            if self.get_platform() == image.get_platform() :
                # xen image check for hvm
                if image.is_hvm():
                    return self.is_hvm() # node needs to be hvm enabled as well
                else:
                    return True
        return False


   
    # check if a given dom can be migrated to the destination node
    def migration_op_checks(self, vm_list, dest_node,live):       
       (err_list, warn_list) = VNode.migration_op_checks(self, vm_list, dest_node, live)
       
       # src is not same as dest

       self._compare_node_info(dest_node, "xen_major", err_list)
       self._compare_node_info(dest_node, "xen_minor", err_list)

       # find total mem requirements and check against avail mem

       if len(vm_list) < 2:
          return (err_list, warn_list)

       if not live:
          return (err_list, warn_list)

       total_vm_mem = 0
       for vm in vm_list:
          if vm.is_running():
             total_vm_mem += int(vm["memory"])
       if dest_node.is_up():
           node_free_mem = self.guess_free_mem(dest_node)
           if total_vm_mem > node_free_mem:
              err_list.append(("Memory", "Insufficient memory on destination node. " \
                              "Total VM memory %s, free memory on destination node %s " %
                              (total_vm_mem, node_free_mem)))


               
       
       return (err_list, warn_list)

    def guess_free_mem(self, dest_node):
       mem = dest_node["memory"]
       free_mem = dest_node["free_memory"]
       node_free_mem = 0
       if mem and free_mem:
           dom0Mem = int(mem)
           dom0Min = 256 # assume that dom0 can ballon down to 256 M
           if dom0Mem > dom0Min :
               node_free_mem = int(free_mem) + dom0Mem - dom0Min
               print "returning adjusted free mem", node_free_mem
           else:
               node_free_mem = int(free_mem )


       return node_free_mem

       

    ## TBD : Make output of these checks more structured.
    ##       Test name, Context (vm name), message
    def migration_vm_checks(self, vm_name, dest_node, live):
       """
       Implements a series of compatiblity checks required for successful
       migration.
       """
       (err_list, warn_list) = VNode.migration_vm_checks(self, vm_name,
                                                         dest_node, live)
       
       if self.is_up():
            vm = self.get_dom(vm_name)
       else:
            vm = DBHelper().find_by_name(VM,vm_name)
       if vm == None :
          err_list.append(("VM", "VM %s not found."% vm_name))
          return (err_list, warn_list)


       # mem assumed to be in MB (same unit)
       vm_memory = 0
       if vm.is_running():
          vm_memory = vm["memory"]

       if dest_node.is_up():
           node_free_mem =  self.guess_free_mem(dest_node)
           if int(vm_memory) >  node_free_mem:
              err_list.append(("Memory","Insufficient memory on destination node. " \
                              "VM memory %s, free memory on destination node %s " % 
                              (vm["memory"], node_free_mem)))

       # TBD : compare CPUs. This needs to encode compatibility list.
       #       check AMD/INTEL
       #       X86/X32

       # 32 bit vs 64 bit kernel

       # critical files available or not.
       vm_conf = vm.get_config()
       if vm_conf is not None and dest_node.is_up():
          bootloader = vm_conf["bootloader"]
          if bootloader and bootloader.strip() is not "":
             if not dest_node.node_proxy.file_exists(bootloader.strip()):
                err_list.append(("Bootloader","Bootloader %s for %s vm not found on destination node." % (bootloader.strip(), vm.name)))
          kernel = vm_conf["kernel"]
          if kernel and kernel.strip() is not "":
             if not dest_node.node_proxy.file_exists(kernel.strip()):
                err_list.append(("Kernel","Kernel %s for %s vm not found on destination node." % (kernel.strip(), vm.name)))
          ramdisk = vm_conf["ramdisk"]
          if ramdisk and ramdisk.strip() is not "":
             if not dest_node.node_proxy.file_exists(ramdisk.strip()):
                err_list.append(("Ramdisk", "Ramdisk %s for %s vm not found on destination node." % (ramdisk.strip(), vm.name)))
     
       # hvm availablity
       if vm_conf and vm_conf.is_hvm() \
          and dest_node.get_platform_info().get("xen_caps","").find("hvm")==-1:
          err_list.append(("HVM","VM %s requires hvm capabilities which are not found on destination node." % (vm.name)))


       # TBD : PAE kernel check

       return (err_list, warn_list)
       

    def _compare_node_info(self,dest_node, key, msg_list):
#       src_val = self[key]
#       dest_val = dest_node[key]
       src_val = self.get_platform_info().get(key)
       dest_val = dest_node.get_platform_info().get(key)

       if src_val != dest_val:
          msg_list.append((key.upper(), key+" version is not the same on both"+
                "source server and destination server. Source : "+to_str(src_val)+
                ", Destination "+to_str(dest_val)))

#    def get_platform_info(self):
#        platform_dict =self.environ['platform_info']
#        if platform_dict is None:
#            platform_dict={}
#            vmm_info = self.get_vmm_info()
#            xen_ver =""
#            xen_major = to_str(vmm_info['xen_major'])
#            xen_minor = to_str(vmm_info['xen_minor'])
#            xen_extra = to_str(vmm_info['xen_extra'])
#            xen_ver += xen_major + "." + xen_minor + xen_extra
#
#            platform_dict['xen_version'] =xen_ver
#            caps_value =  vmm_info['xen_caps']
#            if caps_value:
#                caps_value = caps_value.strip().replace(" ",", ")
#                platform_dict['xen_caps']=caps_value
#
#            platform_dict['xen_major']=vmm_info['xen_major']
#            platform_dict['xen_minor']=vmm_info['xen_minor']
#            self.environ['platform_info']=platform_dict
#            self.save_platform_info(platform_dict)
#        return platform_dict

    def get_platform_info_display_names(self):
        display_dict = {key_platform_xen_version:display_platform_xen_version,
                        key_platform_xen_caps:display_platform_xen_caps}
        return display_dict

    def get_VM_count(self):
        return (VNode.get_VM_count(self) -1) # adjust for dom0

    def getEnvHelper(self):
        return XenNodeEnvHelper(self.id,None)

    def populate_platform_info(self):
        platform_dict={}
        vmm_info = self.get_vmm_info()
        xen_ver =""
        xen_major = to_str(vmm_info['xen_major'])
        xen_minor = to_str(vmm_info['xen_minor'])
        xen_extra = to_str(vmm_info['xen_extra'])
        xen_ver += xen_major + "." + xen_minor + xen_extra

        platform_dict['xen_version'] =xen_ver
        caps_value =  vmm_info['xen_caps']
        if caps_value:
            caps_value = caps_value.strip().replace(" ",", ")
            platform_dict['xen_caps']=caps_value
        return platform_dict


class XenNodeEnvHelper(NodeEnvHelper):

    def populate_mem_info(self):
        m_node=DBSession.query(ManagedNode).filter(ManagedNode.id==self.node_id).one()
        xm_dict=m_node.get_vmm().xm_info()
        memory_values = []
        if xm_dict is not None:
            memory_values.append(xm_dict['total_memory'])
            memory_values.append(xm_dict['free_memory'])
        
        return memory_values
    
class MetricsHelper:
    """A Helper to fetch and format runtime metrics from a Xen Host"""

    FRAME_CMD = 'xentop -b -i 2 -d 1'
    
    def __init__(self, node):
        self.node = node

    def getFrame(self,filter=False):
        """returns a dictionary containing metrics for all running domains
        in a frame"""
 
        xen_ver=self.node.get_platform_info().get("xen_version")
        xen_ver=xen_ver.split(".")
        xen_version=int(xen_ver[0])

        if xen_version>=int(constants.XEN_NEW_VERSION):
            self.FRAME_CMD = 'xentop -b -i 2 -d 1 -f'


        (retbuf, retcode) = self.node.node_proxy.exec_cmd(self.FRAME_CMD,
                                                          self.node.exec_path)
        if retcode:
            LOGGER.error("metrics Command error on Server:"+self.node.hostname)
            LOGGER.error("command = "+self.FRAME_CMD)
            err = "retcode :%s, error :%s" % (retcode,retbuf)
            LOGGER.error(err)
            raise Exception(err)

        # hack to eliminate unwanted vbd entries.
        cleansed_retbuf = re.sub('vbd.*\n','',retbuf)

        frame = {} # the output metric frame (dict of dict's)


        #extract the xen version
        m = re.search('xentop.*(Xen.*?)\n',cleansed_retbuf,re.S)
        if not m:
           #build it from node info
           v = "Xen " + to_str(self.node["xen_major"]) + "." +to_str(self.node["xen_minor"])+ \
               self.node["xen_extra"]
           frame['VER'] = v
        else:
           frame['VER'] = m.group(1)

        #initialise aggregation counters
        frame['VM_TOTAL_CPU'] = 0.0  # not normalized cpu %
        frame['VM_TOTAL_MEM'] = 0.0  # memory used (not %)
        frame['VM_TOTAL_CPU(%)'] = 0.0
        frame['VM_TOTAL_MEM(%)'] = 0.0

        frame['VM_TOTAL_NETS'] = 0
        frame['VM_TOTAL_NETTX(k)'] = 0
        frame['VM_TOTAL_NETRX(k)'] = 0

        frame['VM_TOTAL_VBDS']   = 0
        frame['VM_TOTAL_VBD_OO'] = 0
        frame['VM_TOTAL_VBD_RD'] = 0
        frame['VM_TOTAL_VBD_WR'] = 0

        # split the returned buffer into individual frame buffers ...
        frames = re.split('xentop.*\n',cleansed_retbuf,re.S)
        #... and use the last frame buffer for creating the metric frame
        fbuffer = frames[-1:][0]

        # extract host cpu and mem configuration
        m = re.search('Mem:(.*) total.*CPUs:(.*)',fbuffer)
        if not m:
           # build info from node info
           cpu_str = to_str(self.node["nr_cpus"]) + " @ " + \
                     to_str(self.node["cpu_mhz"]) + "MHz"
           frame['SERVER_CPUs'] = cpu_str
           frame['SERVER_MEM'] =  to_str(self.node["total_memory"]) + "M"
#           host_total_mem=float(self.node["total_memory"])

        else:
           frame['SERVER_CPUs'] = m.group(2).strip()
           mem=float(m.group(1).strip()[:-1])/1024
           frame['SERVER_MEM'] = to_str(mem)+ "M"
#           host_total_mem=mem

        # extract overall runtime domain stats
        m = re.search('(\d+) running.*(\d+) paused.*(\d+) crashed',fbuffer)
        
        mem_buf =  re.search("Mem:[ \t]+(\d+)k total,[ \t]+(\d+).*\n", fbuffer)
        host_mem=0.0
        if mem_buf != None:
            total_mem = int(mem_buf.group(1))/1024  # in MB
            used_mem = int(mem_buf.group(2))/1024   # in MB
            host_mem=(float(used_mem)/float(total_mem))*100            
        else:
            xm_dict=self.node.get_vmm().xm_info()
            #print xm_dict,"-------\n\n",xm_dict.get('sxp_info')
            if xm_dict is not None:
                totalmem=xm_dict['total_memory']
                freemem=xm_dict['free_memory']
                host_mem=((float(totalmem)-float(freemem))/float(totalmem))*100
#            FRAME_XM_INFO="xm info | grep -i memory | awk \'{print $3}\'"
#            (retbuf, retcode) = self.node.node_proxy.exec_cmd(FRAME_XM_INFO,
#                                                        self.node.exec_path)
#
#            if retcode==0:
#                totalmem=retbuf.split("\n")[0]
#                freemem=retbuf.split("\n")[1]
#                host_mem=((float(totalmem)-float(freemem))/float(totalmem))*100
        
        running = 0
        paused  = 0
        crashed = 0
        dom0_cpu = 0
        
        agg_found = False
        if not m:
           # do aggregation in the loop later
           frame['RUNNING_VMs'] = 0
           frame['PAUSED_VMs']  = 0
           frame['CRASHED_VMs'] = 0
           frame['TOTAL_VMs'] = 0
        else:
            ###commented on 25/11/09
            ###we can consider only the convirt created vms
#           agg_found = True
#           frame['RUNNING_VMs'] = int(m.group(1).strip())
#           frame['PAUSED_VMs']  = int(m.group(2).strip())
#           frame['CRASHED_VMs'] = int(m.group(3).strip())
           frame['RUNNING_VMs'] = 0
           frame['PAUSED_VMs']  = 0
           frame['CRASHED_VMs'] = 0
           frame['TOTAL_VMs'] = 0
           pass
           ###end

        # parse the metric frame buffer for per domain stats
        lines = fbuffer.split('\n')[:-1]
        mbuffer = ''
        # strip unused entries at the top of the buffer
        # and extract the metric (sub)buffer
        

##         for l in lines:
##             if l.strip().startswith('NAME'):
##                 mbuffer = lines[lines.index(l):]
##                 break

        for i in range(1,len(lines)+1):
           ndx = len(lines) - i
           l = lines[ndx]
           if l.strip().startswith('NAME'):
              mbuffer = lines[ndx:]
              break

        # construct the metric frame as a dict of dictionaries
        # containing metric-name, metric-value pairs
        cleanup_exp = re.compile('[a-zA-Z]+\s[a-zA-Z]+ | n/a')
        outside_vms=[]
        for d in mbuffer[1:]:
            cleansed = re.sub(cleanup_exp,'None',d)
            d_frame = dict(zip(mbuffer[0].split(),cleansed.split()))

            st = d_frame["STATE"]
            ###filtering out crashed VMs
            if st and st[0] == 'd':
                continue

            ###added on 25/11/09
            ###to consider only the convirt created vms
            dom_names,vm_dict=self.node.get_all_dom_names()
            frame['TOTAL_VMs'] = len(dom_names)

            if d_frame["NAME"]!= 'Domain-0' and d_frame["NAME"] not in dom_names:
                if not agg_found:
                   st = d_frame["STATE"]
                   if st and st != "n/a":
                      if st[5] == 'r':
                         d_frame["STATE"] = VM.RUNNING
                      elif st[2] == 'b':
                         d_frame["STATE"] = VM.RUNNING
                      elif st[4] == 'p':
                         d_frame["STATE"] = VM.PAUSED
                      elif st[3] == 'c':
                         d_frame["STATE"] = VM.CRASHED
                      elif st == '------':
                         d_frame["STATE"] = VM.RUNNING
                      else:
                         d_frame["STATE"] = VM.SHUTDOWN
                
                outside_vms.append(dict(name=d_frame["NAME"],status=d_frame["STATE"]))
                continue
            ###end
            
            if not agg_found:
               st = d_frame["STATE"]
               d_frame["STATE"] = VM.SHUTDOWN
               if st and st != "n/a" and len(st)>5:
                  # NOTE : xentop has its own state format string.
                  # I cant believe this mess.                  
                  if st[5] == 'r':
                     frame['RUNNING_VMs'] += 1
                     d_frame["STATE"] = VM.RUNNING
                  elif st[2] == 'b':
                     frame['RUNNING_VMs'] += 1
                     d_frame["STATE"] = VM.RUNNING
                  elif st[4] == 'p':
                     frame['PAUSED_VMs'] += 1
                     d_frame["STATE"] = VM.PAUSED
                  elif st[3] == 'c':
                     frame['CRASHED_VMs'] += 1
                     d_frame["STATE"] = VM.CRASHED
                  elif st == '------':
                     ###unknown state is counted as running
                     ###need to think through
                     frame['RUNNING_VMs'] += 1
                     d_frame["STATE"] = VM.UNKNOWN
                  else:
                     d_frame["STATE"] = VM.SHUTDOWN



            if d_frame.get('CPU(%)') is not None:
               if d_frame['NAME'] != 'Domain-0':
                  # keep running count of total cpu util (not-normalized)
                  frame["VM_TOTAL_CPU"] += float(d_frame["CPU(%)"])

                  dom = vm_dict[d_frame["NAME"]]
                  vcpus = float(dom.getVCPUs())
                  d_frame['VM_CPU(%)'] = d_frame['CPU(%)']
                  if vcpus > 1: # adjust the utilization to 100%
                     #print d_frame["NAME"],"===",d_frame['CPU(%)'],"New::::::::::::",to_str(float(d_frame['CPU(%)']) / (vcpus))
                     d_frame['VM_CPU(%)'] = to_str(float(d_frame['CPU(%)']) / vcpus)

               nr_cpus = self.node["nr_cpus"]
               if nr_cpus > 1: # adjust the utilization to 100%
                  d_frame['CPU(%)'] = to_str(float(d_frame['CPU(%)']) / nr_cpus)

                                          
            self.node.augment_storage_stats(d_frame["NAME"], d_frame)
            
            frame[d_frame["NAME"]] = d_frame
            # compute running aggregates
            if d_frame['NAME'] != 'Domain-0':
                frame['VM_TOTAL_CPU(%)'] += float(d_frame['CPU(%)'])
                frame['VM_TOTAL_MEM(%)'] += float(d_frame['MEM(%)'])

                frame['VM_TOTAL_NETS'] += int(d_frame['NETS'])
                frame['VM_TOTAL_NETTX(k)'] += int(d_frame['NETTX(k)'])
                frame['VM_TOTAL_NETRX(k)'] += int(d_frame['NETRX(k)'])

                frame['VM_TOTAL_VBDS'] += int(d_frame['VBDS'])  
                frame['VM_TOTAL_VBD_OO'] += int(d_frame['VBD_OO'])
                frame['VM_TOTAL_VBD_RD'] += int(d_frame['VBD_RD'])
                frame['VM_TOTAL_VBD_WR'] += int(d_frame['VBD_WR'])
            else:
                dom0_cpu=float(d_frame.get('CPU(%)'))

        if filter:
            self.node.insert_outside_vms(outside_vms)

        # vm memory used in the same units as total memory.
        frame['VM_TOTAL_MEM'] =  (frame['VM_TOTAL_MEM(%)'] * self.node["total_memory"]) / 100.0

        frame['HOST_MEM(%)']=host_mem
        frame['HOST_CPU(%)']=frame['VM_TOTAL_CPU(%)'] + dom0_cpu
        
        # do not report Dom0
        if frame['RUNNING_VMs'] > 0 : 
           frame['RUNNING_VMs'] = frame['RUNNING_VMs'] - 1 


        self.node.update_storage_totals(frame)
        return frame
        

# Test code
if __name__ == "__main__":
    test_domu = "test"
    host = "localhost"
    dom_file = '/etc/xen/test'
    dom_2b_started = 'test'
    dom_2b_shutdown = 'test'

    username = 'root'
    passwd = ''
    
    # basic connectivity
    remote = False
    if not remote:
        host = "localhost"
    else:
        host = '192.168.123.155'
        test_domu = "test"
        dom_file = '/etc/xen/test'
        dom_2b_started = 'test'
        dom_2b_shutdown = 'test'
        
    managed_node = XenNode(hostname=host,
                           username = username,
                           password = passwd,
                           isRemote=remote)

    ## create/destroy dom
    dom_config = XenConfig(managed_node, dom_file)
    dom_config["memory"] = 256
    dom_config["vif"] = ['bridge=xenbr1']
    m = { 'VM_NAME':'foo', 'IMAGE_NAME':'anaconda' } 
    dom_config.instantiate_config(m)
    print dom_config.default_computed_options, dom_config.get_computed_options()
    dom_config.save("/foo/test_config")

    sys.exit(0)
    
    dom_config = XenConfig(managed_node,dom_file)
    dom_name = managed_node.create_dom(dom_config)
    print 'resident?', managed_node.isResident(dom_name)
    managed_node.destroy_dom(dom_name)
    print 'Doms b4 removal: ',managed_node.get_dom_names()
    managed_node.remove_dom_config(dom_file)
    print 'Doms post removal: ',managed_node.get_dom_names()

    dom_name = managed_node.create_dom_from_file(dom_file)
    print 'resident?', managed_node.isResident(dom_name)
    managed_node.destroy_dom(dom_name)
    print 'Doms b4 removal: ',managed_node.get_dom_names()
    managed_node.remove_dom_config(dom_file)
    print 'Doms post removal: ',managed_node.get_dom_names()
    
    ## start / stop dom and check its running state    

    managed_node.add_dom_config(dom_file)
    for name in  managed_node.get_dom_names():
        print name
        
    ## start / stop dom and check its running state
    managed_node.start_dom(dom_2b_started)
    print 'resident?', managed_node.isResident(dom_2b_started)
    print 'memory: ',managed_node.get_dom(dom_2b_started)["memory"] 
    print 'destroying ... '
    managed_node.destroy_dom(dom_2b_started)
    print "resident?" ,managed_node.isResident(dom_2b_shutdown)
    
    
    sys.exit(0)
    #################################################
    
    doms  = managed_node.get_doms()  # test dom information.
    for dom in doms:
        print "##### some info from dom object for dom  ###"
        for key in ("name", "memory", "kernel"):
            print key, "=" , dom[key]

        if dom.is_resident():
            print "device" ,"=", dom["device"]  #priniting first device only, BUG!!
            print "image" , "=", dom["image"]
        else:
            print "disk"," ="
            for disk in dom.get_config().getDisks():
                print disk
            print "network", "=", dom.get_config()["vif"]


    managed_node.remove_dom_config(dom_file)
    for name in  managed_node.get_dom_names():
        print name


    # get doms by name or id
    print "Access domain by name as well as id"
    dom_by_name = doms[test_domu]
    dom_by_id = doms[doms[test_domu].id]

    print dom_by_name.name, dom_by_id.name


    # get the stats
##     print "### get measurement snapshot ###"
##     stats = dom_by_name.get_snapshot()
##     for stat in stats:
##         print stat,"=",stats[stat]


    # empty dom config, create a new file
    print "### new empty config and creating a file."
    newcfg = XenConfig(managed_node)
    newcfg["name"] = "Txx"
    newcfg["memory"] = 299
    newcfg.set_filename("/foo/Txx")
    newcfg.write()

    f = managed_node.node_proxy.open("/foo/Txx")
    x = f.read(1024)
    print x
    f.close()

    print "### read config from /etc/xen/auto and write them to /foo"
    ## Dom Config
    for f in managed_node.node_proxy.listdir("/etc/xen/auto"):
        fin = "/etc/xen/auto/"+f
        print fin
        d = XenConfig(managed_node, fin)
        d.save("/foo/" + f)
    

    print "### get first file in /etc/xen/auto and dump its info"
    ## access this through dom
    d = None
    for f in managed_node.node_proxy.listdir("/etc/xen/auto"):
        fin = "/etc/xen/auto/"+f
        d = XenDomain(managed_node, fin)
        break    # pick up first file
    

    if d != None:
        print "#### dumping config ####"
        cfg =  d.get_config()
        cfg.dump()
        print "disk config"
        disks = cfg.getDisks()
        for disk in disks:
            print disk
    
        print "### modified memory to 300, dumping again ### "
        cfg['memory'] = 300
        cfg.dump()
        
    else:
        print "No Dom in /etc/auto"
    


    ## test the nodeinfo
    print "########## Host information ##########"
    for key in ("system", "host","release", "version", "machine", "nr_cpus",
                "nr_nodes","sockets_per_node",
                "cores_per_socket", "threads_per_core",
                "cpu_mhz","total_memory","free_memory","xen_caps",
                "platform_params","xen_changeset"):
        
        print key,"=",managed_node[key]


    print "########## getting dom0 information from managed node ##########"
    # Note dom0 information does not contain few things available in
    # other domus, example, uptime,device, network..!? 
    for key in ("cpu_time", "state","uptime", "online_vcpus"):
        print key,"=",managed_node[key]
    

    

    sys.exit(0)
    
    ### test create
    cfg = XenConfig(managed_node, "/etc/xen/T99")
    cfg["name"] = "T99"
    cfg["memory"] = 256
    cfg["vif"] = []
    cfg["vcpu"] = 1
    cfg["disk"] = ['file:/domu_disks/T99',xvda,w]

    d = managed_node.create_dom(cfg)
    print d["memory"], d.is_resident()

    
    

    
    
