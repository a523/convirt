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

from convirt.model.VM import vifEntry
from convirt.core.utils.utils import dynamic_map,randomMAC
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
from convirt.core.utils.IPy import *
from convirt.viewModel.NodeService import NodeService
from convirt.viewModel.ImageService import ImageService
import Basic
from convirt.model import DBSession
from convirt.model.network import NwDef, NwManager
from convirt.model.Groups import ServerGroup
from convirt.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink
from convirt.model.ManagedNode import ManagedNode
from convirt.model.SyncDefinition import SyncDef
from convirt.model.Sites import Site
import convirt.core.utils.utils
from convirt.core.utils.constants import *
constants = convirt.core.utils.constants
from convirt.model.DBHelper import DBHelper
from convirt.model.VM import VM
import traceback
import logging
LOGGER = logging.getLogger("convirt.viewModel")

nw_type_map = {NwDef.PUBLIC_NW : "Public",
               NwDef.HOST_PRIVATE_NW: "Host Private ",
               NwDef.NETWORK: "Network"
               }
available_nws=[{'name':"Default" ,'value': "$DEFAULT_BRIDGE"},
             {'name':"xenbr0" ,'value': "xenbr0"},
             {'name':"xenbr1" ,'value': "xenbr1"},
             {'name':"xenbr2" ,'value': "xenbr2"},
             {'name':"br0"    ,'value': "br0"},
             {'name':"br1"    ,'value': "br1"},
             {'name':"br2"    ,'value': "br2"},
             {'name':"eth0"   ,'value': "eth0"},
             {'name':"eth1"   ,'value': "eth1"},
             {'name':"eth2"   ,'value': "eth2"},
            ]

class NetworkService:
    def __init__(self):
        self.nw_manager = Basic.getNetworkManager()
        self.managed_node = Basic.getManagedNode()
        self.sync_manager = SyncDef()
        self.manager=Basic.getGridManager()

    def get_available_nws(self, auth,mode,node_id, op_level=None):
        result=[]
        if mode in ["edit_image_settings"]:
            result = available_nws
            
        else: # "PROVISION_VM", "EDIT_VM_CONFIG"
            nw_map = {}

            managed_node=NodeService().get_managed_node(auth,node_id)
            if mode in ["provision_vm" ,"provision_image"]:
                nw_map["Default"] = "$DEFAULT_BRIDGE"
                result.append(dict(value="$DEFAULT_BRIDGE",name="Default"))

            bridges = managed_node.get_bridge_info()
            site_id=None
            group_id = None
            #set the op_level none so that we can get all the networks created on the server (networks present in serverdeflinks table for that server)
            op_level=None
            for nw in self.nw_manager.get_defns(to_unicode(constants.NETWORK), site_id, group_id, node_id, op_level):
                bridge=None
                network = None
                if nw.ipv4_info and nw.ipv4_info.get("ip_network"):
                    network = nw.ipv4_info.get("ip_network")

                if nw.bridge_info and nw.bridge_info.get("name"):
                    bridge = nw.bridge_info.get("name")


                if bridge and network:
                    desc = "%s (%s, %s)" % (nw.name,
                                            bridge,
                                            network)
                elif bridge:
                    desc = "%s (%s)" % (nw.name,
                                        bridge,)
                elif network:
                    desc = "%s (%s)" % (nw.name,
                                        network,)

                if nw.bridge_info and nw.bridge_info.get("name"):
                    nw_map[desc] =  nw.bridge_info.get("name")
                    result.append(dict(value=nw.bridge_info.get("name"),name=desc))            
            if bridges is not None:
                for n in bridges.itervalues():
                    name = n["name"]
                    if name not in nw_map.itervalues():
                        desc = name + " network"
                        if n.get("network"):
                            desc = "%s (%s,%s)" % (desc, name, n["network"])
                        nw_map[desc] = name
                        result.append(dict(value=name,name=desc))
            
            #init_combo(self.widgets.available_nw_combo,nw_map)
        return result

    def get_new_nw_entry(self, image_conf = None):
        return (vifEntry('mac=$AUTOGEN_MAC,bridge=$DEFAULT_BRIDGE'), None)

    def get_vif_entry(self,auth,mode,node_id):
        if mode in ["EDIT_IMAGE","PROVISION_VM"]:
            (vif_entry, nw_entry) = self.get_new_nw_entry(None)
        else:
            # generate mac address and get the DEFAULT_BRIDGE if any
            managed_node=NodeService().get_managed_node(auth,node_id)
            mac=randomMAC()
            if managed_node is not None:
                bridge = managed_node.get_default_bridge()

            if not bridge:
                bridge="xenbr0"
            if managed_node.platform == 'kvm':
                bridge='br0'
                
            vif_entry=vifEntry('mac=%s,bridge=%s' % (mac,bridge))
        return vif_entry

    def get_nws(self,auth,image_id=None,dom_id=None,node_id=None, op_level=None):
        vm_config=None
        if dom_id is not None:
