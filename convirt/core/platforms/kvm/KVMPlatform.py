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

# Integration class for the platform
import os

from convirt.model.Platform import Platform
from KVMDomain import KVMConfig
from KVMNodeFactory import KVMNodeFactory

class KVMPlatform(Platform):

    @classmethod
    def get_default_location(cls):
        return __file__

    def __init__(self, platform, client_config):
        Platform.__init__(self, platform, client_config)
            
    # initialize platform
    def init(self):
        Platform.init(self)

    # return if the platform is KVM enabled.
    def detectPlatform(self, managed_node):
        # check whether the local kvm is enabled
        return managed_node.node_proxy.file_exists("/dev/kvm")

    # return if the other necessary elements are in place for managing
    # KVM environment
    def runPrereqs(self, managed_node):
        kvm_enabled = managed_node.node_proxy.file_exists("/dev/kvm")
        kvm_access = managed_node.node_proxy.file_is_writable("/dev/kvm")
        if not kvm_enabled:
            return (False, ["KVM not enabled. Can not find /dev/kvm"])
        if not kvm_access:
            return (False, ["You do not have permission to manage VMs via KVM. Try running as root."])
        return (True, [])
    
    def get_node_factory(self):
        return KVMNodeFactory()

    # return an instance of a config given a filename
    def create_vm_config(self, node=None, filename=None,config=None):
        return  KVMConfig(node, filename,config)
        
    

