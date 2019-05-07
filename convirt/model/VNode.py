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


# This class represents a node with a virtualized platform
# 
#
from convirt.core.utils.utils import Poller
from convirt.core.utils.utils import to_unicode,to_str, p_task_timing_start,p_task_timing_end
import convirt.core.utils.constants
from ManagedNode import ManagedNode
from convirt.model.DBHelper import DBHelper
from convirt.model.Entity import Entity
from convirt.model.VM import VM, OutsideVM
from convirt.model.Metrics import MetricsService
from convirt.model.NodeInformation import Category,Component,Instance
constants = convirt.core.utils.constants
import traceback, pprint, socket, logging
from datetime import datetime
from convirt.model.availability import AvailState, update_avail
from convirt.model import DBSession
from convirt.model.LockManager import LockManager
from sqlalchemy import func
LOGGER = logging.getLogger("convirt.model.VNode")
AVL_LOGGER = logging.getLogger("AVAIL_TIMING")

class VNode(ManagedNode):
    """
    Interface that represents a node being managed.It defines useful APIs
    for clients to be able to do Management for a virtualized Node
    """

    """
    
    ## Here is a list of methods in the interface
    def connect(self)
    def disconnect(self)
    def is_in_error(self)

    ## VM list 
    def get_VM_count(self)
    def get_dom_names(self)
    def get_doms(self)
    def get_dom(self)
    def refresh(self)

    def add_dom_config(self, filename)
    def remove_dom_config(self, filename)

    # create/start new VMs
    def create_dom(self, config)
    def create_dom_from_file(self, filename)


    # Xen legacy
    def isDom0(self)
    def isDomU(self)

    # VM ops
    def get_state(self, name)
    def is_resident(self, name)
    def state_dom(self,name)
    def pause_dom(self, name)
    def resume_dom(self,name)
    def shutdown_dom(self, name)
    def destroy_dom(self,name)
    def reboot_dom(self, name)

    
    def restore_dom(self, name)
    def migrate_dom(self, name, dest, live, bw=None)


   ## NOTE : Migration checks interfaces are likely to change
   # return (errlist, warnlist)
   # err/warn list = list of tuple(category, message) 
   def migration_checks(self, vm_list, dest_node, live, bw=None)

   # Metrics
   def get_metrics(self)

   # vmm capabilities and host information as seen by vmm.
   # Note  : this information is exposed via __getitem__
   # the default behavior calls the vmm.info()
   def get_vmm_info(self)
   
   ## TBD : Make vmm info  more explicit. VMMInfo which can describe the values
            as well as has metadata like categories, display names etc. 
      

   # directory to store config files
   def get_auto_config_dir() - directory where the config files should be stored
                           for them to come up when machine boots
   def get_config_dir() - directoy to store vm configs.
   
    
    """

    """
    This class represents a concrete implementation of the inteface
    which makes it easy to add new platform. It is not necessary to
    follow the same implementation pattern.
    """

    """
    If you wish to leverage the implementation, you can leverage the default
    implementation of the vm ops that delegates the ops to the vm.

    -- Concrete Node should implement
    # Factory methods
    def new_config(self, filename)
    def new_vm_from_config(self, config)
    def mew_vm_from_info(self, info)

    def get_running_vms(self)    
    -- VMM
        Return a handle to the vmm proxy. The handle via which all the
        vm ops can be done.
        
       def _init_vmm(self)
       def get_vmm(self) - default implementation caches the value given
                           by _init_vmm

       Expects vmm to implement
        -- info() - information about the vmm
        -- is_in_error() - if the vmm is in some error state.
        -- connect() - connect to the vmm (if not connected)
        -- disconnect() - disconnect from the vmm


    -- The default implementation of get_metrics provides a metric cache for
       storing the last collected value, and using polling facility to
       update it. To use this, implement the
       def get_metric_snapshot(self)
       
    -- For the migration operation as a whole do a bunch of checks.
       Return values same as migration_checks
          def migration_op_checks(self, vm_list, dest_node,live)
          
    -- For migrating a given vm, do a bunch of checks
       Return values same as migration_checks
         def migration_vm_checks(self, vm_name, dest_node, live)

    -- can this server handle hvm images ? /Fully virtualized VMs
         def is_hvm(self)

    -- return true/false if the particular node can handle a given image or not.
       This DOES NOT take care of the run time aspects like mem or cpu.
          def is_image_compatible(self, image):
    
    """

    def __init__(self,
                 platform,
                 #store,
                 hostname = None,
                 username= "root",
                 password=None,
                 isRemote=False,
                 ssh_port = 22,
                 helper = None,
                 use_keys = False,
                 address = None):

        ManagedNode.__init__(self, hostname,
                             ssh_port,
                             username, password,
                             isRemote,
                             helper,
                             use_keys,
                             address)
        self.platform = platform
        self._managed_domfiles = None
        self._vmm = None
        #self.store = store
        self._node_info = None
        self.dom_list = None
        self.dom_list=self.get_dom_list()

        self.metrics_poller = None
        self.POLLING_INTERVAL = 5.0 # default no.of seconds between each metric fetch
        self.MAX_POLLS = 4 # default number of times metrics poller iterates

    def init_on_load(self):
        ManagedNode.init_on_load(self)
        self.platform = self.type
        self._managed_domfiles = None
        self._vmm = None
        self._node_info = None
        self.dom_list = None
        self.dom_list=self.get_dom_list()

        self.metrics_poller = None
        self.POLLING_INTERVAL = 5.0 # default no.of seconds between each metric fetch
        self.MAX_POLLS = 4 # default number of times metrics poller iterates

    # directory where the config files should be stored
    # for them to come up when machine boots
    def get_auto_config_dir(self):
        return ""
    # directoy to store vm configs.
    def get_config_dir(self):
        return "/var/cache/convirt/vm_configs"
    
    def get_platform(self):
        return self.platform
    
    def get_dom_list(self):
        if self.dom_list is None:
            self.dom_list = DomListHelper(self)
        return self.dom_list

    """ derived class to provide information about vmm capabilities
        and node as seen by vmm.
    """
    def get_vmm_info(self):
        return self.get_vmm().info()

    def get_managed_domfiles(self):
        if self._managed_domfiles is None:            
            self._managed_domfiles = []
            nodes=DBHelper().filterby(Entity,[],[Entity.entity_id==self.id])
            if len(nodes)>0:
                n=nodes[0]
                for v in n.children:
                    self._managed_domfiles.append(self.get_config_dir()+v.name)
        return self._managed_domfiles

    def _init_vmm(self):
        return None

    def get_vmm(self):
        if self._vmm is None:
            self._vmm = self._init_vmm()
        return self._vmm

    # return a dictionary of running VMs
    def get_running_vms(self):
        return {}

    @property
    def managed_domfiles(self):
        if self._managed_domfiles is None:
            self._managed_domfiles = self.get_managed_domfiles()
        return self._managed_domfiles
    @property
    def node_info(self):
        if self._node_info is None:
            self._node_info = self.get_vmm_info()
        return self._node_info

    
    # encapsulate the Virtualized Platform related info,
    def __getitem__(self, param):
        vmm_info = self.get_vmm_info()
        if vmm_info is not None:
            if vmm_info.has_key(param):
                return vmm_info[param]

        #return ManagedNode.__getitem__(self, param)
        return None


    # override, as we need to be more specific
    def is_in_error(self):
        return self.is_server_in_error() or self.is_vmm_in_error()

    def is_server_in_error(self):
        return ManagedNode.is_in_error(self)

    def is_vmm_in_error(self):
        return self.get_vmm().is_in_error()

    def connect(self):
        ManagedNode.connect(self)
        self.get_vmm().connect()
        self.refresh()

    def disconnect(self):
        if self._vmm is not None:
            self.get_vmm().disconnect()
            self._vmm = None
        ManagedNode.disconnect(self)

    # Factory and helpers to create VMs
    # Given a filename, return concrete config object
    def new_config(self, filename):
        return None

    # Given config, return a concrete VM
    def new_vm_from_config(self, config):
        return None

    # Given runtime info, return a concrete VM
    def new_vm_from_info(self, info):
        return None

    # public methods
    def get_VM_count(self):
        return len(self.dom_list)# includes Dom0

    def get_Managed_VM_count(self):
        node_ent=DBHelper().get_entity(self.id)
        return len(node_ent.children)

    ## Add the platform info to the environment
    def _init_environ(self):
        node_env = ManagedNode._init_environ(self)