#                dom=NodeService().get_dom(auth,dom_id,node_id)
            dom=DBHelper().find_by_name(VM,dom_id)
            vm_config=dom.get_config()

        elif image_id is not None:
            image=ImageService().get_image(auth,image_id)
            (vm_config,img_conf)=image.get_configs()

        if not vm_config:
            return
        managed_node=None
        if node_id is not None:
            managed_node=NodeService().get_managed_node(auth,node_id)
            if managed_node is not None:
                self.managed_node=managed_node
        vifs = vm_config.getNetworks()
        result=[]

        for vif in vifs:
            result.append(self.get_nw_entry(vif, op_level))
        
        return result


    def get_new_nw(self,auth,image_id,mode,node_id, op_level=None):
#        if image_id is not None:
#            image=ImageService().get_image(auth,image_id)
#            (vm_config,image_config)=image.get_configs()
        result=[]
        if mode in ["edit_image_settings","provision_vm","provision_image"]:
            (vif_entry, nw_entry) = self.get_new_nw_entry()
        else:
            managed_node=NodeService().get_managed_node(auth,node_id)
            # generate mac address and get the DEFAULT_BRIDGE if any
            mac=randomMAC()
            if managed_node is not None:
                bridge = managed_node.get_default_bridge()

            if not bridge:
                bridge="xenbr0"
            if managed_node.platform == 'kvm':
                bridge='br0'

            vif_entry=vifEntry('mac=%s,bridge=%s' % (mac,bridge))
            nw_entry = None

