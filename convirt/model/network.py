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

# Manages network definitions
# Each network definition represents a network to which a VM can connect to.

#
# In future this would be enhanced to
# a. support VDE like networks (Private networks spanning machines)
# b. Centralized DHCP modifications
#

from datetime import datetime
from convirt.core.utils.utils import copyToRemote, getHexID, mkdir2
from convirt.core.utils.utils import dynamic_map
from convirt.core.utils.utils import to_unicode,to_str
import convirt.core.utils.utils
from convirt.core.utils.constants import *
constants = convirt.core.utils.constants
import os, tg
import pprint, traceback

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.schema import UniqueConstraint,Index
from sqlalchemy.orm import relation, backref

#Import for Storage and Network classes
from convirt.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink
from convirt.model.ManagedNode import ManagedNode
from convirt.model.Groups import ServerGroup
from convirt.model.Entity import Entity, EntityRelation
from convirt.model.Sites import Site
from convirt.model import DeclarativeBase, DBSession
from convirt.model.Authorization import AuthorizationService

from convirt.model.SyncDefinition import SyncDef

import logging
LOGGER = logging.getLogger("convirt.model")

# Bridge info
#  -- name : Bridge Name
#  -- phy_list : List of interfaces to be added.
#  -- dhcp : True or False
#  -- static_address = Map containing static ipv4 information for the bridge

# VLAN info  (furture)
#  -- id : vland id 

# Bond info (future)
#  - name : Bond name
#  - params : Bond settings (QOS, scheme etc)
#  - slaves : List of interfaces

# IPV4 information : (furture ? : Used for NAT forwarding)
#  - ip_network : network definition : 192.168.12.0/24

# DHCP information
#   dhcp_start: start address
#   dhcp_end: : end address
#   dhcp_server : server hosting dhcp. None for host private n/w meaning on the 
#                 managed network 
#   dhcp_server_creds : credentials to update dhcp server.
#

# nat_info : NAT information
#  interface : interfaces to forward to.

class NwDef(DeclarativeBase):
    PUBLIC_NW = to_unicode("PUBLIC_NW")
    HOST_PRIVATE_NW = to_unicode("HOST_PRIVATE_NW")
    NETWORK = to_unicode("NETWORK")

    __tablename__ = 'network_definitions'

    #Columns
    id = Column(Unicode(50), primary_key=True)
    type = Column(Unicode(50))
    name = Column(Unicode(50))
    description = Column(Unicode(100))
    is_deleted = Column(Boolean)
    bridge_info = Column(PickleType)
    vlan_info = Column(PickleType)
    bond_info = Column(PickleType)
    ipv4_info = Column(PickleType)
    dhcp_info = Column(PickleType)
    nat_info = Column(PickleType)
    scope = Column(String(2))

    def __init__(self,id, type, name, description, is_deleted, scope,
                 bridge_info=dynamic_map(),
                 vlan_info=dynamic_map(), 
                 bond_info=dynamic_map(),
                 ipv4_info=dynamic_map(),
                 dhcp_info=dynamic_map(),
                 nat_info=dynamic_map(),
                 status=None):
                 
        self.id = id
        if self.id is None:
            self.id = getHexID()
        
        self.type = type
        self.name = name
        self.description = description

        self.is_deleted = is_deleted

        self.bridge_info = bridge_info
        self.vlan_info   = vlan_info
        self.bond_info   = bond_info
        self.ipv4_info   = ipv4_info
        self.dhcp_info   = dhcp_info
        self.nat_info    = nat_info
        self.status = status           #definition status to be displayed in the grid - IN_SYNC/ OUT_OF_SYNC
        self.scope = scope              #To identify definition scope of definition since we are showing all the  definitions (server and pool level) at server level.

    def set_deleted(self, value=True):
        self.is_deleted = value


    def get_deleted(self):
        return self.is_deleted

    
    def is_nated(self):
        if self.nat_info and self.nat_info.get("interface"):
            return True
        else:
            return False

    def get_definition(self):
        desc = ""
        if self.type == self.HOST_PRIVATE_NW:
            desc += self.ipv4_info.get("ip_network")
            """
            if self.dhcp_info:
                desc += " (%s-%s)" % (self.dhcp_info.get("dhcp_start"), 
                                     self.dhcp_info.get("dhcp_end"))
            if self.is_nated():
                desc += ", NAT to "
                desc += self.nat_info.get("interface")
            """
        elif self.type == self.PUBLIC_NW:
            if self.bridge_info and self.bridge_info.get("phy_list"):
                if self.ipv4_info and self.ipv4_info.get("ip_network"):
                    desc = "%s (%s) connected to %s" % (self.bridge_info.get("name"), 
                                                        self.ipv4_info.get("ip_network"),
                                                        self.bridge_info.get("phy_list"))
                else:
                    desc = "%s connected to %s" % (self.bridge_info.get("name"), 
                                                   self.bridge_info.get("phy_list"))
            else:
                if self.ipv4_info and self.ipv4_info.get("ip_network"):
                    desc = "%s (%s)" % (self.bridge_info.get("name"), 
                                        self.ipv4_info.get("ip_network"))
                else:
                    desc = "%s" % (self.bridge_info.get("name"),)
        return desc

    def __repr__(self):
        return to_str({"id":self.id,
                    "type":self.type,
                    "name":self.name,
                    "description":self.description,
                    "bridge_info" : self.bridge_info,
                    "vlan_info" : self.vlan_info,
                    "bond_info" : self.bond_info,
                    "ipv4_info" : self.ipv4_info,
                    "dhcp_info" : self.dhcp_info,
                    "nat_info"  : self.nat_info,
                    "is_deleted" : self.is_deleted
                    })

