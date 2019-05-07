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
# Currently this is implemented for Xen. (Later we can separate this
# and fromalize the interface. )


import sys,os,re,types,time

from convirt.core.utils.utils import PyConfig
from convirt.core.utils.NodeProxy import Node
from convirt.core.utils.constants import *
from convirt.model.VM import VM,VMConfig,VMStats,VMOperationException,DiskEntry
from convirt.core.platforms.xen.xen_constants import my_platform
from convirt.core.utils.utils import getHexID
from convirt.core.utils.utils import to_unicode,to_str,mktempfile
import convirt.core.utils.constants
constants=convirt.core.utils.constants
class XenDomain(VM):
    """
    This represent Doms. It encapsulates information about
    running virtual machine : state as well as resource stats
    """
    __mapper_args__ = {'polymorphic_identity': u'xen'}
    
    def __init__(self, node,config=None, vm_info=None):
        """
        initialize using vm_info.
        a. can be used to create a new dom
        b. can be used to instantiate dom representation of a runnig dom.
        """
        VM.__init__(self, node, config,vm_info)

    # called by base class post construction
    # set id, name, and is_resident state
    def init(self):
        if self._config:
            self.name = self._config.name
            self._is_resident = False
        elif self._vm_info is not None:
            self.name = self._vm_info.name
            self.pid = self._vm_info.domid
            self._is_resident = True
            
    def set_vm_info(self,vm_info):
        self._vm_info=vm_info
        self.pid = self._vm_info.domid
        self._is_resident = True

    def get_platform(self):
        return my_platform

    def isDom0(self):
        """Test wether the dom is dom0"""
        return self.is_resident() and self.pid == 0

    def isDomU(self):
        """Test wether the dom is a guest dom"""
        return self.is_resident() and self.pid > 0

    
    def __getitem__(self, param):
        if param == "name":
            return self.name
        else:
            if self._vm_info is not None:
                return self._vm_info[param]
            return None

    ## start
    def _start(self):
        self._start_vm()
    
    def _start_vm(self):       
        if self._config is None:
            raise Exception("Configuration not set. Can not start domain")
        try:            
            name=self._config.options['name']
            filename=mktempfile(self.node,name)
            file =self.node.node_proxy.open(filename, "w")
            for name,value in self._config.options.iteritems():
                if name=="disk":
                    disks=[]
                    for disk in value:
                        disks.append(disk.replace('lvm:', 'phy:', 1))
                    value=disks
                if type(value) in [types.UnicodeType]:
                    value=to_str(value)
                file.write("%s = %s\n" % (name, repr(value)))
            file.close()
         
        except Exception, e:
            import traceback
            traceback.print_exc()  
            raise e
        
        start_paused = 0
        if self._config.options.get("start_paused") == True:
           cmd = "xm create " + filename + " -p"
        else:
           cmd = "xm create " + filename
        print cmd
        (output, exit_code) = self.node.node_proxy.exec_cmd(cmd,self.node.exec_path)
        if not exit_code:            
            self.refresh()
        else:
            raise Exception("Domain could not be started: " + output)

    ## get stats
    def get_snapshot(self):
        if self._stats == None:
            self._stats = XenStats(self)
        return self._stats.get_snapshot()

    # return the (cmd, args)
    def get_console_cmd(self):
        managed_node = self.node
        # determine the architecture for the node
        print managed_node.environ
        if re.search('64', managed_node.get_os_info().get(key_os_machine,"")):
            arch_libdir = 'lib64'
        else:
            arch_libdir = 'lib'

        cmd = "/usr/"+arch_libdir+"/xen/bin/xenconsole"
        base = os.path.basename(cmd)
        return (cmd, [base, to_str(self.pid)])

    def get_vnc_port(self):
        path = '/local/domain/' + to_str(self.pid) + '/console/vnc-port'
        cmd = 'xenstore-read -p '
        (output, status) = self.node.node_proxy.exec_cmd(cmd + path)
        if status == 0 and output is not None:
            (p, port) = output.split(":")
            if port is not None:
                # the tightvnc viewer has explicit syntax for specifying port
                # while the realvnc takes both.
                # here, we assume that the base port which is usually 5900
                # is always divisible with 100.
                port = to_str(int(port) - 5900)
                return port

        return None

    def is_graphical_console(self):
        if self.get_vnc_port() is None:
            return False
        return True

    def check_reboot_state(self,wait_time):
        ###TBD: consider acpi flag 
        old_pid=self.pid 
        for x in range(0,wait_time):
            time.sleep(1)
            self.node.refresh()
            if self.pid != old_pid:
                ###dom rebooted successfully
                return True
        return False


# For now, we can implement the Xen specific stuff. Later we should
# drive it through metadata. (what attributes supported in file and
# running doms,nested attribute support) [May be do it now?]
#
class XenConfig(VMConfig):
    """
    represnts startup config object (information in the conf file)
    """

    imps = VMConfig.imps + ["#from xen.util.ip import *"]

    # XenConfig follows
    def __init__(self, node=None, filename = None, config=None):
        # call base class
        VMConfig.__init__(self, node, filename, config) 

        # xen specific stuff.
        for k in ("xm_help", "xm_file"):
            if self.options.has_key(k):
                del self.options[k]


    # custom read_conf
    def read_conf(self, init_glob=None, init_locs=None):
        # Leverage the fact that conf files are python syntax.
        # save on parsing code
        
        # Create global and local dicts for the file.
        # Initialize locals to the vars.
        globs = {}
        locs = {}
        
        cmd = '\n'.join(self.imps + 
                        [ "#from xen.xm.help import Vars",
                          "xm_file = '%s'" % self.filename,
                          "xm_help = %d" % 0,
                          "#xm_vars = Vars(xm_file, xm_help, locals())"
                          ])

        # Use exec to do the standard imports and
        # define variables we are passing to the script.
        exec cmd in globs, locs
        return PyConfig.read_conf(self, globs, locs)
    

    # Xen specific validation.
    def validate(self):
        """Attempts to validate that the settings are not going to lead to
        any errors when the dom is started, and returns a list of the
        errors as strings"""

        result = []

        if not self["name"]:
            result.append("Missing domain name.")

        if not self["disk"]:
            result.append("Missing disk specification.")

        if not self["bootloader"]:
            # if a bootloader is not specified,
            # check for valid kernel and ramdisk
            for parm in ("kernel"): # ramdisk is optional
                if not self[parm] or not self.node.node_proxy.file_exists(self[parm]):
                    result.append("Invalid file name for %s." % parm)
                    

        for parm, nodeval in (("memory", "total_memory"),
                               ("vcpus", "nr_cpus")):
            if self[parm] and int(self[parm]) > int(ManagedNode.getNodeVal(nodeval)):
                result.append("More %s requested than total %s." % (parm,
                                                                    parm))

        return result



    

class XenStats(VMStats):
    """
    represents statatistics/measurements for a dom. (CPU, I/O etc)
    This is abstracted out so we can cut over to some other source for
    runtime statastics/measurements
    """

    def __init__(self, dom):
        """
        constructor, dom for which the stats are to be obtained.
        """
        VMStats.__init__(self,dom)

    def get_snapshot(self):
        self.dom.refresh()
        for stat in ("memory", "cpu_time"):
            self.stat[stat] = dom[stat]
        return self.stat


    
### module initialization

    







    
    

    
    
