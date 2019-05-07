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


# VMM for the Xen Platform
from convirt.model.VMM import VMM
from convirt.core.utils.utils import dynamic_map,search_tree
from convirt.core.utils.utils import to_unicode,to_str
from XenServerProxy import ServerProxy, SSHTunnelTransport

# Map the sxp info
class XenVMInfo(dynamic_map):
    def __init__(self, sxp_info):
        dynamic_map.__init__(self)
        self.sxp_info = sxp_info

    def __getattr__(self, name):
        if not self.has_key(name):
            val = search_tree(self.sxp_info, name)
            self.__setattr__(name, val)

        return dynamic_map.__getattr__(self, name)

    def __getitem__(self,name):
        if not self.has_key(name):
            val = search_tree(self.sxp_info, name)
            self.__setattr__(name, val)

        return dynamic_map.__getitem__(self, name)
        


class XenVMM(VMM):
    DEFAULT_PATH = '/RPC2'

    def __init__(self, protocol, host, port, is_remote,
                 ssh_transport=None,
                 ssh_port=22,
                 user = None,
                 password = None,
                 use_keys = None,
                 node = None): # special case, required config.

        # initialize the proxy here..
        self.protocol = protocol
        self.hostname = host
        self.tcp_port = port
        self.is_remote = is_remote
        self.ssh_transport = ssh_transport
        self.username = user
        self.password = password
        self.use_keys = use_keys
        self.node = node

        self.xen_proxy = None
        self.xen_proxy = self._init_vmm()
        self._info = None
        
        self.state_api_exists=None
        self.check_point_supported=None

    def _init_vmm(self):
        if self.xen_proxy is not None:
            return self.xen_proxy

        # share the transport from the node_proxy
        if self.is_remote:
           if self.protocol == "tcp":
               self.xen_proxy = ServerProxy('http://' + self.hostname + ':' + 
                                            to_str(self.tcp_port) + self.DEFAULT_PATH)

           if self.protocol == "ssl":
              self.xen_proxy = ServerProxy('https://' + self.hostname + ':' + 
                                      to_str(self.tcp_port) + self.DEFAULT_PATH)
            
           if self.protocol == "ssh":
              self.xen_proxy = ServerProxy('ssh://' + self.username +'@' +
                                      self.hostname + self.DEFAULT_PATH)

           if self.protocol == "ssh_tunnel":
              self.xen_proxy = ServerProxy('ssh_tunnel://' + self.username +
                                      '@' +
                                      self.hostname + ":" +
                                      to_str(self.tcp_port) +
                                      self.DEFAULT_PATH,
                                      ssh_transport = self.ssh_transport,
                                      user = self.username,
                                      password=self.password,
                                      use_keys = self.use_keys )    
        else:
           self.xen_proxy = ServerProxy('httpu:///var/run/xend/xmlrpc.sock')
           
        return self.xen_proxy


    # implement the interface
    def info(self):