Index("nwdef_id", NwDef.id)

class NwManager:
    s_scripts_location = "/var/cache/convirt/nw"
    s_common_scripts_location = "/var/cache/convirt/common"

    def __init__(self):
        self.defs = {}
        self.group_defn_status = []
        self.node_defn_status = []

    def getType(self):
        return to_unicode(constants.NETWORK)

    def get_defn(self, id):
        defn = DBSession.query(NwDef).filter_by(id=id).first()
        return defn

    # return the nw defintions for a given group    
    def get_defns(self, defType, site_id, group_id, node_id = None, op_level=None, auth=None, group_list=None):
        sync_manager = SyncDef()
        defs_array=[]

        if op_level == constants.SCOPE_DC:
            resultset = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type = defType)
            for row in resultset:
                defn = DBSession.query(NwDef).filter_by(id=row.def_id).first()  #is_deleted=False
                if defn:
                    #set the status here to return and display in grid with definition name.
                    defn.status = row.status
                    defs_array.append(defn)
            
            #getting definitions from each group 
            #getting definitions from each server in the group
            defs_array = self.getDefnsFromGroupList(auth, site_id, group_list, defType, defs_array)
        elif op_level == constants.SCOPE_SP:
            #getting definitions from group and each server in the group
            defs_array = self.getDefnsFromGroupList(auth, site_id, group_list, defType, defs_array)
        elif op_level == constants.SCOPE_S:
            resultset = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_type = defType)
            for row in resultset:
                defn = DBSession.query(NwDef).filter_by(id=row.def_id).first()	#is_deleted=False
                if defn:
                    #set the status here to return and display in grid with definition name.
                    defn.status = row.status
                    defs_array.append(defn)
        #Following condition is for NetworkService().get_available_nws() function.
        #when op_level is none then get all the networks created on the server (networks present in serverdeflinks table for that server)
        elif not op_level:
            resultset = DBSession.query(NwDef)\
                .join((ServerDefLink, ServerDefLink.def_id == NwDef.id))\
                .filter(ServerDefLink.server_id == node_id)\
                .filter(ServerDefLink.def_type == defType)
            
            for defn in resultset:
                if defn:
                    defs_array.append(defn)
                    
        return defs_array

    def getDefnsFromGroupList(self, auth, site_id, group_list, defType, defs_array):
        if group_list:
            #getting definitions from each group
            for group in group_list:
                resultset = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_type = defType)
                for row in resultset:
                    defn = self.get_defn(row.def_id)
                    if defn:
                        #set the status here to return and display in grid with definition name.
                        #node_id is None here
                        defn.status = self.get_defn_status(defn, defType, site_id, group.id, None)
                        defs_array.append(defn)
                
                #getting definitions from each server in the group
                for node in group.getNodeList(auth).itervalues():
                    resultset = DBSession.query(ServerDefLink).filter_by(server_id=node.id, def_type = defType)
                    for row in resultset:
                        defn = DBSession.query(NwDef).filter_by(id=row.def_id, scope=constants.SCOPE_S).first()
                        if defn:
                            #set the status here to return and display in grid with definition name.
                            defn.status = row.status
                            defs_array.append(defn)
        return defs_array

    def get_defn_status(self, defn, defType, site_id, group_id, node_id):
        status=None
        if defn.scope == constants.SCOPE_DC:
            dc_defn = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_id = defn.id, def_type = defType).first()
            if dc_defn:
                status = dc_defn.status
        elif defn.scope == constants.SCOPE_SP:
            sp_defn = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id = defn.id, def_type = defType).first()
            if sp_defn:
                status = sp_defn.status
        elif defn.scope == constants.SCOPE_S:
            s_defn = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_id = defn.id, def_type = defType).first()
            if s_defn:
                status = s_defn.status
        return status

    # return the Network definitions for a given group    
    def getSiteDefListToAssociate(self, site_id, group_id, defType):
        sdArray=[]
        if site_id:
            dc_rs = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=defType)
            for row in dc_rs:
                sp_def = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=row.def_id, def_type=defType).first()
                if not sp_def:
                    defn = DBSession.query(NwDef).filter_by(id=row.def_id, scope=constants.SCOPE_DC).first()
                    if defn:
                        defn.status = row.status
                        sdArray.append(defn)
        return sdArray

    #This function would convert the specified object into dictionary object. This dictionary object would be stored in database.
    def get_dic(self, objDic):
        objDic_new={}
        objArrayKeys=[]
        objArrayKeys = objDic.keys()
        for key in objArrayKeys:
            objDic_new[key] = objDic[key]

        if objDic_new:
            returnVal = objDic_new
        else:
            returnVal = None
        return returnVal

    def get_group_status(self, def_id, group_id):
        for g in self.group_defn_status:
            if g.group_id == group_id and g.def_id == def_id :
                return g

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
        s_src_scripts_location=tg.config.get("nw_script")
        s_src_scripts_location=os.path.abspath(s_src_scripts_location)
        
        s_common_src_scripts_location=tg.config.get("common_script")
        s_common_src_scripts_location=os.path.abspath(s_common_src_scripts_location)

        LOGGER.info("Source script location= " + to_str(s_src_scripts_location))
        LOGGER.info("Destination script location= " + to_str(self.s_scripts_location))
        copyToRemote(s_src_scripts_location, dest_node, self.s_scripts_location)
        
        LOGGER.info("Common source script location= " + to_str(s_common_src_scripts_location))
        LOGGER.info("Common destination script location= " + to_str(self.s_common_scripts_location))
        copyToRemote(s_common_src_scripts_location, dest_node, self.s_common_scripts_location)

    def exec_script(self, node, group, defn, defType, op=constants.GET_DETAILS):
        type = defn.type

        self.prepare_scripts(node, type, defType)
        script_name = os.path.join(self.s_scripts_location,"scripts",
                                   "nw.sh")
        
        log_dir = node.config.get(prop_log_dir)
        
        if log_dir is None or log_dir == '':
            log_dir = DEFAULT_LOG_DIR


        log_filename = os.path.join(log_dir, "nw/scripts",
                                         "nw_sh.log")

        # create the directory for log files
        mkdir2(node,os.path.dirname(log_filename))

        br_info = self.props_to_cmd_param(defn.bridge_info)
        vlan_info = self.props_to_cmd_param(defn.vlan_info)
        ipv4_info = self.props_to_cmd_param(defn.ipv4_info)
        bond_info = self.props_to_cmd_param(defn.bond_info)
        dhcp_info = self.props_to_cmd_param(defn.dhcp_info)
        nat_info = self.props_to_cmd_param(defn.nat_info)

        # help script find its location
        script_loc = os.path.join(self.s_scripts_location, "scripts")
        
        if type:
            script_args = " -t " + type
        if br_info:
            script_args += " -b " + br_info
        if vlan_info:
            script_args += " -v " + vlan_info
        if ipv4_info:
            script_args += " -i " + ipv4_info
        if bond_info:
            script_args += " -p " + bond_info
        if dhcp_info:
            script_args += " -d " + dhcp_info
        if nat_info:
            script_args += " -n " + nat_info
        if op:
            script_args += " -o " + op
        if script_loc:
            script_args += " -s " + script_loc
        if log_filename:
            script_args += " -l " + log_filename 

        cmd = script_name +  script_args
        LOGGER.info("Command= " + to_str(cmd))
        
        # execute the script
        output = "Success"
        exit_code = 0
        (output, exit_code) = node.node_proxy.exec_cmd(cmd)

        LOGGER.info("Exit Code= " + to_str(exit_code))
        LOGGER.info("Output of script= " + to_str(output))

        #if exit_code != 0:
        #    raise Exception(output)
        
        return (exit_code, output)

    def CheckOp(self, op, errs):
        if not (op in [constants.ATTACH, constants.DETACH]):
            errs.append("Invalid network defn sync op " + op) 
            raise Exception("Invalid network defn sync op " + op )
        return errs

    def getSyncMessage(self, op):
        messasge=None
        if op == constants.ATTACH:
            messasge="Network created successfully."
        elif op == constants.DETACH:
            messasge="Network removed successfully."
        return messasge

    def associate_defn_to_groups(self, site, sp_ids, defn, defType, op, def_manager, auth, errs):
        pass

    def sync_node_defn(self, node, group_id, site_id, defn, defType, op, def_manager=None, update_status=True, errs=None, processor=None):
        sync_manager = SyncDef()
        sync_manager.sync_node_defn(node, group_id, site_id, defn, defType, op, def_manager, update_status, errs)
        
    def remove_storage_disk(self, storage_id):
        pass
    
    def is_storage_allocated(self, storage_id):
        return False
    
    def SaveScanResult(self, storage_id, grid_manager, scan_result=None, site_id=None):
        pass
    
    def RemoveScanResult(self, scan_result=None):
        pass
    
    def remove_vm_links_to_storage(self, storage_id):
        pass
    
    def Recompute(self, defn):
        pass