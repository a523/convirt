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

# Manages shared storage definitions
# Each storage definition represents the shared storage as seen from the
# clients perspective.
# In future this would be enhanced to
# a. model the server view as well
# b. Separate SharedServer entity to which each of the storage definition
#    would belong

#from sqlalchemy import create_engine
from sqlalchemy import func, outerjoin, join
from datetime import datetime
from convirt.core.utils.utils import copyToRemote, getHexID, mkdir2
from convirt.core.utils.utils import to_unicode,to_str, p_timing_start, p_timing_end
import convirt.core.utils.utils
from convirt.core.utils.constants import *
constants = convirt.core.utils.constants
import os, tg, transaction
import pprint
from tg import session

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.schema import UniqueConstraint,Index
from sqlalchemy.orm import relation, backref

#Import for Storage and Network classes
from convirt.model import DeclarativeBase, DBSession
from convirt.model.ManagedNode import ManagedNode
from convirt.model.Groups import ServerGroup
from convirt.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink, StorageDisks, Storage_Stats, Upgrade_Data
from convirt.model.VM import VMDisks, VMStorageLinks, VM
from convirt.model.Entity import Entity, EntityRelation
from convirt.model.Sites import Site
from convirt.core.utils.utils import dynamic_map
from convirt.model.Authorization import AuthorizationService

from convirt.model.SyncDefinition import SyncDef

import logging
LOGGER = logging.getLogger("convirt.model")
STRG_LOGGER = logging.getLogger("STORAGE_TIMING")

class StorageDef(DeclarativeBase):
    __tablename__ = 'storage_definitions'

    #Columns
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(100), nullable=False)
    type = Column(Unicode(50), nullable=False)
    description = Column(Unicode(250))
    connection_props = Column(PickleType)
    creds_required = Column(Boolean)
    creds = Column(PickleType)
    is_deleted = Column(Boolean)
    scope = Column(String(2))

    def __init__(self, id, name, type, description,
                connection_props, scope, creds_required = False, is_deleted = False, status = None):  

        self.id = id
        if self.id is None:
            self.id = getHexID()
        
        self.name = name
        self.type = type
        self.description = description

        self.connection_props = connection_props
        self.creds_required = creds_required
        self.creds = {}
        self.total_size = 0
        self.is_deleted = is_deleted
        self.status = status
        self.scope = scope
        
    def sanitized_creds(self):
        if self.creds and self.creds.get("password"):
            new_creds = self.creds.copy()
            new_creds["password"] = None
            return new_creds
        return self.creds

    def __repr__(self):
        return to_str({"id":self.id,
                    "type":self.type,
                    "name":self.name,
                    "description":self.description,
                    "connection_props" : self.connection_props,
                    "creds_required":self.creds_required,
                    "creds" : self.sanitized_creds()
                    })

    def get_connection_props(self):
        return self.connection_props

    def set_connection_props(self, cp):
        self.connetion_props = cp

    def get_creds(self):
        return self.creds

    def get_creds(self):
        return self.creds
    
    def set_creds(self, creds):
        self.creds = creds

    def get_stats(self):
        ss=None
        dc_def = DBSession.query(DCDefLink).filter_by(def_id=self.id).first()
        if dc_def:
            ss = DBSession.query(Storage_Stats).filter_by(entity_id=dc_def.site_id, storage_id=self.id).first()
        return ss

    def set_status(self, status):
        self.status = status

Index("strgedef_id", StorageDef.id)

