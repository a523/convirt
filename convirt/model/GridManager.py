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
#

from tg import session
from convirt.model.ManagedNode import ManagedNode
from convirt.model.Groups import ServerGroup
from convirt.core.utils.constants import *
import convirt.core.utils.utils
from convirt.core.utils.NodeProxy import Node
from pprint import pprint
from datetime import datetime
import time,re,string
from convirt.core.utils.utils import uuidToString,getHexID,dynamic_map,vm_config_write,\
                instantiate_configs,merge_pool_settings,validateVMSettings,randomUUID,copyToRemote,\
                mktempfile,get_config_text, p_timing_start,p_timing_end,p_task_timing_start,p_task_timing_end
from convirt.core.utils.utils import to_unicode,to_str,notify_node_down
utils = convirt.core.utils.utils
constants = convirt.core.utils.constants
from convirt.model.Entity import *
from convirt.model.DBHelper import DBHelper
import tg
import os, socket, tempfile, traceback, stat
from convirt.core.platforms.xen.XenNode import XenNode
from convirt.core.platforms.kvm.KVMNode import KVMNode
from convirt.model.Sites import Site
from convirt.model.ImageStore import ImageStore
from convirt.model.VM import VM, VMDisks, VMStorageLinks, VMStorageStat, VMDiskManager, OutsideVM
from convirt.model.ImageStore import Image
from convirt.model import DBSession

from convirt.model.Authorization import AuthorizationService
from convirt.model.Metrics import MetricsService, MetricVMRaw, MetricVMCurr, MetricServerRaw, MetricServerCurr, DataCenterRaw, DataCenterCurr
from convirt.core.utils.phelper import AuthenticationException
from convirt.config.ConfigSettings import ClientConfiguration
from convirt.model.storage import StorageDef, StorageManager
from convirt.model.network import NwDef, NwManager
from convirt.model.SyncDefinition import SyncDef
from convirt.model.SPRelations import SPDefLink, DCDefLink, ServerDefLink, StorageDisks
from convirt.model.notification import Notification
from convirt.model.EmailManager import EmailManager
from convirt.model.availability import AvailState,AvailHistory
from sqlalchemy.orm import eagerload
from convirt.model.Credential import Credential
import logging,tg,time,transaction
from convirt.model.LockManager import LockManager

LOGGER = logging.getLogger("convirt.model")
STRG_LOGGER = logging.getLogger("STORAGE_TIMING")
MTR_LOGGER = logging.getLogger("METRICS_TIMING")

class GridManager:

    # creds_helper will eventually become part of XenNodeFactory
    def __init__(self,client_config, registry,creds_helper):
        self.client_config=client_config
        self.registry = registry
        self.group_list = {}
        self.node_list = {} # nodes that are not categorized
        self.storage_manager = StorageManager()
        self.network_manager = NwManager()
        self.sync_manager = SyncDef()
        
    def getDataCenters(self):
        dcs = DBHelper().get_all(Site)
        return dcs

    def getImageStores(self):
        iss = DBHelper().get_all(ImageStore)
        return iss

    def getFactory(self, platform):
        factory =  self.registry.get_node_factory(platform)
        if factory :
            return factory

        raise Exception("No factory for %s platform." % platform)

    def _create_default_groups(self):
        auth=AuthorizationService()
        #find the DataCenter Entity
        dc_id=getHexID(constants.DC,[constants.DATA_CENTER])
        dc=DBHelper().filterby(Entity,[],[Entity.entity_id==dc_id])[0]
        for name in ["Desktops", "QA Lab", "Servers"]:
            grp = ServerGroup(name)
            auth.add_entity(grp.name,grp.id,to_unicode(constants.SERVER_POOL),dc)
            DBHelper().add(grp)

        #self._save_groups()

    def _find_groups(self, node_name, group_list_map = None):
        # given a node name find all the group names to which it belongs
        grp = []

        if group_list_map is None:
            group_list_map = {}
            for g in self.group_list:
#                group_map[g] = self.group_list[g].getNodeNames()
                group_list_map[g] = {"node_list" : self.group_list[g].getNodeNames()}

        for group_name in group_list_map.keys():
            g = group_list_map[group_name]
            node_list = g["node_list"]
            if node_name in node_list:
                grp.append(group_name)

        return grp


    def discoverNodes(self,ip_list):
        pass

    def getGroupList(self,auth,site_id=None):
        if site_id:
            group_list=[]
            groups = DBSession.query(EntityRelation).filter_by(src_id = site_id)
            for eachgroup in groups:
                group = DBSession.query(ServerGroup).filter_by(id = eachgroup.dest_id).first()
                if group:
                    group_list.append(group)
            return group_list
        else:
            ents=auth.get_entities(to_unicode(constants.SERVER_POOL))
            ids = [ent.entity_id for ent in ents]
            grplist= DBHelper().filterby(ServerGroup,[],[ServerGroup.id.in_(ids)])
            return grplist

    def get_sp_list(self,site_id, def_id, auth):
        objSPList={}
        if site_id:
            group_list=[]
            groups = DBSession.query(EntityRelation).filter_by(src_id = site_id)
            for eachgroup in groups:
                associated = False
                one_group={}
                group = DBSession.query(ServerGroup).filter_by(id = eachgroup.dest_id).first()
                if group:
                    #Check privileges
                    ent = auth.get_entity(group.id)
                    if auth.has_privilege("ADD_STORAGE_DEF", ent) and\
                        auth.has_privilege("REMOVE_STORAGE_DEF", ent):
                        
                        group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id=def_id).first()
                        if group_defn:
                            associated = True
                    
                        #add group to list
                        one_group['id'] = group.id
                        one_group['associated'] = associated
                        one_group['serverpool'] = group.name
                        group_list.append(one_group)
                    else:
                        LOGGER.info("User has no privilege on " + to_str(group.name) + " for ATTACH and DETACH storage")
            objSPList['rows'] = group_list
        return objSPList


    def getGroupNames(self,auth):
        grpnames=auth.get_entity_names(to_unicode(constants.SERVER_POOL))
        return grpnames

    def getGroup(self,auth,groupId):
        ent=auth.get_entity(groupId)
        if ent is not None:
            grp=DBHelper().find_by_id(ServerGroup,groupId)
            return grp
        return None

    def get_dom(self, auth, domId):
        ent=auth.get_entity(domId)
        if ent is not None:
            return DBHelper().find_by_id(VM,domId)

    def get_doms(self,auth,nodeId):
        managed_node = self.getNode(auth,nodeId)
        if managed_node is None:
            raise Exception("Can not find the Server.")
        doms=[]
        node=auth.get_entity(nodeId)
        dom_names=auth.get_entity_names(to_unicode(constants.DOMAIN),parent= node)
        for domname in dom_names:
            single_dom = managed_node.get_dom(domname)
            if single_dom:
                doms.append(single_dom)
        return doms

    def get_node_doms(self,auth,nodeId):
        managed_node = self.getNode(auth,nodeId)
        if managed_node is None:
            raise Exception("Can not find the Server.")
        doms=[]
        node=auth.get_entity(nodeId)
        dom_ids=auth.get_entity_ids(to_unicode(constants.DOMAIN),parent= node)
        doms = DBSession.query(VM).filter(VM.id.in_(dom_ids)).all()
        return doms

    def get_running_doms(self,auth,nodeId):
        domlist=self.get_doms(auth,nodeId)
        runningdoms=[]
        for dom in domlist:
            if dom.is_resident():
                runningdoms.append(dom)
        return runningdoms

    def get_dom_names(self, auth, nodeId):
        ent=auth.get_entity(nodeId)
        if ent is not None:
            dom_names=auth.get_entity_names(to_unicode(constants.DOMAIN),parent=ent)
            return dom_names
        return []

    def getNodeNames(self, auth, groupId = None):
        if groupId is None:
            return []
        else:
            ent=auth.get_entity(groupId)
            nodes=auth.get_entity_names(to_unicode(constants.MANAGED_NODE),parent=ent)
            return nodes

    def getNodeList(self, auth, groupId=None):
        if groupId is None:
            return []
        else:
            ent=auth.get_entity(groupId)
            nodelist=[]
            if ent is not None:
                child_ents=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=ent)
                ids = [child_ent.entity_id for child_ent in child_ents]
                nodelist= DBHelper().filterby(ManagedNode,[],[ManagedNode.id.in_(ids)],[ManagedNode.hostname.asc()])
            return nodelist
        return []

    def getNode(self, auth, nodeId):
        ent=auth.get_entity(nodeId)
        if ent is not None:
            return DBHelper().find_by_id(ManagedNode,nodeId)


    def addNode(self,auth, node, groupId = None):

        soc_count = node.get_socket_info()        
        node.socket = soc_count
        if groupId is None:
            raise Exception("Invalid Group.")
        else:
            ent=auth.get_entity(groupId)
            if not auth.has_privilege('ADD_SERVER',ent):
                    raise Exception(constants.NO_PRIVILEGE)
            if ent is not None:
                try:
                    nodes=DBHelper().filterby(ManagedNode,[],[ManagedNode.hostname==node.hostname])
                    if len(nodes)>0:
                        raise Exception("Server %s already exists." % node.hostname)
                    auth.add_entity(node.hostname,node.id,to_unicode(constants.MANAGED_NODE),ent)
                    node.isHVM = node.is_HVM()
                    DBHelper().add(node)
                    ah = AvailHistory(node.id, ManagedNode.UP, AvailState.MONITORING,\
                            datetime.utcnow(), u"Newly created Node")
                    DBSession.add(ah)
#                    node.refresh_avail()
#                    self.updateMetrics(auth,None,node.id)
                    node._init_environ()
                    #call on_add_node() after adding the node to database since we should get reference of the node in the database while syncing and updating db table for status.
                    site = self.getSiteByGroupId(groupId)
                    site_id=None
                    if site:
                        site_id=site.id
                    self.sync_manager.on_add_node(node.id, groupId, site_id, auth, self.storage_manager)
                    self.sync_manager.on_add_node(node.id, groupId, site_id, auth, self.network_manager)
                    try:
                        self.updateMetrics(auth,None,node.id)
                    except Exception, e:
                        traceback.print_exc()
                except Exception, e:
                    traceback.print_exc()
                    DBSession.rollback()
                    transaction.begin()
                    raise e

    def removeNode(self,auth, nodeId, force=False):
        ent=auth.get_entity(nodeId)
        if not auth.has_privilege('REMOVE_SERVER',ent):
            raise Exception(constants.NO_PRIVILEGE)        

        #call on_remove_node() method before deleting entity and node since we should get node reference for storage/network def delete operation.
        groupId = ent.parents[0].entity_id
        site = self.getSiteByGroupId(groupId)
        site_id=None
        if site:
            site_id=site.id
        self.sync_manager.on_remove_node(nodeId, groupId, site_id, auth, self.storage_manager)
        self.sync_manager.on_remove_node(nodeId, groupId, site_id, auth, self.network_manager)

        domlist=self.get_node_doms(auth,nodeId)
        for dom in domlist:
            self.remove_dom_config_file(auth, dom.id, nodeId)
        
        auth.remove_entity_by_id(nodeId)
        # added code to delete record from curr metrics for the removed server
        MetricsService().DeleteCurrentMetrics(constants.SERVER_CURR,nodeId)
        node=DBHelper().find_by_id(ManagedNode,nodeId)
        node.remove_environ()
        OutsideVM.onRemoveNode(node.id)
        DBHelper().delete(node)

    def editNode(self,auth,node):
        ent=auth.get_entity(node.id)
        if not auth.has_privilege('EDIT_SERVER',ent):
            raise Exception(constants.NO_PRIVILEGE)

        DBHelper().add(node)
        node.refresh_environ()

    def transferNode(self, auth, source_group_id,dest_group_id, node_id, forcefully):
        vm_list=[]
        ent=auth.get_entity(node_id)
        grp=auth.get_entity(dest_group_id)
        if not auth.has_privilege('ADD_SERVER',grp) or not auth.has_privilege('TRANSFER_SERVER',ent):
            raise Exception(constants.NO_PRIVILEGE)
        if ent is not None:
            sync_manager = SyncDef()
            if forcefully == 'false':
                sync_manager.validate_transfer_node(node_id, source_group_id, auth)
            
            site = self.getSiteByGroupId(source_group_id)
            site_id=None
            if site:
                site_id = site.id
                
            self.sync_manager.on_transfer_node(node_id, source_group_id, dest_group_id, site_id, auth, self.storage_manager)
            self.sync_manager.on_transfer_node(node_id, source_group_id, dest_group_id, site_id, auth, self.network_manager)
            # here we are updating the entity irrespective of the status of the syncing operation. However we feel that there has to be a check whether all the definitions have been attached and detached properly before moving the entity. 
            auth.update_entity(ent,parent=grp)
            
            #Start - run matching algorithm
            vm_list = self.get_vms_from_pool(auth, source_group_id)
            if vm_list:
                for eachvm in vm_list:
                    self.remove_vm_storage_links_only(eachvm.id)
                    error = self.matching_on_AddEditDelete_vm(auth, 'TRANSFER_SERVER', eachvm.id)
                    if error:
                        LOGGER.error(to_str(error))
            #End - run matching algorithm
            #Recompute storage stats
            self.storage_manager.recompute_on_transfer_node(auth, dest_group_id, self)

    def getNodeMetrics(self,auth,node):
        #managed_node=self.getNode(auth,node.hostname,group_name)
        #domnames=self.get_dom_names(auth, node.id)
        metrics=node.get_metrics()
        
        ###commented on 25/11/09
        ###node.get_metrics() returns only convirt related info