#       for vif in vif_entry:
        result.append(self.get_nw_entry(vif_entry, op_level))
        
        return result

    def get_edit_network_details(self,nw_id):
        try:
            network_value={}
            nw = self.nw_manager.get_defn(nw_id)
            print "network===name",nw.name

            dhcp_range_value = None
            #This change is done to read the attributes of dict object.
            if nw.dhcp_info and nw.dhcp_info["dhcp_start"] and\
                    nw.dhcp_info["dhcp_end"]:
                dhcp_range_value = nw.dhcp_info["dhcp_start"] + " - " +\
                    nw.dhcp_info["dhcp_end"]
	    
            network_value["nw_id"]=nw_id
            network_value["name"]=nw.name
            network_value["description"]=nw.description
            network_value["bridge_info_name"]=nw.bridge_info["name"]
            network_value["bridge_info_phy_list"]=None #Takeing None since we are not getting phy_list attribute in dict
            network_value["nw_bridge_info_name"]=nw.bridge_info["name"]
            network_value["nw_ipv4_info_ip_network"]=nw.ipv4_info["ip_network"]
            network_value["dhcp_range_value"]=dhcp_range_value
            network_value["nw_nat_info_interface"]=nw.nat_info["interface"]
            #network_value["nw_nat_forward"]=nw.is_nated()
            if nw.nat_info and nw.nat_info["interface"]:
                network_value["nw_nat_forward"]=True
            else:
                network_value["nw_nat_forward"]=False
            
        except Exception, ex:
            raise ex
        return network_value

    def edit_nw_defn(self,nw_id,nw_name,nw_desc):
        nw_name=(nw_name)
        nw_desc=(nw_desc)
        try:
            errmsgs=[]
            common_desc = { "Network name":nw_name,
                            "Network description":nw_desc}
            for key in common_desc:
                v = common_desc.get(key)
                if not v:
                    errmsgs.append("%s is required." % (key,))
            if errmsgs:
                if len(errmsgs)>0:
                     return {'success':False,'msg':to_str(errmsgs).replace("'","")}
            
            #Identify definition scope here. Since we do not have node here. We are checking the definition in spdeflinks table. If definition is present in the table then the definition is at pool level else it is at server level.
            # going ahead we could think of adding scope in the defintion tables so that we can directly take the scope from definition
            row = DBSession.query(SPDefLink).filter_by(def_id = nw_id).first()
            if row:
                scope = constants.SCOPE_SP
            else:
                scope = constants.SCOPE_S
            
            #Validation for duplicate name
            alldefns=None
            if scope == constants.SCOPE_S:
                node_defn = DBSession.query(ServerDefLink).filter_by(def_id = nw_id).first()
                if node_defn:
                    alldefns = DBSession.query(ServerDefLink).filter_by(server_id = node_defn.server_id, def_type = to_unicode(constants.NETWORK))
            elif scope == constants.SCOPE_SP:
                group_defn = DBSession.query(SPDefLink).filter_by(def_id = nw_id).first()
                if group_defn:
                    alldefns = DBSession.query(SPDefLink).filter_by(group_id = group_defn.group_id, def_type = to_unicode(constants.NETWORK))
            elif scope == constants.SCOPE_DC:
                group_defn = DBSession.query(DCDefLink).filter_by(def_id = nw_id).first()
                if group_defn:
                    alldefns = DBSession.query(DCDefLink).filter_by(site_id = group_defn.site_id, def_type = to_unicode(constants.NETWORK))
            
            if alldefns:
                for eachdefn in alldefns:
                    defnTemp = DBSession.query(NwDef).filter_by(id=eachdefn.def_id, name=nw_name).first()
                    if defnTemp and defnTemp.id != nw_id:
                        raise Exception("Network definition with the same name already exists")   

            defn = DBSession.query(NwDef).filter_by(id=nw_id).first()
            group = None
            auth = None
            self.sync_manager.update_defn(defn, nw_name, nw_desc, None, group, auth, constants.NETWORK, constants.ATTACH, self.nw_manager, 'UPDATE_NETWORK_DEF')
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'msg':'Network Edited'}
            
    def get_nw_det(self,bridge,mac,model, op_level=None):
        result=[]
        vif_entry=vifEntry('mac=%s,bridge=%s,model=%s' % (mac,bridge,model))
        
#       for vif in vif_entry:
        result.append(self.get_nw_entry(vif_entry, op_level))

        return result

    def get_nw_entry(self, vif_entry, op_level=None):
        nw = self.find_nw(vif_entry, op_level)
        (nw_type, nw_name, nw_desc, nw_mac, bridge_name,model) = self.get_nw_details(vif_entry, nw)
