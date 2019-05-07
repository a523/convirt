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
# author : ConVirt Team
#
# This module is developed to hold some common functions for storage and network as follows.
#   .Add definition
#   .Remove definition
#   .Update definition
#   .Update node X definition
#   .Add node definition
#   .Add group definition
#   .Sync definition
#   .Sync node X definition
#   .Sync node
#   .Sync all definition on server
#   .Sync all definition in server pool
#   .VM running check
#   .Validation while transferring node
#   .Identify scope of definition
# The functions in this module is called from StorageManager, NwManager, StorageService and  NetworkService.
# The parameter def_manager is the reference of either StorageManager or NwManager class. 
# The reference to the def_manager class is used to invoke any function from StorageManager or NwManager class.

from datetime import datetime
from convirt.core.utils.utils import copyToRemote, get_path, mkdir2
from convirt.core.utils.utils import to_unicode,to_str
import convirt.core.utils.utils
from convirt.core.utils.constants import * #used as in other files
constants = convirt.core.utils.constants
import os, transaction
import fileinput
from tg import session

from convirt.model import DBSession
from convirt.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink, Storage_Stats
from convirt.model.Sites import Site
from convirt.model.Groups import ServerGroup
from convirt.model.ManagedNode import ManagedNode
from convirt.model.Metrics import MetricsCurr
from convirt.model.VM import VM, VMStorageLinks

from sqlalchemy.orm import eagerload

import logging
LOGGER = logging.getLogger("convirt.model")