#        for key in metrics.keys():
#            if key not in domnames and key!='Domain-0' and isinstance(metrics[key],dict):
#                del metrics[key]
        ###end
        return metrics

    def refreshNodeMetrics(self,auth,node):
        try:
            node.connect()
        except AuthenticationException ,ex:
            raise Exception("Server not authenticated.")
        except Exception ,ex:            
            raise ex
        try:
            self.collectMetrics(auth,node)
        except Exception ,ex:            
            raise ex

    # Function to get the node metrics from the managed_node and insert
    # the metrics data in raw/current VM tables
    def collectMetrics(self, auth, managed_node):
        metrics=self.getNodeMetrics(auth,managed_node)
        ms = MetricsService()
        ent=auth.get_entity(managed_node.id)
        child_ents=auth.get_entities(to_unicode(constants.DOMAIN),parent=ent)
		# loop to get the vm id to be inserted in the VM metrics table since
        # the dictionary does not have VM id but VM name.
        for child_ent in child_ents:
            if child_ent.name not in metrics.keys():
                #ms.deleteMetricsData(child_ent.entity_id, 'VM_METRIC_CURR')
                continue
            else:
                #for keys in metrics:
                    #if keys==child_ent.name: # if the correct vm found
                        #dict_data = metrics[keys]
                        #vm_metrics_obj = MetricVMRaw()
                        #ms.insertMetricsData(dict_data, child_ent.entity_id,\
                                            #vm_metrics_obj, 'VM_METRIC_RAW')
                        #curr_metrics_obj = MetricVMCurr()
                        #ms.insertMetricsData(dict_data, child_ent.entity_id,\
                                        #curr_metrics_obj, 'VM_METRIC_CURR')
                continue

    # Function which gets the metrics data from the VM current metrics table
    # and returns a list of dictionaries to be displayed on the dashboard.
    def getCurrentMetrics(self, auth, managed_node):
        ms = MetricsService()
        vmmetrics = {}
        ent=auth.get_entity(managed_node.id)
        child_ents=auth.get_entities(to_unicode(constants.DOMAIN),parent=ent)
        for vm in child_ents:
            # data returned from the current metrics table.
            metrics = ms.getVMMetricsData('VM_METRIC_CURR', vm) 
            if metrics:
                vmmetrics[vm.name]=metrics
        return vmmetrics


    def do_node_action(self,auth,nodeId, action):
        ent=auth.get_entity(nodeId)
        if not auth.has_privilege(action.upper(),ent):
            raise Exception(constants.NO_PRIVILEGE)

#        managed_node=self.getNode(auth,nodeId)
#        domains = self.get_dom_names(auth,nodeId)
        #print domains
        err_doms=[]
        for e in ent.children:
            try:
                if action=='start_all':
                    action='start'
                elif action=='shutdown_all':
                    action='shutdown'
                elif action=='kill_all':
                    action='kill'
                self.do_dom_action(auth, e.entity_id, ent.entity_id, action)
            except Exception ,ex:
                traceback.print_exc()
                err_doms.append( e.name+"-"+ to_str(ex))
        #self.updateMetrics(auth,None,nodeId)
        if err_doms:
            err_str = "Error in Virtual Machines:- "+to_str(err_doms).replace("'", "")
            raise Exception(err_str)
        
    def restore_dom(self,auth, nodeId, file):
        ent=auth.get_entity(nodeId)
        if not auth.has_privilege('RESTORE_HIBERNATED',ent):
            raise Exception(constants.NO_PRIVILEGE)
        managed_node=DBHelper().find_by_id(ManagedNode,nodeId)
        managed_node.restore_dom(file)

#    def list_nodes(self):
#        print "## DUMP =="
#        for name in self.getNodeNames():
#            print "Node name" ,  name
#        for g in self.group_list:
#            print "group ", g
#        print "## END DUMP =="



    def cloneNode(self,source_node, dest):
        pass


    def migrateDomains(self, auth, source_node, vm_list, dest, live, force=False, all=False):
        ex_list = []
        
        ent=auth.get_entity(dest.id)
        if not auth.has_privilege('ADD_VM',ent):
            raise Exception(constants.NO_PRIVILEGE)
        try:
            try:
#                if len(vm_list) > 0 :
#                    if not force:
#                        (err_list, warn_list) = \
#                                   source_node.migration_checks(vm_list,
#                                                                dest, live)
                        
                for vm in vm_list:
                    try:
                        ent=auth.get_entity(vm.id)
                        if ent is not None and not auth.has_privilege('MIGRATE_VM',ent):
                            raise Exception(constants.NO_PRIVILEGE)
                        #source_node.migrate_dom(vm.name, dest, live)
                        LOGGER.info("process the migration of vm:"+vm.name)
                        self.migrateDomain(auth, vm.name,source_node,dest, live,
                                           force = True) # checks done
                    except Exception, ex1:
                        traceback.print_exc()
                        ex_list.append("Error migrating " + vm.name + " : " + to_str(ex1))

            except Exception, ex:
                traceback.print_exc()
                raise ex
        finally:
            if len(ex_list) > 0:
                msg = "Errors in migrate all operations \n"
                for m in ex_list:
                    msg = msg + m + "\n"
                raise Exception(msg)



    def migrateNode(self, auth, source_node, dest, live, force = False):
        """ Migrate all vms on this node to a dest node."""

        ent1=auth.get_entity(source_node.id)
        ent2=auth.get_entity(dest.id)
        if not auth.has_privilege('MIGRATE_ALL',ent1) or not auth.has_privilege('ADD_VM',ent2):
            raise Exception(constants.NO_PRIVILEGE)

        vm_list = []
        for vm in self.get_node_doms(auth,source_node.id):
#            if not vm.isDom0():
            vm_list.append(vm)

        self.migrateDomains(auth, source_node, vm_list, dest, live, force)

    def cloneDomain(self,source_dom_name,
                    source_node,
                    dest_node=None):
        pass

    def migrateDomain(self, auth, source_dom_name,
                      source_node,
                      dest_node, live, force = False):
#        dom = source_node.get_dom(source_dom_name)
        dom=DBHelper().find_by_name(VM,source_dom_name)
#        state = dom.get_state()
#        running=False
#        if dom.is_running():
#            running = True

#        if not force and running:
#            (err_list, warn_list) = source_node.migration_checks([dom],
#                                                                 dest_node,
#                                                                 live)

        ## No good mechanism for sucess or failue till we cutover to
        # task / XenAPI
        try:
            if dom.is_running():
                if dest_node.is_up():
                    destid=dest_node.id
                    srcid=source_node.id
                    dom.status=constants.MIGRATING
                    DBSession.add(dom)
                    transaction.commit()
                    dest_node=DBSession.query(ManagedNode).filter(ManagedNode.id==destid).one()
                    source_node=DBSession.query(ManagedNode).filter(ManagedNode.id==srcid).one()
                    LOGGER.info("issue the migrate command")
                    source_node.migrate_dom(source_dom_name, dest_node, live)
                else:
                    raise Exception("Running VM %s cannot be migrated to a down node " % (dom.name,))
        except socket.timeout:
            print "ignoring timeout on migration "
            pass
        except Exception, e:
            traceback.print_exc()
            dom=DBSession.query(VM).filter(VM.id==dom.id).first()
            dom.status=None
            DBSession.add(dom)
            transaction.commit()
            raise e

        wait_time_over=False
        disappeared=False
        if dom.is_running():
            LOGGER.info("Wait for migration to complete")
            wait_time=dom.get_wait_time('migrate')
            (disappeared, wait_time_over) = self.wait_for_migration(wait_time, \
                                        source_node, source_dom_name, dest_node)            

        dom=DBSession.query(VM).filter(VM.id==dom.id).first()
        if source_node.is_up() or dest_node.is_up():
            LOGGER.info("process the vm config file")
            self.process_config_file(dom,source_node,dest_node)

        dom.status=None
        DBSession.add(dom)        

        if wait_time_over==True:
            transaction.commit()
            ###wait time exceeded. assume migrate failed.
            msg='VM did not appear in destination node .'
            if disappeared==False:
                msg='VM still running in source node after '\
                        +str(wait_time)+ 'seconds.'
            raise Exception(msg)

        # move config files if necessary.
        #self.move_config_file(source_dom_name, source_node, dest_node)
        srvr=auth.get_entity(dest_node.id)
        LOGGER.info("update the server-vm entity relation")
        auth.update_entity_by_id(dom.id,parent=srvr)
        transaction.commit()

    def wait_for_migration(self, wait_time, source_node, dom_name, dest_node):

        i=0
        wait_time_over=False
        disappeared=False
        while i <= wait_time:
            time.sleep(1)
            try:
                ###calling running vms: get metrics will filter out non convirt vms
                if disappeared==False and \
                    (source_node.get_running_vms().has_key(dom_name) or \
                    source_node.get_running_vms().has_key("migrating-"+dom_name)):
                    if i==wait_time:
                        wait_time_over=True
#                    i+=1
#                    continue
                else:
                    disappeared=True
                    i=0
                    while i < 5:
                        time.sleep(1)
                        metrics=dest_node.get_running_vms()
                        i+=1
                        if metrics.has_key(dom_name):
                            return (disappeared, wait_time_over)
                    return (True, True)
            except Exception, e:
                LOGGER.error("Error "+e)
                traceback.print_exc()
            i+=1
        return (disappeared, wait_time_over)

    def move_config_file(self, dom_name, source_node, dest_node):
        dom = source_node.get_dom(dom_name)
        if dom and dom.get_config():
            config = dom.get_config()
            target_filename = config["config_filename"]
            isLink = False
            mode = source_node.node_proxy.lstat(target_filename).st_mode
            if stat.S_ISLNK(mode) is True:
                isLink = True
                print "CONFIG NAME  = ", config.filename
                target = source_node.node_proxy.readlink(config.filename)
                # transform the relative links to absolute
                print "ORIG TARGET  = ", target
                target = os.path.join(os.path.dirname(config.filename), target)
                print "TARGET  = ", target
                target_filename = os.path.abspath(target)
                print "TARGET FILENAME = ", target_filename


            if target_filename is not None:
                if dest_node.node_proxy.file_exists(target_filename):
                    # we are done:
                    pass
                else:
                    # create a temp file on the client node.
                    # and move it to the dest node.
                    (t_handle, t_name) = tempfile.mkstemp(prefix=dom_name)
                    try:
                        source_node.node_proxy.get(target_filename,
                                                   t_name)
                        utils.mkdir2(dest_node,
                                     os.path.dirname(target_filename))
                        dest_node.node_proxy.put(t_name,
                                                 target_filename)
                        source_node.node_proxy.remove(target_filename)

                    finally:
                        os.close(t_handle)
                        os.remove(t_name)

                if isLink:
                    dest_node.node_proxy.symlink(target_filename,
                                                 config.filename)
                    source_node.node_proxy.remove(config.filename)

            # now lets reassociate the config with the new node.
            dest_node.add_dom_config(config.filename)
            source_node.remove_dom_config(config.filename)


    # config file handling.
    def process_config_file(self,dom,source_node, dest_node):
        if dom and dom.get_config():
            config = dom.get_config()
            if source_node.is_up():
                target_filename = config["config_filename"]
                if source_node.node_proxy.file_exists(target_filename):
                    source_node.node_proxy.remove(target_filename)
            if dest_node.is_up():
                config.set_managed_node(dest_node)
                config.set_filename(config["config_filename"])
                if not dest_node.node_proxy.file_exists(config.filename):
                    config.write()

    # server pool related functions.

    def getGroupVars(self,auth, groupId):
        ent=auth.get_entity(groupId)
        if not auth.has_privilege('VIEW_GROUP_PROVISIONING_SETTINGS',ent):
            raise Exception(constants.NO_PRIVILEGE)
        group=DBHelper().find_by_id(ServerGroup,groupId)
        group_vars = group.getGroupVars()

        if not group_vars : # is None:
            # put some dummy ones for users to understand
            group_vars = {}
            group_vars["CLASS_A_STORAGE"] = "#/mnt/nfs_share/class_a"
            group_vars["CLASS_B_STORAGE"] = "#/mnt/nfs_share/class_b"
            group_vars["VM_DISKS_DIR"] = "#/mnt/shared/vm_disk"
            group_vars["VM_CONF_DIR"] = "#/mnt/shared/vm_configs"
            group_vars["DEFAULT_BRIDGE"] = "#br0"
        return group_vars

    def setGroupVars(self, auth, groupId,groupvars):
        ent=auth.get_entity(groupId)
        if not auth.has_privilege('EDIT_GROUP_PROVISIONING_SETTINGS',ent):
            raise Exception(constants.NO_PRIVILEGE)
        group=self.getGroup(auth,groupId)
        group.setGroupVars(groupvars)
        DBHelper().add(group)

    def addGroup(self,auth,grp,siteId):
        ent=auth.get_entity(siteId)
        if not auth.has_privilege('ADD_SERVER_POOL',ent):
            raise Exception(constants.NO_PRIVILEGE)
        try:
            grps=DBHelper().filterby(ServerGroup,[],[ServerGroup.name==grp.name])
            if len(grps)>0:
                raise Exception("Group %s already exists." % grp.name)
            auth.add_entity(grp.name,grp.id,to_unicode(constants.SERVER_POOL),ent)
            DBHelper().add(grp)
            
            self.sync_manager.on_add_group(grp.id)
            self.sync_manager.on_add_group(grp.id)
        except Exception, e:
            traceback.print_exc()
            raise e

    def removeGroup(self,auth, groupId, deep=False):
        ent=auth.get_entity(groupId)
        if not auth.has_privilege('REMOVE_SERVER_POOL',ent):
            raise Exception(constants.NO_PRIVILEGE)

        site = self.getSiteByGroupId(groupId)
        site_id=None
        if site:
            site_id=site.id
        
        self.sync_manager.on_remove_group(site_id, groupId, auth, self.storage_manager)
        self.sync_manager.on_remove_group(site_id, groupId, auth, self.network_manager)

        if deep:
            for node in self.getNodeList(auth,groupId):
                self.removeNode(auth, node.id)
        ent = DBSession.query(Entity).filter(Entity.entity_id==groupId).first()
        auth.remove_entity(ent)
        grp=DBHelper().find_by_id(ServerGroup,groupId)
        DBHelper().delete(grp)