#        print "nw_type===",nw_type,"nw_name==", nw_name,"nw_desc==", nw_desc, "nw_mac==",nw_mac,"brigde==" ,bridge_name
        return dict(type=nw_type, name=nw_name, description=nw_desc, mac=nw_mac,bridge=bridge_name,model=model)

    def find_nw(self, vif, op_level=None):
        bridge_name = vif.get_bridge()
        site_id=None
        group_id = None
        for defn in self.nw_manager.get_defns(to_unicode(constants.NETWORK), site_id, group_id, self.managed_node.id, op_level):
            if defn.bridge_info and defn.bridge_info["name"] == bridge_name:
                return defn

    def get_nw_details(self, vif, nw):
        nw_bridge_name = vif.get_bridge()
        nw_mac = vif.get_mac()
        if nw_mac == "$AUTOGEN_MAC":
            nw_mac = "Autogenerated"

        if nw_bridge_name == "$DEFAULT_BRIDGE":
            nw_bridge_name = "Default"

        nw_name = None
        nw_type = None
        nw_desc = None
        if not nw:
            if nw_bridge_name is not None:
                nw_name = nw_bridge_name + " Network"
                nw_type = NwDef.PUBLIC_NW
                nw_desc = nw_bridge_name
        else:
            nw_name = nw.name
            nw_type = nw.type
            nw_desc = "%s (%s)" % (nw.get_definition(), vif.get_bridge())

        return (nw_type, nw_name, nw_desc, nw_mac,vif.get_bridge(),vif.get_item("model"))

    def get_linked_entity_list(self, auth, defn):
        str_group_list = None
        if defn.scope == constants.SCOPE_DC:
            site_defns = DBSession.query(DCDefLink).filter_by(def_id=defn.id)
            if site_defns:
                for eachdefn in site_defns:
                    site = DBSession.query(Site).filter_by(id=eachdefn.site_id).first()
                    if str_group_list:
                        str_group_list = str_group_list + ", " + site.name
                    else:
                        str_group_list = site.name
        elif defn.scope == constants.SCOPE_SP:
            group_defns = DBSession.query(SPDefLink).filter_by(def_id=defn.id)
            if group_defns:
                for eachdefn in group_defns:
                    group = DBSession.query(ServerGroup).filter_by(id=eachdefn.group_id).first()
                    if str_group_list:
                        str_group_list = str_group_list + ", " + group.name
                    else:
                        str_group_list = group.name
        elif defn.scope == constants.SCOPE_S:
            node_defns = DBSession.query(ServerDefLink).filter_by(def_id=defn.id)
            if node_defns:
                for eachdefn in node_defns:
                    node = DBSession.query(ManagedNode).filter_by(id=eachdefn.server_id).first()
                    if str_group_list:
                        str_group_list = str_group_list + ", " + node.hostname
                    else:
                        str_group_list = node.hostname

        return str_group_list

    def get_nw_defns(self,auth,site_id, group_id, node_id, op_level=None):
        #We were not getting any records so we have added group_id here.
        group_list=[]
        if op_level == constants.SCOPE_DC:
            #getting all the server pools with in data center
            group_list = self.manager.getGroupList(auth, site_id)
        elif op_level == constants.SCOPE_SP:
            group = DBSession.query(ServerGroup).filter_by(id=group_id).first()
            #here group_list would have only one group
            group_list.append(group)
            
        defns = self.nw_manager.get_defns(to_unicode(constants.NETWORK), site_id, group_id, node_id, op_level, auth, group_list)

        bridge_list = []
        result=[]
        
        for defn in defns:
            linked_entity_list = None
            server_name = None
            associated = False
            node_defn = DBSession.query(ServerDefLink).filter_by(def_id=defn.id).first()
            if node_defn:
                node = DBSession.query(ManagedNode).filter_by(id=node_defn.server_id).first()
                if node:
                    server_name = node.hostname

                associated = True
            
            linked_entity_list = self.get_linked_entity_list(auth, defn)
            
            result.append(dict(id=defn.id, name=defn.name, type=nw_type_map[defn.type], description=defn.description, definition=defn.get_definition(), status=defn.status, scope=defn.scope, associated=associated,server=server_name,displayscope=linked_entity_list))
            
            #first check None then inner property
            if defn.bridge_info:
                if defn.bridge_info["name"]:
                    bridge_list.append(defn.bridge_info["name"])
        
        return result

    def get_nw_dc_defns(self, auth, site_id, group_id, node_id):
        result=[]
        defns = self.nw_manager.getSiteDefListToAssociate(site_id, group_id, to_unicode(constants.NETWORK))
        for defn in defns:
            result.append(dict(id=defn.id, name=defn.name, type=nw_type_map[defn.type], description=defn.description, definition=defn.get_definition(), status=defn.status, scope=defn.scope))
        return result

    def get_server_def_list(self,site_id, group_id, def_id):
        try:
            server_def_list=[]
            node_defns = self.sync_manager.get_node_defns(def_id, to_unicode(constants.NETWORK))
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
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',rows=server_def_list)

    def get_nw_address_space_map(self):
        result=[]
        try:
            nw_address_space = { "10.1.0.0/24": "10.1.0.0/24",
                                 "10.2.0.0/24": "10.2.0.0/24",
                                 "10.3.0.0/24": "10.3.0.0/24",
                                 "10.4.0.0/24": "10.4.0.0/24",
                                 }
            for key in nw_address_space.keys():
                result.append(dict(name=key,value=nw_address_space.get(key)))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        return result

    def get_nw_nat_fwding_map(self,auth,node_id ):
        result=[]
        try:
            nw_nat_fwding_map = {"Any interface" : "ANY",}

            managed_node=NodeService().get_managed_node(auth,node_id)
            if managed_node is not None:
                nics = managed_node.get_nic_info()
                if nics:
                    for nic in nics.itervalues():
                        nic_name = nic["name"]
                        nw_nat_fwding_map[nic_name] = nic_name

            for key in nw_nat_fwding_map.keys():
               result.append(dict(name=key,value=nw_nat_fwding_map.get(key)))
            
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        return result

    def nw_address_changed(self, ip_value):
