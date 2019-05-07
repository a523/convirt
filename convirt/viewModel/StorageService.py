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
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# author : Jd <jd_jedi@users.sourceforge.net>
from tg import session
from convirt.model.Groups import ServerGroup
from convirt.model.ManagedNode import ManagedNode
from convirt.core.utils import constants
from convirt.core.utils.phelper import AuthenticationException
import Basic
from convirt.model.storage import StorageDef, StorageManager
from convirt.model import DBSession
from convirt.model.VM import VM, VMDisks, VMStorageLinks
from convirt.model.SPRelations import ServerDefLink, SPDefLink,DCDefLink, StorageDisks, Storage_Stats
from convirt.model.storage import StorageDef
from convirt.model.SyncDefinition import SyncDef
from convirt.model.Sites import Site
import convirt.core.utils.utils
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
from convirt.core.utils.constants import *
constants = convirt.core.utils.constants

import logging,traceback
LOGGER = logging.getLogger("convirt.viewModel")

class StorageService:
    def __init__(self):
        self.storage_manager = Basic.getStorageManager()
        self.manager=Basic.getGridManager()
        self.sync_manager = SyncDef()

    def get_storage_types(self):
        try:
            storage_type_list=[]
            storage_dic={"Network File Storage (NFS)":constants.NFS,
                         "Internet SCSI (iSCSI)": constants.iSCSI,
                         "ATA Over Ethernet (AOE)": constants.AOE,
                        }
            for storage_values in storage_dic.keys():
                storage_dic_temp={}
                storage_dic_temp["name"]=storage_values
                storage_dic_temp["value"]=storage_dic[storage_values]
                storage_type_list.append(storage_dic_temp)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"

        return dict(success='true',rows=storage_type_list)

    def get_vm_id_list(self, auth, node_entities, vm_id_list):
        #loop through each server
        for eachnode in node_entities:
            #get vm (domain) list
            vms=auth.get_entities(constants.DOMAIN,parent=eachnode)
            for eachvm in vms:
                vm_id_list.append(eachvm.entity_id)
        return vm_id_list

    def get_vm_local_usage(self, vm_name):
        #get vm disks for the vm.
        #find out local disks.
        #get local_usage
        local_usage=0.00
        if vm_name:
            vm = DBSession.query(VM).filter_by(name=vm_name).first()
            if vm:
                vm_id = vm.id
                vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
                if vm_disks:
                    for each_vm_disk in vm_disks:
                        vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=each_vm_disk.id).first()
                        #when link is not found then it is local storage.
                        if not vm_storage_link:
                            local_usage += each_vm_disk.disk_size
        return local_usage
    
    def get_storage_usage(self, auth, site_id, group_id, scope, defn):
        #get vm id list inside the site or group whatever the scope is.
        #get the list of storage disk for the storage
        #check the link between vm id and storage disk id.
        #if the link exists then take the size size and add in usage to get total usage of the storage.
        
        usage=0
        vm_id_list=[]
        
        if scope == constants.SCOPE_DC:
            #get site entity
            site_entity = auth.get_entity(site_id)
            
            #get group list
            groups = auth.get_entities(constants.SERVER_POOL,parent=site_entity)
            for eachgroup in groups:
                #get server list
                nodes=auth.get_entities(constants.MANAGED_NODE,parent=eachgroup)
                vm_id_list = self.get_vm_id_list(auth, nodes, vm_id_list)
                
        elif scope == constants.SCOPE_SP:
            #get group entity
            group_entity = auth.get_entity(group_id)
            #get server list
            nodes = auth.get_entities(constants.MANAGED_NODE,parent=group_entity)
            vm_id_list = self.get_vm_id_list(auth, nodes, vm_id_list)
            
        
        storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=defn.id)
        if storage_disks:
            for each_disk in storage_disks:
                vm_storage_link = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=each_disk.id).first()
                if vm_storage_link:
                    vm_id=None
                    vm_disk = DBSession.query(VMDisks).filter_by(id=vm_storage_link.vm_disk_id).first()
                    if vm_disk:
                        vm_id = vm_disk.vm_id
                    for each_vm_id in vm_id_list:
                        if each_vm_id == vm_id:
                            usage += vm_disk.disk_size
        return usage
        
    def get_storage_def_list(self,auth,site_id,group_id,scope=None):
        storage_list=[]
        try:
            if site_id == 'data_center':
                site = self.manager.getSiteByGroupId(group_id)
                if site:
                    site_id = site.id
            sds = self.storage_manager.get_sd_ids(site_id, group_id, to_unicode(constants.STORAGE), scope)
            if sds:
                for item in sds:
                    temp_sd_dic={}
                    s_def = self.storage_manager.get_sd(item, site_id, group_id, to_unicode(constants.STORAGE))
                    
                    associated = False
                    node_defn = DBSession.query(ServerDefLink).filter_by(def_id=s_def.id).first()
                    if node_defn:
                        associated = True
    
                    #check None here to avoid None exception
                    if s_def:
                        #get a group list string of the associated server pools with this definition
                        usage=""
                        if scope == constants.SCOPE_DC:
                            ss = DBSession.query(Storage_Stats).filter_by(entity_id=site_id, storage_id=s_def.id).first()
                            if ss:
                                usage = ss.allocation_in_DC
                        elif scope == constants.SCOPE_SP:
                            ss = DBSession.query(Storage_Stats).filter_by(entity_id=group_id, storage_id=s_def.id).first()
                            if ss:
                                usage = ss.allocation_in_SP

                        str_group_list = None
                        group_defns = DBSession.query(SPDefLink).filter_by(def_id=s_def.id)
                        if group_defns:
                            for eachdefn in group_defns:
                                group = DBSession.query(ServerGroup).filter_by(id=eachdefn.group_id).first()
                                if str_group_list:
                                    str_group_list = str_group_list + ", " + group.name
                                else:
                                    str_group_list = group.name
                                    
                        total=0.00
                        ss = s_def.get_stats()
                        if ss:
                            total = ss.total_size
                        definition=self.get_defn(s_def)
                        temp_sd_dic['stats']="" #s_def.stats
                        temp_sd_dic['name']=s_def.name
                        temp_sd_dic['connection_props']=s_def.connection_props
                        temp_sd_dic['type']=s_def.type
                        temp_sd_dic['id']=s_def.id
                        temp_sd_dic['creds']=s_def.creds
                        temp_sd_dic['creds_required']=s_def.creds_required
                        temp_sd_dic['size']=total
                        temp_sd_dic['definition']=definition
                        temp_sd_dic['description']=s_def.description
                        temp_sd_dic['status']=s_def.status
                        temp_sd_dic['scope']=s_def.scope
                        temp_sd_dic['associated']=associated
                        temp_sd_dic['serverpools']=str_group_list
                        """
                        if not total:
                            total = 0.00
                        """
                        if not usage:
                            usage = 0
                        #calculate percentage here
                        """
                        if float(total) > 0:
                            usage=(float(usage)*100)/float(total)
                        else:
                            usage=0.00
                        """
                        temp_sd_dic['usage']=usage
    
                        storage_list.append(temp_sd_dic)
            else:
                LOGGER.info("Storages are not found.")
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return dict(success=False, msg=to_str(ex).replace("'",""), rows=storage_list)
        return dict(success=True, rows=storage_list)

    def get_dc_storage_def_list(self,auth,site_id,group_id):
        storage_list=[]
        try:
            if site_id == 'data_center':
                site = self.manager.getSiteByGroupId(group_id)
                if site:
                    site_id = site.id
            
            defn_list = self.storage_manager.getSiteDefListToAssociate(site_id, group_id, to_unicode(constants.STORAGE))
            if defn_list:
                for s_def in defn_list:
                    temp_sd_dic={}
                    #check None here to avoid None exception
                    if s_def:
                        total=0.00
                        if s_def.get_stats():
                            #total = s_def.get_stats().get("TOTAL")
                            objStats = s_def.get_stats()
                            if objStats:
                                total = objStats.total_size

                        definition=self.get_defn(s_def)
                        temp_sd_dic['stats']="" #s_def.stats
                        temp_sd_dic['name']=s_def.name
                        temp_sd_dic['connection_props']=s_def.connection_props
                        temp_sd_dic['type']=s_def.type
                        temp_sd_dic['id']=s_def.id
                        temp_sd_dic['creds']=s_def.creds
                        temp_sd_dic['creds_required']=s_def.creds_required
                        temp_sd_dic['size']=total
                        temp_sd_dic['definition']=definition
                        temp_sd_dic['description']=s_def.description
                        temp_sd_dic['status']=s_def.status
                        temp_sd_dic['scope']=s_def.scope
    
                        storage_list.append(temp_sd_dic)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return dict(success=False, msg=to_str(ex).replace("'",""), rows=storage_list)
        return dict(success=True, rows=storage_list)

    def get_server_storage_def_list(self,auth,node_id):
        storage_list=[]
        try:

            defn_list = self.sync_manager.get_server_defns(node_id, to_unicode(constants.STORAGE))
            if defn_list:
                for item in defn_list:
                    temp_sd_dic={}
                    s_def = self.storage_manager.get_defn(item[0])

                    #check None here to avoid None exception
                    if s_def:
                        total=0.0
                        if s_def.get_stats():
                            #total = s_def.get_stats().get("TOTAL")
                            objStats = s_def.get_stats()
                            if objStats:
                                total = objStats.total_size

                        definition=self.get_defn(s_def)
                        temp_sd_dic['stats']="" #s_def.stats
                        temp_sd_dic['name']=s_def.name
                        temp_sd_dic['connection_props']=s_def.connection_props
                        temp_sd_dic['type']=s_def.type
                        temp_sd_dic['id']=s_def.id
                        temp_sd_dic['creds']=s_def.creds
                        temp_sd_dic['creds_required']=s_def.creds_required
                        temp_sd_dic['size']=total
                        temp_sd_dic['definition']=definition
                        temp_sd_dic['description']=s_def.description
                        #temp_sd_dic['status']=s_def.status
                        temp_sd_dic['scope']=s_def.scope
                        #temp_sd_dic['associated']=associated

                        storage_list.append(temp_sd_dic)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        return storage_list

    def add_storage_def(self,auth, site_id, group_id, node_id, type, opts, op_level=None, sp_ids=None, scan_result=None):
        new_sd = self.get_valid_sd(type,opts, op_level)
        site = self.manager.getSite(site_id)
        group=self.manager.getGroup(auth,group_id)
        node = None
        group_list = self.manager.getGroupList(auth, site_id)
        try:
            sdlist = self.storage_manager.get_sds(site_id, group_id)
            for sd in sdlist:
                if new_sd.name==sd.name:
                    raise Exception("Storage share with same name already exists.")
            errs=[]
            errs = self.update_storage_def(auth, new_sd, None, None, None, site, group, op_level, True, sp_ids, errs, scan_result)
            if errs:
                if len(errs) > 0:
                    add_mode=True
                    self.sync_manager.remove_defn(new_sd, site, group, node, auth, to_unicode(constants.STORAGE), constants.DETACH, "REMOVE_STORAGE_DEF", self.storage_manager, self.manager, add_mode, group_list, op_level)
                    return {'success':False,'msg':to_str(errs).replace("'","")}
        except Exception, ex:
            print_traceback()
            err_desc = to_str(ex).replace("'","")
            err_desc = err_desc.strip()
            LOGGER.error(err_desc)
            try:
                add_mode=True
                defn_temp = self.storage_manager.get_sd(new_sd.id, None, None, None)
                if defn_temp:
                    self.sync_manager.remove_defn(defn_temp, site, group, node, auth, to_unicode(constants.STORAGE), constants.DETACH, "REMOVE_STORAGE_DEF", self.storage_manager, self.manager, add_mode, group_list, op_level)
            except Exception, ex1:
                print_traceback()
                LOGGER.error(to_str(ex1).replace("'",""))
                raise Exception(to_str(ex1))
            if err_desc:
                raise Exception(err_desc)
            return "{success: false,msg: '" + err_desc + "'}"
        return "{success: true,msg: 'Storage Added.'}"

    def edit_storage_def(self, auth, storage_id, site_id, groupId, type, op_level, sp_ids, opts):
        try:
            site = self.manager.getSite(site_id)
            group=self.manager.getGroup(auth,groupId)
            #new_sd = self.get_valid_sd(type,opts)
            new_name = opts.get("name")
            new_desc = opts.get("description")
            self.update_storage_def(auth, None, new_name, new_desc, storage_id, site, group, op_level, False, sp_ids)
            self.SaveScanResult(storage_id, site_id)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'","").strip(),"'}"
        return "{success: true,msg: 'Storage Updated.'}"

    def get_valid_sd(self, type, options, scope):
        creds_req = False
        creds = {}
        conn_options = {}
        if type == constants.iSCSI:     # conn_props = target, options
            creds_req = True
            creds["username"] = options.get("username")
            creds["password"] = options.get("password")

            conn_options["server"] = options.get("portal")
            conn_options["target"] = options.get("target")
            conn_options["options"] = options.get("options")
            conn_options["username"] = options.get("username")
            conn_options["password"] = options.get("password")

        if type == constants.NFS:       # conn_props = share, mount_point, mount_options
            conn_options["server"] = options.get("server")
            conn_options["share"] = options.get("share")
            conn_options["mount_point"] = options.get("mount_point")
            conn_options["mount_options"] = options.get("mount_options")

        if type == constants.AOE:       # conn_props = interfaces
            conn_options["interface"] = options.get("interface")

        new_sd = StorageDef(None, to_unicode(options.get("name")), type, to_unicode(options.get("description")), conn_options, scope, creds_req)

        if creds_req == True:
            new_sd.set_creds(creds)

        if options["total_cap"] != 'null':
            options["total_cap"] = str(options.get("total_cap")).strip()
            if options["total_cap"]:
                total_cap = str(options.get("total_cap"))
                if not total_cap:
                    total_cap = 0
        print "new_sd=====",new_sd
        return new_sd

    def associate_defns(self, site_id, group_id, def_type, def_ids, auth, op_level=None):
        error_desc=""
        site = self.manager.getSite(site_id)
        group=self.manager.getGroup(auth,group_id)
        group_list = self.manager.getGroupList(auth, site_id)
        def_id_list = def_ids.split(",")
        for def_id in def_id_list:
            new_sd = DBSession.query(StorageDef).filter_by(id=def_id).first()
            node = None
            try:
                associate=True
                self.sync_manager.add_defn(new_sd, site, group, node, auth, to_unicode(constants.STORAGE), constants.ATTACH, "ADD_STORAGE_DEF", self.storage_manager, self.manager, op_level, associate)
                
                #matching disks on association of storage.
                vm_disks = self.manager.get_vm_disks_from_pool(auth, group_id)
                storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=def_id)
                if storage_disks:
                    for eachdisk in storage_disks:
                        self.manager.matching_disk_on_discover_storage(vm_disks, eachdisk.id)
            except Exception, ex:
                error_desc = to_str(ex)
                print_traceback()
                LOGGER.error(to_str(ex).replace("'",""))
                #if we get any exception while adding/ sync definition then are removing the definition.
                add_mode=True
                try:
                    self.sync_manager.remove_defn(new_sd, site, group, node, auth, to_unicode(constants.STORAGE), constants.DETACH, "REMOVE_STORAGE_DEF", self.storage_manager, self.manager, add_mode, group_list, op_level)
                except Exception, ex1:
                    print_traceback()
                    LOGGER.error(to_str(ex1).replace("'",""))
                    raise Exception(to_str(ex1))
                if error_desc:
                    raise Exception(error_desc)
        return  {'success':True,'msg':'Storage Added'}

    def update_storage_def(self, auth, new_sd, new_name, new_desc, storage_id, site, group, op_level, new=True, sp_ids=None, errs=None, scan_result=None):
        if new == True:
            #Validation for duplicate name
            if group:
                group_defns = DBSession.query(SPDefLink).filter_by(group_id = group.id)
            elif site:
                group_defns = DBSession.query(DCDefLink).filter_by(site_id = site.id)

            for group_defn in group_defns:
                rowSDef = DBSession.query(StorageDef).filter_by(id=group_defn.def_id, name=new_name).first()
                if rowSDef:
                        raise Exception("Storage definition with the same name already exists")

            node = None
            self.sync_manager.add_defn(new_sd, site, group, node, auth, to_unicode(constants.STORAGE), constants.ATTACH, "ADD_STORAGE_DEF", self.storage_manager, self.manager, op_level, sp_ids, scan_result)
        else:
            #Validation for duplicate name
            if group:
                group_defns = DBSession.query(SPDefLink).filter_by(group_id = group.id)
            elif site:
                group_defns = DBSession.query(DCDefLink).filter_by(site_id = site.id)

            for group_defn in group_defns:
                rowSDef = DBSession.query(StorageDef).filter_by(id=group_defn.def_id, name=new_name).first()
                if rowSDef and rowSDef.id != storage_id:
                    raise Exception("Storage definition with the same name already exists")

            defn = DBSession.query(StorageDef).filter_by(id=storage_id).first()
            self.sync_manager.update_defn(defn, new_name, new_desc, site, group, auth, to_unicode(constants.STORAGE), constants.ATTACH, self.storage_manager, 'UPDATE_STORAGE_DEF', op_level, sp_ids, self.manager)

    def is_storage_allocated(self, storage_id):
        returnVal = False
        msg = "NOT_IN_USE"
        try:
            returnVal = self.storage_manager.is_storage_allocated(storage_id)
            if returnVal:
                msg = "IN_USE"
            return "{success: true,msg: '" + msg + "'}"
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            return "{success: false,msg: '" + to_str(ex) + "'}"

    def remove_storage_def(self, auth,storage_id,site_id,groupId, op_level=None):
        try:
            site = self.manager.getSite(site_id)
            group=self.manager.getGroup(auth,groupId)
            group_list = self.manager.getGroupList(auth, site_id)
            sd_to_remove = self.storage_manager.get_sd(storage_id, site_id, groupId, to_unicode(constants.STORAGE))
            node = None
            add_mode=False
            warning_msg = self.sync_manager.remove_defn(sd_to_remove, site, group, node, auth, to_unicode(constants.STORAGE), constants.DETACH, "REMOVE_STORAGE_DEF", self.storage_manager, self.manager, add_mode, group_list, op_level)
            if warning_msg:
                return "{success: true,msg: '" + warning_msg + "'}"
            
            return "{success: true,msg: 'Storage Removed'}"
        except Exception, ex:
            print_traceback()
            err_desc = to_str(ex).replace("'","")
            err_desc = err_desc.strip()
            LOGGER.error(to_str(err_desc))
            return "{success: false,msg: '" + err_desc + "'}"

    #we are not using this function now.
    def rename_storage_def(self,auth,new_name,storage_id,groupId): pass

    def get_vm_linked_with_storage(self, storage_disk_id):
        vm=None
        if storage_disk_id:
            vm_storage_link = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=storage_disk_id).first()
            if vm_storage_link:
                vm_disk = DBSession.query(VMDisks).filter_by(id=vm_storage_link.vm_disk_id).first()
                if vm_disk:
                    vm = DBSession.query(VM).filter_by(id=vm_disk.vm_id).first()
        return vm
    
    def edit_test_output(self, details):
        objStat={}
        objSummary={}
        objDetailsList=[]
        objStorageDetails={}
        
        if details:
            objSummary = details.get("SUMMARY")
            total_size = objSummary.get("TOTAL")
            #Here total is of type of string. We are striping it in case it is blank like " " while storing in db.
            objSummary["TOTAL"] = to_str(total_size).strip()
            
            objStorageDetails = details.get("STORAGE_DETAILS")
            details_list = details.get("DETAILS")
    
            for objDetails in details_list:
                storage_disk_id=None
                storage_allocated=False
                vm_name=None
                disk_name=None
                
                if objDetails.get("uuid"):
                    unique_path = str(objDetails.get("uuid")).strip()
                    storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=unique_path).first()
                    storage_allocated = "No"
                    if storage_disk:
                        if storage_disk.storage_allocated == True:
                            storage_allocated = "Yes"
                            storage_disk_id = storage_disk.id
                
                    uuid_param = to_str(unique_path).split("/")
                    disk_name = uuid_param[len(uuid_param)-1]

                objDetails['STORAGE_ALLOCATED'] = storage_allocated
                objDetails['DISKS'] = disk_name
                if storage_disk_id:
                    vm = self.get_vm_linked_with_storage(storage_disk_id)
                    if vm:
                        vm_name = vm.name
                objDetails['VM_NAME'] = vm_name
                objDetailsList.append(objDetails)
        
        objStat["STORAGE_DETAILS"] = objStorageDetails
        objStat["DETAILS"] = objDetailsList
        objStat["SUMMARY"] = objSummary
        return objStat
        
    def get_storage_for_test(self, storage_id):
        objStat={}
        objSummary={}
        objDetailsList=[]
        objDetails={}
        objStorageDetails={}
        
        disk_name=None
        storage_type=None
        total_size=0
        available_size=0
            
        if storage_id:
            defn = self.storage_manager.get_defn(storage_id)
            if defn:
                stats = defn.get_stats()
                if stats:
                    total_size = stats.total_size
                    objStorageDetails = []  #stats.get("STORAGE_DETAILS")
                    storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=defn.id)
                    for each_storage_disk in storage_disks:
                        if objDetails:
                            objDetailsList.append(objDetails)
                            objDetails={}
                        
                        objDetails['STORAGE_DISK_ID'] = None
                        objDetails['STORAGE_ALLOCATED'] = False
                        objDetails['USED'] = each_storage_disk.size #disk_size
                        objDetails['SIZE'] = each_storage_disk.actual_size
                        objDetails['CurrentPortal'] = None
                        objDetails['Target'] = None
                        objDetails['uuid'] = each_storage_disk.unique_path
                        objDetails['State'] = None
                        objDetails['Lun'] = None
                        objDetails['VM_NAME'] = None
        
                    objStat['name'] = defn.name
                    objStat['success'] = True
                    objStat['type'] = defn.type
                    objStat['id'] = defn.id
                    objStat['op'] = constants.GET_DISKS
            
        if objStorageDetails:
            objStat["STORAGE_DETAILS"] = objStorageDetails
        if objDetails:
            objDetailsList.append(objDetails)
            objStat["DETAILS"] = objDetailsList
        if objSummary:
            objStat["SUMMARY"] = objSummary
        return objStat
        
    def get_storage_disks_for_test(self, storage_id, show_available, vm_config_action, disk_option):
        objStat={}
        objSummary={}
        objDetailsList=[]
        objDetails={}
        objStorageDetails=[]
        disk_name=None
        storage_type=None
        total_size=0
        available_size=0
        vm_name=None        
        storage_disks=None
        if vm_config_action == "provision_vm" or vm_config_action == "provision_image":
            if disk_option == "CREATE_DISK":
                objStat = self.get_storage_for_test(storage_id)
                return objStat
            
        if show_available=="true":
            storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id, storage_allocated=False)
        else:
            storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
        
        if storage_id:
            defn = self.storage_manager.get_defn(storage_id)
            if defn:
                stats = defn.get_stats()
                if stats:
                    total_size = stats.total_size
                    objSummary["TOTAL"] = total_size
                    
                    storage_detail={}
                    storage_detail["AVAILABLE"] = stats.available_size
                    storage_detail["USED"] = stats.used_size
                    storage_detail["SIZE"] = stats.total_size
                    storage_detail["MOUNT"] = ""
                    storage_detail["FILESYSTEM"] = ""
                    storage_detail["VOLUME_GROUP"] = ""
                    storage_detail["uuid"] = ""
                    objStorageDetails.append(storage_detail)
        
        if storage_disks:
            for each_storage_disk in storage_disks:
                if objDetails:
                    objDetailsList.append(objDetails)
                    objDetails={}

                disk_name = each_storage_disk.disk_name
                storage_type = each_storage_disk.storage_type
                storage_id = each_storage_disk.storage_id
                
                objDetails['STORAGE_DISK_ID'] = each_storage_disk.id
                if each_storage_disk.storage_allocated == True:
                    objDetails['STORAGE_ALLOCATED'] = "Yes"
                else:
                    objDetails['STORAGE_ALLOCATED'] = "No"
                #objDetails['AVAILABLE'] = available_size #each_storage_disk.available_size
                objDetails['USED'] = each_storage_disk.size
                objDetails['SIZE'] = each_storage_disk.actual_size
                objDetails['CurrentPortal'] = each_storage_disk.current_portal
                objDetails['Target'] = each_storage_disk.target
                objDetails['uuid'] = each_storage_disk.unique_path
                objDetails['State'] = each_storage_disk.state
                objDetails['Lun'] = each_storage_disk.lun
                vm_name=None
                vm = self.get_vm_linked_with_storage(each_storage_disk.id)
                if vm:
                    vm_name = vm.name
                objDetails['VM_NAME'] = vm_name

                disk_name=None
                unique_path = each_storage_disk.unique_path
                if unique_path:
                    uuid_param = to_str(unique_path).split("/")
                    disk_name = uuid_param[len(uuid_param)-1]
                
                objDetails['DISKS'] = disk_name

            objStat['name'] = defn.name
            objStat['success'] = True
            objStat['type'] = storage_type
            objStat['id'] = storage_id
            objStat['op'] = constants.GET_DISKS
            
        if objStorageDetails:
            objStat["STORAGE_DETAILS"] = objStorageDetails
        if objDetails:
            objDetailsList.append(objDetails)
            objStat["DETAILS"] = objDetailsList
        if objSummary:
            objStat["SUMMARY"] = objSummary
        return objStat
        
    def storage_def_test(self,auth, storage_id, nodeId, groupId, site_id, type, mode, opts, scope, show_available="true", vm_config_action=None, disk_option=None):
        if mode == "SELECT":
            #here getting records from database, from storage_disks table.
            result = self.get_storage_disks_for_test(storage_id, show_available, vm_config_action, disk_option)
            return result
        
        try:
            #Clear earlier scan result from session if there is.
            self.storage_manager.RemoveScanResult()

            group=self.manager.getGroup(auth,groupId)
            managed_node=self.manager.getNode(auth,nodeId)
            try:
                managed_node.connect()
            except AuthenticationException ,ex:
                if opts.has_key('username') and opts.has_key('password'):
                    managed_node.set_credentials(opts['username'], opts['password'])
                    try:
                        managed_node.connect()
                    except AuthenticationException ,ex:
                        LOGGER.error(to_str(ex).replace("'",""))
                        return "{success: false,msg: '",to_str(ex).replace("'",""),"',error:'Not Authenticated'}"
                else:
                    return "{success: false,msg: '",to_str(ex).replace("'",""),"',error:'Not Authenticated'}"

            sd=None
            print mode,"storage_id=============",storage_id
            if mode=='TEST' or mode=='EDIT' or mode=='SELECT':
                sd = self.storage_manager.get_sd(storage_id, site_id, groupId, to_unicode(constants.STORAGE))
            else:
                sd = self.get_valid_sd(type,opts, scope)

            if site_id:
                if site_id == 'data_center':
                    site=self.manager.getSiteByGroupId(group.id)
                else:
                    site=self.manager.getSite(site_id)
            else:
                site = self.manager.getSiteByGroupId(group.id)
            result=self.test_storage_def(auth,managed_node,group,site,sd)
            if result and (mode=='NEW' or mode=='EDIT'):
                try:
                    #store scan result in session
                    session[constants.SCAN_RESULT] = result
                    session.save()
                except Exception, ex:
                    print_traceback()
                    LOGGER.error("Error while keeping the scan result in session: " + to_str(ex).replace("'", ""))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result

    def test_storage_def(self,auth,managed_node,group,site,sd):
        details = None
        testmsg = None

        try:
            details = self.storage_manager.get_sd_details(auth,sd, managed_node, group, site, to_unicode(constants.STORAGE), self.storage_manager)
            details = self.edit_test_output(details)
        except Exception, ex:
            testmsg=ex

        if details == None or len(details) == 0 or testmsg != None:
            if testmsg:
                LOGGER.info(to_str(testmsg).replace("'",""))
            else:
                testmsg = ""
            return dict(success=False,msg=to_str(testmsg).replace("'",""))
        else:
            details["success"]="true"
        LOGGER.debug("details"+ str(details))
        return details

    def get_defn(self, sd):
        if not sd:
            return ""
        desc = None
        if sd.type == constants.NFS:
            desc = sd.connection_props["server"] + ", " + \
                   sd.connection_props["share"]
        elif sd.type == constants.iSCSI:
            desc = sd.connection_props["server"] + ", " + \
                   sd.connection_props["target"]
        elif sd.type == constants.AOE:
            desc =  sd.connection_props["interface"]

        if not desc:
            return ""
        else:
            return desc

    def get_server_def_list(self,site_id, group_id, def_id):
        try:
            server_def_list=[]
            node_defns = self.sync_manager.get_node_defns(def_id, to_unicode(constants.STORAGE))
            if node_defns:
                for eachdefn in node_defns:
                    temp_dic={}
                    if eachdefn:
                        node = DBSession.query(ManagedNode).filter_by(id=eachdefn.server_id).first()

                        temp_dic['id']=eachdefn.server_id
                        if node:
                            temp_dic['name']=node.hostname
                        else:
                            temp_dic['name']=None
                        temp_dic['status']=eachdefn.status
                        if eachdefn.details:
                            temp_dic['details']=eachdefn.details
                        else:
                            temp_dic['details']=None

                        server_def_list.append(temp_dic)
        except Exception, ex:
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',rows=server_def_list)

    def get_total_storage(self,auth,site_id,group_id,scope=None):
        
        try:
            result=self.get_storage_def_list(auth,site_id,group_id,scope)
            total_storage=0.00
            stge_res=result.get('rows')
            for val in stge_res:
                if val.get('size'):
                    total_storage=total_storage+float(val.get('size'))
            
            return total_storage
        except Exception, ex:
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        
    def update_disks_size(self, auth):
        sites = DBSession.query(Site)
        if sites:
            for eachsite in sites:
                #site = DBSession.query(Sites).filter_by(id=eachsite.id).first()
                site_entity = auth.get_entity(eachsite.id)
                #get all groups in the site.
                group_entities = auth.get_entities(to_unicode(constants.SERVER_POOL), site_entity)
                #loop through each group in the site
                for eachgroup in group_entities:
                    group = DBSession.query(ServerGroup).filter_by(id=eachgroup.entity_id).first()
                    if group:
                        group_entity = auth.get_entity(group.id)
                        #get all nodes in the group
                        node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), group_entity)
                        #loop through each node in the group
                        for eachnode in node_entities:
                            node = DBSession.query(ManagedNode).filter_by(id=eachnode.entity_id).first()
                            server_def_link = DBSession.query(ServerDefLink).filter_by(server_id=node.id)
                            if server_def_link:
                                for each_link in server_def_link:
                                    defn = DBSession.query(StorageDef).filter_by(id=each_link.def_id).first()
                                    if defn:
                                        self.test_storage_def(auth, node, group, eachsite, defn)
                            
    def RemoveScanResult(self):
        result=self.storage_manager.RemoveScanResult()
        return result

    def SaveScanResult(self, storage_id, site_id):
        scan_result=None
        result=self.storage_manager.SaveScanResult(storage_id, self.manager, scan_result, site_id)
        return result


if __name__ == "__main__":
     storage_ser=StorageService()
     group = ServerGroup("Servers")
     try:
#        new_sd=storage_ser.get_valid_sd()
#        print new_sd
#        storage_ser.update_storage_def(new_sd,None, True)


         sdl=storage_ser.get_storage_def_list("Desktops")
         for sd in sdl:
            print "\n",sd

#        sd_to_remove = storage_manager.get_sd("8e7c40e6-d92a-65b7-15b7-1216abf4362d")
#        storage_manager.remove_sd(sd_to_remove,group)
     except Exception,(e):
        print "error=",e
