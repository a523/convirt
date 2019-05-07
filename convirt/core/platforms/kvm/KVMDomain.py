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


# KVM Domain

import sys,os,re,types,time


from convirt.core.utils.utils import search_tree, PyConfig,mktempfile
from convirt.core.utils.NodeProxy import Node
from convirt.core.utils.constants import *
from convirt.model.VM import *
from convirt.core.platforms.kvm.kvm_constants import my_platform
from convirt.core.utils.utils import getHexID
from convirt.model.availability import AvailState
import convirt.core.utils.constants
constants=convirt.core.utils.constants
class KVMDomain(VM):
    __mapper_args__ = {'polymorphic_identity': u'kvm'}
    
    def __init__(self, node,config=None, vm_info=None):
        """
        initialize using dom_info.
        a. can be used to create a new dom
        b. can be used to instantiate dom representation of a runnig dom.
        """
        VM.__init__(self, node, config, vm_info)
        
    def init(self):
        if self._config:
            self.name = self._config.name
            self._is_resident = False
        elif self._vm_info:
            self.name = self._vm_info.name
            self.pid = self._vm_info.id
            self._is_resident = True
            
    def set_vm_info(self,vm_info):
        self._vm_info=vm_info
        self.pid = self._vm_info.id
        self._is_resident = True

    def get_platform(self):
        return my_platform

        
    def __getitem__(self, param):
        if param == "name":
            return self.name
        else:
            if self._vm_info:
                return self._vm_info[param]
            return None

    # override the save
    def _save(self, filename):
        cfg = self.get_config()
        if cfg is None: # This can be relaxed later 
            raise Exception("Can not save snapshot without associated config.")
        self.node.get_vmm().save(self.pid, filename, cfg)

    # override migrate, as we need to pass more context
    def _migrate(self, dest,live, port):
        cfg = self.get_config()
        
        if cfg is None:
            raise Exception("Can not migrate KVM. Did not find any config associated with VM.\n Use Import VM Config and import the config file for this VM.")
        #print "cfg is None", cfg is None
        import copy
        cfg_clone = copy.copy(cfg) # shallow clone : Be careful

        if cfg_clone is None:
            raise Exception("Can not migrate KVM. Could not clone config associated with VM.")
        #print "cfg_clone is None", cfg_clone is None
        cfg_clone.set_filename(mktempfile(dest, self.name))
        cfg_clone.set_managed_node(dest)
        cfg_clone.write()

        self.node.get_vmm().migrate(self.pid, dest, live, port, cfg_clone)

    # return the (cmd, args)
    def get_console_cmd(self):
        return None
    
    def get_vnc_port(self):
        if self._vm_info is not None:
            vnc_port_string = self._vm_info.get("vnc")
            if vnc_port_string and vnc_port_string[0] == ':':
                return int(vnc_port_string[1:])
        return None

    def is_graphical_console(self):
        return True



    ## get stats
    def get_snapshot(self):
        if self._stats == None:
            self._stats = KVMStats(self)
        return self._stats.get_snapshot()

    def check_pause_state(self,values,wait_time,cmd_result):
        ###no reliable method to check if the kvm m/c is in paused state.
        ###relying on the o/p of KVMProxy pause method
        return cmd_result==True


    def check_unpause_state(self,values,wait_time,cmd_result):
        ###no reliable method to check if the kvm m/c is in paused state.
        ###relying on the o/p of KVMProxy unpause method
        return cmd_result==True

    def check_reboot_state(self,wait_time):
        ###TBD: consider acpi flag and see pid changes
        time.sleep(wait_time)
        return True
    
    def status_check(self):
        ###method to decide whether to proceed with metrics collection
        (cont,msg) = VM.status_check(self)
        if cont==False:
            return (cont,msg)
        if self.status == constants.PAUSED:
            msg="Virtual Machine "+self.name+"(KVM) is in Paused state."
            return (True,msg)
        return (True,None)

class KVMConfig(VMConfig):
    """
    represnts startup config object (information in the conf file)
    """


    # DomConfig follows
    def __init__(self, node, filename = None, config = None):
        """
        read stuff from file and populate the config
        when filename is None, creates an empty config
        """
        VMConfig.__init__(self, node,filename, config)
        

    # kvm specific validation.
    def validate(self):
        """Attempts to validate that the settings are not going to lead to
        any errors when the dom is started, and returns a list of the
        errors as strings"""

        result = []

        if not self["name"]:
            result.append("Missing domain name.")

        if not self["disk"]:
            result.append("Missing disk specification.")

        return result

# Not used
class KVMStats(VMStats):
    """
    represents statatistics/measurements for a vm. (CPU, I/O etc)
    This is abstracted out so we can cut over to some other source for
    runtime statastics/measurements
    """

    def __init__(self, vm):
        """
        constructor, dom for which the stats are to be obtained.
        """
        VMStats.__init__(self, vm)

    def get_snapshot(self):
        # get it from /proc/pid
        # OR run top -b -p <self.vm.pid>
        # 
        #for stat in ("memory", "cpu_time"):
        #   self.stat[stat] = ...
        return self.stat
    
    
### module initialization

    







    
    

    
    