#        del self.group_list[groupId]
#        self._save_groups()


    def shutdown(self):
        # iterate through each node and disconnect it
        groups = self.getGroupList()
        for group in groups.itervalues():
            nodes = self.getNodeList(group.name)
            for n in nodes.itervalues():
                try:
                    n.disconnect()
                except Exception, ex:
                    print ex
        ungrouped_nodes = self.getNodeList()
        for n in ungrouped_nodes.itervalues():
            try:
                n.disconnect()
            except Exception, ex:
                print ex

   
    def import_dom_config(self, auth, nodeId,directory, file_list):
        ent=auth.get_entity(nodeId)
        if not auth.has_privilege("IMPORT_VM_CONFIG_FILE",ent):
            raise Exception(constants.NO_PRIVILEGE)

        managed_node = self.getNode(auth,nodeId)
        if managed_node is None:
            raise Exception("Can not find the Server.")

        for filename in file_list:
            try:
                file = os.path.join(directory, filename)
                dom = managed_node.add_dom_config(file)
                d_config= dom.get_config()

                # for PV images boot is optional, but ConVirt UI seems to need it. patch it.
                if d_config and d_config.get("boot") is None:
                   d_config["boot"] = "c"

                if re.sub(ImageStore.VM_INVALID_CHARS_EXP,"", dom.name) != dom.name:
                    raise Exception("VM name can not contain special chars %s" % ImageStore.VM_INVALID_CHARS)
                if dom.name == '':
                    raise Exception("VM name can not be blank.")

                config_from_file=dom.get_config()
                #setting vm_id to config since vm config has old vm_id from vm config file.
                config_from_file.set_id(dom.id)
                file = "$VM_CONF_DIR"+"/"+filename
                config_from_file["config_filename"]=file
                grp=self.getGroup(auth,ent.parents[0].entity_id)
                template_map = {}
                if grp is not None:
                    grp_settings = grp.getGroupVars()
                    merge_pool_settings(config_from_file,{},grp_settings, True)
                    for key in grp_settings:
                        template_map[key]=grp_settings[key]
                if template_map.get("VM_CONF_DIR") is None:
                    template_map["VM_CONF_DIR"] = tg.config.get("VM_CONF_DIR")
                config_from_file.instantiate_config(template_map)
                config_from_file.set_filename(config_from_file["config_filename"])
                dom.vm_config=get_config_text(dom.get_config())
                miss_options=[]
                for opt in constants.reqd_config_options:
                    val = config_from_file.get(opt)
                    if val is None:
                        miss_options.append(opt)
                if len(miss_options)>0:
                    raise Exception("Following option(s) are missing in the config file:-"+str(miss_options))
#                config_from_file = managed_node.new_config(file)
#                config_from_file.update_storage_stats() # update storage stats
#                config_from_file.write()
                doms=DBHelper().filterby(VM,[],[VM.name==dom.name])
                if len(doms)>0:
                    raise Exception("VM %s already exists." % dom.name)

                group_id = ent.parents[0].entity_id
                vm_disks = self.get_vm_disks_from_UI(dom.id, config_from_file)
                error =  self.pre_matching_on_AddEditDelete_vm(auth, "IMPORT_VM_CONFIG_FILE", dom.id, vm_disks)
                if error:
                    raise Exception(error)

                auth.add_entity(dom.name,dom.id,to_unicode(constants.DOMAIN),ent)
                DBHelper().add(dom)
                managed_node.refresh()
                self.updateMetrics(auth,None,nodeId)
                if dom:
                    self.update_vm_disks(auth, dom.id, nodeId, config_from_file)
                
                DBSession.query(OutsideVM).filter(OutsideVM.node_id==nodeId).\
                    filter(OutsideVM.name==dom.name).delete()
                transaction.commit()
                config_from_file.set_managed_node(managed_node)
                config_from_file.write()
                #Recompute storage stats
                self.storage_manager.recompute_on_import_config(dom.id)
            except Exception, ex:
                traceback.print_exc()
                err=to_str(ex).replace("'", " ")
                raise Exception('Error adding file, '+file+'. '+err)        
        managed_node = self.getNode(auth,nodeId)
        managed_node.refresh_vm_avail()
        
    def remove_vm(self,auth,domId,nodeId, force=False):
        ent=auth.get_entity(domId)
        if not auth.has_privilege('REMOVE_VM',ent):
            raise Exception(constants.NO_PRIVILEGE)
        nodeId=ent.parents[0].entity_id
        dom = self.get_dom(auth,domId)
        if not dom:
            raise Exception("Can not find the specified VM.")

        if dom.is_running():
            try:
                self.do_dom_action(auth,domId,nodeId,constants.KILL)
            except Exception,e:
                traceback.print_exc()
                raise e
        try:
            dom = DBSession.query(VM).filter(VM.id==domId).\
                  options(eagerload("current_state")).first()

            managed_node = self.getNode(auth,nodeId)
            dom.get_config().set_filename(dom.get_config()["config_filename"])

            try:
                connected = True
                try:
                    managed_node.connect()
                except Exception, e:
                    connected = False
                    traceback.print_exc()
            finally:
                if connected == True or force == False :
                    self.cleanupQCDomain(managed_node, dom)
                if connected == False and force == True :
                    msg = "Can not connect to server "+managed_node.hostname+\
                                to_str(e)+" Skipping vm disk deletion."
                    LOGGER.error(msg)
                    print msg
            #get a list of storage id corresponding to the vm
            storage_id_list = self.storage_manager.get_storage_id_list(domId)
            #remove all vm storage links and vm disks links.
            # This is because the VM is going to get deleted from the database
            self.remove_all_vm_storage_links(dom.id)
            #remove storage_disks records
            StorageManager().remove_storage_disks(dom.id)

            DBHelper().delete(dom)
            auth.remove_entity_by_id(domId)
            ###added on 26/11/09
            MetricsService().DeleteCurrentMetrics(constants.VM_CURR, domId)
            self.updateMetrics(auth,domId,nodeId)
            ###end
            #managed_node.remove_dom_config(dom.get_config().filename)

            #matching vm disks with storage_disks and updating vm_storage_links table
            self.matching_on_AddEditDelete_vm(auth, "REMOVE_VM", dom.id)
            #Recompute storage stats
            self.storage_manager.Recompute_on_remove_vm(storage_id_list)
        except Exception, e:
            traceback.print_exc()
            raise e


    def remove_dom_config_file(self,auth,domId,nodeId):
        ent=auth.get_entity(domId)
        if not auth.has_privilege('REMOVE_VM_CONFIG',ent):
            raise Exception(constants.NO_PRIVILEGE)
        dom = self.get_dom(auth,domId)
        if not dom:
            raise Exception("Can not find the specified VM.")
        dom_config = dom.get_config()
#        filename=dom.get_config().filename
#        managed_node=self.getNode(auth,nodeId)
#        if managed_node.remove_dom_config(filename):

        #get a list of storage id corresponding to the vm
        storage_id_list = self.storage_manager.get_storage_id_list(domId)
        #remove all vm storage links and vm disks links.
        # This is because the VM is going to get deleted from the database
        self.remove_all_vm_storage_links(dom.id)
        
        DBHelper().delete(dom)
        auth.remove_entity_by_id(domId)
#        domfilename = dom_config.get("config_filename")
#        managed_node=self.getNode(auth,nodeId)
#        if domfilename and managed_node.is_up() and \
#                            managed_node.node_proxy.file_exists(domfilename):
#            managed_node.node_proxy.remove(domfilename)
        self.updateMetrics(auth,domId,nodeId)
        #Recompute storage stats
        self.storage_manager.Recompute_on_remove_vm(storage_id_list)
        
    def save_dom_config_file(self,auth,domId,nodeId,content):
        ent=auth.get_entity(domId)
        if not auth.has_privilege('EDIT_VM_CONFIG_FILE',ent):
            raise Exception(constants.NO_PRIVILEGE)
        r = self.check_vm_config_datas(content)
        if not r.get('success'):
            raise Exception(r.get('msg'))
        dom = self.get_dom(auth,domId)
        filename=dom.get_config()["config_filename"]
        managed_node=self.getNode(auth,nodeId)
        dom.vm_config=content
        DBHelper().add(dom)
        file = managed_node.node_proxy.open(filename, "w")
        file.write(content)
        file.close()

    def check_vm_config_datas(self, content):
        """
            Validate Virtual machine configuration datas, come from the UI "Edit Virtual Machine config file".
            Format of configuration data is, key = value,
            Example:
            platform = u'xen'
            on_reboot = 'restart'
            backup_retain_days = 30
        """
#        print "------>", type(content), content
        l = content.strip().split('\n')
#        print "\n\n---->", l
        #check for datas with missing '=' signe and value
        invalid_datas = [x for x in l if len(x.split("=", 1))==1]
#        print "\n\n------>invalid_datas",invalid_datas
        if invalid_datas:
            msg = 'Invalid entry in config : %s ' %(','.join(invalid_datas))
            return dict(success = False, msg = msg)
        ll = [x.split("=", 1) for x in l if len(x.split("=", 1))==2]
#        print "\n\n------>",ll
        #convert ll to dictionary
        dic = dict(ll)
        msg = ''
        for key, value in dic.items():
            try:
                eval(value)
            except Exception , ex:
                msg = 'Invalid value for attribute : %s ' %key
                return dict(success = False, msg = msg)
        return dict(success = True, msg = msg)



    def save_dom(self,auth,domId,nodeId,file,directory):
        ent=auth.get_entity(domId)
        if not auth.has_privilege('HIBERNATE_VM',ent):
            raise Exception(constants.NO_PRIVILEGE)
        managed_node = self.getNode(auth,nodeId)
        dom = managed_node.get_dom(domId)
        if directory and not managed_node.node_proxy.file_exists(directory):
            utils.mkdir2(managed_node, directory)
        if dom.is_resident():
            dom._save(file)

    def reserve_disks(self, vm_config, hex_id):
        try:
            transaction.begin()
            #loop through all the attached to VM.
            for file in vm_config.getDisks():
                #get disk name
                unique_path = file.filename
                
                #check the storage disk should not be reserved.
                storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=unique_path).first()
                if storage_disk:
                    #if storage disk is not reserved, not allocated and not in read only mode then reserve it.
                    if not storage_disk.transient_reservation and not storage_disk.storage_allocated and file.mode != 'r':
                        storage_disk.transient_reservation = hex_id
                        LOGGER.info("Storage disk " + to_str(unique_path) + " is reserved.")
                    else:
                        #We can use read only disk even if it is reserved.
                        #do not raise exception for read only disk.
                        if not storage_disk.storage_allocated and file.mode != 'r':
                            #if storage disk is reserved then throw exception
                            raise Exception("Storage disk " + to_str(unique_path) + " is already being used by other Virtual Machine.")
            
            transaction.commit()
        except Exception, ex:
            LOGGER.error(str(ex))
            transaction.abort()
            raise Exception(str(ex))
        
    def unreserve_disks(self, vm_config, hex_id=None):
        LOGGER.info("Unreserving storage disks...")
        if not vm_config:
            LOGGER.info("vm config not present. So can not unreserve disks.")
            return
        
        #loop through all the attached to VM.
        for file in vm_config.getDisks():
            #get disk name
            unique_path = file.filename
                
            #check whether the storage disk is reserved.
            storage_disk = None
            if hex_id:
                storage_disk = DBSession.query(StorageDisks)\
                .filter_by(unique_path=unique_path, transient_reservation=hex_id).first()
            
            if storage_disk:
                #unreserve storage disk
                storage_disk.transient_reservation = None
                #Commit is needed here because the code would be run in the task.
                #If you do not commit then changes will not get saved in database.
                transaction.commit()
                LOGGER.info("Storage disk " + to_str(unique_path) + " is unreserved.")

    def unreserve_disks_on_cms_start(self):
        LOGGER.info("Unreserving storage disks on CMS start...")
        #get all the storage disks
        storage_disk_list = DBSession.query(StorageDisks).filter(StorageDisks.transient_reservation != None)
        for storage_disk in storage_disk_list:
            #unreserve storage disk.
            storage_disk.transient_reservation = None
            LOGGER.info("Storage disk " + to_str(storage_disk.unique_path) + " is unreserved.")
        transaction.commit()

    def edit_vm_config(self, auth, vm_config, dom, context, group_id=None, vm_disks=None, hex_id=None):
        start = p_timing_start(LOGGER, "edit_vm_config")
        try:
            ent=auth.get_entity(dom.id)
            if not auth.has_privilege('CHANGE_VM_SETTINGS',ent):
                raise Exception(constants.NO_PRIVILEGE)
            
            self.reserve_disks(vm_config, hex_id)
                
            vm_config.set_managed_node(context.managed_node)
            vm_config.update_storage_stats()

            error = self.pre_matching_on_AddEditDelete_vm(auth, 'EDIT_VM_CONFIG', dom.id, vm_disks)
            if error:
                raise Exception(error)

            ent.name = vm_config['vmname']
            dom.name = vm_config['vmname']
            vm_config['name']=vm_config['vmname']
            dom.vm_config=get_config_text(vm_config)
            #dom.set_config=vm_config
            dom.template_version=context.template_version
            dom.os_flavor=vm_config["os_flavor"]
            dom.os_name=vm_config["os_name"]
            dom.os_version=vm_config["os_version"]
    
            vm_config.write()
            DBHelper().add(dom)
            DBHelper().add(ent)
        except Exception, ex:
            traceback.print_exc()
            raise Exception(str(ex))
        p_timing_end(LOGGER, start)
        
    def edit_image(self, auth, vm_config, image_config, context):
        
        ent=auth.get_entity(context.image.id)
        original_imageid=context.image.id


        if not auth.has_privilege('EDIT_IMAGE_SETTINGS',ent):
            raise Exception(constants.NO_PRIVILEGE)
#            vm_config.write()
#            image_config.write()
        if context.update_template:
            prev_image=context.image
            prev_image.id=getHexID()
#            print original_imageid,"==\n\n",prev_image.id

            DBHelper().add(prev_image)
            DBSession.flush()
            edit_image=Image(original_imageid, context.image.platform, context.image.name, context.image.location)
            edit_image.prev_version_imgid=original_imageid