#        value = get_value(widget)
        result={}
        try:
            if ip_value:
                x = IP(ip_value)
                start = x[len(x)/2]
                end = x[-1]
                range = "%s-%s" % (start.strNormal(), end.strNormal())
                result["range"]=range
            else:
                result["range"]=""
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        return result
    
    def get_new_private_bridge_name(self,auth,node_id,group_id, site_id, op_level=None):
        result={}
        try:
            bridge=self.get_new_bridge_name(auth,"pbr%d",node_id,group_id,site_id, op_level)
            result["bridge"]=bridge
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        return result

    def get_new_bridge_name(self, auth,template,node_id,group_id,site_id, op_level=None):
        new_name = ""
        bridge_names = self.get_all_known_bridges(auth,node_id,group_id,site_id, op_level)
        # convention name pbr0-pbrN
        for i in range(0,1000):
            name = template % (i,)
            if name in bridge_names:
                continue
            else:
                new_name = name
                break

        return new_name

    def get_all_known_bridges(self,auth,node_id,group_id,site_id, op_level=None):
        bridge_names = []
        
        managed_node=NodeService().get_managed_node(auth,node_id)
        if managed_node is not None:
            bridges = managed_node.get_bridge_info()
            if bridges:
                bridge_names = bridge_names + bridges.keys()

        if self.nw_manager:
#            pool_id, node_id = get_ids_from_context(self.context)
            #we are passing group_id here for getting server pool level definitions
            defns = self.nw_manager.get_defns(to_unicode(constants.NETWORK), site_id, group_id, node_id, op_level)
            #check None here
            if defns is not None:
                for defn in defns:
                    if defn.bridge_info and defn.bridge_info["name"]:
                        n = defn.bridge_info["name"]
                        if n not in bridge_names:
                            bridge_names.append(n)

        return bridge_names
        
    def get_status(self, def_id, pool_id, node_id):
        status = "N/A" #network.UNKNOWN
        if pool_id is None:
            nstatus_info = self.nw_manager.get_node_status(def_id,node_id)
            if nstatus_info:
                status = nstatus_info.status
        else:
            gstatus_info = self.nw_manager.get_group_status(def_id,pool_id)
            if gstatus_info:
                status = gstatus_info.status

        return status

    def associate_nw_defns(self, site_id, group_id, node_id, def_type, def_ids, auth, op_level=None):
        site = self.manager.getSite(site_id)
        group = self.manager.getGroup(auth,group_id)
        
        def_id_list = def_ids.split(",")
        for def_id in def_id_list:
            defn = self.nw_manager.get_defn(def_id)
            node = DBSession.query(ManagedNode).filter_by(id=node_id).first()
            try:
                #associate=True
                self.sync_manager.add_defn(defn, site, group, node, auth, to_unicode(constants.NETWORK), constants.ATTACH, "ADD_NETWORK_DEF", self.nw_manager, self.manager, op_level, None)
            except Exception, ex:
                print_traceback()
                LOGGER.error(to_str(ex).replace("'",""))
                #if we get any exception while adding/ sync definition then are removing the definition.
                add_mode=True
                group_list = self.manager.getGroupList(auth, site_id)
                self.sync_manager.remove_defn(defn, site, group, node, auth, to_unicode(constants.NETWORK), constants.DETACH, "REMOVE_NETWORK_DEF", self.nw_manager, self.manager, add_mode, group_list, op_level)
                return {'success':False,'msg':to_str(ex).replace("'","")}
        return  {'success':True,'msg':'Network Added'}

    def add_nw_defn(self,auth,nw_name,nw_desc,nw_device,nw_address_space,nw_dhcp_range,nat_radio,nw_nat_fwding,site_id,group_id,node_id,scope=None):
#        print   "nw_desc,nw_device,nw_address_space,nw_dhcp_range,nw_nat_fwding,pool_id,node_id",
        nw_name=(nw_name)
        nw_desc=(nw_desc)
        nw_device=(nw_device)
        nw_address_space=(nw_address_space)
        nw_dhcp_range=(nw_dhcp_range)        
        node_id=(node_id)

        ## Jd
        ## For now create host private networks.
        ## This needs to be revisited when we add VLAN support.
        scope=constants.SCOPE_S

        if site_id == 'data_center':
            site = self.manager.getSiteByGroupId(group_id)
            if site:
                site_id = site.id
        else:
            site = self.manager.getSite(site_id)

        group_list = self.manager.getGroupList(auth, site_id)
        try:
            nw_id = None
            group = None
            managed_node = None
            new_nw_def = None

            #we were getting server pool None so we have added this query here
            if group_id:
                group= DBSession.query(ServerGroup).filter_by(id = group_id).first()
                
            managed_node=NodeService().get_managed_node(auth,node_id)

    #        if is_public=='true':
    #            nw_type = NwDef.PUBLIC_NW
    #        else:
    #            nw_type = NwDef.HOST_PRIVATE_NW
            #nw_type= self.get_nw_type()

            nw_type=NwDef.HOST_PRIVATE_NW #Set to Private Network for now
            errors=self.validate_new_nw_def(auth,"ADD",nw_type,nw_name,nw_desc,nw_device,nw_address_space,nw_dhcp_range,nat_radio,nw_nat_fwding,site_id,group_id,node_id, scope)
            if errors:
                if len(errors)>0:
                    return {'success':False,'msg':to_str(errors).replace("'","")}

            if nw_type == NwDef.PUBLIC_NW:
    #            nw_device = nw_device_entry
                nw_phy_if = nw_phy_if_entry
                bridge_info = dynamic_map()
                bridge_info.name = nw_device
                bridge_info.phy_list = nw_phy_if
                new_nw_def = NwDef(nw_id,nw_type,nw_name,nw_desc,False,scope,
                                    bridge_info=bridge_info)

            else:
#
                bridge_info = dynamic_map()
                bridge_info.name = nw_device

                ipv4_info = dynamic_map()
                ipv4_info.ip_network = nw_address_space

                # assign first address in the range to the
                # bridge
                ip = IP(nw_address_space)
                bridge_info.ip_address = ip[1].strNormal()
                bridge_info.netmask = ip.netmask().strNormal()

                dhcp_info = dynamic_map()
                r = nw_dhcp_range.split("-")
                if len(r) == 2:
                    dhcp_info.dhcp_start = r[0].strip()
                    dhcp_info.dhcp_end = r[1].strip()

                nat_info = dynamic_map()
                nat_info.interface = nw_nat_fwding

                new_nw_def = NwDef(nw_id,nw_type,nw_name,nw_desc,False,scope,
                                    bridge_info=bridge_info,ipv4_info=ipv4_info,dhcp_info=dhcp_info,nat_info=nat_info)
                #convert following parameters into dictionary object to save into network_definitions table.
                new_nw_def.bridge_info = self.get_dic(new_nw_def.bridge_info)
                new_nw_def.vlan_info = self.get_dic(new_nw_def.vlan_info)
                new_nw_def.bond_info = self.get_dic(new_nw_def.bond_info)
                new_nw_def.ipv4_info = self.get_dic(new_nw_def.ipv4_info)
                new_nw_def.dhcp_info = self.get_dic(new_nw_def.dhcp_info)
                new_nw_def.nat_info = self.get_dic(new_nw_def.nat_info)

#                manager = Basic.getGridManager()
#                group=manager.getGroup(pool_id)
#                print "pool_id==",pool_id,"node_id==",node_id
                
                errs = []

                #Validations
                if scope == constants.SCOPE_S:
                    alldefns = DBSession.query(ServerDefLink).filter_by(server_id = managed_node.id, def_type = to_unicode(constants.NETWORK))
                elif scope == constants.SCOPE_SP:
                    alldefns = DBSession.query(SPDefLink).filter_by(group_id = group_id, def_type = to_unicode(constants.NETWORK))
                elif scope == constants.SCOPE_DC:
                    alldefns = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type = to_unicode(constants.NETWORK))

                for node_defn in alldefns:
                    #Check for duplicate name
                    rowNF = DBSession.query(NwDef).filter_by(id=node_defn.def_id, name=new_nw_def.name).first()
                    if rowNF:
                        return {'success':False,'msg':"Network definition with the same name already exists"}
                        #raise Exception("Network definition with the same name already exists")

                    #Check for address range
                    rowNF = DBSession.query(NwDef).filter_by(id=node_defn.def_id).first()
                    if rowNF:
                        if new_nw_def.ipv4_info.get("ip_network") == rowNF.ipv4_info.get("ip_network"):
                            return {'success':False,'msg':"Network definition with the same address space already exists"}
                            #raise Exception("Network definition with the same address space already exists")


                errs = self.sync_manager.add_defn(new_nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.ATTACH, "ADD_NETWORK_DEF", self.nw_manager, self.manager, scope)
                
                if scope == constants.SCOPE_DC or scope == constants.SCOPE_SP:
                    oos_count = 0
                    status = to_unicode(constants.IN_SYNC)
                    details = None
                    self.sync_manager.add_node_defn(managed_node.id, new_nw_def.id, to_unicode(constants.NETWORK), status, details, constants.SCOPE_S)
                    op = constants.ATTACH
                    update_status=True
                    errs=[]
                    self.nw_manager.sync_node_defn(managed_node, group_id, site_id, new_nw_def, to_unicode(constants.NETWORK), op, self.nw_manager, update_status, errs)
                    
                if errs:
                    if len(errs) > 0:
                        add_mode=True
                        self.sync_manager.remove_defn(new_nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.DETACH, "REMOVE_NETWORK_DEF", self.nw_manager, self.manager, add_mode, group_list, scope)
                        return {'success':False,'msg':to_str(errs).replace("'","")}
            print "WEb  New definition ",new_nw_def

        except Exception, ex:
            import traceback
            print print_traceback()
            print "Exception===",ex
            LOGGER.error(to_str(ex).replace("'",""))
            #if we get any exception while adding/ sync definition then are removing the definition.
            add_mode=True
            if new_nw_def:
                self.sync_manager.remove_defn(new_nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.DETACH, "REMOVE_NETWORK_DEF", self.nw_manager, self.manager, add_mode, group_list, scope)
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return  {'success':True,'msg':'Network Added'}

    def validate_new_nw_def(self,auth,mode,nw_type,nw_name,nw_desc,bridge,nw_address_space,nw_dhcp_range,nat_radio,nw_nat_fwding,site_id,group_id,node_id, op_level):
        errmsgs = []


        priv_nw_desc=  {"Network bridge device":bridge,
                            "Address space":nw_address_space,
                            "DHCP address range":nw_dhcp_range,
                            "NAT Forwarding":nw_nat_fwding,
                            "Network name":nw_name,
                            "Network description":nw_desc,
                            "nat_radio":nat_radio
                            }