#        if self._info == None:
        if self._info is None :
            self._info = XenVMInfo(self.xen_proxy.xend.node.info()) # dom0 special VM Info
        return self._info

    def xm_info(self):
        return XenVMInfo(self.xen_proxy.xend.node.info()) # dom0 special VM Info

    def is_in_error(self):
        if isinstance(self.xen_proxy, ServerProxy):
          if self.xen_proxy is not None:
             return  self.xen_proxy._last_error is not None
          else:
             return True
       #elif isinstance(self.xen_proxy, base_pkg.ServerProxy):
       #   return False


    def connect(self):
        self._init_vmm()

    def disconnect(self):
        self.xen_proxy.close()
        self.xen_proxy = None
        self.state_api_exists=None
        self.check_point_supported=None



    # VM List
    def get_vms(self):
        vm_list_info = []
        if self.state_api_exists is None:
            #print "Calling listMethods to figure out if with_state API exists or not ", self.node.hostname
            rpc_methods = self.xen_proxy.system.listMethods()
            if "xend.domains_with_state" in rpc_methods:
                self.state_api_exists=True
            else:
                self.state_api_exists=False
         
        if not self.state_api_exists:
            #print "calling 30 API ", self.node.hostname
            vm_list_info = self.xen_proxy.xend.domains(1)
        else:
            #print "calling 31 API ", self.node.hostname
            vm_list_info = self.xen_proxy.xend.domains_with_state(True, #details
                                                                  'all',#state
                                                                  1) # full
        #import pprint; pprint.pprint(vm_list_info)
        if vm_list_info:
            ndx = 0
            for info in vm_list_info:
                vm_list_info[ndx] = XenVMInfo(info[1:])
                ndx += 1
                
        return vm_list_info
       


    # VM ops
    

    """ refresh the vm information """
    def refresh(self,id):
        return XenVMInfo(self.xen_proxy.xend.domain(id))


    def save(self, id, filename, checkpoint=True):
        if self.check_point_supported is None:
            rpc_methods = self.xen_proxy.system.listMethods()
            #signature=self.xen_proxy.system.methodSignature("xend.domain.save")
            # 
            # Ooops : signatures not supported. :(
            # Lets do best guess to see if checkpoint is supported or not.
            # Use the method name present in only 3.1 to guess 3.1+ stack.
            rpc_methods = self.xen_proxy.system.listMethods()
            if "xend.domains_with_state" in rpc_methods:
                self.check_point_supported=True
            else:
                self.check_point_supported=False

        if self.check_point_supported:
            self.xen_proxy.xend.domain.save(id, filename, checkpoint)
        else:
            self.xen_proxy.xend.domain.save(id, filename)

    def restore(self,filename):
        self.xen_proxy.xend.domain.restore(filename)


    def reboot(self, id):
        self.xen_proxy.xend.domain.shutdown(id, 'reboot')


    def start_dom(self, id):
        pass

    def shutdown(self,id):
        self.xen_proxy.xend.domain.shutdown(id, 'poweroff')


    def destroy(self,id):
        self.xen_proxy.xend.domain.destroy(id)
       

    def pause(self,id):
        self.xen_proxy.xend.domain.pause(id)


    def unpause(self,id):
        self.xen_proxy.xend.domain.unpause(id)


    def suspend(self,id):
        self.xen_proxy.xend.domain.suspend(id)


    def resume(self,id):
        self.xen_proxy.xend.domain.resume(id)


    def migrate(self, id, dst,live,port):
        self.xen_proxy.xend.domain.migrate(id,
                                           dst.get_address(),
                                           live, 0, port) 
        
    def start(self,config):
        raise Exception("Not implemented")



    # change to live running VM
    def setVCPUs(self, id, value):
        self.xen_proxy.xend.domain.setVCpuCount(id, value)

    def setMem(self, id, value):
        self.xen_proxy.xend.domain.setMemoryTarget(id, value)

    #### JD: TODO : cut these disk ops to use disk entry.
    # attach disks to live VM.
    def attachDisks(self,id,attach_disk_list):
        cmd=""
        for disk_data in attach_disk_list:
            disk_data_split=disk_data.split(",")
            cmd="xm block-attach "+to_str(id)+" "+disk_data_split[0]+" "+disk_data_split[1]+" "+disk_data_split[2]
            (output,code)=self.node.node_proxy.exec_cmd(cmd)
            if code==0:
                print "Attached=",disk_data
            else:
                raise Exception(output)

    # detach disks from live VM.
    def detachDisks(self,id,detach_disk_list, force=True):
        cmd=""
        for disk_data in detach_disk_list:
            disk_data_split=disk_data.split(",")
            device = disk_data_split[1]
            if device.find(":cdrom") > -1:
                index = device.find(":cdrom")
                device = device[0:index]

            cmd="xm block-detach "+to_str(id)+" "+device + " "
            if force:
                cmd = cmd + " --force"
            (output,code)=self.node.node_proxy.exec_cmd(cmd)
            if code==0:
                print "Detached=",disk_data
            else:
                raise Exception(output)

    