#            edit_image.version=prev_image.version
            edit_image.version=context.new_version
#            edit_image.set_next_version()
        else:
            edit_image=context.image
#        print "----------------\n\n",edit_image.get_version()
        edit_image.vm_config=get_config_text(vm_config)
        edit_image.image_config=get_config_text(image_config)

        edit_image.os_flavor=context.os_flavor
        edit_image.os_name=context.os_name
        edit_image.os_version=context.os_version

        DBHelper().add(edit_image)
        image_config.write()
        vm_config.write()

    def edit_vm_info(self, auth, vm_config, vm_info, dom, context, \
                     initial_disks, final_disks, group_id=None, vm_disks=None, hex_id=None):
        ent=auth.get_entity(dom.id)
        if not auth.has_privilege('CHANGE_VM_SETTINGS',ent):
            raise Exception(constants.NO_PRIVILEGE)

        self.reserve_disks(vm_config, hex_id)

        vm_config.set_managed_node(context.managed_node)
        mem = vm_info["memory"]
        vcpus = vm_info["vcpus"]
        dom.setMem(mem)
        dom.setVCPUs(vcpus)
        
        error = self.pre_matching_on_AddEditDelete_vm(auth, 'EDIT_VM_INFO', dom.id, vm_disks)
        if error:
            raise Exception(error)
        
        detach_disk_list=[val for val in initial_disks \
                          if val not in final_disks]
        attach_disk_list=[val for val in final_disks \
                          if val not in initial_disks]
                          
        if detach_disk_list:
            dom.detachDisks(detach_disk_list)
        if attach_disk_list:
            dom.attachDisks(attach_disk_list)

        dom.template_version=context.template_version
        dom.os_flavor=vm_config["os_flavor"]
        dom.os_name=vm_config["os_name"]
        dom.os_version=vm_config["os_version"]

        vm_config.update_storage_stats()
        dom.vm_config=get_config_text(vm_config)
        #dom.set_config=vm_config
        DBHelper().add(dom)
        vm_config.write()

    # Provisioning process
    def provision(self,auth,context,img_name, group_id=None, vm_disks=None, hex_id=None):

        # instantiate the configs
        v_config = context.vm_config
        i_config = context.image_config
        # add/set a uui to the config
        #v_config["uuid"] = uuidToString(randomUUID())

        # create is_remote map by position.
        image_id=context.image_id
        managed_node = context.managed_node
        start=context.start

        self.reserve_disks(v_config, hex_id)

        try:
            ent=auth.get_entity(managed_node.id)
            if not auth.has_privilege('PROVISION_VM',ent):
                raise Exception(constants.NO_PRIVILEGE)

            vmname=context.vm_config['name']
            doms=DBHelper().filterby(VM,[],[VM.name==vmname])
            if len(doms)>0:
                raise Exception("VM %s already exists." % vmname)
            id=getHexID()

            v_config["uuid"]=id

            store,managed_node,vm_config_file,vm_config=vm_config_write(auth,context,image_id,v_config,
                                            i_config,img_name)
            vm = managed_node.new_vm_from_config(vm_config)
            vm.id=id
            vm.image_id=image_id
            vm.template_version=context.image.version
            vm.os_flavor=v_config["os_flavor"]
            vm.os_name=v_config["os_name"]
            vm.os_version=v_config["os_version"]
            vm.created_user=auth.user.user_name
            vm.created_date=datetime.utcnow()

            error = self.pre_matching_on_AddEditDelete_vm(auth, 'PROVISION_VM', id, vm_disks)
            if error:
                raise Exception(error)

            (out, exit_code, log_filename) = \
                    store.execute_provisioning_script(auth,
                                                      managed_node,
                                                      image_id,
                                                      v_config,
                                                      i_config)
             # execute the provisioning script            
            if exit_code == 0:
                try:
                    #managed_node.add_dom_config(vm_config_file)
                    auth.add_entity(vmname,id,to_unicode(constants.DOMAIN),ent)
                    vm_config.update_storage_stats()
                    vm.vm_config=get_config_text(vm_config)
                    DBHelper().add(vm)
                    managed_node.refresh_vm_avail()
                    transaction.commit()
                    vm_config.write()
                    if start=='yes':
                        self.do_dom_action(auth,id,managed_node.id,'start')
                    else:
                        self.updateMetrics(auth,id,managed_node.id)

                    return vm.id
                except Exception, e:
                    traceback.print_exc()
                    raise e
            else:
                print "out==",out, "exit_code=",exit_code,"log", log_filename
                raise Exception("Script Output\n------------------\n"+out+\
                                "\n------------------\n Log is available at "+log_filename)

        except Exception, e:
            traceback.print_exc()
            raise e

    def cleanupQCDomain(self,managed_node, dom, vbdlocation=''):
        """ Delete the xen configuration file and associated
        disk devices created during a quickcreate"""
        dom_config = None
        if dom:
            dom_config = dom.get_config()

        if dom_config:
            domfilename = dom_config.filename
            if domfilename and managed_node.node_proxy.file_exists(domfilename):
                managed_node.node_proxy.remove(domfilename)


            for file in dom_config.getDisks():
                # skip read only volumes, they are likely to be shared
                # or cdroms.
                # THIS IS NOT COMPLETE SOLN, NEED to prompt user for each
                # disk is the right soln
                if file.mode.find("w") == -1:
                    continue
                # dont mess with /dev/disk/ area. (Lun, AOE disks)
                vm_disk_types = tg.config.get(constants.vm_disk_types)
                try:
                    vm_disk_types = eval(vm_disk_types)
                except Exception, e:
                    vm_disk_types = ['file','tap:aio','tap:qcow','tap:vmdk']
                    print e
                if file.filename and (file.filename.strip().find("/dev/disk/")==0 or file.filename.strip().find("/dev/etherd/") == 0):
                    continue
                if file.type == 'phy' or file.type == 'lvm':
                    try:
                        managed_node.lvm_proxy.removeLogicalVolume(file.filename)
                        print 'deleting: ' + file.filename
                    except OSError, err:
                        print "error deleting " + file.filename,err
                elif file.type in vm_disk_types:
                    if managed_node.node_proxy.file_exists(file.filename):
                        print 'deleting: ' + file.filename
                        managed_node.node_proxy.remove(file.filename)
        else:
            print "Couldn't find the domain %s. Skipping deletion" % name

    def do_dom_action(self,auth,domId,nodeId,action):
        ent=auth.get_entity(domId)
        if not auth.has_privilege(action.upper(),ent):
            raise Exception(constants.NO_PRIVILEGE)
        try:
            nodeId=ent.parents[0].entity_id
            node=self.getNode(auth,nodeId)
            dom = node.get_dom(ent.name)
            result = False
            if action=='start':
                if not dom.is_resident():
                    dom._start()
                    # added to update curr metrics immediaty to reflect the status in dashboard
                    #commented because in kvm getmetrics pid becomes None
                    #as we are setting the state of dom to VM.RUNNING
                    #self.collectVMMetrics(auth, node)

                else:
                    #raise Exception("Virtual Machine "+ent.name+" is already running")
                    LOGGER.info("Virtual Machine "+ent.name+" is already running.")
            else:
                if dom.is_resident():
                    if action=='pause':
                        result = dom._pause()
                    if action=='unpause':
                        result = dom._unpause()
                    if action=='reboot':
                        dom._reboot()
                    if action=='shutdown':
                        dom._shutdown()
                        ###commented on 26/11/09
                        ###Collect metrics task will update the shutdown VMs status
                        #MetricsService().DeleteCurrentMetrics(constants.VM_CURR,domId)
                    if action=='kill':
                        dom._destroy()
                        #MetricsService().DeleteCurrentMetrics(constants.VM_CURR,domId)
                        ###end
                else:
                    if action in [constants.KILL,constants.SHUTDOWN]:
                        LOGGER.info("Virtual MachineLOGGER "+ent.name+" is not running.")
                    else:
                        raise Exception("Virtual Machine "+ent.name+" is not running")


            dom.check_action_status(action,result)

            if action == 'start':
                metrics=node.get_metrics()
                data_dict=metrics.get(dom.name)
                if data_dict is not None:
                    time.sleep(5)
                metrics=node.get_metrics()
                data_dict=metrics.get(dom.name)
                if data_dict is None:
                    is_hvm=dom.is_hvm()
                    #vm_info=dom.get_info()
                    #dom_id=vm_info['domid']
                    err='VM went down after 5 seconds.'
                    if is_hvm == False:
                        if node.node_proxy.file_exists(constants.XEN_LOG_PATH):
                           f=None
                           try:
                              f = node.node_proxy.open(constants.XEN_LOG_PATH, 'r')
                              err_log=self.tail(f,10)
                              for e in err_log:
                                 err += e
                           finally:
                              if f is not None:
                                 f.close()
                    raise Exception(err)
                try:
                    ret_msg=None
                    vm_config=dom.get_config()
                    update_dom=False
                    if dom.is_hvm():
                        boot = vm_config.get('boot')
                        n_boot = vm_config.get('next_boot_device')
                        if n_boot is not None:
                            if boot != n_boot:
                                vm_config['boot']=n_boot
                                ret_msg="value of config option boot changed to "+n_boot
                                update_dom=True
                    else:
                        boot = vm_config.get('bootloader')
                        n_boot = vm_config.get('next_bootloader')
                        if n_boot is not None:
                            if boot != n_boot:
                                vm_config['bootloader']=n_boot
                                vm_config['save_ramdisk']=vm_config['ramdisk']
                                vm_config['ramdisk']=''
                                vm_config['save_kernel']=vm_config['kernel']
                                vm_config['kernel']=''
                                ret_msg="value of config option bootloader changed to "+n_boot
                                update_dom=True

                    if update_dom==True:
                        dom.vm_config=get_config_text(vm_config)
                        DBSession.add(dom)
                        #print "\n\n=======",vm_config.options
                        vm_config.set_filename(vm_config['config_filename'])
                        vm_config.write()
                        LOGGER.info(to_str(ret_msg))
                except Exception, e:
                    traceback.print_exc()
                    print "Exception: ", e
                dom.start_monitoring()
            elif action=='shutdown' or action=='kill':
                dom.stop_monitoring()
            transaction.commit()
            #node.refresh()
            self.updateMetrics(auth,domId,nodeId)
            node=self.getNode(auth,nodeId)
            node.refresh_vm_avail()
        except Exception, e:
            traceback.print_exc()
            raise e

    def status_check(self,action,sl,state,values,node,dom):

        xl=0
        if action == 'reboot':
           rebooted=dom.check_reboot_state(sl)
           if rebooted:
               return
           else:
               raise Exception(action+' failed due to timeout')

        for counter in range(xl,sl):
            time.sleep(1)
            node.refresh()
            metrics=node.get_metrics()
            data_dict=metrics.get(dom.name)
                     
            if data_dict is not None:
                state=data_dict.get('STATE')
            if action=='shutdown' or action=='kill':
                if data_dict is None:
                    return
            elif state in values:
                return
            
        if action=='shutdown' or action=='kill':
           if data_dict is not None:
               raise Exception(action+' failed due to timeout')

        elif state not in values:
               raise Exception(action+' failed due to timeout')

    def tail(self,f, n):
        
        pos, lines = n+1, []
        while len(lines) <= n:
            try:
                try:
                    f.seek(-pos, 2)
                except IOError:
                  f.seek(0)
                  break
            finally:
                    lines = list(f)
            pos *= 2
        return lines[-n:]

    def set_dom_device(self,auth,dom,boot):
        ent=auth.get_entity(dom.id)
        if not auth.has_privilege('SET_BOOT_DEVICE',ent):
            raise Exception(constants.NO_PRIVILEGE)

        vm_config = dom.get_config()
        if not vm_config:
            raise Exception('No configuration file associated with this VM.')

        if boot is not None:
            vm_config['boot'] = boot
            dom.vm_config=get_config_text(vm_config)
            DBHelper().add(dom)
            nodeid=ent.parents[0].entity_id
            mgd_node= DBSession.query(ManagedNode).filter(ManagedNode.id==nodeid).first()
            vm_config.set_managed_node(mgd_node)
            vm_config.set_filename(dom.get_config()["config_filename"])
            vm_config.write()

    def save_appliance_info(self,auth,dom,config):
        ent=auth.get_entity(dom.id)
        if not auth.has_privilege('SAVE_APPLIANCE_INFO',ent):
            raise Exception(constants.NO_PRIVILEGE)

        dom.vm_config=get_config_text(config)
        DBHelper().add(dom)
        nodeid=ent.parents[0].entity_id
        mgd_node= DBSession.query(ManagedNode).filter(ManagedNode.id==nodeid).first()
        config.set_managed_node(mgd_node)
        config.set_filename(dom.get_config()["config_filename"])
        config.write() 

    #Added by gizli: Cutover from NodeService
    def migrate_vm(self, auth, dom_list, source_node_id,\
                    dest_node_id, isLive, isForce, migrate_all): 
        managed_node = self.getNode(auth, source_node_id)
        dest_node = self.getNode(auth, dest_node_id)

#        vm_list = []
#        if migrate_all:
#            for vm in managed_node.get_doms():
#                if not vm.isDom0():
#                    vm_list.append(vm)
#        else:
#            dom = managed_node.get_dom(dom_name)
#            vm_list = [dom]
        #managed_node.connect()
        if dest_node.is_up():
            dest_node.connect()
#        if not isForce:
#            (e, w) = managed_node.migration_checks(vm_list, dest_node, isLive)
#            if len(e) > 0 or len(w) > 0:
#                result = []
#                for err in e:
#                    (cat, msg) = err
#                    result.append(dict(type='error',category=cat,message=msg))
#                for warn in w:
#                    (cat, msg) = warn
#                    result.append(dict(type='warning',category=cat,message=msg))
#                return result
        vm_list=[]
#        vm_name=[]
#        metrics=managed_node.get_metrics()
        for domid in dom_list:
            doms=DBHelper().filterby(VM,[],[VM.id==domid])
            if len(doms)>0:                
                vm_list.append(doms[0])