#        if node_env["platform_info"] is None:
#            node_env["platform_info"] = self.get_platform_info()
        return node_env

    def refresh_environ(self):
        ManagedNode.refresh_environ(self)        

#    def get_platform_info(self):
#        return None
#    
#    def save_platform_info(self,platform_dict):
#        instances=[]
#        comp=DBHelper().filterby(Component,[],[Component.type==to_unicode('platform_info')])[0]
#        for k1,v1 in platform_dict.iteritems():
#            inst=Instance(to_unicode(k1))
#            inst.value=to_unicode(v1)
#            inst.display_name=to_unicode('')
#            inst.component=comp
#            inst.node_id=self.id
#            instances.append(inst)
#        DBHelper().add_all(instances)
        
    def get_platform_info_display_names(self):
        return None

    def populate_platform_info(self):
        platform_dict = self.get_vmm_info()
        return platform_dict

    def get_dom_ids(self):
        return self.dom_list.iterkeys()

    def get_dom_names(self):
        """
        return lists containing names of doms running on this node.
        exceptions :
        """
        names = []        
        for k in self.dom_list.iterkeys():
            names.append(self.get_dom(k).name)
        return names

    def get_all_dom_names(self):
        """
        return list containing names of doms under this node from database.
        exceptions :
        """
        names = []
        vm_dict={}
        nodes=DBHelper().filterby(Entity,[],[Entity.entity_id==self.id])
        if len(nodes)>0:
            n=nodes[0]
            ids = [v.entity_id for v in n.children]
            vms = DBHelper().filterby(VM,[],[VM.id.in_(ids)])

            for v in vms:
                names.append(v.name)
                vm_dict[v.name]=v
        return (names,vm_dict)

    def get_doms(self):
        """
        returns list containing information about nodes running on
        this node.
        returns list of Dom objects
        exceptions :
        NOTE: in most cases, get_dom_names() is a better option.
        """
        return self.dom_list

    def get_dom(self, name):
        if self.dom_list[name] is None:
            for dom in self.dom_list:
                if dom.name==name:
                    return dom
        return self.dom_list[name]


    def isDom0(self, name):
        if self.get_dom(name):
            return self.get_dom(name).isDom0()
        else:
            return False

    def isDomU(self, name):
        if self.get_dom(name):
            return self.get_dom(name).isDomU()
        else:
            return False

    def get_state(self, name):
        if self.get_dom(name):
            return self.get_dom(name).get_state()
        else:
            return None

    def is_resident(self, name):
        if self.get_dom(name):
            return self.get_dom(name).is_resident()
        else:
            return False


    def create_dom(self, config):
        """
        create a new dom given a particular config.
        exceptions:
        """
        if config.filename is None:
            raise Exception("filename must be set in the config.")
        #config.write()
        #dom_name = self.add_dom_config(config.filename)
        #self.start_dom(dom_name)
        new_vm = self.new_vm_from_config(config)
        new_vm._start(config)
        #self.get_dom(dom_name)._start(config)
        self.refresh()
        return config.name

    def create_dom_from_file(self, filename):
        config = self.new_config(filename)
        new_vm = self.new_vm_from_config(config)
        new_vm._start(config)
        #dom_name = self.add_dom_config(filename)
        #self.start_dom(dom_name)
        self.refresh()
        return config.dom_name

    def refresh(self):
        self.dom_list.refresh()

        # Manage external files.
    def add_dom_config(self, filename):
        return self.dom_list.add_dom_config(filename)

    def remove_dom_config(self, filename):
        return self.dom_list.remove_dom_config(filename)


        # Metrics
    def get_metrics(self, refresh=False,filter=False):
        ###commented on 28/11/09
        ###removing poller thread
