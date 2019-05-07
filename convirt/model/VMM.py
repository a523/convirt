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

# Contains Interface recommended to be implemented by new VMM proxy.
# VMM proxy is to be used by the VNode and VM, and not directly by the client.

class VMM:

    # interface methods

    """ info about the vmm capabilities and node info as seen by vmm """
    def info(self):
        return {}

    """ if the vmm is in some error state."""
    def is_in_error(self):
        return False

    """  connect to the vmm (if not connected)"""
    def connect(self):
        pass

    """ disconnect from the vmm """
    def disconnect(self):
        pass


    # VM List
    # return the list of known VMs
    def get_vms(self):
        pass
    
    def save(self, id, filename):
        pass

    def restore(self,filename):
        pass

    def reboot(self, id):
        pass

    def shutdown(self,id):
        pass

    def destroy(self,id):
        pass

    def pause(self,id):
        pass

    def unpause(self,id):
        pass

    def suspend(self,id):
        pass

    def resume(self,id):
        pass

    def migrate(self, id, dst,live,port):
        pass

    def start(self,id):
        pass


    # refresh running vm information
    def refresh(self, id):
        pass

    # change to live running VM
    def setVCPUs(self, id, value):
       pass

    def setMem(self, id, value):
       pass
    # attach disks in memory
    def attachDisks(self,id,attach_disk_list):
       pass

    # detach disks in memory
    def detachDisks(self,id,detach_disk_list):
       pass