#                vm_state_dict=metrics.get(doms[0].name)
#                if vm_state_dict is not None:
#                    vm_name.append(doms[0].name)
        
        if migrate_all:
            self.migrateNode(auth, managed_node, dest_node, True, isForce)
        else:
            self.migrateDomains(auth, managed_node, vm_list, dest_node,\
                                True, isForce)
#        sl=0.0
#        sl=tg.config.get(constants.migrate_time)
#        sl=float(sl)
#        time.sleep(sl)

        self.updateMetrics(auth,None,dest_node.id)
        self.updateMetrics(auth,None,managed_node.id)

#        metrics=dest_node.get_metrics()
#        for v in vm_name:
#            data_dict=metrics.get(v)
#            if data_dict is None:
#               raise Exception('migrate failed')

    def resume_migrate_vm(self, auth, dom_list, source_node_id,\
                    dest_node_id, isLive, isForce, migrate_all,\
                    recover = False):
        managed_node = self.getNode(auth, source_node_id)
        dest_node = self.getNode(auth, dest_node_id)

        if dest_node.is_up():
            dest_node.connect()

        src_ent = DBSession.query(Entity).filter(Entity.entity_id==managed_node.id).first()
        dest_ent = DBSession.query(Entity).filter(Entity.entity_id==dest_node.id).first()
        running_vms = dest_node.get_running_vms()
        #print "\n\n======running_vms===",running_vms
        if migrate_all:
            fail_ents=vm_ents = auth.get_entities(to_unicode(constants.DOMAIN),parent=src_ent)
            succ_ents=[]
            for vm_ent in vm_ents:
                migration_status=False
                if recover == True:
                    migration_status=running_vms.has_key(vm_ent.name)
                else:
                    migration_status=self.get_migration_status(running_vms, managed_node, vm_ent, dest_node)
                if migration_status == True:
                    succ_ents.append(vm_ent)
                    fail_ents.remove(vm_ent)
                    auth.update_entity_by_id(vm_ent.entity_id,parent=dest_ent)
            transaction.commit()
            if len(fail_ents)>0:
                names=[e.name for e in fail_ents]
                raise Exception("Failed to migrate following Virtual Machines: "+to_str(names))

            #self.migrateNode(auth, managed_node, dest_node, True, isForce, requester=requester)
        else:
            fail_ents=vm_ents = DBSession.query(Entity).filter(Entity.entity_id.in_(dom_list)).all()
            pend_ents=[]
            for vm_ent in vm_ents:
                if vm_ent.parents[0].entity_id == source_node_id:
                    migration_status=False
                    if recover == True:
                        migration_status=running_vms.has_key(vm_ent.name)
                    else:
                        migration_status=self.get_migration_status(running_vms, managed_node, vm_ent, dest_node)
                    if migration_status == True:
                        fail_ents.remove(vm_ent)
                        auth.update_entity_by_id(vm_ent.entity_id,parent=dest_ent)
                    else:
                        pend_ents.append(vm_ent.entity_id)
                else:
                    fail_ents.remove(vm_ent)

            transaction.commit()
            if len(fail_ents)>0:
                names=[e.name for e in fail_ents]
                raise Exception("Failed to migrate following Virtual Machines: "+to_str(names))

#            vm_list=DBSession.query(VM).filter(VM.id.in_(pend_ents)).all()
#            if len(vm_list)!=0:
#                self.migrateDomains(auth, managed_node, vm_list, dest_node,\
#                                True, isForce, requester=requester)

        try:
            self.updateMetrics(auth,None,dest_node.id)
            self.updateMetrics(auth,None,managed_node.id)
        except Exception, e:
            traceback.print_exc()
            LOGGER.error(to_str(e))

    def get_migration_status(self, dest_running_vms, managed_node, vm_ent, dest_node):
        if dest_running_vms.has_key(vm_ent.name):
            dom = DBSession.query(VM).filter(VM.id==vm_ent.entity_id).first()
            wait_time=dom.get_wait_time(constants.MIGRATE)
            disappeared=wait_time_over=False
            if managed_node.is_up():
                src_running_vms = managed_node.get_running_vms()
                if src_running_vms.has_key(dom.name) or \
                            src_running_vms.has_key("migrating-"+dom.name):
                    (disappeared, wait_time_over) = self.wait_for_migration(wait_time, \
                                managed_node, dom.name, dest_node)
            ###if wait time is not over, that means vm got migrated successfully
            ###i.e. dissapppeared from source and running in destination node
            if wait_time_over != True:
                return True
        return False

    def get_ssh_info(self,auth,nodeId,address,client_platform):
        print "------address-------", address
        result         = {}
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id==nodeId).first()
        hostname     = str(managed_node.hostname)
        credentials = DBSession.query(Credential).filter(Credential.entity_id==nodeId).first();

        uname       = str(credentials.cred_details['username'])
        port        = str(credentials.cred_details['ssh_port'])
        
        client_config = ClientConfiguration()
        sshhost      = client_config.get(constants.prop_ssh_forward_host)##Intermediate Server's hostname
        sshport      = client_config.get(constants.prop_ssh_forward_port)##Intermediate Server's Port
        sshuser      = client_config.get(constants.prop_ssh_forward_user)##Intermediate Server's Username
        sshpwd       = client_config.get(constants.prop_ssh_forward_password)##Intermediate Server's Password
        sshkey       = client_config.get(constants.prop_ssh_forward_key)
        ssh_file_loc     = client_config.get(constants.ssh_file)
        ssh_tunnel_setup = client_config.get(constants.prop_ssh_tunnel_setup)
        ssh_log_level    = client_config.get(constants.prop_ssh_log_level)

        msg = "ManagedNode Infos## hostname:%s, uname:%s, port:%s" %(hostname, uname, port)
        print msg
        LOGGER.info(msg)
        msg = "IntermediateServer Infos## sshhost:%s, sshport:%s, sshuser:%s, sshpwd:%s, sshkey:%s, ssh_file_loc:%s, ssh_tunnel_setup:%s, ssh_log_level:%s"\
                %(sshhost, sshport, sshuser, sshpwd, sshkey, ssh_file_loc, ssh_tunnel_setup, ssh_log_level)
        print msg
        LOGGER.info(msg)

        if sshhost == '' or (sshhost != constants.LOCALHOST and (sshuser == '' or sshpwd == '' )) or sshport == '' :
            #For non localhost Intermediate Server, we must given username, password and port
            msg = "For non localhost intermediate server, please specify username, password and port in development.ini"
            print msg
            LOGGER.error(msg)
            raise Exception('SSH forwarding is not configured. ')

#        if sshhost == constants.LOCALHOST or  sshhost == '127.0.0.1':
#             applet_cmd       = self.formAppletCommandForSSH(client_platform,port,sshuser,sshhost)
#             result['command'] = applet_cmd
#             return result
#        else:

        ports = sshport.split(':')
        if len(ports) >2 or len(ports) == 0 or sshport == None:
          raise Exception('SSH Port numbers are not configured properly. For Example,6900:7000')

        forward_port = None
        ssh_node=self.create_node(sshhost,sshuser,sshpwd)## Create Intermediate Server.

        if ssh_node is None:
         raise Exception("Can not connect to SSH Host, "+sshhost+".")

        try:
            forward_port = str(ssh_node.get_unused_port(int(ports[0]),int(ports[1])))
        except Exception, e:
            LOGGER.error(to_str(e))
            traceback.print_exc()
            raise e

        #Create temporary file
        temp_file_name = forward_port+'_'+port+'_'
        temp_file = mktempfile(ssh_node,temp_file_name,'.log')
        log_level = '-d ' * int(ssh_log_level)
        cmd = 'socat '+log_level+'TCP-LISTEN:'+str(forward_port)+" EXEC:'/usr/bin/ssh -i "+ str(ssh_file_loc)+\
                ' -p '+str(port) +" "+ str(uname)+'@'+str(hostname)+\
                " socat - TCP\:127.0.0.1\:"+to_str(port)+" '> "+temp_file+" 2>&1 &"
        print "-----cmd------", cmd
        if ssh_tunnel_setup:
            result['forwarding']= 'Enabled'
            msg = "SSH forwarding enabled through Server:%s" %(sshhost)
            print msg
            LOGGER.info(msg)
            ##Setup Portforwarding in Intermediate Server(sshhost)
            (output,exit_code) = ssh_node.node_proxy.exec_cmd(cmd,timeout=None)
            if exit_code == 1:
                 raise Exception("Error forwarding the port to SSH Host. "+output)
            ##SSH to ManagedNode through Intermediate Server(sshhost)
            if not sshuser:
                sshuser = "root"
            applet_cmd  = self.formAppletCommandForSSH(client_platform,forward_port,sshuser,sshhost,address)
        else:
            result['forwarding']= 'Disabled'
            msg = "SSH forwarding disabled"
            print msg
            LOGGER.info(msg)
            ##Direct SSH to ManagedNode.
            applet_cmd  = self.formAppletCommandForSSH(client_platform,port,uname,hostname,None)

        print "applet cmd==",applet_cmd
        result['command'] = applet_cmd
        #Intermediate Server
        result['hostname']=sshhost
        result['port']=sshport
        #Managed node
        result['server']=hostname
        
        return result


    def formAppletCommandForSSH(self,osname,forwardport,username,host,address):
        applet_cmd    = None
        port_variable =  None
        value_map     = {}
        command = template_str = None

        if osname   == constants.WINDOWS:
             command = tg.config.get(constants.PUTTY_CMD)
#             if host == constants.LOCALHOST:
#                 command = command.replace('$USER@', '')
             port_variable = str(forwardport)+ ' '
             value_map[constants.PORT]    = port_variable 
             
        elif osname  == constants.LINUX:
             command = tg.config.get(constants.SSH_CMD)
#             if host== constants.LOCALHOST:
#                 command=command.replace('$USER@', '')
             port_variable = str(forwardport)+ ' '
             value_map[constants.PORT]  = port_variable 

        if host=='localhost' and address:
            host=address

        template_str = string.Template(command)
        value_map[constants.USER]      = str(username)
        value_map[constants.APPLET_IP] = str(host)
        applet_cmd = to_str(template_str.safe_substitute(value_map))

        return applet_cmd


    def get_vnc_info(self,auth,nodeId,domId,address):
        managed_node = self.getNode(auth,nodeId)
        credentials=managed_node.get_credentials()
        dom = managed_node.get_dom(domId)
        result={}
        hostname=managed_node.address
        host_ssh_port=credentials["ssh_port"]
        vnc_node=None
        if hostname is None:
            hostname=managed_node.hostname

        client_config=ClientConfiguration()
        use_vnc_proxy=client_config.get(constants.prop_use_vnc_proxy)
        print "===============use_vnc_proy=========", use_vnc_proxy
        vnchost=client_config.get(constants.prop_vnc_host)
        vncport=client_config.get(constants.prop_vnc_port)
        vncuser=client_config.get(constants.prop_vnc_user)
        vncpwd=client_config.get(constants.prop_vnc_password)
        
        if not vnchost or not vncport or not vncuser or vncport.find(':')==-1:
            raise Exception("VNC Host,Port & User should be configured properly.")
        
        (start,end)=vncport.split(':')
        if not start or not end:
            raise Exception("VNC Port should be configured properly."+\
                            "(start:end)")
#        forward_port=None
#        try:
#           forward_port=random.randrange(int(start),int(end))
#        except Exception, e:
#            print e
#            raise Exception("Port Numbers should be valid numbers.")
        
        result['hostname']=address
        result['port']='00'
        result['server']=managed_node.hostname
        result['server_ssh_port']=managed_node.ssh_port
        result['vnc_display']='00'        
        result['height']=dom.get_attribute_value(constants.VNC_APPLET_HEIGHT,\
                            tg.config.get(constants.VNC_APPLET_HEIGHT))
        result['width']=dom.get_attribute_value(constants.VNC_APPLET_WIDTH,\
                            tg.config.get(constants.VNC_APPLET_WIDTH))
        result['new_window']=dom.get_attribute_value(constants.VNC_APPLET_PARAM_OPEN_NEW_WINDOW,\
                            tg.config.get(constants.VNC_APPLET_PARAM_OPEN_NEW_WINDOW))
        result['show_control']=dom.get_attribute_value(constants.VNC_APPLET_PARAM_SHOW_CONTROL,\
                            tg.config.get(constants.VNC_APPLET_PARAM_SHOW_CONTROL))
        result['encoding']=dom.get_attribute_value(constants.VNC_APPLET_PARAM_ENCODING,\
                            tg.config.get(constants.VNC_APPLET_PARAM_ENCODING))
        result['restricted_colours']=dom.get_attribute_value(constants.VNC_APPLET_PARAM_RESTRICTED_COLOURS,\
                            tg.config.get(constants.VNC_APPLET_PARAM_RESTRICTED_COLOURS))
        result['offer_relogin']=dom.get_attribute_value(constants.VNC_APPLET_PARAM_OFFER_RELOGIN,\
                            tg.config.get(constants.VNC_APPLET_PARAM_OFFER_RELOGIN))
        
        if not dom.is_resident():
            return result
        if dom.is_graphical_console():
            vnc_port = dom.get_vnc_port()
            #vnc_display = to_str(vnc_port)
            vnc_display = 5900+int(vnc_port)

#            list=DBHelper().filterby(ManagedNode,[],\
#                            [ManagedNode.hostname==vnchost])
            list=[]
            if len(list)>0:
                vnc_node=list[0]
            elif not use_vnc_proxy :
                vnc_node = managed_node
                vnchost = managed_node.hostname
            else:
                vnc_node=self.create_node(vnchost,vncuser,vncpwd)

            if vnc_node is None:
                raise Exception("Can not connect to VNC Host, "+vnchost+".")

            try:
                start = int(start)
                end = int(end)
            except Exception, e:
                print "Exception: ", e
                raise Exception("Port Numbers should be valid numbers.")

            try:
                forward_port = vnc_node.get_unused_port(start,end)
            except Exception, e:
                LOGGER.error(to_str(e))
                traceback.print_exc()
                raise e

            if forward_port is None:
                raise Exception("No ports are free in the given range."\
                                +"("+start+":"+end+")")
            (cmd,temp_file)=self.get_port_forward_cmd(use_vnc_proxy,forward_port,vncuser,hostname,host_ssh_port,\
                                            vnc_display,dom)
            print use_vnc_proxy,forward_port,vncuser,hostname,vnc_display
            print cmd
            

            (output,exit_code)=vnc_node.node_proxy.exec_cmd(cmd,timeout=None)
            
            if exit_code==1:
                raise Exception("Error forwarding the vnc display to VNC Host. "+output)