#        pub_widget_desc= [ ("nw_device_entry", "Network bridge device"),
#                           ("nw_phy_if_entry", "Physical Netowrk interface"),
#                           ]
#        common_desc = [ nw_name,nw_desc]


        if mode == "ADD" : # no edit planned            
            for key in priv_nw_desc.keys():
                    v = priv_nw_desc.get(key)
                    if nat_radio=="false":
                        if key == "NAT Forwarding":
                            continue
                    if not v:
                        errmsgs.append("%s is required." % (key,))

            if nw_type == NwDef.HOST_PRIVATE_NW:
#                nw_dhcp_range = get_value(self.widgets.nw_dhcp_range_entry)
                if nw_dhcp_range:
                    r = nw_dhcp_range.split("-")
                    if len(r) !=2:
                        errmsgs.append("DHCP should be in start-end format. e.g. 192.168.1.128 - 192.168.1.254")

#            priv_bridge_name = get_value(self.widgets.nw_priv_device_entry)
#            print "bridge===",bridge,"---BRIdg-",self.get_all_known_bridges(node_id,pool_id)
            if bridge in self.get_all_known_bridges(auth,node_id,group_id,site_id, op_level):
                errmsgs.append("Bridge (%s) already exist, please choose different name." % (bridge))

        else:
            common_desc = { "Network name":nw_name,
                            "Network description":nw_desc}
            for key in common_desc:
                v = common_desc.get(key)
                if not v:
                    errmsgs.append("%s is required." % (key,))

        return errmsgs
    
    #Added group_id parameter here to get group.
    def remove_nw_defn(self,auth,def_id, site_id, group_id, node_id, op_level=None):
        try:
            def_id=(def_id)
            node_id=(node_id)
            nw_def = self.nw_manager.get_defn(def_id)
	    
#            print "reeeeeeeeee",nw_def
#            network_name=nw_def.name
#            manager = Basic.getGridManager()
#            group=manager.getGroup(pool_id)
            
            site=self.manager.getSite(site_id)
            group=None
            if group_id:
                group= DBSession.query(ServerGroup).filter_by(id = group_id).first()
            
            managed_node=NodeService().get_managed_node(auth,node_id)
            group_list = self.manager.getGroupList(auth, site_id)
            add_mode=False
            self.sync_manager.remove_defn(nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.DETACH, "REMOVE_NETWORK_DEF", self.nw_manager, self.manager, add_mode, group_list, op_level)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'msg':'Network Removed'}

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

    def get_network_models(self):

        infolist=[]
        infolist.append(dict(name="i82551",value="i82551"))
        infolist.append(dict(name="i8255715",value="i8255715"))
        infolist.append(dict(name="i82559er",value="i82559er"))
        infolist.append(dict(name="ne2k-pci",value="ne2k-pci"))
        infolist.append(dict(name="ne2k-isa",value="ne2k-isa"))
        infolist.append(dict(name="pcnet",value="pcnet"))
        infolist.append(dict(name="rtl8139",value="rtl8139"))
        infolist.append(dict(name="rmc91c111",value="rmc91c111"))
        infolist.append(dict(name="lance",value="lance"))
        infolist.append(dict(name="mef-fec",value="mef-fec"))
        infolist.append(dict(name="virtio",value="virtio"))
        return infolist

if __name__ == "__main__":

    manager = Basic.getGridManager()
    managed_node = manager.getNode("Servers", "localhost")
    nw=NetworkService()
    nw.get_available_nws(managed_node, "PROVISION_VM")