#        if refresh:
#            self.metrics = self.get_metric_snapshot()
#        else:
#            if self.metrics is None:
#                # first time get_metrics has been called
#                self.get_metrics(refresh=True)
#
#            if self.metrics_poller is None or not self.metrics_poller.isAlive():
#                # kick off ascynchronous metrics polling
#                # ... MAX_POLLS polls at POLLING_INTERVAL second intervals
#                self.metrics_poller = Poller(self.POLLING_INTERVAL,self.get_metrics,
#                                             args=[True],max_polls=self.MAX_POLLS)
#                self.metrics_poller.start()
        ###end
        self.metrics = self.get_metric_snapshot(filter=filter)
        return self.metrics

        # return the current snapshot of all running vms.
        # Map of a Map containing stats for each VM.
        # TBD: Document the keys expected.
    def get_metric_snapshot(self):
        return None

    def get_raw_metrics(self,hrs=None):
        return MetricsService().getServerMetrics(self.id,hrs)

    def get_vcpu_count(self):
        ent=DBHelper().filterby(Entity,[],[Entity.entity_id==self.id])[0]
        vmids=[x.entity_id for x in ent.children]
        vms=DBHelper().filterby(VM,[],[VM.id.in_(vmids)])
        vcpus=0
        for vm in vms:
            vcpus+=int(vm.get_config()['vcpus'])

        return vcpus
        # dom operations
    def start_dom(self, name):
        """
        start the given dom
        exceptions:
        """
        # deligate to the dom itself
        self.get_dom(name)._start()


    def pause_dom(self, name):
        """
        pause a running dom
        exceptions:
        """
        self.get_dom(name)._pause()


    def resume_dom(self, name):
        """
        pause a running dom
        exceptions:
        """
        self.get_dom(name)._resume()


    def shutdown_dom(self, name):
        """
        shutdown a running dom.
        """
        self.get_dom(name)._shutdown()


    def destroy_dom(self, name):
        """
        destroy dom
        """
        self.get_dom(name)._destroy()
        self.refresh()

    def reboot_dom(self, name):
        """
        reboot dom
        """
        self.get_dom(name)._reboot()

    def restore_dom(self, filename):
        """
        restore from snapshot file
        """
        vmm = self.get_vmm()
        if vmm:
            vmm.restore(filename)
        self.refresh()

    def migrate_dom(self, name, dest_node, live):
        """
        destroy dom
        """
        dom = self.get_dom(name)
        if dom.isDom0():
            return Exception(name + " can not be migrated.")
        self.get_dom(name)._migrate(dest_node, live,
                                    port=dest_node.migration_port)

        self.refresh()


    def migration_checks(self, vm_list, dest_node,live):
       err_list = []
       warn_list = []

       (op_e_list, op_w_list) = self.migration_op_checks(vm_list,dest_node, live)
       if op_e_list is not None:
          err_list = err_list + op_e_list
       if op_w_list is not None:
          warn_list = warn_list + op_w_list
          
       for vm in vm_list:
          (vm_e_list, vm_w_list) = self.migration_vm_checks(vm.name, dest_node, live)
          if vm_e_list is not None:
             err_list = err_list + vm_e_list
          if vm_w_list is not None:
             warn_list = warn_list + vm_w_list

       return (err_list, warn_list)


    def augment_storage_stats(self, dom_name, dom_frame, dom=None):
        # augment snapshot_dom with the storage stats
        if dom is None:
            dom = self.get_dom(dom_name)
        if dom:
            cfg = dom.get_config()
            if cfg is not None:
                ss = cfg.get_storage_stats()
                if ss:
                    total_shared = ss.get_shared_total()
                    total_local = ss.get_local_total()
                    dom_frame[constants.VM_SHARED_STORAGE] = total_shared
                    dom_frame[constants.VM_LOCAL_STORAGE] = total_local
                    dom_frame[constants.VM_TOTAL_STORAGE] = total_local + total_shared



    def update_storage_totals(self, frame):
        total_shared = 0.0
        total_local = 0.0
        ## for d_f in frame.itervalues():
        ##    if isinstance(d_f, dict):
        ##        ss = d_f.get(constants.VM_SHARED_STORAGE)
        ##        if ss:
        ##            total += ss

        # count storage used by non-running VMs as well.
        for dom in self.get_doms():
            cfg = dom.get_config()
            if cfg:
                ss = cfg.get_storage_stats()
                if ss:
                    total_shared += ss.get_shared_total()
                    total_local += ss.get_local_total()

        frame[constants.VM_SHARED_STORAGE] = total_shared
        frame[constants.VM_LOCAL_STORAGE] = total_local
        frame[constants.VM_TOTAL_STORAGE] = total_shared + total_local


    # check if a given dom can be migrated to the destination node
    def migration_op_checks(self, vm_list, dest_node,live):
        err_list = []
        warn_list = []
        for vm in vm_list:
            if vm.is_running() and not dest_node.is_up():
                err_list.append(("Status", "Running VM %s cannot be migrated to a down node" % (vm.name,)))
        return (err_list, warn_list)

    ## TBD : Make output of these checks more structured.
    ##       Test name, Context (vm name), message
    def migration_vm_checks(self, vm_name, dest_node, live):
        """
        Implements a series of compatiblity checks required for successful
        migration.
        """
        err_list = []
        warn_list = []

        if self.is_up():
            vm = self.get_dom(vm_name)
        else:
            vm = DBHelper().find_by_name(VM,vm_name)
        if vm == None :
            err_list.append(("VM", "VM %s not found."% vm_name))
            return (err_list, warn_list)       
        # the platform check
        node_platform = dest_node.get_platform()
        vm_platform = vm.get_platform()
        if vm_platform != node_platform:
            err_list.append(("Platform", "The destination node does not support required platform (%s)" % (vm_platform,)))


        vm_conf = vm.get_config()
        # config file and all vbds are available.
        if vm_conf is not None and dest_node.is_up():
            des = vm_conf.getDisks()
            if des:
                for de in des:
                    if not dest_node.node_proxy.file_exists(de.filename):
                        err_list.append(("Disk ", 
                                         "VM Disk %s not found on the destination node %s" % (de.filename, dest_node.hostname)))

        return (err_list, warn_list)

    # can handle hvm images ? /Fully virtualized VMs
    def is_hvm(self):
        #checks the property in DB
        return self.isHVM

    # return true/false if the particular node can handle a given image or not.
    # this DOES NOT take care of the run time aspects like mem or cpu.
    def is_image_compatible(self, image):
        raise Exception("is_image_compatible not implemented : ", self.__class__)


    def get_unused_display(self):

        #For check port with 'netstat' command output, and get unused port.
        port = self.get_unused_port(5920, 6000)
        ###In 'get_vnc_info' method of Gridmanager, we are adding 5900
        ###to last_vnc to get vnc_display port.
        last_vnc = port - 5900
        return last_vnc

    def heartbeat(self):
        if self.isRemote == False:
            return [self.UP, u'Localhost is always up']
        else:
            creds = self.get_credentials()
            ssh_port = creds["ssh_port"]
            if ssh_port is None:
                ssh_port = 22
            hostname = self.hostname
            sock=None
            try:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    #FIXME: Make timeout configurable
                    sock.settimeout(2)
                    sock.connect((hostname, ssh_port))
                except socket.timeout:
                    return [self.DOWN, u'Ping timed out. Host unreachable.']
                except socket.gaierror, e:
                    return [self.DOWN, u'Hostname not found. ' + to_unicode(e)]
                except Exception, ex:
                    return [self.DOWN, to_unicode(ex)]
            finally:
                if sock is not None:
                    sock.close()
            return [self.UP, u'Ping succeeded']
                

    def vm_heartbeat(self):
        mtr = self.get_metrics(refresh = True)
                
        ret_val = {}
        vm_names = self.get_all_dom_names()[0]
        for vm in vm_names:
            try:
                state = mtr[vm]['STATE']
            except KeyError:
                #not found, assume shutdown
                state = VM.SHUTDOWN
            ret_val[vm] = [state, None]
        return ret_val

    def refresh_vm_avail(self):
        from convirt.model.Entity import EntityRelation
        from sqlalchemy import and_
        from sqlalchemy.orm import eagerload
        strt = p_task_timing_start(AVL_LOGGER, "VMHeartBeat", self.id, log_level="DEBUG")
        vm_states = self.vm_heartbeat()
        p_task_timing_end(AVL_LOGGER, strt)
        #print "\nvm_states===",vm_states,"\n======================="
        ###first check if the node is actually UP . if the node is down we
        ###should not create an AvailabilityEvent for VM as this should be
        ###handled by NodeAvailability. if the node is UP we have to check
        ###if nodeavailability is aware of this(avail_state of node = UP).
        ###if not we should skip & let nodeavailability take care of this.
        ###even otherwise it shouldn't be an issue as we would have marked
        ###all vms down already.
        is_up=(self.heartbeat()[0] == self.UP)
        if is_up==True:
            if not self.is_up():
                return
        strt = p_task_timing_start(AVL_LOGGER, "ProcessVMHeartBeat", self.id, log_level="DEBUG")
        #print "\is_up===",is_up,"\n======================="
        timestamp = datetime.utcnow()
        #The reason why get_doms is not used for below is to optimize
        #the query by eagerloading the current_state relation
        for vm in DBSession.query(VM).\
                  filter(and_(and_(VM.id == EntityRelation.dest_id,\
                                   EntityRelation.src_id == self.id),\
                              EntityRelation.relation == u'Children')).\
                  options(eagerload("current_state")):

            #skipping if vm is migrating
            if vm.status==constants.MIGRATING:
                continue
            #find vm in vm_states
            try:
                [new_state, reason] = vm_states[vm.name]
            except KeyError:
                #We should never reach here since the heartbeat function
                #should give a deterministic answer for everyone
                continue
            if vm.current_state is None:
                vm.current_state = AvailState(vm.id, None, None, None, None)
            if vm.current_state.avail_state != new_state:
                from convirt.model.UpdateManager import UIUpdateManager
                UIUpdateManager().set_updated_entities(vm.id)
                try:
                    LockManager().get_lock(constants.AVAIL_STATE,self.id, constants.DOMAIN, constants.Table_avail_current)
                    update_avail(vm, new_state, vm.current_state.monit_state, \
                                timestamp, reason, LOGGER, is_up)
                finally:
                    LockManager().release_lock()
        p_task_timing_end(AVL_LOGGER, strt)

    def refresh_avail(self, auth, exit_code=-1, isUp=False):
        node_id = self.id
        strt = p_task_timing_start(AVL_LOGGER, "HeartBeat", self.hostname, log_level="DEBUG")

        if exit_code != 0:
            [new_state, reason] = self.heartbeat()
        else:
            if isUp:
                new_state=self.UP
                reason="Host is up"
            else:
                new_state=self.DOWN
                reason="Host is down"

        p_task_timing_end(AVL_LOGGER, strt)
        timestamp = datetime.utcnow()
        strt = p_task_timing_start(AVL_LOGGER, "ProcessHeartBeat", self.hostname, log_level="DEBUG")
        if self.current_state is None:
            #initialize status
            self.current_state = AvailState(node_id, \
                                            None, None, None, None)
        if self.current_state.avail_state != new_state:
                from convirt.model.UpdateManager import UIUpdateManager
                UIUpdateManager().set_updated_entities(node_id)
                try:
                    LockManager().get_lock(constants.AVAIL_STATE,node_id, constants.MANAGED_NODE, constants.Table_avail_current)
                    update_avail(self, new_state, self.current_state.monit_state, \
                            timestamp, reason, LOGGER, auth=auth)
                finally:
                    LockManager().release_lock()
        p_task_timing_end(AVL_LOGGER, strt)

    def insert_outside_vms(self,vm_names):
        try:
            vm_count=DBSession.query(func.count(OutsideVM.name)).\
                filter(OutsideVM.node_id==self.id).all()
            DBSession.query(OutsideVM).filter(OutsideVM.node_id==self.id).delete()
            for vm in vm_names:
                outside_vm=OutsideVM(vm.get("name"),self.id,vm.get("status"))
                DBSession.add(outside_vm)
            if len(vm_names)!=vm_count[0][0]:
                from convirt.model.UpdateManager import UIUpdateManager
                UIUpdateManager().set_updated_entities(self.id)
        except Exception,e:
#            traceback.print_exc()
            LOGGER.error("Error in set_remote(): " + str(e))


class DomListHelper:
    """
    Class represent list of dom being tracked by this managed
    node. 
    """
    # for implementing domlist

    def __init__(self, node):
        self._dom_dict = None
        self.node = node

    def _init_dom_list(self):
        """ take the dominfo from the API and return list of doms
        """
        if self._dom_dict is None:
            self.refresh()
        return self._dom_dict

    def __getattr__(self, name):
        if name == 'dom_dict':
            return self._init_dom_list()


    def refresh(self):
        # get a list of VMs running
        vmm = self.node.get_vmm()
        current_dict = self.node.get_running_vms()        

        nodes=DBHelper().filterby(Entity,[],[Entity.entity_id==self.node.id])
        if len(nodes)>0:
            n=nodes[0]
            for v in n.children:
                vm=DBHelper().find_by_id(VM, v.entity_id)
                if vm is not None:
                    vm.node=self.node
                    vm._config.managed_node=self.node
                    if current_dict.get(vm.name,None) is not None:                        
                        vm.set_vm_info(current_dict.get(vm.name)._vm_info)
                        del current_dict[vm.name]
                    current_dict[vm.id] = vm

        self._dom_dict = current_dict

    def __getitem__(self, item):
        if not item: return None
        if type(item) is int:
            for name, dom in self.dom_dict.iteritems():
                if dom.is_resident() and dom.id == item:
                    return dom
        else:
            if self.dom_dict.has_key(item):
                return self.dom_dict[item]
            else:
                return None

    def __len__(self):
        return len(self.dom_dict)

    def __iter__(self):
        return self.dom_dict.itervalues()


    def iterkeys(self):
        return self.dom_dict.keys()

    def itervalues(self):
        return self.dom_dict.itervalues()

        # start tracking file
    def add_dom_config(self, filename):

#        if filename in self.node.managed_domfiles:
#            config = self.node.new_config(filename)
#            return self.node.new_vm_from_config(config)
#        else:
        config = self.node.new_config(filename)
        config.update_storage_stats() # update storage stats
#        config.write()
        new_dom = self.node.new_vm_from_config(config)
        #self.node.managed_domfiles.append(filename)
#            self.node.store.set(self.node.hostname,constants.prop_domfiles,
#                                repr(self.node.managed_domfiles),
#                    )
        self.dom_dict[new_dom.name] = new_dom

        return new_dom

    def remove_dom_config(self, filename):

        if filename in self.node.managed_domfiles:
            self.node.managed_domfiles.remove(filename)
#            self.node.store.set(self.node.hostname,constants.prop_domfiles,
#                                repr(self.node.managed_domfiles),
#                    )
            # check if running, shutdown, remove, etc.
            for d in self.dom_dict.itervalues():
                if d.get_config() is not None and \
                       d.get_config().filename == filename:
                    del self.dom_dict[d.name]
                    return True

        return False

 