#            view_log="&nbsp;&nbsp;<a href=# onClick=show_log(&quot;"+temp_file+"&quot;)>View Log File Content</a> "
            if use_vnc_proxy and vnchost=='localhost':
                vnchost=address
            result['hostname']=vnchost
            result['port']=forward_port            
            result['server']=managed_node.hostname
            result['vnc_display']=vnc_display
#            result['temp_file']=temp_file+view_log
            result['temp_file']=temp_file
        else:
            raise Exception('VNC is not enabled for this VM.')
        return result

    def create_node(self,hostname,username,password):
        use_keys=(password==None and hostname!='localhost')
        isRemote=(hostname!='localhost')
        vnc_node=ManagedNode(hostname = hostname,
                             ssh_port = 22,
                             username=username,
                             password=password,
                             isRemote=isRemote,
                             helper = None,
                             use_keys = use_keys,
                             address = hostname)
        try:
            vnc_node.connect()
        except Exception, e:
            print "Exception: ", e
            return None
        return vnc_node    

    def get_port_forward_cmd(self,use_vnc_proxy,forward_port,vncuser,hostname,host_ssh_port,vnc_display,dom):
        prename=to_str(forward_port)+"_"+to_str(vnc_display)+"_"
        temp_file =mktempfile(None,prename,".log")        
        log_level = 3
        try:
            log_level=dom.get_vnc_log_level()
        except Exception, e:
            print "Exception: ", e

        vnc_log_level='-d '*log_level
        if use_vnc_proxy:
            cmd="socat "+vnc_log_level+" TCP-LISTEN:"+to_str(forward_port)+\
                " EXEC:'/usr/bin/ssh -o StrictHostKeyChecking=no -p " + str(host_ssh_port) + " " +vncuser+"@"+hostname+\
                " socat - TCP\:127.0.0.1\:"+to_str(vnc_display)+"' > "+temp_file+" 2>&1 &"
        else:
           # Direct connection to managed node.
            cmd="socat "+vnc_log_level+" TCP-LISTEN:"+to_str(forward_port)+\
                " EXEC:'socat - TCP\:127.0.0.1\:"+to_str(vnc_display)+"' > "+temp_file+" 2>&1 &"
        return (cmd,temp_file)

    """
    Function to get the node metrics from the managed_node and insert the metrics data in
    VM RAW/CURR tables
    """
    def collectVMMetrics(self, auth, node_id, metrics=None):
        managed_node=DBSession.query(ManagedNode).filter(ManagedNode.id==node_id).one()
        #print metrics,"\n\n\n"
        if metrics is None:
            try:
                metrics=self.getNodeMetrics(auth,managed_node)
            except Exception, e:
                metrics={}
                traceback.print_exc()
                LOGGER.error(to_str(e))
                
        ent=auth.get_entity(managed_node.id)
        child_ents=auth.get_entities(to_unicode(constants.DOMAIN),parent=ent)
        """
        loop to get the vm id to be inserted in the VM metrics table since the dictionary does not
        have VM id but VM name.
        """
        keys=metrics.keys()
        for child_ent in child_ents:
            dom=DBSession.query(VM).filter(VM.id==child_ent.entity_id).one()
            
#            if dom.status==constants.MIGRATING:
#                LOGGER.error("VM "+dom.name+", is on migration. "+\
#                            "Not updating current metrics.")
#                continue
#            state = None
            (cont, msg)=dom.status_check()
            if cont==False:
                LOGGER.error(msg)
                continue
            if msg is not None:
                LOGGER.error(msg)
            ###added on 26/11/09
            ###entering the shutdown vms status in metrics
            if child_ent.name in keys:                
                dict_data = metrics[child_ent.name]
#                if state is not None:
#                    dict_data={'STATE':state}
#                vm_metrics_obj = MetricVMRaw()
#                ms.insertMetricsData(dict_data, child_ent.entity_id, vm_metrics_obj)
                self.insert_data(dict_data,child_ent)
            else:
                dict_data={'STATE':VM.SHUTDOWN}
#                if state is not None:
#                    dict_data={'STATE':state}
                ###to show storage related info for shutdown vms
                ###metrics will have info only gor running vms
                managed_node.augment_storage_stats(child_ent.name, dict_data, dom)
#                vm_metrics_obj = MetricVMRaw()
#                ms.insertMetricsData(dict_data, child_ent.entity_id, vm_metrics_obj)
                self.insert_data(dict_data,child_ent)
#            for keys in metrics:
#                if keys==child_ent.name: # if the correct vm found
#                    dict_data = metrics[keys]
#                    vm_metrics_obj = MetricVMRaw()
#                    ms.insertMetricsData(dict_data, child_ent.entity_id, vm_metrics_obj)
            ###end


    def insert_data(self,dict_data,child_ent):
        vm_metrics_obj = MetricVMRaw()
        ms = MetricsService()
        try:
            LockManager().get_lock(constants.METRICS, child_ent.entity_id, constants.COLLECT_METRICS, constants.Table_metrics+"/"+constants.Table_metrics_curr)
            ms.insertMetricsData(dict_data, child_ent.entity_id, vm_metrics_obj)
        finally:
            LockManager().release_lock()

    """
    Function to get the node metrics from the managed_node and insert the metrics data in
    SERVER RAW/CURR tables
    """ 
    def collectServerMetrics(self, auth, m_node,filter=False):

        node_status = "Not Connected"
        reason=""
        try:
            m_node.connect()
            node_status = "Connected"
        except Exception ,ex:
            reason=to_str(ex)
            node_status = "Not Connected"
            #traceback.print_exc()
            LOGGER.error("Error connecting to server:"+ to_str(m_node.hostname) + "." + to_str(ex))
#        if m_node.is_authenticated():
#            node_status = "Connected"
#        else:
#            node_status = "Not Connected"

        node_snapshot={}
        node_down=node_up=False
        if m_node is not None:                
            try:
                serverCurrInstance = MetricsService().getServerCurrMetricsData(constants.SERVER_CURR, m_node.id)
                if node_status == "Connected":                    
                    if serverCurrInstance and serverCurrInstance.state!="Connected":
                        node_up=True
                if node_status != "Connected":
                    if serverCurrInstance and serverCurrInstance.state=="Connected":
                        node_down=True

                if m_node.is_authenticated() and not m_node.is_in_error():
                    node_snapshot = None
                    #dom_count = 0
                    try:
                        strt = p_task_timing_start(MTR_LOGGER, "NodeGetMterics", m_node.id)
                        node_snapshot = m_node.get_metrics(filter=filter)
                        p_task_timing_end(MTR_LOGGER, strt)
                    except Exception ,ex:
                        print "error getting info for ", m_node.hostname, ex
                        traceback.print_exc()
                        pass

                    if node_snapshot is None:
                        node_snapshot = {}
                        node_snapshot["NODE_NAME"] = m_node.hostname

                    node_snapshot["NODE_NAME"]= m_node.hostname
                    node_snapshot["NODE_STATUS"]= node_status
                    ###commented on 25/11/09
                    ###node.get_metrics() returns total vms
    #                try:
    #                    dom_count = m_node.get_VM_count()
    #                    node_snapshot["TOTAL_VMs"] = dom_count
    #                except Exception ,ex:
    #                    #print "error getting dom count ", m_node.hostname, ex
    #                    pass
                    ###end
                else:
                    node_snapshot = {"NODE_NAME":m_node.hostname,
                                        "NODE_STATUS":node_status
                                        }
            except Exception, e:
                traceback.print_exc()
                LOGGER.error(e)

            node_snapshot["NODE_PLATFORM"] = m_node.platform

        ms = MetricsService()
        server_metrics_obj = MetricServerRaw()
        try:
            LockManager().get_lock(constants.METRICS, m_node.id, constants.COLLECT_METRICS, constants.Table_metrics+"/"+constants.Table_metrics_curr)
            ms.insertServerMetricsData(node_snapshot, m_node.id, server_metrics_obj)
        finally:
            LockManager().release_lock()
#        transaction.commit()
        if node_up==True:
            self.node_up_action(auth, m_node.id)
        if node_down==True:
            notify_node_down(m_node.hostname,reason)
        return node_snapshot

    """
    Function to insert the metrics data in SERVER_POOL RAW/CURR tables. the data in the SERVER_POOL
    is rolled-up data from server metrics table
    """    
    def collectServerPoolMetrics(self, auth, pool_id):
        node_list = self.getNodeList(auth, pool_id)
        connected = 0
        # obtain the server connected status to display in the dashboard        
        for m_node in node_list:
            if m_node is None :            
                continue
            if m_node is not None:
                try:
                    if not m_node.is_authenticated():
                        m_node.connect()
                    if m_node.is_authenticated() and not m_node.is_in_error():
                        connected = connected + 1
                except Exception, e:
                    LOGGER.error(e)
        """
        added to insert serverpool metrics. the calculation for pool is
        done from the values of server_metrics_raw table. the function
        takes pool_id as a parameter.
        """
        ms = MetricsService()
        try:
            LockManager().get_lock(constants.METRICS, pool_id, constants.COLLECT_METRICS, constants.Table_metrics+"/"+constants.Table_metrics_curr)
            ms.collect_serverpool_metrics(pool_id,connected,auth)
        finally:
            LockManager().release_lock()

    """
    This is a thread function to collect metrics at VM/SERVER/POOL level at the specified
    interval.This function is responsible for updating current as well as raw tables.
    """

#
#    def collect_metrics_for_all_nodes(self, auth):
#        serverpool_ents = auth.get_entities(to_unicode(constants.SERVER_POOL))
#        # loop through all the server_pools present in the data centre
#        for serverpool_ids in serverpool_ents:
#            node_list = self.getNodeList(auth, serverpool_ids.entity_id)
#            #node_list.sort()
#            node_ids=[]
#            for m_node in node_list:
#                node_ids.append(m_node.id)
#            for node_id in node_ids:
#                m_node=DBSession.query(ManagedNode).filter(ManagedNode.id==node_id).one()
##            for m_node in node_list:
#                if m_node is None :
#                    continue
#
#                #call function to store the Server metrics into the database
#                node_snapshot=self.collectServerMetrics(auth, m_node,filter=True)
#
#                #call function to store the VM metrics into the database table
#                self.collectVMMetrics(auth, node_id, node_snapshot)


    def updateMetrics(self, auth, domId=None,nodeId=None,groupId=None):
        if domId is None and nodeId is None and groupId is None:
            self.collect_metrics_for_all_nodes(auth)
            return

        if groupId is not None:
            node_list = self.getNodeList(auth, groupId)
            for m_node in node_list:
                if m_node is None :
                    continue

                node_id=m_node.id
                #print "\n\nGROUPPPPP\n\n"
                node_snapshot=self.collectServerMetrics(auth, m_node)
                self.collectVMMetrics(auth, node_id, node_snapshot)

            self.collectServerPoolMetrics(auth, groupId)
            return

        if nodeId is not None:
            ent=auth.get_entity(nodeId)
            m_node=self.getNode(auth, nodeId)

            if m_node is None :
                return

            node_snapshot=self.collectServerMetrics(auth, m_node)
            self.collectVMMetrics(auth, nodeId, node_snapshot)
            #print "\n\nNODEEEEEEEEEEEEE\n\n"
            pool_id=ent.parents[0].entity_id
            self.collectServerPoolMetrics(auth, pool_id)
            return 

        if domId is not None:
            ent=auth.get_entity(domId)
            node=ent.parents[0]
            m_node=self.getNode(auth, node.entity_id)

            if m_node is None :
                return

            node_snapshot=self.collectServerMetrics(auth, m_node)
            self.collectVMMetrics(auth, node.entity_id, node_snapshot)
            #print "\n\nDOMMMMMMMMMMMMM\n\n"
            pool_id=node.parents[0].entity_id
            self.collectServerPoolMetrics(auth, pool_id)
            return 

    def node_up_action(self, auth, node_id):
        task_ids=[]
        try:
            node_ent = DBSession.query(Entity).filter(Entity.entity_id == node_id).first()
            if node_ent:
                from convirt.viewModel.TaskCreator import TaskCreator
                tc = TaskCreator()
                vm_ids = [d.entity_id for d in node_ent.children]
                doms = DBSession.query(VM).filter(VM.id.in_(vm_ids)).all()
                for dom in doms:
                    config = dom.get_config()
                    if config and config.get("auto_start_vm")==1:
                        tid=tc.vm_action(auth, dom.id, node_id, constants.START)
                        task_ids.append(tid)
        except Exception, e:
            traceback.print_exc()
        
        return task_ids

    def getSiteByGroupId(self, group_id):
        site=None
        entity = DBSession.query(EntityRelation).filter_by(dest_id = group_id).first()
        if entity:
            site = DBSession.query(Site).filter_by(id = entity.src_id).first()
        return site

    def getSite(self, site_id):
        site = DBSession.query(Site).filter_by(id=site_id).first()
        return site

    def send_notifications(self,auth):
        """
        send E-mail for failed tasks.
        """
	notification_count = 500
	try:
	    notification_count=int(tg.config.get(constants.NOTIFICATION_COUNT))
	except Exception, e:
            print "Exception: ", e
        notifications=DBSession.query(Notification).filter(Notification.mail_status == False).\
                order_by(Notification.error_time.asc()).limit(notification_count).all() 
        emanager=EmailManager()
        for n in notifications:
            sent=False
            email = n.emailId
            if n.subject is None:
                message = n.task_name + " Task failed at "+ to_str(n.error_time) \
                            + "\n\n" +to_str(n.error_msg)
                subject = "ConVirt - Failed Task: "+n.task_name
            else:
                subject = n.subject
                message = to_str(n.error_msg)
            sent=emanager.send_email(email, message, subject, 'html')
            if sent == True:
                n.mail_status=True
                DBHelper().update(n)
            else:
                LOGGER.error("Error Sending Notification:-"+subject)
                break

    def get_vm_disks_from_UI(self, vm_id, config):
        vm_disks=[]
        if config:
#            vm_id=None
#            vm = DBSession.query(VM).filter_by(name=vm_name).first()
#            if vm:
#                vm_id = vm.id

            storage_status_object = config.get("storage_status_object")
            if storage_status_object:
                disk_stat = storage_status_object.get("disk_stat")
                if disk_stat:
                    for each_disk_stat in disk_stat:
                        disk={}
                        vm_disk_id=None
                        objVMDisk = DBSession.query(VMDisks).filter_by(vm_id=vm_id, disk_name=each_disk_stat.get("filename")).first()
                        if objVMDisk:
                            vm_disk_id = objVMDisk.id
                        disk["vm_id"] = vm_id
                        disk["id"] = vm_disk_id
                        disk["disk_name"] = each_disk_stat.get("filename")
                        disk["read_write"] = each_disk_stat.get("mode")
                        vm_disks.append(disk)
        return vm_disks

    def manage_vm_disks(self, auth, vm_id, node_id, config, mode, removed_disk_list):
        LOGGER.info("Managing VM disks...")
        if config:
            vm = DBSession.query(VM).filter_by(id=vm_id).first()
            vm_config=None
            if vm:
                vm_id = vm.id
                vm_config = vm.get_config()
                vm_config.set_id(vm_id)
                managed_node=DBSession.query(ManagedNode).filter_by(id=node_id).first()
                vm_config.set_managed_node(managed_node)
            else:
                vm_id = None
            
            storage_status_object = config.get("storage_status_object")
            if storage_status_object:
                disk_stat = storage_status_object.get("disk_stat")
                if disk_stat != None:
#                    if len(disk_stat)>0:
#                        #remove all vm storage links
#                        self.remove_all_vm_storage_links(vm_id)
                    self.remove_all_vm_storage_links(vm_id)
                    sequence=0
                    for each_disk_stat in disk_stat:
                        #each_disk_stat.get("type")
                        storage_disk_id = each_disk_stat.get("storage_disk_id")
                        disk_name = each_disk_stat.get("filename")
                        dev_type = each_disk_stat.get("device")
                        read_write = each_disk_stat.get("mode")
                        is_shared = each_disk_stat.get("shared")
                        actual_size = 0
                        if disk_name:
                            actual_size,disk_dev_type = VMDiskManager(vm_config).get_disk_size(None, disk_name)
                        
                        actual_size_GB = self.storage_manager.convert_to_GB_from_Bytes(actual_size)
                        disk_size = each_disk_stat.get("size")
                        disk_size_GB = self.storage_manager.convert_to_GB(disk_size)
                        if mode == "EDIT_VM_CONFIG" or mode == "EDIT_VM_INFO":
                            if disk_size=="null" or disk_size=="" or disk_size==None or disk_size==0:
                                disk_size = self.storage_manager.convert_to_MB(actual_size_GB)
                                disk_size_GB = self.storage_manager.convert_to_GB(disk_size)
