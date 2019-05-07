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
from convirt.core.utils.utils import get_platform_defaults
from convirt.core.utils.constants import prop_default_computed_options

class XenPlatform(Platform):

    @classmethod
    def get_default_location(cls):
        return __file__


    def __init__(self, platform, client_config):
        Platform.__init__(self, platform, client_config)

            
    # initialize platform
    def init(self):
        xen_config_computed_options = self.client_config.get(prop_default_computed_options)
        if xen_config_computed_options is None:
            defaults = ["arch", "arch_libdir", "device_model"]
        else:
            defaults = eval(xen_config_computed_options)
        import XenDomain
        XenDomain.XenConfig.set_computed_options(defaults)




    # return if the platform is Xen
    def detectPlatform(self, managed_node):
        # check whether the local kernel is recognisable as xen
        return managed_node.node_proxy.file_exists("/proc/xen/capabilities")

    # return if the other necessary elements are in place for managing Xen environment
    def runPrereqs(self, managed_node):
        (out, code) = managed_node.node_proxy.exec_cmd("id -u")
        if code == 0:
            if out.strip() == "0":
                return (True,[])
            else:
                return (False, ["Must be running as root to manage Xen environment."])
        else:
            return (False, ["Error executing prereq for %s : %s" % (my_platform, out)])
        return (True, [])

    def get_node_factory(self):
        import XenNodeFactory
        return XenNodeFactory.XenNodeFactory()

    # return an instance of a config given a filename
    def create_vm_config(self, node=None, filename=None,config=None):
        import XenDomain
        return  XenDomain.XenConfig(node, filename,config)
        
    