class StorageManager:
    s_scripts_location = "/var/cache/convirt/storage"
    FILE_BASED_STORAGE = [constants.NFS]
    STORAGE_FOR_CREATION = []
    STORAGE_FOR_REMOVAL = []
    
    def __init__(self):
        self.storage_processors = { constants.NFS : self.nfs_processor,
                                    constants.iSCSI : self.iscsi_processor,
                                    constants.AOE : self.aoe_processor
                                    }
        #reinitialize here so that it will not get reappended each time when it is initialized.
        self.STORAGE_FOR_CREATION = []
        self.STORAGE_FOR_CREATION = self.get_storage_for_creation_list(self.FILE_BASED_STORAGE)
        self.STORAGE_FOR_REMOVAL = []
        self.STORAGE_FOR_REMOVAL = self.get_storage_for_removal_list(self.FILE_BASED_STORAGE)

    def get_storage_for_creation_list(self, storage_type_list):
        temp_list = []
        temp_list.extend(storage_type_list)
        return temp_list

    def get_storage_for_removal_list(self, storage_type_list):
        temp_list = []
        temp_list.extend(storage_type_list)
        return temp_list

    def getType(self):
        return to_unicode(constants.STORAGE)

    # return the storage definitions for a given group    
    def getSiteDefListToAssociate(self, site_id, group_id, defType):
        sdArray=[]
        if site_id:
            dc_rs = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=defType)
            if dc_rs:
                for row in dc_rs:
                    sp_def = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=row.def_id, def_type=defType).first()
                    if not sp_def:
                        defn = DBSession.query(StorageDef).filter_by(id=row.def_id, scope=constants.SCOPE_DC).first()
                        if defn:
                            defn.status = row.status
                            sdArray.append(defn)
        return sdArray

    # return the storage definitions for a given group    
    def get_sds(self, site_id, group_id):
        if group_id:
            rs = DBSession.query(SPDefLink).filter_by(group_id=group_id)
        elif site_id:
            rs = DBSession.query(DCDefLink).filter_by(site_id=site_id)

        sdArray=[]
        for row in rs:
            row_nw = DBSession.query(StorageDef).filter_by(id=row.def_id).first()
            if row_nw:
                sdArray.append(row_nw)
        return sdArray

    # return list of definition ids in the group
    def get_sd_ids(self, site_id, group_id, defType, scope):
        ids_array=[]
        def_ids=None
        if scope == constants.SCOPE_SP or scope == constants.SCOPE_S:
            def_ids = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_type = to_unicode(defType))
        elif scope == constants.SCOPE_DC:
            def_ids = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type = to_unicode(defType))
        
        if def_ids:
            for row in def_ids:
                ids_array.append(row.def_id)

        return ids_array

    #It return storage definitions
    def get_sd(self, sd_id, site_id, group_id, defType):
        status = None
        rsSD = DBSession.query(StorageDef).filter_by(id=sd_id).first()
        if rsSD:
            if rsSD.scope == constants.SCOPE_SP:
                group_defn = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_type=to_unicode(defType), def_id=sd_id).first()
            elif rsSD.scope == constants.SCOPE_DC:
                group_defn = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=to_unicode(defType), def_id=sd_id).first()
                
            if group_defn:
                status = group_defn.status    # getting definition status (IN_SYNC/ OUT_OF_SYNC) to display in grid on UI 

            rsSD.status = status
        return rsSD

    def get_defn(self, id):
        defn = DBSession.query(StorageDef).filter_by(id=id).first()
        return defn

    # execute the GET_DISK on the give node and return the results
    def get_sd_details(self, auth, sd, node, group, site, defType, def_manager):
        details = None
        groupId = None
        existing_def = None
        
        if group:
            groupId = group.id
        else:
            entity = auth.get_entity(node.id)
            if entity:
                groupId = entity.parents[0].entity_id

        sync_manager = SyncDef()
        try:
            #Get sync the definition and get disk details
            result_processor = self.storage_processors[sd.type]
            errs=[]
            op=constants.GET_DISKS
            update_status = False
            details = sync_manager.sync_node_defn(node,groupId, site.id, sd, to_unicode(defType), op, def_manager, update_status, errs, processor=result_processor)
        except Exception, ex:
            #mount point validation
            existing_def=self.isDefnExists(sd, node)
            #if there is a existing mount point then do not ATTACH it again.
            if existing_def:
                LOGGER.info("Definition already exists. This definition matches with the existing definition " + existing_def.name + " on the server " + node.hostname)
            
            #ATTACH here
            op = constants.ATTACH
            sync_manager.sync_node_defn(node,groupId, site.id, sd, defType, op, def_manager)
            
            #Get sync the definition and get disk details
            result_processor = self.storage_processors[sd.type]
            errs=[]
            op=constants.GET_DISKS
            update_status = False
            details = sync_manager.sync_node_defn(node,groupId, site.id, sd, defType, op, def_manager, update_status, errs, processor=result_processor)
            
            #DETACH here
            #if it is a existing mount point then do not DETACH it.
            if not existing_def:
                op = constants.DETACH
                sync_manager.sync_node_defn(node,groupId, site.id, sd, defType, op, def_manager)

        return details
        
    def parse_diskdetails(self,output, result):
        disk_details = []
        if output:
            for i in output.splitlines():            
                d={}
                if not i:
                    continue
                i = i.strip()
                if i.find("DISK_DETAILS") !=0:
                    continue
                for j in i.split('|'):
                    nameAndValue = j.lstrip().split('=')                
                    d[nameAndValue[0]]= nameAndValue[1]
                del d['DISK_DETAILS']
                disk_details.append(d)
        return disk_details

    def parse_output(self,output, result):
        Lista = []
        if output:
            for i in output.splitlines():
                d={}
                if not i:
                    continue
                i = i.strip()
            
                if i.find("OUTPUT") !=0:
                    continue
                for j in i.split('|'):
                    nameAndValue = j.lstrip().split('=')
                    d[nameAndValue[0]]= nameAndValue[1]
                del d['OUTPUT']
                Lista.append(d)
        return Lista

    def parse_summary(self,output, result):
        if output:
            for i in output.splitlines():
                d={}
                if not i:
                    continue
                i = i.strip()
            
                if i.find("SUMMARY") !=0:
                    continue
                for j in i.split('|'):
                    nameAndValue = j.lstrip().split('=')
                    d[nameAndValue[0]]= nameAndValue[1]
                del d['SUMMARY']
                return d
        return None

    # storage processor
    def nfs_processor(self, op, output, result):
        LOGGER.debug("nfs processor called with \n"+ str(output))
        if op == "GET_DISKS_SUMMARY":
            result["SUMMARY"] = self.parse_summary(output,result)
        else:
            result["STORAGE_DETAILS"] = self.parse_output(output,result)
            result["DETAILS"] = self.parse_diskdetails(output,result)
            result["SUMMARY"] = self.parse_summary(output,result)
            
    def iscsi_processor(self, op, output, result):
        LOGGER.debug("iscsi processor called with \n"+ str(output))
        if op == "GET_DISKS_SUMMARY":
            result["SUMMARY"] = self.parse_summary(output,result)
        else:
            result["STORAGE_DETAILS"] = self.parse_output(output,result)
            result["DETAILS"] = self.parse_output(output,result)
            result["SUMMARY"] = self.parse_summary(output,result)


    def aoe_processor(self, op, output, result):
        LOGGER.debug("aoe processor called with \n" + str(output))
        if op == "GET_DISKS_SUMMARY":
            result["SUMMARY"] = self.parse_summary(output,result)
        else:
           result["STORAGE_DETAILS"] = self.parse_output(output,result)
           result["DETAILS"] = self.parse_output(output,result)
           result["SUMMARY"] = self.parse_summary(output,result)

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

    def prepare_scripts(self, dest_node, type, defType):
        s_src_scripts_location=tg.config.get("storage_script")
        s_src_scripts_location=os.path.abspath(s_src_scripts_location)

        LOGGER.info("Source script location= " + to_str(s_src_scripts_location))
        LOGGER.info("Destination script location= " + to_str(self.s_scripts_location))
        copyToRemote(s_src_scripts_location, dest_node, self.s_scripts_location)
        
        common_function_script_name = os.path.join(s_src_scripts_location,"storage_functions")
        LOGGER.info("Common source script location= " + to_str(common_function_script_name))
        
        dest_location = os.path.join(self.s_scripts_location,"scripts")
        LOGGER.info("Common destination script location= " + to_str(dest_location))
        
        copyToRemote(common_function_script_name, dest_node, dest_location, "storage_functions")

    def exec_script(self, node, group, defn, defType, op=constants.GET_DETAILS):
        type = defn.type

        self.prepare_scripts(node, type, defType)
        
        script_name = os.path.join(self.s_scripts_location,"scripts",
                                type, "storage.sh")
        
        log_dir = node.config.get(prop_log_dir)
        
        if log_dir is None or log_dir == '':
            log_dir = DEFAULT_LOG_DIR

        log_filename = os.path.join(log_dir, "storage/scripts",
                                    type, "storage_sh.log")
        
        # create the directory for log files
        mkdir2(node,os.path.dirname(log_filename))
        
        if type == constants.NFS:
            mount_point = defn.connection_props.get("mount_point")
            
            # create the directory for mount point for NFS mounting
            if mount_point.startswith("/") == True:
                mkdir2(node, mount_point)
        
        cp = self.props_to_cmd_param(defn.connection_props)
        
        creds_str = self.props_to_cmd_param(defn.creds)
        
        password = defn.creds.get("password")
        
        # help script find its location
        script_loc = os.path.join(self.s_scripts_location,"scripts")
        
        file_filter = "*.disk.xm"
        
        if type:
            script_args = " -t " + type
        if cp:
            script_args += " -c " + cp
        if creds_str:
            script_args += " -p " + creds_str
        if op:
            script_args += " -o " + op
        if script_loc:
            script_args += " -s " + script_loc
        if log_filename:
            script_args += " -l " + log_filename
        if file_filter:
            script_args += " -w " + file_filter
            
        
        cmd = script_name +  script_args
        #show password in *****
        cmd_temp = cmd.replace("password=" + to_str(password), "password=*****")
        LOGGER.info("Command= " + to_str(cmd_temp))

        # execute the script
        output = "Success"
        exit_code = 0
        (output, exit_code) = node.node_proxy.exec_cmd(cmd)            

        LOGGER.info("Exit Code= " + to_str(exit_code))
        LOGGER.info("Output of script= " + to_str(output))
        return (exit_code, output)

    def CheckOp(self, op, errs):
        if not (op in [constants.GET_DISKS, constants.GET_DISKS_SUMMARY, constants.ATTACH, constants.DETACH]):
            errs.append("Invalid storage defn sync op " + op) 
            raise Exception("Invalid storage defn sync op " + op )
        return errs

    # This function checks whether there is a duplicate entry in the database for definition
    #Name the function
    def isDefnExists(self, defn, node):
        returnVal=None

        #get new def parameters
        con_props_new = defn.connection_props
        server_new = con_props_new.get("server")
        share_new = con_props_new.get("share")
        mount_point_new = con_props_new.get("mount_point")
        target_new = con_props_new.get("target")

        node_defns = DBSession.query(ServerDefLink).filter_by(server_id=node.id)
        for eachdefn in node_defns:
            sd = DBSession.query(StorageDef).filter_by(id=eachdefn.def_id).first()
            if sd:
                #get existing def parameters
                con_props = sd.connection_props
                server = con_props.get("server")
                share = con_props.get("share")
                local_server = node.hostname
                mount_point = con_props.get("mount_point")
                target = con_props.get("target")

                #checking duplicate here
                if defn.type == constants.NFS and server == server_new and share == share_new and mount_point == mount_point_new:
                    returnVal=sd
                elif defn.type == constants.iSCSI and server == server_new and target == target_new:
                    returnVal=sd
        return returnVal

    def getSyncMessage(self, op):
        messasge=None
        if op == constants.ATTACH:
            messasge="Mount operation is done successfully."
        elif op == constants.DETACH:
            messasge="Unmount operation is done successfully."
        return messasge
    
    def sync_node_defn(self, node, group_id, site_id, defn, defType, op, def_manager=None, update_status=True, errs=None, processor=None):
        pass

    def manage_storage_disk(self, storage_id, grid_manager, scan_result, site_id):
        LOGGER.info("Managing storage disks...")
        defn = self.get_defn(storage_id)
        if defn:
            total_size=0
            used_size=0
            available_size=0
            if scan_result:
                objStorage_details = scan_result.get("STORAGE_DETAILS")
                objStorage_details = objStorage_details[0]
                objSummary = scan_result.get("SUMMARY")
                objStats_details = scan_result.get("DETAILS")
        
                #store storage total_size, storage used_size and storage available_size in storage_stats table
                #Note: In case of iscsi, you won't get used_size and available_size.
                ss_new_rec = False
                ss = DBSession.query(Storage_Stats).filter_by(entity_id=site_id, storage_id=storage_id).first()
                if not ss:
                    ss_new_rec = True
                    ss = Storage_Stats()
                    #This is missing change in nfs issue (zero size issue). This fix is for following error.
                    #Exception: The transaction is inactive due to a rollback in a subtransaction.  Issue rollback() to cancel the transaction.
                    ss.id = getHexID()
                    ss.entity_id = site_id
                    ss.storage_id = storage_id
                    
                if objSummary:
                    total_size = objSummary.get("TOTAL")
                if objStorage_details:
                    used_size = objStorage_details.get("USED")
                    available_size = objStorage_details.get("AVAILABLE")

                ss.total_size = total_size
                ss.used_size = used_size
                ss.available_size = available_size
                if ss_new_rec:
                    DBSession.add(ss)
                LOGGER.info("Storage stat is updated")
                    
                #store data in storage_disks table for each disk.
                if objStats_details:
                    for eachdetail in objStats_details:
                        actual_size = eachdetail.get("SIZE")
                        used_size = eachdetail.get("USED")
                        unique_path = eachdetail.get("uuid")
                        current_portal = eachdetail.get("CurrentPortal")
                        target = eachdetail.get("Target")
                        state = eachdetail.get("State")
                        lun = eachdetail.get("Lun")
                        
                        #decide here to add or update the disk record
                        storage_disk = DBSession.query(StorageDisks).filter_by(storage_id=storage_id, unique_path=unique_path).first()
                        if storage_disk:
                            #update record
                            if not used_size:
                                used_size=0
                            if used_size==0:
                                used_size=actual_size
                            storage_disk.size = float(used_size)
                            storage_disk.actual_size = float(actual_size)
                            storage_disk.state = state
                            storage_disk.lun = lun
                        else:
                            #add new record
                            storage_allocated = False
                            self.add_storage_disk(storage_id, actual_size, used_size, unique_path, current_portal, target, state, lun, storage_allocated, grid_manager)
                        
                        #delete record
                        #compare the stats object with database records and decide which disk is not in the stats
                        #object. Consider that disk is physically deleted. So remove the entry for database.
                        all_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
                        if all_disks:
                            for each_disk in all_disks:
                                disk_found=False
                                #Assume that entry does not have any unique_path would not be a disk.
                                #Delete nfs container entry here.
                                if not str(each_disk.unique_path).strip():
                                    DBSession.delete(each_disk)
                                    continue
                                    
                                for each_stat in objStats_details:
                                    if str(each_stat.get("uuid")).strip() == str(each_disk.unique_path).strip():
                                        disk_found=True
                                
                                #This disk is deleted
                                if disk_found==False:
                                    vm_storage_link = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=each_disk.id).first()
                                    if vm_storage_link:
                                        LOGGER.info("The storage disk (" + each_disk.disk_name + ") is in use so that it can not be deleted.")
                                    else:
                                        DBSession.delete(each_disk)
                    
                #recalculate storage stats
                self.Recompute(defn)
                        
    def is_storage_allocated(self, storage_id):
        returnVal=False
        if storage_id:
            disk = DBSession.query(StorageDisks).filter_by(storage_id=storage_id, storage_allocated=True).first()
            if disk:
                LOGGER.info("Storage (" + str(disk.disk_name) + ") is in use.")
                returnVal=True
        return returnVal
    
    def remove_storage_disk(self, storage_id):
        if storage_id:
            disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
            for eachdisk in disks:
                DBSession.delete(eachdisk)

    def remove_storage_disks(self, vm_id):
        LOGGER.info("Removing storage disks...")
        vm_config = None
        vm = DBSession.query(VM).filter_by(id=vm_id).first()
        if vm:
            vm_config = vm.get_config()
            for file in vm_config.getDisks():
                filename = file.filename
                #if there are any duplicate entry present for the disk then it should also get deleted. So here we are fetching record list.
                disks = DBSession.query(StorageDisks).filter_by(unique_path=filename)
                for eachdisk in disks:
                    #only remove those storage which are present in the list STORAGE_FOR_REMOVAL.
                    if eachdisk.storage_type in StorageManager().STORAGE_FOR_REMOVAL:
                        DBSession.delete(eachdisk)
                        LOGGER.info("Storage disk " + to_str(eachdisk.unique_path) + " is removed.")

    def manage_defn_to_groups(self, site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager):
        #This function will work for association as well as disassociation of a definition to the server pool.
        result={}
        if group:
            result = self.manage_defn_to_group(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
        else:
            if site:
                site_entity = auth.get_entity(site.id)
                #get all groups in the site.
                group_entities = auth.get_entities(to_unicode(constants.SERVER_POOL), site_entity)
            
                #loop through each group in the site
                for eachgroup in group_entities:
                    group = DBSession.query(ServerGroup).filter_by(id=eachgroup.entity_id).first()
                    result = self.manage_defn_to_group(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
            else:
                LOGGER.error("Error: Site is None")
        return result

    def manage_defn_to_group(self, site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager):
        #This function will work for association as well as disassociation of a definition to the server pool.
        try:
            sync_manager = SyncDef()
            
            #check definition whether it is already associated with the pool or not.
            associated = self.is_associated_to_group(group, defn)
            
            #check this group whether it is marked for association or not.
            marked_for_association = self.is_present_in_list(group.id, sp_ids)
            
            #Associate here
            if associated == False and marked_for_association == True:
                details = None
                status = constants.OUT_OF_SYNC

                group_entity = auth.get_entity(group.id)
                #get all nodes in the group
                node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), group_entity)
                
                #loop through each node in the group
                for eachnode in node_entities:
                    sync_manager.add_node_defn(eachnode.entity_id, defn.id, defType, status, details)
                
                oos_count = len(node_entities)
                status = constants.OUT_OF_SYNC
                #Add definition to spdeflinks table.
                sync_manager.add_group_defn(group.id, defn.id, defType, status, oos_count)
                
                #matching disks on association of storage.
                vm_disks = grid_manager.get_vm_disks_from_pool(auth, group.id)
                storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=defn.id)
                if storage_disks:
                    for eachdisk in storage_disks:
                        #self.manager.matching_disk_on_discover_storage(eachdisk.id)
                        grid_manager.matching_disk_on_discover_storage(vm_disks, eachdisk.id)
                    
            #Disassociate here
            if associated == True and marked_for_association == False:
                add_mode=False
                #disassociate definition from the group.
                sync_manager.disassociate_defn(site, group, auth, defn, defType, add_mode, grid_manager)
        except Exception, ex:
            LOGGER.error(to_str(ex).replace("'",""))
            raise Exception(ex)
            return dict(success=False, msg=to_str(ex).replace("'",""))
        return dict(success=True, msg='Storage Associated')
                        
    def is_present_in_list(self, str_id, str_ids):
        #check whether the id (str_id) is present in the id list (str_ids) or not and return true/false.
        returnVal=False
        if str_ids!= None:
            id_list = str_ids.split(",")
            for eachid in id_list:
                if to_str(eachid) == to_str(str_id):
                    returnVal=True
                    return returnVal
        return returnVal

    def is_associated_to_group(self, group, defn):
        #check whether the definition is associated to the group or not and return true/false.
        returnVal=False
        group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id=defn.id).first()
        if group_defn:
            returnVal=True
        return returnVal

    def calculate_disk_size(self, storage_disk_id, vm_disk_id, disk_size, op):
        vm_disk=None
        if not disk_size:
            disk_size=0
        
        if vm_disk_id:
            vm_disk = DBSession.query(VMDisks).filter_by(id=vm_disk_id).first()
            if vm_disk:
                vm_disk.size = self.convert_to_GB(disk_size)
        
        if storage_disk_id:
            storage_disk = DBSession.query(StorageDisks).filter_by(id=storage_disk_id).first()
            if storage_disk:
                storage_allocated = storage_disk.storage_allocated
                if op == "+":
                    #storage is unavailable now
                    if vm_disk:
                        if vm_disk.read_write == "w":
                            storage_allocated = True
                elif op == "-":
                    #Make it available only when the vm disk which is getting removed should be having mode read_write (w).
                    #storage is available for use now
                    if vm_disk:
                        if vm_disk.read_write == "w":
                            storage_allocated = False
                
                #storage availability is updated
                storage_disk.storage_allocated = storage_allocated
                
    def update_size_in_storage_def(self, storage_id, unique_path, used_size):
        LOGGER.info("Updating storage stats...")
        defn = DBSession.query(StorageDef).filter_by(id=storage_id).first()
        if defn:
            stats = defn.stats
            if stats:
                objStats={}
                objSummary={}
                objDetailsList=[]
                objDetails=[]
                objStorage_details=[]
                
                objStorage_details = stats.get("STORAGE_DETAILS")
                objSummary = stats["SUMMARY"]
                if not objSummary:
                    LOGGER.error("Error: SUMMARY object is not found. Can not update size in storage_definitions table.")
                    return
                    
                if float(objSummary.get("TOTAL"))>0:
                    total_size = self.convert_to_MB(objSummary.get("TOTAL"))
                if not total_size:
                    total_size=0
                    
                objDetailsList = stats["DETAILS"]
                if not objDetailsList:
                    LOGGER.error("Error: DETAILS object is not found. Can not update size in storage_definitions table.")
                    return
                
                if objDetailsList:
                    total_used_size=0
                    for each_disk in objDetailsList:
                        if each_disk.get("uuid"):
                            if each_disk.get("uuid") == unique_path:
                                if float(used_size)>0:
                                    each_disk["USED"] = self.convert_to_GB(used_size)
                                else:
                                    each_disk["USED"] = 0
                            if float(each_disk.get("USED"))>0:
                                total_used_size += self.convert_to_MB(each_disk.get("USED"))
                            objDetails.append(each_disk)
    
                    objStats["name"] = stats.get("name")
                    objStats["type"] = stats.get("type")
                    objStats["id"] = stats.get("id")
                    objStats["op"] = stats.get("op")
                    
                    #calculate available size here
                    available_size = (total_size - total_used_size)
                    objSummary["AVAILABLE"] = self.convert_to_GB(available_size)
                    
                    objStats["SUMMARY"] = objSummary
                    objStats["DETAILS"] = objDetails
                    objStats["STORAGE_DETAILS"] = objStorage_details
                    
                defn.stats = objStats
        
    def convert_to_MB(self, size_in_GB):
        if not size_in_GB:
            size_in_GB=0

        size_in_GB = float(size_in_GB)
        if size_in_GB > 0:
            #since 1 GB is equal to 1024 MBs
            size = (size_in_GB * 1024)
        else:
            size = 0
        size = round(size, 2)
        return size
        
    def convert_to_GB(self, size_in_MB):
        if not size_in_MB:
            size_in_MB=0
            
        size_in_MB = float(size_in_MB)
        if size_in_MB > 0:
            #since 1024 MBs are equal to 1 GB
            size = (size_in_MB/1024)
        else:
            size = 0
        size = round(size, 2)
        return size

    def convert_to_GB_from_Bytes(self, size_in_Bytes):
        #since 1024 Bytes are equal to 1 KB
        #since 1024 KBs are equal to 1 MB
        #since 1024 MBs are equal to 1 GB
        GB_BYTES = 1024.0 * 1024.0 * 1024.0
        
        if not size_in_Bytes:
            size_in_Bytes=0
            
        size_in_Bytes = float(size_in_Bytes)
        if size_in_Bytes > 0:
            size = (size_in_Bytes/GB_BYTES)
        else:
            size = 0
        size = round(size, 2)
        return size

    def add_storage_disk(self, storage_id, actual_size, size, unique_path, current_portal, target, state, lun, storage_allocated, grid_manager, added_manually=False, defn=None):
        storage_disk_id=None
        if storage_id:
            mount_point=None
            file_system=None
            storage_type=None
            disk_name=None
            if not defn:
                defn = self.get_defn(storage_id)
            if defn:
                disk_name = defn.name
                storage_type = defn.type
                #objStats = defn.get_stats()
                #objStorage_details = objStats.get("STORAGE_DETAILS")
                #if objStorage_details:
                    #mount_point = objStorage_details[0].get("MOUNT")
                    #file_system = objStorage_details[0].get("FILESYSTEM")
    
            #check duplicate disk entry in database
            storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=unique_path).first()
            if storage_disk:
                LOGGER.info("Storage disk record for " + to_str(unique_path) + " already present in database.")
                storage_disk_id = storage_disk.id
            else:
                #add new record
                storage_disk = StorageDisks()
                storage_disk_id = getHexID()
                storage_disk.id = storage_disk_id
                storage_disk.storage_id = storage_id
                storage_disk.storage_type = storage_type
                storage_disk.disk_name = disk_name
                storage_disk.mount_point = mount_point
                storage_disk.file_system = file_system
                if not actual_size:
                    actual_size=0
                if not size:
                    size=0
                storage_disk.actual_size = float(actual_size)
                storage_disk.size = float(size)
                storage_disk.unique_path = unique_path
                storage_disk.current_portal = current_portal
                storage_disk.target = target
                storage_disk.state = state
                storage_disk.lun = lun
                storage_disk.storage_allocated = storage_allocated
                storage_disk.added_manually = added_manually
                DBSession.add(storage_disk)
                #match to vm disk
                #if storage_disk_id:
                #    grid_manager.matching_disk_on_discover_storage(storage_disk_id)
        return storage_disk_id
            
    def RemoveScanResult(self, scan_result=None):
        try:
            if scan_result:
                #when this scan_result is passed as a parameter, session object is not present.
                #so make a exit from here.
                return "{success:true, msg:''}"
            
            try:
                scan_result = session.get(constants.SCAN_RESULT)
            except Exception, ex:
                info_msg = to_str(ex).replace("'","")
                LOGGER.info(info_msg)
            
            if scan_result:
                session[constants.SCAN_RESULT] = None
                session.save()
            return "{success:true, msg:''}"
        except Exception, ex:
            error_msg = to_str(ex).replace("'","")
            LOGGER.error(error_msg)
            return "{success:false, msg:'" + error_msg + "'}"

    def GetScanResult(self):
        scan_result=None
        scan_result = session.get(constants.SCAN_RESULT)
        return scan_result
    
    def SaveScanResult(self, storage_id, grid_manager, scan_result=None, site_id=None):
        try:
            if not scan_result:
                try:
                    scan_result = session.get(constants.SCAN_RESULT)
                except Exception, ex:
                    info_msg = to_str(ex).replace("'","")
                    LOGGER.info(info_msg)
            
            if scan_result:
                success = False
                success = scan_result.get("success")
                if not success:
                    LOGGER.info("Scan is failed. Can not update sizes.")
                    #when there is error in scan then do not update sizes.
                    return
                
                defn = self.get_defn(storage_id)
                if defn:
                    #add/update/remove entry of storage disk in storage_disks table
                    self.manage_storage_disk(defn.id, grid_manager, scan_result, site_id)
                    LOGGER.info("Storage stats and storage disks are updated.")
                else:
                    LOGGER.info("Storage stats is not updated since storage is not found.")
            return "{success:true, msg:''}"
        except Exception, ex:
            error_msg = to_str(ex).replace("'","")
            LOGGER.error(error_msg)
            return "{success:false, msg:'" + error_msg + "'}"

    def Recompute_on_remove_vm(self, storage_id_list):
        for storage_id in storage_id_list:
            defn = self.get_defn(storage_id)
            self.Recompute(defn)
            
    def get_storage_id_list(self, vm_id):
        storage_id_list=[]
        if vm_id:
            disks=DBSession.query(StorageDisks, VMDisks, VMStorageLinks)\
            .filter(VMDisks.vm_id==vm_id)\
            .filter(VMDisks.id==VMStorageLinks.vm_disk_id)\
            .filter(StorageDisks.id==VMStorageLinks.storage_disk_id)
                    
            if disks:
                for disk in disks:
                    storage_disk = disk[0]
                    storage_id = storage_disk.storage_id
                    storage_id_list.append(storage_id)
        return storage_id_list

    def lock_ss_row(self, rec):
        rec.locked = True
        
    def unlock_ss_row(self, rec):
        rec.locked = False
    
    def Recompute(self, defn):
        LOGGER.info("Recomputing storage stats...")
        start = p_timing_start(STRG_LOGGER, "Recompute main ")
        if not defn:
            LOGGER.info("Storage definition not found.")
            return
        
        #get site_id
        site_id = 0
        dc_def = DBSession.query(DCDefLink).filter_by(def_id=defn.id, def_type=constants.STORAGE).first()
        if dc_def:
            site_id = dc_def.site_id
        else:
            sites = DBSession.query(Site)
            site_id = sites[0].id

        #get total size of all the storages in Data Center
        total_storage_size_in_DC = self.get_total_storage(site_id, None, constants.SCOPE_DC)
 
        #get total, used and available size of the storage from storage disks.
        (total_size, used_size) = self.get_storage_sizes(defn, site_id)
        
        #***DC*******************
        #update DC record for storage allocation
        self.update_storage_stats_for_datacenter(defn, site_id, total_size, total_storage_size_in_DC)
        LOGGER.info("DC records is populated.")
        
        #***Server Pool*******************
        #update DC record for storage available size (irrespective of SP)
        self.update_storage_stats_for_serverpool(defn, site_id, total_size, total_storage_size_in_DC)
        LOGGER.info("Server pool records are populated.")
        
        #***Server*******************
        self.update_storage_stats_for_server(defn, site_id, total_storage_size_in_DC)
        LOGGER.info("Server and VM records are populated.")
        p_timing_end(STRG_LOGGER, start)

    def get_storage_sizes(self, defn, site_id):
        #get total, used and available size of the storage from storage disks.
        total_size=0
        used_size=0
        ss = DBSession.query(Storage_Stats).filter_by(entity_id=site_id, storage_id=defn.id).first()
        if ss:
            total_size = ss.total_size
            used_size = ss.used_size
        """
        storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=defn.id)
        if storage_disks:
            for storage_disk in storage_disks:
                actual_size = storage_disk.actual_size
                total_size = total_size + actual_size
                
                disk_size = storage_disk.size
                used_size = used_size + disk_size
                
        """
        if not total_size:
            total_size = 0
        if not used_size:
            used_size = 0
        return (total_size, used_size)
    
    def update_storage_stats_for_datacenter(self, defn, site_id, total_size, total_storage_size_in_DC):
        start = p_timing_start(STRG_LOGGER, "Recompute (update_storage_stats_for_datacenter) ")
        #***DC*******************
        #get definition used size in the DC by VMs.
        storage_used_in_DC = self.get_storage_used_in_site(site_id, defn)
        if not storage_used_in_DC:
            storage_used_in_DC=0
        
        storage_allocation_at_DC = self.get_storage_allocation_at_DC(site_id, total_storage_size_in_DC)
        if not storage_allocation_at_DC:
            storage_allocation_at_DC = 0
            
        #update DC record for definition total size, used size, available size and allocation
        context={}
        context["QUERY_FOR"] = "DEF"
        context["entity_id"] = site_id
        context["storage_id"] = defn.id
        if total_size:
            context["allocation_in_DC"] = (100 * float(storage_used_in_DC))/float(total_size)
        else:
            context["allocation_in_DC"] = 0
        self.update_storage_stats(context)
        
        #update storage allocation at DC.
        context={}
        context["QUERY_FOR"] = "ENTITY"
        context["entity_id"] = site_id
        context["storage_allocation_at_DC"] = storage_allocation_at_DC
        self.update_storage_stats(context)
        p_timing_end(STRG_LOGGER, start)

    def get_total_storage_size_in_DC(self, site_id):
        #Note: This function should take sum of total_size of all the storages in the data center
        #from storage_stats table. But it is taking sum of actual_size of all the disks from storage_disks 
        #table so we are not using this function. Instead of that we are using self.get_total_storage() function.
        
        total_storage_size_in_DC=0
        rs=DBSession.query(func.sum(StorageDisks.actual_size).label('disk_size'))\
            .join((StorageDef, StorageDef.id == StorageDisks.storage_id)).first()

        total_storage_size_in_DC = rs.total_size
        if not total_storage_size_in_DC:
            total_storage_size_in_DC = 0
        return total_storage_size_in_DC

    def update_storage_stats_for_serverpool(self, defn, site_id, total_size, total_storage_size_in_DC):
        start = p_timing_start(STRG_LOGGER, "Recompute (update_storage_stats_for_serverpool) ")
        #***Server Pool*******************
        #get a list of vm_disks in the data center to find out storage used in the data center by VMs.
        storage_used_in_DC = self.get_storages_used_in_site(site_id)
        #Storage Available is calculated irrespective of SP so all the SPs and DC are having same value for Storage Available field. So Storage Available will be updated for each SP.
        storage_available = float(total_storage_size_in_DC) - float(storage_used_in_DC)
        
        #update DC record for storage available size (irrespective of SP)
        #This field is independent of storage definition.
        context={}
        context["QUERY_FOR"] = "ENTITY"
        context["entity_id"] = site_id
        context["storage_avail_in_SP"] = storage_available
        self.update_storage_stats(context)

        #if definition is detached from a group then the link would not be present in SPDefLink table.
        #So we will not get that group. But we need to update stats for that group also. So we are taking
        #all groups for updating stats.
        """
        sp_def_list = DBSession.query(SPDefLink).filter_by(def_id=defn.id, def_type=constants.STORAGE)
        if sp_def_list.count()<=0:
            #on disassociate/remove of storage, link with storage would not found in the above table.
            #so take all the groups for looping.
            sp_def_list = DBSession.query(ServerGroup)
        """
        sp_def_list = DBSession.query(ServerGroup)
        if sp_def_list:
            #loop through each group definition
            for sp_def in sp_def_list:
                group_id = sp_def.id
                    
                #get a list of vm_disks in the group to find out storage used in the SP by VMs.
                storage_used_in_SP = self.get_storage_used_in_group(group_id, defn)
                if not storage_used_in_SP:
                    storage_used_in_SP=0
                
                #update SP record for storage allocation at DC
                #This field is dependent on storage definition
                context={}
                context["QUERY_FOR"] = "ENTITY"
                context["entity_id"] = group_id
                context["storage_id"] = defn.id
                if total_size:
                    context["allocation_in_SP"] = (100 * float(storage_used_in_SP))/float(total_size)
                else:
                    context["allocation_in_SP"] = 0
                self.update_storage_stats(context)
                
                #get multiple storages used size in the SP by VMs.
                storages_used_in_SP = self.get_storages_used_in_group(group_id)
                if not storages_used_in_SP:
                    storages_used_in_SP=0

                #update SP record for storage used size
                #These fields are independent of storage definition
                context={}
                context["QUERY_FOR"] = "ENTITY"
                context["entity_id"] = group_id
                context["storage_used_in_SP"] = storages_used_in_SP
                context["storage_avail_in_SP"] = storage_available
                self.update_storage_stats(context)
        p_timing_end(STRG_LOGGER, start)
    
    def update_storage_stats_for_server(self, defn, site_id, total_storage_size_in_DC):
        start = p_timing_start(STRG_LOGGER, "Recompute (update_storage_stats_for_server) ")
        #***Server*******************
        from convirt.viewModel import Basic
        grid_manager=Basic.getGridManager()

        #update server record for allocation
        node_def_list = DBSession.query(ServerDefLink.server_id.label("node_id"), EntityRelation.src_id.label("group_id"))\
        .join((EntityRelation, EntityRelation.dest_id == ServerDefLink.server_id))\
        .filter(ServerDefLink.def_id == defn.id)\
        .filter(ServerDefLink.def_type == constants.STORAGE)\
        .filter(EntityRelation.relation == "Children")
        if node_def_list.count()<=0:
            #on disassociate/remove of storage, link with storage would not found in the above table.
            #so take all the servers for looping.
            node_def_list = DBSession.query(ManagedNode.id.label("node_id"), EntityRelation.src_id.label("group_id"))\
            .join((EntityRelation, EntityRelation.dest_id == ManagedNode.id))\
            .filter(EntityRelation.relation == "Children")

        if node_def_list:
            #get total storage size in the DC

            for node_def in node_def_list:

                node_id = node_def.node_id
                group_id = node_def.group_id
                #get parent
                #entity = auth.get_entity(node_id)
                #group_id = entity.parents[0].entity_id

                #get total used size on the server by VMs
                strg_usage_for_S = self.get_storage_usage_for_server(node_id)

                #get total storage size in the SP
                total_strg_size_sp = self.get_total_storage(site_id, group_id, constants.SCOPE_SP)
                
                #update Server entity record for storage allocation for DC and SP level (server tab on UI)
                context={}
                context["QUERY_FOR"] = "ENTITY"
                context["entity_id"] = node_id
                if total_storage_size_in_DC:
                    context["allocation_at_S_for_DC"] =\
                    (100 * float(strg_usage_for_S))/float(total_storage_size_in_DC)
                else:
                    context["allocation_at_S_for_DC"] = 0
                if total_strg_size_sp:
                    context["allocation_at_S_for_SP"] = (100 * float(strg_usage_for_S))/float(total_strg_size_sp)
                else:
                    context["allocation_at_S_for_SP"] = 0
                self.update_storage_stats(context)

                #***Virtual machine*******************
                #update VM record for local storage, shared storage, allocation
                #vm_list = grid_manager.get_node_doms(auth, node_id)
                #get children (vms)
                entity_rel_list = DBSession.query(EntityRelation).filter_by(src_id=node_id, relation="Children")
                for entity_rel in entity_rel_list:
                    self.update_storage_stats_for_vm(entity_rel.dest_id)
        p_timing_end(STRG_LOGGER, start)
                    
    def update_storage_stats_for_vm(self, vm_id):
        #***Virtual machine*******************
        (shared_size, local_size) = self.get_storage_size(vm_id)
        context={}
        context["QUERY_FOR"] = "ENTITY"
        context["entity_id"] = vm_id
        context["local_storage_at_VM"] = local_size
        context["shared_storage_at_VM"] = shared_size
        self.update_storage_stats(context)

        
    def update_storage_stats(self, context):
        ss=None
        entity_id = context.get("entity_id")
        storage_id = context.get("storage_id")
        
        #This check is here to avoid IntegrityError.
        if storage_id:
            defn = self.get_defn(storage_id)
            if not defn:
                LOGGER.info("Storage definition does not exist so that Storage table can not be updated with the definition.")
                return
        """
        if auth:
            entity = auth.get_entity(entity_id)
            if entity:
                entity_name = entity.name
        """
        if context.get("QUERY_FOR") == "DEF":
            ss = DBSession.query(Storage_Stats).filter_by(entity_id = entity_id, storage_id = storage_id).first()
        elif context.get("QUERY_FOR") == "ENTITY":
            if storage_id:
                ss = DBSession.query(Storage_Stats).filter_by(entity_id = entity_id, storage_id = storage_id).first()
            else:
                ss = DBSession.query(Storage_Stats).filter_by(entity_id = entity_id, storage_id=None).first()
        
        if ss:  #update record
            if not ss.locked:
                self.lock_ss_row(ss)
                if context.get("entity_id"):
                    ss.entity_id = context.get("entity_id")
                if context.get("storage_id"):
                    ss.storage_id = context.get("storage_id")
                if context.get("total_size"):
                    ss.total_size = context.get("total_size")
                elif context.get("total_size") == 0:
                    ss.total_size = 0
                    
                if context.get("used_size"):
                    ss.used_size = context.get("used_size")
                elif context.get("used_size") == 0:
                    ss.used_size = 0
                    
                if context.get("available_size"):
                    ss.available_size = context.get("available_size")
                elif context.get("available_size") == 0:
                    ss.available_size = 0
                    
                if context.get("allocation_in_DC"):
                    ss.allocation_in_DC = context.get("allocation_in_DC")
                elif context.get("allocation_in_DC") == 0:
                    ss.allocation_in_DC = 0
                    
                if context.get("allocation_in_SP"):
                    ss.allocation_in_SP = context.get("allocation_in_SP")
                elif context.get("allocation_in_SP") == 0:
                    ss.allocation_in_SP = 0
                    
                if context.get("storage_used_in_SP"):
                    ss.storage_used_in_SP = context.get("storage_used_in_SP")
                elif context.get("storage_used_in_SP") == 0:
                    ss.storage_used_in_SP = 0
                    
                if context.get("storage_avail_in_SP"):
                    ss.storage_avail_in_SP = context.get("storage_avail_in_SP")
                elif context.get("storage_avail_in_SP") == 0:
                    ss.storage_avail_in_SP = 0
                    
                if context.get("allocation_at_S_for_DC"):
                    ss.allocation_at_S_for_DC = context.get("allocation_at_S_for_DC")
                elif context.get("allocation_at_S_for_DC") == 0:
                    ss.allocation_at_S_for_DC = 0
                    
                if context.get("allocation_at_S_for_SP"):
                    ss.allocation_at_S_for_SP = context.get("allocation_at_S_for_SP")
                elif context.get("allocation_at_S_for_SP") == 0:
                    ss.allocation_at_S_for_SP = 0
                    
                if context.get("local_storage_at_VM"):
                    ss.local_storage_at_VM = context.get("local_storage_at_VM")
                elif context.get("local_storage_at_VM") == 0:
                    ss.local_storage_at_VM = 0
                
                if context.get("shared_storage_at_VM"):
                    ss.shared_storage_at_VM = context.get("shared_storage_at_VM")
                elif context.get("shared_storage_at_VM") == 0:
                    ss.shared_storage_at_VM = 0
                    
                if context.get("storage_allocation_at_DC"):
                    ss.storage_allocation_at_DC = context.get("storage_allocation_at_DC")
                elif context.get("storage_allocation_at_DC") == 0:
                    ss.storage_allocation_at_DC = 0
                    
                self.unlock_ss_row(ss)
                #commit the transaction since it is in task.
                #transaction.commit()
                LOGGER.info("The record is updated.")
            else:
                LOGGER.info("The record is locked. So the record can not be updated.")
        else:   #add record
            ss = Storage_Stats()
            ss.id = getHexID()
            ss.entity_id = context.get("entity_id")
            ss.storage_id = context.get("storage_id")
            ss.total_size = context.get("total_size")
            ss.used_size = context.get("used_size")
            ss.available_size = context.get("available_size")
            ss.allocation_in_DC = context.get("allocation_in_DC")
            ss.allocation_in_SP = context.get("allocation_in_SP")
            ss.storage_used_in_SP = context.get("storage_used_in_SP")
            ss.storage_avail_in_SP = context.get("storage_avail_in_SP")
            ss.allocation_at_S_for_DC = context.get("allocation_at_S_for_DC")
            ss.allocation_at_S_for_SP = context.get("allocation_at_S_for_SP")
            ss.local_storage_at_VM = context.get("local_storage_at_VM")
            ss.shared_storage_at_VM = context.get("shared_storage_at_VM")
            ss.storage_allocation_at_DC = context.get("storage_allocation_at_DC")
            DBSession.add(ss)
            LOGGER.info("The record is created.")
    
    def remove_storage_stats(self, def_id, entity_id):
        ss=None
        if def_id:
            ss = DBSession.query(Storage_Stats).filter_by(storage_id=def_id).first()
        elif entity_id:
            ss = DBSession.query(Storage_Stats).filter_by(entity_id=entity_id).first()
        
        if ss:
            DBSession.delete(ss)
            
    def get_storage_used_in_site(self, site_id, defn):
        start = p_timing_start(STRG_LOGGER, "Recompute (get_storage_used_in_site) ", log_level="DEBUG")
        total_shared_size=0
        rs=DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id))\
        .join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id))\
        .join((DCDefLink, DCDefLink.def_id == StorageDisks.storage_id))\
        .filter(DCDefLink.site_id == site_id)\
        .filter(DCDefLink.def_id == defn.id)\
        .filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id == site_id))))))).first()
        total_shared_size = rs.disk_size
        
        if not total_shared_size:
            total_shared_size = 0
        p_timing_end(STRG_LOGGER, start)
        return total_shared_size
        
    def get_storages_used_in_site(self, site_id):
        start = p_timing_start(STRG_LOGGER, "Recompute (get_storage_used_in_site) ", log_level="DEBUG")
        total_shared_size=0
        rs=DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id))\
        .join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id))\
        .join((DCDefLink, DCDefLink.def_id == StorageDisks.storage_id))\
        .filter(DCDefLink.site_id == site_id)\
        .filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id == site_id))))))).first()
        total_shared_size = rs.disk_size
        
        if not total_shared_size:
            total_shared_size = 0
        p_timing_end(STRG_LOGGER, start)
        return total_shared_size
    
    def get_storage_used_in_group(self, group_id, defn):
        start = p_timing_start(STRG_LOGGER, "Recompute (get_storage_used_in_group) ", log_level="DEBUG")
        total_shared_size=0
        rs=DBSession.query(func.sum(VMDisks.disk_size).label('disk_size'))\
        .join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id))\
        .join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id))\
        .join((SPDefLink, SPDefLink.def_id == StorageDisks.storage_id))\
        .filter(SPDefLink.group_id == group_id)\
        .filter(SPDefLink.def_id == defn.id)\
        .filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id == group_id))))).first()
        total_shared_size = rs.disk_size
        
        if not total_shared_size:
            total_shared_size = 0
        p_timing_end(STRG_LOGGER, start)
        return total_shared_size
        
    def get_storages_used_in_group(self, group_id):
        total_shared_size=0
        rs=DBSession.query(func.sum(VMDisks.disk_size).label('disk_size'))\
        .join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id))\
        .join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id))\
        .join((SPDefLink, SPDefLink.def_id == StorageDisks.storage_id))\
        .filter(SPDefLink.group_id == group_id)\
        .filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id == group_id))))).first()
        total_shared_size = rs.disk_size
        
        if not total_shared_size:
            total_shared_size = 0
        return total_shared_size
            
    #function moved here from DashboardService
    def get_storage_usage_for_server(self, node_id):
        start = p_timing_start(STRG_LOGGER, "Recompute (get_storage_usage_for_server) ", log_level="DEBUG")
        usage=0.0
        rs=DBSession.query(func.sum(VMDisks.disk_size).label('disk_size'))\
        .join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id))\
        .join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id))\
        .join((ServerDefLink, ServerDefLink.def_id == StorageDisks.storage_id))\
        .filter(ServerDefLink.server_id == node_id)\
        .filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.src_id == node_id)\
        .filter(EntityRelation.relation == "Children"))).first()
        usage = rs.disk_size
        
        if not usage:
            usage = 0
        p_timing_end(STRG_LOGGER, start)
        return usage
            
    #function moved here from DashboardService
    def get_storage_size(self, vm_id):
        shared_size = 0.00
        local_size = 0.00
        if vm_id:
            disks=DBSession.query(VMDisks, VMStorageLinks).outerjoin((VMStorageLinks,\
            VMDisks.id==VMStorageLinks.vm_disk_id)).filter(VMDisks.vm_id==vm_id)
            if disks:
                for disk in disks:
                    vm_disk = disk[0]
                    vm_storage_link = disk[1]
                    disk_size = vm_disk.disk_size
                    if disk_size:
                        if vm_storage_link:
                            shared_size += disk_size
                        else:
                            local_size += disk_size
        return (shared_size, local_size)

    def get_storage_allocation_at_DC(self, site_id, total_storage_size_in_DC):
        start = p_timing_start(STRG_LOGGER, "Recompute (get_storage_allocation_at_DC) ")
        storage_allocation_at_DC = 0
        total_shared_size=0
        #get total shared size used in the DC
        rs=DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id))\
        .join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id))\
        .join((DCDefLink, DCDefLink.def_id == StorageDisks.storage_id))\
        .filter(DCDefLink.site_id == site_id)\
        .filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id)\
        .filter(EntityRelation.relation == "Children")\
        .filter(EntityRelation.src_id == site_id))))))).first()
        total_shared_size = rs.disk_size
        
        if not total_shared_size:
            total_shared_size = 0

        if not total_storage_size_in_DC:
            total_storage_size_in_DC = 0
        
        if total_storage_size_in_DC:
            storage_allocation_at_DC = (100 * float(total_shared_size))/float(total_storage_size_in_DC)
        else:
            storage_allocation_at_DC = 0
        p_timing_end(STRG_LOGGER, start)
        return storage_allocation_at_DC
        
    def get_total_storage(self, site_id, group_id, scope):
        start = p_timing_start(STRG_LOGGER, "Recompute (get_total_storage) ")
        total_size=0
        rs=None
        if scope == constants.SCOPE_DC:
            #get total size of all the storage in Data Center
            rs=DBSession.query(func.sum(Storage_Stats.total_size).label('total_size'))\
            .join((DCDefLink, DCDefLink.def_id == Storage_Stats.storage_id))\
            .filter(DCDefLink.site_id == site_id).first()
            
        elif scope == constants.SCOPE_SP:
            #get total size of all the storages in Server Pool
            rs=DBSession.query(func.sum(Storage_Stats.total_size).label('total_size'))\
            .join((SPDefLink, SPDefLink.def_id == Storage_Stats.storage_id))\
            .filter(SPDefLink.group_id == group_id).first()
        
        if rs:
            total_size = rs.total_size
        
        if not total_size:
            total_size=0
        p_timing_end(STRG_LOGGER, start)
        return total_size

    def storage_stats_data_upgrade(self):
        upgraded=False
        upgrade_data = DBSession.query(Upgrade_Data).filter_by(name=to_unicode(constants.STORAGE_STATS), version=to_unicode("2.0-2.0.1")).first()
        if upgrade_data:
            upgraded = upgrade_data.upgraded
            
        if not upgraded:
            LOGGER.info("Data upgrading for storage stats for version 2.0 to 2.0.1...")
            def_list = DBSession.query(StorageDef)
            for defn in def_list:
                LOGGER.info("Recomputing for definition " + to_str(defn.name))
                self.Recompute(defn)
                
            #update upgrade_data table for the upgrade of version 2.0 to 2.0.1
            upgrade_data = Upgrade_Data()
            upgrade_data.id = to_unicode(getHexID())
            upgrade_data.name = to_unicode(constants.STORAGE_STATS)
            upgrade_data.version = to_unicode("2.0-2.0.1")
            upgrade_data.description = to_unicode("Recomputing storage stats")
            upgrade_data.upgraded = True
            DBSession.add(upgrade_data)
            transaction.commit()
            LOGGER.info("Database for storage stats is upgraded for version 2.0 to 2.0.1.")
        else:
            LOGGER.info("Database for storage stats is already upgraded for version 2.0 to 2.0.1.")

    def recompute_on_transfer_node(self, auth, group_id, grid_manager):
        LOGGER.info("Recomputing storage stats on transfer of node...")
        vm_list=[]
        vm_list = grid_manager.get_vms_from_pool(auth, group_id)
        if vm_list:
            for eachvm in vm_list:
                #get storage disks attached to the VM
                sds = DBSession.query(StorageDisks)\
                    .join((VMStorageLinks, VMStorageLinks.storage_disk_id == StorageDisks.id))\
                    .join((VMDisks, VMDisks.id == VMStorageLinks.vm_disk_id))\
                    .join((VM, VM.id == VMDisks.vm_id))\
                    .filter(VMDisks.vm_id == eachvm.id)
                for each_sd in sds:
                    defn = self.get_defn(each_sd.storage_id)
                    self.Recompute(defn)

    def recompute_on_import_config(self, vm_id):
        LOGGER.info("Recomputing storage stats on import config...")
        sds = DBSession.query(StorageDisks)\
            .join((VMStorageLinks, VMStorageLinks.storage_disk_id == StorageDisks.id))\
            .join((VMDisks, VMDisks.id == VMStorageLinks.vm_disk_id))\
            .join((VM, VM.id == VMDisks.vm_id))\
            .filter(VMDisks.vm_id == vm_id)
        for each_sd in sds:
            defn = self.get_defn(each_sd.storage_id)
            self.Recompute(defn)