#                            else:
#                                disk_size_GB = each_disk_stat.get("size")
                        
                        disk_type = each_disk_stat.get("type")
                        file_system = each_disk_stat.get("fs_type")
                        storage_id = each_disk_stat.get("storage_id")
                        
                        defn=None
                        storage_type=""
                        defn = StorageManager().get_defn(storage_id)
                        if defn:
                            storage_type = defn.type
                            
                        #add in storage_disks for NFS while provisioning. Since while provisioning it creates disk.
                        if (mode == "PROVISION_VM") and (storage_type in StorageManager().STORAGE_FOR_CREATION):
                            #here add allocated as false in matching algorith, it will be set appropriatly.
                            storage_allocated=False
                            added_manually = False
                            storage_disk_id = self.storage_manager.add_storage_disk(storage_id, actual_size_GB, disk_size_GB, disk_name, None, None, None, None, storage_allocated, self, added_manually, defn)
                            disk_size_GB=actual_size_GB

                        vm_disk = self.add_vm_disk(vm_id, disk_name, disk_size_GB, dev_type, read_write, disk_type, is_shared, file_system,sequence=sequence)
                        sequence=sequence+1
        #matching vm disks with storage_disks and updating vm_storage_links table
        error_msg=None
        error_msg = self.matching_on_AddEditDelete_vm(auth, mode, vm_id, removed_disk_list)
        if error_msg:
            raise Exception(error_msg)

    
    def add_vm_disk(self, vm_id, disk_name, disk_size, dev_type, read_write, disk_type, is_shared, file_system, vm_memory=None,sequence=None):
        #add in vm_disks table
        vm_disk = VMDisks()
        vm_disk.id = getHexID()
        vm_disk.vm_id = vm_id
        vm_disk.disk_name = disk_name
        if not disk_size:
            disk_size=0
        vm_disk.disk_size = float(disk_size)
        vm_disk.dev_type = dev_type
        vm_disk.read_write = read_write
        vm_disk.disk_type = disk_type
        vm_disk.is_shared = is_shared
        vm_disk.file_system = file_system
        if vm_memory:
            vm_disk.vm_memory = vm_memory
        else:
            vm_disk.vm_memory = self.get_vm_memory(vm_id)
        vm_disk.sequence=sequence
        DBSession.add(vm_disk)
        return vm_disk
        
    def add_vm_storage_link(self, vm_disk_id, storage_disk_id):
        try:
            #when we run the matching algorith for the rest of the vms except the vm which is getting edited,
            #we find the links in the add_vm_storage_link table. So in this case we should not add duplicate link.
            #And we should not throw unique contraint exception also to keep the operation go on. So this check is here.
            vm_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=vm_disk_id, storage_disk_id=storage_disk_id).first()
            if not vm_link:
                #Add in vm_storage_links table. Establish vm disk and storage disk link here.
                if vm_disk_id and storage_disk_id:
                    vm_storage_link = VMStorageLinks()
                    vm_storage_link.id = getHexID()
                    vm_storage_link.vm_disk_id = vm_disk_id
                    vm_storage_link.storage_disk_id = storage_disk_id
                    DBSession.add(vm_storage_link)
        except Exception, ex:
            traceback.print_exc()
            LOGGER.error("Can not add duplicate vm disk and storage disk link.")
        
    def get_vm_memory(self, vm_id):
        vm_memory=0
        vm = DBSession.query(VM).filter_by(id=vm_id).first()
        if vm:
            vm_config = vm.vm_config
            if vm_config:
                vm_config_param_list = str(vm_config).split("=")
                for each_param in vm_config_param_list:
                    if each_param[0].strip() == "memory":
                        vm_memory = each_param[1].strip()
                        
        return vm_memory

    def remove_vm_storage_link(self, vm_disk_id):
        vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=vm_disk_id).first()
        if vm_storage_link:
            #Remove vm storage link here. Remove from vm_storage_links table.
            storage_disk_id = vm_storage_link.storage_disk_id
            DBSession.delete(vm_storage_link)
            
            #calculate disk size
            vm_disk = DBSession.query(VMDisks).filter_by(id=vm_disk_id).first()
            if vm_disk:
                disk_size = vm_disk.disk_size
            op = "-"
            self.storage_manager.calculate_disk_size(storage_disk_id, vm_disk.id, disk_size, op)

    def remove_vm_storage_links_only(self, vm_id):
        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
        if vm_disks:
            for vm_disk in vm_disks:
                #Remove the vm storage link from vm_storage_links table.
                self.remove_vm_storage_link(vm_disk.id)
        
    def remove_all_vm_storage_links(self, vm_id):
        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
        if vm_disks:
            for vm_disk in vm_disks:
                #Remove the vm storage link from vm_storage_links table.
                self.remove_vm_storage_link(vm_disk.id)
                #Remove the vm disk from vm_disks table.
                self.remove_vm_disk(vm_disk.id)

    def remove_vm_links_to_storage(self, storage_id, vm_id_list=None):
        #this functions will be called while detaching storage from group.
        #if vm_list is present then the storage link to the vm would be deleted only.
        storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
        if storage_disks:
            for eachdisk in storage_disks:
                vm_storage_links=[]
                if vm_id_list:
                    #get a list of vm links with storage in the group (vm_list is from a group)
                    for vm_id in vm_id_list:
                        v_s_link = DBSession.query(VMStorageLinks)\
                        .join((VMDisks, VMDisks.id==VMStorageLinks.vm_disk_id))\
                        .join((VM, VM.id==VMDisks.vm_id))\
                        .filter(VM.id==vm_id)\
                        .filter(VMStorageLinks.storage_disk_id==eachdisk.id).first()
                        vm_storage_links.append(v_s_link)
                else:
                    #get a list of vm links with storage
                    vm_storage_links = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=eachdisk.id)
                

                if vm_storage_links:
                    for eachlink in vm_storage_links:
                        if eachlink:
                            #Remove the vm storage link from vm_storage_links table.
                            self.remove_vm_storage_link(eachlink.vm_disk_id)
                            #Remove the vm disk from vm_disks table.
                            self.remove_vm_disk(eachlink.vm_disk_id)
        
    def remove_vm_disk(self, vm_disk_id):
        vm_disk = DBSession.query(VMDisks).filter_by(id=vm_disk_id).first()
        if vm_disk:
            DBSession.delete(vm_disk)
            
    
    def update_vm_disks(self, auth, vm_id, node_id, config):
        if config:
            self.remove_all_vm_storage_links(vm_id)
            self.add_vm_disks_from_config(config)
        #matching vm disks with storage_disks and updating vm_storage_links table
        self.matching_vm_disks(auth, vm_id)

    def add_vm_disks_from_config(self, config):
        if config:
            filename=None
            disk_size=0
            device=None
            mode=None
            type=None   #file/physical device
            is_shared=False  #shared/unshared
            file_system=None
            backup_content=None
            i=0

            vm = DBSession.query(VM).filter_by(name=config.name).first()
            if vm:
                vm_id = vm.id
                for de in config.getDisks():
                    type = de.type
                    filename = de.filename
                    device =de.device
                    mode = de.mode
                    disk_size,device_temp = VMDiskManager(config).get_disk_size(None, filename)
        
                    #add in vm_disks table
                    disk_size_temp = self.storage_manager.convert_to_GB_from_Bytes(disk_size)
                    vm_disk = self.add_vm_disk(vm_id, filename, disk_size_temp, device, mode, type, is_shared, file_system, backup_content,sequence=i)
                    i += 1

        
    def pre_matching_on_AddEditDelete_vm(self, auth, mode, vm_id, vm_disks=None):
        LOGGER.info("Running pre-matching logic for VM disks...")
        start = p_timing_start(STRG_LOGGER, "pre_matching_on_AddEditDelete_vm", log_level="DEBUG")
        #purpose: If you are adding vm_disk in read_write mode. Then check if the disk is allocated in 
        #read_write mode and link is present. This check is for rest of the VM (except the VM being edited). 
        #If the disk found then throw exception.
        #This is for following mode 
        #"PROVISION_VM", "IMPORT_VM_CONFIG_FILE", "TRANSFER_SERVER", "EDIT_VM_CONFIG", "EDIT_VM_INFO", "REMOVE_VM"
        
        error_msg = ""
        if mode == "PROVISION_VM" or mode == "IMPORT_VM_CONFIG_FILE"  or mode == "TRANSFER_SERVER" or mode == "EDIT_VM_CONFIG" or mode == "EDIT_VM_INFO" or mode == "REMOVE_VM":
            for each_vm_disk in vm_disks:
                disk_name = each_vm_disk.get("disk_name")
                read_write = each_vm_disk.get("read_write")
                LOGGER.info("Disk name is " + to_str(disk_name))
                
                if read_write == "w":
                    #In following query if you get records then throw the exception.
                    #If you are getting records that means the disk is allocated by any VM in read_write mode.
                    result = DBSession.query(VMDisks)\
                    .join((StorageDisks, StorageDisks.unique_path == VMDisks.disk_name))\
                    .join((VMStorageLinks, VMStorageLinks.storage_disk_id == StorageDisks.id))\
                    .join((VM, VM.id == VMDisks.vm_id))\
                    .filter(StorageDisks.storage_allocated == True)\
                    .filter(VMDisks.read_write != "r")\
                    .filter(VMDisks.disk_name == disk_name)\
                    .filter(VM.id != vm_id).first()
                    if result:
                        #Here we are throwing exception.
                        #get the vm name and disk name for constructing message..
                        #get the VM name, whom the disk is already associated with.
                        rs = DBSession.query(VM.name, VMDisks.disk_name)\
                        .join((VMDisks, VMDisks.vm_id == VM.id))\
                        .filter(VMDisks.id == result.id).first()
                        error_msg = "Invalid disk entry. Storage disk " + to_str(rs.disk_name) + " is allocated to virtual machine " + to_str(rs.name) + " in read-write mode."
                        LOGGER.error(to_str(error_msg))
                        break
        p_timing_end(STRG_LOGGER, start)
        return error_msg
            
    def matching_on_AddEditDelete_vm(self, auth, mode, vm_id, removed_disk_list=None):
        start = p_timing_start(STRG_LOGGER, "matching_on_AddEditDelete_vm ", log_level="DEBUG")
        #This function is called on provision, edit setting and remove vm.
        #The vm disk which is become free, check whether any other vm is using the disk and establish a link between vm and storage disk for the vm.
        error_msg=None
        if mode == "PROVISION_VM" or mode == "TRANSFER_SERVER" or mode == "EDIT_VM_CONFIG" or mode == "EDIT_VM_INFO" or mode == "REMOVE_VM":
            error_msg = self.matching_vm_disks(auth, vm_id, removed_disk_list)
        p_timing_end(STRG_LOGGER, start)
        return error_msg
                    
    def get_vms_from_pool(self, auth, group_id):
        vm_list=[]
        if group_id:
            group_entity = auth.get_entity(group_id)
            node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), group_entity)
            if node_entities:
                for eachnode in node_entities:
                    vm_entities = auth.get_entities(to_unicode(constants.DOMAIN), eachnode)
                    for eachvm in vm_entities:
                        vm = DBSession.query(VM).filter_by(id=eachvm.entity_id).first()
                        if vm:
                            vm_list.append(vm)
        return vm_list
                
    def get_vm_disks_from_pool(self, auth, group_id):
        vm_disk_list=[]
        if group_id:
            group_entity = auth.get_entity(group_id)
            node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), group_entity)
            if node_entities:
                for eachnode in node_entities:
                    vm_entities = auth.get_entities(to_unicode(constants.DOMAIN), eachnode)
                    for eachvm in vm_entities:
                        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=eachvm.entity_id)
                        if vm_disks:
                            for eachdisk in vm_disks:
                                vm_disk_list.append(eachdisk)
        return vm_disk_list
        
    def get_storage_disks_from_pool(self, group_id):
        start = p_timing_start(STRG_LOGGER, "pre_matching (get_storage_disks_from_pool) ", log_level="DEBUG")
        storage_disk_list=[]
        if group_id:
            storage_disks = DBSession.query(StorageDisks.id, StorageDisks.storage_id, StorageDisks.storage_type,\
            StorageDisks.disk_name, StorageDisks.mount_point, StorageDisks.file_system,\
            StorageDisks.actual_size, StorageDisks.size.label("disk_size"), StorageDisks.unique_path,\
            StorageDisks.current_portal, StorageDisks.target, StorageDisks.state, StorageDisks.lun,\
            StorageDisks.storage_allocated, StorageDisks.transient_reservation)\
            .join((StorageDef, StorageDef.id == StorageDisks.storage_id))\
            .join((SPDefLink, SPDefLink.def_id == StorageDef.id))\
            .filter(SPDefLink.group_id == group_id)
            if storage_disks:
                return storage_disks
        p_timing_end(STRG_LOGGER, start)
        return storage_disk_list
                                        
    def get_storage_disks_from_storage(self, storage_id):
        storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
        return storage_disks
    
    def matching_vm_disks(self, auth, vm_id, removed_disk_list=None):
        start = p_timing_start(STRG_LOGGER, "matching_vm_disks ")
        error_msg = ""
        if vm_id:
            #get all the vm disks of the vm which is being edited.
            vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
            if vm_disks:
                LOGGER.info("Matching for the VM which is being processed...")
                for each_vm_disk in vm_disks:
                    disk_name = each_vm_disk.disk_name
                    LOGGER.info("Disk name - " + to_str(disk_name))
                    #Start--------------------------------
                    #This section is for the VM which is being edited.
                    #This will call the matching logic and set allocation in storage_disks 
                    #and read_write, is_shared in vm_disks table for the vm which is being editted.
                    #This will also add vm_disk and storage_disk in vm_storage_link table.
                    s_disk = DBSession.query(StorageDisks).filter(StorageDisks.unique_path == disk_name).first()
                    if s_disk:
                        isMatched, msg = self.matching_logic(each_vm_disk, s_disk)
                    #End--------------------------------
                    
            #Start--------------------------------
            #This section is for removed disk.
            #This will run matching_logic for removed disk.
            #This section will check if any other VM can use this removed disk which has become free for use
            #for other VMs. And set allocation, read_write and is_shared in database. And create vm storage link.
            if removed_disk_list:
                LOGGER.info("Matching for removed disks...Lets see if other VM can use this disk...")
                for removed_disk in removed_disk_list:
                    disk_name = removed_disk
                    LOGGER.info("Removed disk name - " + to_str(disk_name))
                    rs = DBSession.query(VMDisks, StorageDisks)\
                    .join((StorageDisks, StorageDisks.unique_path == VMDisks.disk_name))\
                    .join((VM, VM.id == VMDisks.vm_id))\
                    .filter(VMDisks.disk_name == disk_name)\
                    .filter(VM.id != vm_id).first()
                    if rs:
                        v_disk = rs[0]
                        s_disk = rs[1]
                        isMatched, msg = self.matching_logic(v_disk, s_disk)
            #End--------------------------------
        p_timing_end(STRG_LOGGER, start)
        return error_msg
                            

    def matching_disk_on_discover_storage(self, vm_disks, storage_disk_id):
        #This would be executed when you would associate any storage disk to the server pool.
        #It will try to match that disk to any existing vm disk.
        #if it is matched then it would create a link in vm_storage_links table.
        #get all the vm disks related to all the vms.
        if vm_disks:
            #get the newly added storage disk
            storage_disk = DBSession.query(StorageDisks).filter_by(id=storage_disk_id).first()
            if storage_disk:
                #compare vm disk with storage disk on unique_path.
                for each_vm_disk in vm_disks:
                    self.matching_logic(each_vm_disk, storage_disk)
                
    def matching_logic(self, vm_disk, storage_disk):
        start = p_timing_start(STRG_LOGGER, "matching_logic ")
        isMatched=False
        msg = None
        if str(vm_disk.disk_name).strip() == str(storage_disk.unique_path).strip():
            #matching disk is found here
            LOGGER.info("Matching disk (" + str(vm_disk.disk_name) + ") is found")
            #check whether storage is allocated or not. If it is not then
            #update vm_disk table with storage_disk_id
            if storage_disk.storage_allocated == False:
                #storage is not allocated
                LOGGER.info("Storage (" + str(vm_disk.disk_name) + ") is not allocated")
                #Add link in vm_storage_links table.
                self.add_vm_storage_link(vm_disk.id, storage_disk.id)
                #update the shared and read_write mode
                vm_disk.is_shared = True
                vm_disk.read_write = 'w'
                isMatched=True
                #calculate disk size here
                op = "+"
                self.storage_manager.calculate_disk_size(storage_disk.id, vm_disk.id, vm_disk.disk_size, op)
            elif vm_disk.read_write == "r":
                #storage is allocated
                LOGGER.info("Storage (" + to_str(vm_disk.disk_name) + ") is allocated. Adding vm disk link in readonly mode.")
                self.add_vm_storage_link(vm_disk.id, storage_disk.id)
                #update the shared flag
                vm_disk.is_shared = True
                isMatched=True
                #calculate disk size here
                op = "+"
                self.storage_manager.calculate_disk_size(storage_disk.id, vm_disk.id, vm_disk.disk_size, op)
            else:
                isMatched=True
                vm_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=vm_disk.id, storage_disk_id=storage_disk.id).first()
                if vm_link:
                    LOGGER.info("vm disk and storage disk link already exists so we are not throwing exception or logging error.")
                else:
                    LOGGER.error("Matching disk (" + str(vm_disk.disk_name) + ") is found. The disk is already allocated and in read-write mode. So it is invalid disk entry.")
                    msg = "Invalid disk entry."

        p_timing_end(STRG_LOGGER,start)
        return (isMatched, msg)
 
    def fix_vm_disk_entries(self, auth, **kwargs):
        """
            Update Disks of all Virtual Machines under Datacenter
            http://127.0.0.1:8091/fix_vm_disk_entries
            Updating Disks of all Virtual Machines under Server 192.168.1.14
            http://127.0.0.1:8091/fix_vm_disk_entries?server=192.168.1.14
        """
        hint = "<u><b>" + "Help" + "</b></u><br/>"
        hint += """
            Update Disks of all Virtual Machines under Datacenter <br/>
            http://127.0.0.1:8091/fix_vm_disk_entries?datacenter=Datacenter  <br/><br/>
            Updating Disks of all Virtual Machines under Server Pool: Desktop<br/>
            http://127.0.0.1:8091/fix_vm_disk_entries?serverpool=Desktop <br/><br/>
            Updating Disks of all Virtual Machines under Server: 192.168.1.14<br/>
            http://127.0.0.1:8091/fix_vm_disk_entries?server=192.168.1.14 <br/><br/>
            Updating Disks of Virtual Machine: vm1<br/>
            http://127.0.0.1:8091/fix_vm_disk_entries?vm=vm1 <br/>
            """

        vms = []
        bro_msg = ""
        bro_msg += hint
        bro_msg += "<br/><u><b>" + "Update Disks" + "</b></u><br/>"
        log_msg = "Update Disks"
        LOGGER.info(log_msg)
        br_str = "<br/>"
        hr_str = "<hr/>"
        server = kwargs.get("server")
        serverpool = kwargs.get("serverpool")
        vmname = kwargs.get("vm")
        datacenter = kwargs.get("datacenter")

        if vmname:
            ### VM ###
            vm_ent = auth.get_entity_by_name(vmname, to_unicode(constants.DOMAIN))
            if not vm_ent:
                bro_msg += br_str + "Could not find Virtual Machine:%s" %(vmname)
                log_msg = "Could not find Virtual Machine:%s" %(vmname)
                LOGGER.info(log_msg)
            else:
                dom = DBSession.query(VM).filter(VM.id == vm_ent.entity_id).\
                        filter(VM.type.in_([u'xen', u'kvm'])).first()
                if not dom:
                    bro_msg += br_str + "Could not find Virtual Machine:%s" %(vmname)
                    log_msg = "Could not find Virtual Machine:%s" %(vmname)
                    LOGGER.info(log_msg)
                else:
                    vms = [dom]
        elif server:
            ### Server ###
            host_ent = auth.get_entity_by_name(server, to_unicode(constants.MANAGED_NODE))
            if not host_ent:
                bro_msg += br_str + "Could not find Server:%s" %(server)
                log_msg = "Could not find Server:%s" %(server)
                LOGGER.info(log_msg)
            else:
                host = DBSession.query(ManagedNode).filter(ManagedNode.id == host_ent.entity_id).\
                        filter(ManagedNode.type.in_([u'xen', u'kvm'])).first()
                if not host:
                    bro_msg += br_str + "Could not find Server:%s" %(server)
                    log_msg = "Could not find Server:%s" %(server)
                    LOGGER.info(log_msg)
                else:
                    bro_msg += br_str + "Updating Disks of all Virtual Machines under Server:%s" %(server)
                    log_msg = "Updating Disks of all Virtual Machines under Server:%s" %(server)
                    LOGGER.info(log_msg)
                    bro_msg += br_str + hr_str
                    vm_ids = [ent.entity_id for ent in host_ent.children]
                    ##Only for Generic VMs (xen and kvm)
                    vms = DBSession.query(VM).filter(VM.id.in_(vm_ids)).\
                            filter(VM.type.in_([u'xen', u'kvm'])).all()
        elif serverpool:
            ### Server Pool ###
            sp_ent = auth.get_entity_by_name(serverpool, to_unicode(constants.SERVER_POOL))
            if not sp_ent:
                bro_msg += br_str + "Could not find ServerPool1:%s" %(serverpool)
                log_msg = "Could not find ServerPool:%s" %(serverpool)
                LOGGER.info(log_msg)
            else:
                sp = DBSession.query(ServerGroup).filter(ServerGroup.id == sp_ent.entity_id).\
                        filter(ServerGroup.type == None).first()
                if not sp:
                    bro_msg += br_str + "Could not find ServerPool2:%s" %(serverpool)
                    log_msg = "Could not find ServerPool:%s" %(serverpool)
                    LOGGER.info(log_msg)
                else:
                    bro_msg += br_str + "Updating Disks of all Virtual Machines under ServerPool:%s" %(serverpool)
                    log_msg = "Updating Disks of all Virtual Machines under ServerPool:%s" %(serverpool)
                    LOGGER.info(log_msg)
                    bro_msg += br_str + hr_str
                    host_ents = [ent for ent in sp_ent.children]
                    vm_ids = [ent.entity_id for host_ent in host_ents for ent in host_ent.children]
                    ##Only for Generic VMs (xen and kvm)
                    vms = DBSession.query(VM).filter(VM.id.in_(vm_ids)).\
                            filter(VM.type.in_([u'xen', u'kvm'])).all()
        elif datacenter:
            ### Datacenter ###
            bro_msg += br_str + "Updating Disks of all Virtual Machines under Datacenter"
            log_msg = "Updating Disks of all Virtual Machines under Datacenter"
            LOGGER.info(log_msg)
            bro_msg += br_str + hr_str
            ##Only for Generic VMs (xen and kvm)
            vms = DBSession.query(VM).filter(VM.type.in_([u'xen', u'kvm'])).all()


        for vm in vms:
            host = None
            host_ent = None
            vm_ent = auth.get_entity(vm.id)
            if vm_ent.parents:
                host_ent =  vm_ent.parents[0]

            if not host_ent:
                bro_msg += br_str + "Could not find Server entity of Virtual Machine:%s" %(vm.name)
                log_msg = "Could not find Server entity of Virtual Machine:%s" %(vm.name)
                LOGGER.info(log_msg)
                continue
            else:
                host = DBSession.query(ManagedNode).filter(ManagedNode.id == host_ent.entity_id).first()

            if not host:
                bro_msg += br_str + "Could not find Server of Virtual Machine:%s" %(vm.name)
                log_msg = "Could not find Server of Virtual Machine:%s" %(vm.name)
                LOGGER.info(log_msg)
                continue
            else:
                d_config = vm.get_config()
                d_config.set_managed_node(host)
                bro_msg += br_str + "Updating Disks of Virtual Machine:%s" %(vm.name)
                log_msg = "Updating Disks of Virtual Machine:%s" %(vm.name)
                LOGGER.info(log_msg)
                try:
                    self.update_vm_disks(auth, vm.id, host.id, d_config)
                    bro_msg += hr_str
                except Exception, ex:
                    ex_str = to_str(ex).replace("'","")
                    bro_msg += br_str + ex_str
                    log_msg = ex_str
                    LOGGER.info(log_msg)
                    continue
        return bro_msg

    