class SyncDef:
    def __init__(self): pass

    # add a nw definition to a group.
    def add_defn(self, defn, site, group, node, auth, defType, op, action_op, def_manager, grid_manager, op_level, sp_ids=None, scan_result=None):
        #Get definition scope here
        scope = op_level

        #Check privileges
        if scope == constants.SCOPE_S:
            entityId = node.id
        elif scope == constants.SCOPE_SP:
            entityId = group.id
        elif scope == constants.SCOPE_DC:
            entityId = site.id
        
        ent = auth.get_entity(entityId)
        if not auth.has_privilege(action_op, ent):
            raise Exception(constants.NO_PRIVILEGE)

        #Save definition
        DBSession.add(defn)
        #update storage stats and storage disks table with the disks here
        #The change is for following issue.
        #Exception: The transaction is inactive due to a rollback in a subtransaction.  Issue rollback() to cancel the transaction.
        def_manager.SaveScanResult(defn.id, grid_manager, scan_result, site.id)
        #remove scan result from session
        def_manager.RemoveScanResult(scan_result)
        
        errs = []
        details = None
        status = to_unicode(constants.OUT_OF_SYNC)
        
        #Save server and network definition link details
        if scope == constants.SCOPE_DC:               #data center level
            #Add definition to dcdeflinks table since the definition scope is DC.
            #there is no server linked with this definition so the oos_count is zero.
            #since oos_count is zero, we need to keep status as IN_SYNC
            oos_count = 0
            status = to_unicode(constants.IN_SYNC)
            self.add_site_defn(site.id, defn.id, defType, status, oos_count)
            
            #associate definition to selected server pools. 
            def_manager.manage_defn_to_groups(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
        elif scope == constants.SCOPE_SP:               #server pool level
            node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), ent)
            for eachnode in node_entities:
                self.add_node_defn(eachnode.entity_id, defn.id, defType, status, details)
            
            #Add definition to deflinks table only when the definition scope is SP.
            oos_count = len(node_entities)
            status = to_unicode(constants.OUT_OF_SYNC)
            self.add_group_defn(group.id, defn.id, defType, status, oos_count)
        elif scope == constants.SCOPE_S:            
            self.add_node_defn(node.id, defn.id, defType, status, details)
            op = constants.ATTACH
            update_status=True
            errs=[]
            def_manager.sync_node_defn(node, group.id, site.id, defn, defType, op, def_manager, update_status, errs)
            
        #compute storage stats
        def_manager.Recompute(defn)

        if errs:
            if len(errs) > 0:
                LOGGER.error("Error:" + to_str(errs))
        
        return errs

    #would be called while saving node definition on add_defn()
    def add_node_defn(self, node_id, def_id, def_type, status, details):
        #Check whether the record is already present...
        row = DBSession.query(ServerDefLink).filter_by(server_id = node_id, def_id = def_id).first()
        if not row:
            node_defn = ServerDefLink()
            node_defn.server_id = to_unicode(node_id)
            node_defn.def_type = to_unicode(def_type)
            node_defn.def_id = def_id
            node_defn.status = to_unicode(status)
            node_defn.details = to_unicode(details)
            node_defn.dt_time = datetime.utcnow()
            DBSession.add(node_defn)
    
    #would be called while saving group definition on add_defn()
    def add_group_defn(self, group_id, def_id, def_type, status, oos_count):
        #Check whether the record is already present...
        row = DBSession.query(SPDefLink).filter_by(group_id = group_id, def_id = def_id).first()
        if not row:
            SPDL = SPDefLink()
            SPDL.group_id = group_id
            SPDL.def_type = def_type
            SPDL.def_id = def_id
            SPDL.status = status
            SPDL.oos_count = oos_count
            SPDL.dt_time = datetime.utcnow()
            DBSession.add(SPDL)

    #would be called while saving group definition on add_defn()
    def add_site_defn(self, site_id, def_id, def_type, status, oos_count):
        #Check whether the record is already present...
        row = DBSession.query(DCDefLink).filter_by(site_id = site_id, def_id = def_id).first()
        if not row:
            DCDL = DCDefLink()
            DCDL.site_id = site_id
            DCDL.def_type = def_type
            DCDL.def_id = def_id
            DCDL.status = to_unicode(status)
            DCDL.oos_count = oos_count
            DCDL.dt_time = datetime.utcnow()
            DBSession.add(DCDL)

    #would remove the nw definition
    def remove_defn(self, defn, site, group, node, auth, defType, op, action_op, def_manager, grid_manager, add_mode=False, group_list=None, op_level=None):
        scope = op_level
        warning_msg=None
        
        #Check privileges
        if scope == constants.SCOPE_S:
            entityId = node.id
        elif scope == constants.SCOPE_SP:
            entityId = group.id
        elif scope == constants.SCOPE_DC:
            entityId = site.id
        
        ent = auth.get_entity(entityId)
        if not auth.has_privilege(action_op, ent):
            raise Exception(constants.NO_PRIVILEGE)

        #delete the definition logically
        if defn:
            #validation check before going for GET_DISKS
            returnVal = def_manager.is_storage_allocated(defn.id)
            if returnVal==True:
                allocated=False
                if op_level == constants.SCOPE_SP and defn.scope == constants.SCOPE_DC:
                    vm_disks = grid_manager.get_vm_disks_from_pool(auth, group.id)
                    storage_disks = grid_manager.get_storage_disks_from_storage(defn.id)
                    if storage_disks:
                        for each_storage_disk in storage_disks:
                            if allocated==True:
                                break
                            for each_vm_disk in vm_disks:
                                vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=each_vm_disk.id, storage_disk_id=each_storage_disk.id).first()
                                if vm_storage_link:
                                    allocated=True
                                    warning_msg = "All the links associated with the storage (" + to_str(defn.name) + ") would be removed"
                                    break
                else:
                    warning_msg = "The storage (" + to_str(defn.name) + ") and all the links associated with it would be removed"
            
            defn.is_deleted = True
            node_defn = DBSession.query(ServerDefLink).filter_by(def_id=defn.id).first()
            if node_defn:
                node = DBSession.query(ManagedNode).filter_by(id=node_defn.server_id).first()

            site_id=None
            group_id=None

            if node:
                if group:
                    group_id=group.id
                else:
                    entity = auth.get_entity(node.id)
                    if entity:
                        group_id = entity.parents[0].entity_id
                group = DBSession.query(ServerGroup).filter_by(id=group_id).first()

                if group:
                    if site:
                        site_id=site.id
                    else:
                        entity = auth.get_entity(group.id)
                        if entity:
                            site_id = entity.parents[0].entity_id
                    site = DBSession.query(Site).filter_by(id=site_id).first()

                #While adding a new definition, if you get any exception and you need to remove that definition then do not do sync operation. It would be OUT_OF_SYNC by default. So just delete the definition. So that add_mode flag is checked.
                if add_mode == False:
                    #call sync operation
                    if defn.scope == constants.SCOPE_S:    #server level
                        self.sync_node_defn(node, group_id, site_id, defn, defType, op, def_manager)
            
        if op_level == constants.SCOPE_SP and defn.scope == constants.SCOPE_DC:
            self.disassociate_defn(site, group, auth, defn, defType, add_mode, grid_manager)
        else:
            #delete definition
            self.delete_defn(defn, site, group, node, auth, defType, def_manager, grid_manager, add_mode, group_list)
        #Recompute storage state
        def_manager.Recompute(defn)
        return warning_msg
    
    def isVMRunningInPool(self, auth, group_id):
        returnVal = False
        
        #get group entity
        ent =auth.get_entity(group_id)
        
        #get server list
        nodes=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=ent)
        for eachnode in nodes:  #loop through each server
            returnVal = self.isVMRunningOnServer(auth, eachnode.entity_id)
            if returnVal == True:
                break
        return returnVal

    def isVMRunningOnServer(self, auth, node_id):
        returnVal = False
        
        #get server entity
        ent =auth.get_entity(node_id)
        #get VM list. Get a list of VMs on the server
        vmIds = auth.get_entity_ids(constants.DOMAIN, parent=ent)
        for eachvmid in vmIds:
            vm = DBSession.query(VM).filter_by(id=eachvmid).options(eagerload("current_state")).first()
            if vm:
                if vm.current_state.avail_state == VM.RUNNING:
                    returnVal = True
                    LOGGER.info("VM is running on server.")
                    break

        return returnVal

    def delete_defn(self, defn, site, group, node, auth, defType, def_manager, grid_manager, add_mode=False, group_list=None):
        LOGGER.info("Deleting definition...")
        scope = defn.scope
        if defn.is_deleted == True:
            if scope == constants.SCOPE_S:    #server level
                allows_delete = False
                node_defn = DBSession.query(ServerDefLink).filter_by(server_id = node.id, def_id = defn.id, def_type = defType).first()
                if node_defn:
                    if add_mode == True:
                        allows_delete = True
                    else:
                        if node_defn.status == constants.IN_SYNC:
                            allows_delete = True

                    if node_defn.status == constants.OUT_OF_SYNC and add_mode == False:
                        LOGGER.info("Definition " + defn.name + " is OUT_OF_SYNC on the server " + node.hostname)

                    if allows_delete == True:
                        LOGGER.info("Allowing to delete definition...")
                        #delete the defn link with the server from serverdeflinks table
                        DBSession.delete(node_defn)
                        
                        #This function is deleting vm storage links as well as vm_disks related to the storage defn.
                        grid_manager.remove_vm_links_to_storage(defn.id)
                        
                        #delete entry from storage disks table
                        def_manager.remove_storage_disk(defn.id)
                        
                        #delete the definition from network_definitions table
                        DBSession.delete(defn)
            
            elif scope == constants.SCOPE_SP:    #server pool level
                rowGroupDef = DBSession.query(SPDefLink).filter_by(group_id = group.id, def_id = defn.id, def_type = defType).first()
                if rowGroupDef:
                    #delete definition link from SPDefLink table. There would be only one record of the definition since it is server pool level record.
                    group_defn = DBSession.query(SPDefLink).filter_by(group_id = group.id, def_id = defn.id, def_type = defType).first() #call delete here
                    if group_defn:
                        DBSession.delete(group_defn)
        
                    #Go through loop here for each server in the server pool.
                    #delete all the definition links for each server from SPDefLink table
                    for node in group.getNodeList(auth).itervalues():
                        node_defn = DBSession.query(ServerDefLink).filter_by(server_id = node.id, def_id = defn.id, def_type = defType).first() # call delete
                        if node_defn:
                            DBSession.delete(node_defn)

                    #This function is deleting vm storage links as well as vm_disks related to the storage defn.
                    grid_manager.remove_vm_links_to_storage(defn.id)

                    #This function is deleting vm storage links as well as vm_disks related to the storage defn.
                    def_manager.remove_storage_disk(defn.id)
                    
                    #delete the definition from storag/ network definitions table
                    DBSession.delete(defn)

            elif scope == constants.SCOPE_DC:    #data center level
                #rowGroupDef = DBSession.query(DCDefLink).filter_by(site_id=site.id, def_id = defn.id, def_type = defType).first()
                #if rowGroupDef:
                    for group in group_list:
                        #delete definition link from DCDefLink table. There would be only one record of the definition since it is data center level record.
                        site_defn = DBSession.query(DCDefLink).filter_by(site_id=site.id, def_id = defn.id, def_type = defType).first()
                        if site_defn:
                            DBSession.delete(site_defn)

                        #delete definition link from SPDefLink table. There would be only one record of the definition since it is server pool level record.
                        group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id = defn.id, def_type = defType).first()
                        if group_defn:
                            DBSession.delete(group_defn)

                        #Go through loop here for each server in the server pool.
                        #delete all the definition links for each server from SPDefLink table
                        for node in group.getNodeList(auth).itervalues():
                            node_defn = DBSession.query(ServerDefLink).filter_by(server_id = node.id, def_id = defn.id, def_type = defType).first()
                            if node_defn:
                                DBSession.delete(node_defn)

                    #This function is deleting vm storage links as well as vm_disks related to the storage defn.
                    grid_manager.remove_vm_links_to_storage(defn.id)

                    #delete entry from storage disks table
                    def_manager.remove_storage_disk(defn.id)
                    
                    #delete records from storage_stats table
                    DBSession.query(Storage_Stats).filter_by(storage_id = defn.id).delete()
                    
                    #delete the definition from storage/ network definitions table when there should not be any link in deflinks and serverdeflinks table so we are checking as follow since this is data center level definition.
                    group_defn = DBSession.query(DCDefLink).filter_by(site_id=site.id, def_id = defn.id, def_type = defType).first()
                    if not group_defn:
                        node_defn = DBSession.query(ServerDefLink).filter_by(def_id = defn.id, def_type = defType).first()
                        if not node_defn:
                            DBSession.delete(defn)
                    transaction.commit()
                    
    def disassociate_defn(self, site, group, auth, defn, defType, add_mode, grid_manager):
            LOGGER.info("Disassociating definition...")
            #Go through loop here for each server in the server pool.
            #delete all the definition links for each server from SPDefLink table
            for node in group.getNodeList(auth).itervalues():
                if node:
                    node_defn = DBSession.query(ServerDefLink).filter_by(server_id = node.id, def_id = defn.id, def_type = defType).first()
                    if node_defn:
                        DBSession.delete(node_defn)

            #delete definition link from SPDefLink table. There would be only one record of the definition since it is server pool level record.
            group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id = defn.id, def_type = defType).first()
            if group_defn:
                DBSession.delete(group_defn)
            #This function is deleting vm storage links as well as vm_disks related to the storage defn.
            vm_id_list=[]
            for node in group.getNodeList(auth).itervalues():
                if node:
                    for vm in grid_manager.get_node_doms(auth, node.id):
                        if vm:
                            vm_id_list.append(vm.id)
                        
            grid_manager.remove_vm_links_to_storage(defn.id, vm_id_list)
            transaction.commit()

    def props_to_cmd_param(self, props):
        cp = ""
        if props:
            for p,v in props.iteritems():
                if v :
                    if cp:
                        cp += "|"
                    cp += "%s=%s" % (p,v)
            cp = "'%s'" % (cp, )
        return cp

    #this would be called while syncing definition. Would update status/oos_count in database.
    def update_node_defn(self, node_id, group_id, site_id, def_id, def_type, status, dt_time, details, scope, defType):
        #update definition status in ServerDefLink table
        node_defn = DBSession.query(ServerDefLink).filter_by(server_id = node_id, def_id = def_id).first()
        if node_defn:
            node_defn.status = status
            node_defn.dt_time = datetime.utcnow()
            node_defn.details = details

        oos_count = 0 # out of sync count
        g_status = to_unicode(constants.IN_SYNC)
    
        #Here we are finding that how many servers are OUT_OF_SYNC with this definition. So getting out of sync count and decide group level sync status to update SPDefLink table with these values.
        rowNodeDefn = DBSession.query(ServerDefLink).filter_by(def_id = def_id, def_type = to_unicode(defType), status = to_unicode(constants.OUT_OF_SYNC))
        if rowNodeDefn:
            oos_count = rowNodeDefn.count()
    
        #Get the status for updating SPDefLink table
        if oos_count > 0:
            g_status = to_unicode(constants.OUT_OF_SYNC)
        else:
            g_status = to_unicode(constants.IN_SYNC)

        #update definition status and oos_count in SPDefLink table
        group_sd=None
        if scope == constants.SCOPE_SP:
            group_sd = DBSession.query(SPDefLink).filter_by(group_id = group_id, def_id = def_id, def_type = to_unicode(defType)).first()
        elif scope == constants.SCOPE_DC:
            group_sd = DBSession.query(DCDefLink).filter_by(site_id = site_id, def_id = def_id, def_type = to_unicode(defType)).first()

        if group_sd:
            group_sd.status = g_status
            group_sd.dt_time = datetime.utcnow()
            group_sd.oos_count = oos_count
            #Keep a note here saying that commit would have to be called here.
            DBSession.flush()
            transaction.commit()
    
    def update_defn(self, defn, new_name, new_desc, site, group, auth, defType, op, def_manager, action_op, op_level=None, sp_ids=None, grid_manager=None):
        #Check privileges
        if group and auth:
            ent = auth.get_entity(group.id)
            if not auth.has_privilege(action_op, ent):
                raise Exception(constants.NO_PRIVILEGE)

        defn.name = new_name
        defn.description = new_desc
    
        #disassociate definition to selected server pool
        errs=[]
        if op_level == constants.SCOPE_DC:
            def_manager.manage_defn_to_groups(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
            
        #recompute storage stats
        def_manager.Recompute(defn)

    def validate_transfer_node(self, nodeId, sourceGroupId, auth):
        vm_running = False
        def_present = False
        
        #check whether definitions exist.
        node_defn = DBSession.query(ServerDefLink).filter_by(server_id = nodeId).first()
        if node_defn:
            def_present = True
            LOGGER.info("Storage/ Network are present on server.")

        #check whether VMs are running.
        vm_running = self.isVMRunningOnServer(auth, nodeId)
        
        if def_present == True and vm_running == True:
            raise Exception("VM_RUNNING")
    
    # return list of definitions in the group
    def get_node_defns(self, def_id, defType):
        defns=[]
        node_defns = DBSession.query(ServerDefLink).filter_by(def_id = def_id, def_type = to_unicode(defType))
        if node_defns:
            for eachdefn in node_defns:
                defns.append(eachdefn)
        return defns

    # return list of definitions associated to the server
    def get_server_defns(self, server_id, defType):
        defns=[]
        defns = DBSession.query(ServerDefLink.def_id).\
                filter_by(server_id = server_id, def_type = defType).all()        
        return defns

    #would be called on adding server node event
    def on_add_node(self, nodeId, groupId, site_id, auth, def_manager):
        op = constants.ATTACH
        
        #If one of them is not present then return from here.
        if not (nodeId or groupId):
            return
        
        defn_list = []
        errs = []
        sync_manager = SyncDef()
        defType = def_manager.getType()
        
        #Link all the definitions in the server pool to this new server node.
        sp_defns = DBSession.query(SPDefLink).filter_by(group_id=to_unicode(groupId))
        if sp_defns:
            for eachdefn in sp_defns:
                defn = def_manager.get_defn(eachdefn.def_id)
                if defn:
                    defn_list.append(defn)

                    #Add these default value to this link definition. These values would get changed after sync operation.
                    status = to_unicode(constants.OUT_OF_SYNC)
                    details = None
                    sync_manager.add_node_defn(nodeId, defn.id, defType, status, details)

    #would be called on removing server node event
    def on_remove_node(self, nodeId, groupId, site_id, auth, def_manager, isTransfer=False):
        op = constants.DETACH
        #If one of them is not present then return from here.
        if not groupId:
            return
        
        defType = def_manager.getType()
        node = DBSession.query(ManagedNode).filter_by(id = nodeId).first()
        
        if node:
            #Get all the definitions linked with this server
            defn_list=[]
            node_defns = DBSession.query(ServerDefLink).filter_by(server_id=nodeId, def_type=defType)
            if node_defns:
                for eachdefn in node_defns:
                    defn = def_manager.get_defn(eachdefn.def_id)
                    if defn:
                        defn_list.append(defn)

            #delete all definition links with this server from serverdeflinks table
            if node_defns:
                for eachdefn in node_defns:
                    defn = def_manager.get_defn(eachdefn.def_id)
                    if defn:
                        #While transferring the server do not delete server definition link.
                        #while deleting node, delete all links with this server.
                        if defn.scope != constants.SCOPE_S: #and isTransfer==False:
                            #Log the error if the definition status is out of sync. But go ahead with deleting the definition link with the server.
                            if eachdefn.status == constants.OUT_OF_SYNC:
                                LOGGER.error("WARNING: The definition status is OUT_OF_SYNC. Still the definition linking with the server is getting deleted. server_id=" + node.id + ", def_id=" + eachdefn.def_id + ", def_type=" + eachdefn.def_type + ", details=" + to_str(eachdefn.details))
                            
                            DBSession.delete(eachdefn)
                        
                        #While transferring the server, do not delete definition.
                        #While deleting node, delete only server level definition.
                        if defn.scope == constants.SCOPE_S and isTransfer==False:
                            DBSession.delete(defn)

    #would be called on add server pool event
    def on_add_group(self, groupId):
        pass

    #would be called on remove server pool event
    def on_remove_group(self, site_id, groupId, auth, def_manager):
        op = constants.DETACH
        
        defType = def_manager.getType()
        site = DBSession.query(Site).filter_by(id=site_id).first()
        group = DBSession.query(ServerGroup).filter_by(id = groupId).first()
        
        defn_list=[]
        #get all the definitions from the group
        #getting pool level definitions here
        sp_defns = DBSession.query(SPDefLink).filter_by(group_id=groupId)
        if sp_defns:
            for eachdefn in sp_defns:
                defn = def_manager.get_defn(eachdefn.def_id)
                if defn:
                    defn_list.append(defn)

        for each_defn in defn_list:
            group_defn = DBSession.query(SPDefLink).filter_by(def_id = each_defn.id, def_type = defType).first()
            if group_defn:
                DBSession.delete(group_defn)

            #delete only those definitions which are having scope server pool.
            #data center level definitions can not be deleted since we are removing server pool only.
            if each_defn.scope == constants.SCOPE_SP:
                DBSession.delete(each_defn)

    #would get call on moving server node from one pool to another pool
    def on_transfer_node(self, nodeId, sourceGroupId, destGroupId, site_id, auth, def_manager):
        #here True is for isTransfer parameter
        self.on_remove_node(nodeId, sourceGroupId, site_id, auth, def_manager,True)
        self.on_add_node(nodeId, destGroupId, site_id, auth, def_manager)

    # Sync the nw definition with the node
    # return code, output, structured output
    # op = REMOVE  : Remove the definition.
    #
    # op = SYNC : Add/Update/Remove a requested network
    #
    #This function does not require auth since it is just syncing node against definition.This function already got node and definition from its parent function which is using auth.
    def sync_node_defn(self, node, group_id, site_id, defn, defType, op, def_manager=None, update_status=True, errs=None, processor=None):
        scope = defn.scope
        dt_time = datetime.utcnow()

        if not errs:
            errs = []
        
        #check for right operator
        errs = def_manager.CheckOp(op, errs)

        try:
            (exit_code, output) = def_manager.exec_script(node, group_id, defn, defType, op)
        except Exception, ex:
            exit_code = 222
            output = to_str(ex)
        
        if exit_code:
            status = to_unicode(constants.OUT_OF_SYNC)
        else:
            status = to_unicode(constants.IN_SYNC)
        LOGGER.info("Status= " + to_str(status))

        if not exit_code:
            if not output:
                output = def_manager.getSyncMessage(op)
        
        details = output
        
        if update_status == True:
            self.update_node_defn(node.id,
                                group_id,
                                site_id,
                                defn.id,
                                defn.type,
                                status,
                                dt_time,
                                details,
                                scope,
                                defType)

        if op == constants.GET_DISKS:
            # lets process the output in to corresponding
            # details structure
            result = {}
            result["type"] = defn.type
            result["id"] = defn.id
            result["op"] = op
            result["name"] = defn.name
            
            # some more common things here
            if processor:
                if exit_code:
                    errs.append("Error: %s, %s, %s" % (defn.name, node.hostname, to_str(output)))
                    raise Exception(output)

                processor(op,output, result)
                LOGGER.info("Result of Processor= " + to_str(result))
                return result
            else:
                errs.append("Can not process output. %s" % op)
                raise Exception("Can not process output. %s" % op )

        if exit_code:
            errs.append("Error: %s, %s, %s" % (defn.name, node.hostname, to_str(output)))
            raise Exception(output)
        else:
            return { "output" :output,
                    "exit_code" : exit_code }
