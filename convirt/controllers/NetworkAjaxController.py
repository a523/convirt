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

from tg import expose
from convirt.lib.base import BaseController
from convirt.controllers.NetworkController import NetworkController

class NetworkAjaxController(BaseController):
    #allow_only = authenticate()
    #/network/

    network_controller=NetworkController()

    @expose(template='json')
    def get_new_nw(self,image_id,mode,node_id=None):
        result=None
        result = self.network_controller.get_new_nw(image_id,mode,node_id)
        return result

    @expose(template='json')
    def get_nw_det(self,bridge,mac,model):
        result = None
        result = self.network_controller.get_nw_det(bridge,mac,model)
        return result


    @expose(template='json')
    def get_nws(self,image_id=None, op_level=None, node_id=None, dom_id=None, _dc=None):
        result = self.network_controller.get_nws(image_id, op_level, node_id, dom_id, _dc)
        return result

    @expose(template='json')
    def get_available_nws(self,mode,op_level=None,node_id=None,_dc=None):
        result = self.network_controller.get_available_nws(mode,op_level,node_id,_dc)
        return result

    @expose(template='json')
    def get_nw_address_space_map(self,_dc=None):
        result = self.network_controller.get_nw_address_space_map(_dc)
        return result

    @expose(template='json')
    def get_nw_nat_fwding_map(self,node_id,_dc=None):
        result = self.network_controller.get_nw_nat_fwding_map(node_id,_dc)
        return result

    #Here passing None as a default value to node_id parameter. If node_id is not passed to this function from UI then take default value as None.
    @expose(template='json')
    def get_nw_defns(self,site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        result = self.network_controller.get_nw_defns(site_id, op_level, group_id, node_id, _dc)
        return result

    @expose(template='json')
    def get_nw_dc_defns(self,site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        result = self.network_controller.get_nw_dc_defns(site_id, op_level, group_id, node_id, _dc)
        return result

    @expose(template='json')
    def nw_address_changed(self, ip_value,_dc=None):
        result = self.network_controller.nw_address_changed(ip_value,_dc)
        return result

    #Here passing None as a default value to node_id parameter. If node_id is not passed to this function from UI then take default value as None.
    #Default value of group_id is taken as None to avoid the error at compilation "non-default argument follows default argument" instead of changing the parameter sequence.
    @expose(template='json')
    def get_new_private_bridge_name(self,node_id=None,group_id=None,site_id=None, op_level=None, _dc=None):
        result = self.network_controller.get_new_private_bridge_name(node_id,group_id,site_id, op_level, _dc)
        return result

    #Here passing None as a default value to node_id parameter. If node_id is not passed to this function from UI then take default value as None.
    @expose(template='json')
    def add_nw_defn(self,nw_name,nw_desc,bridge,nw_address_space,nw_dhcp_range,nat_radio,\
                        nw_nat_fwding,site_id=None, op_level=None, group_id=None,node_id=None):
        result = self.network_controller.add_nw_defn(nw_name,nw_desc,bridge,nw_address_space,\
                        nw_dhcp_range,nat_radio,nw_nat_fwding,site_id, op_level, group_id,node_id)
        return result

    @expose(template='json')
    def get_edit_network_details(self,nw_id):
        result = self.network_controller.get_edit_network_details(nw_id)
        return result

    @expose(template='json')
    def edit_nw_defn(self,nw_id,nw_name,nw_desc):
        result = self.network_controller.edit_nw_defn(nw_id,nw_name,nw_desc)
        return result

    #Here passing None as a default value to node_id parameter. If node_id is not passed to this function from UI then take default value as None.
    #Here adding group_id parameter to get server pool in NetworkService.py file.
    @expose(template='json')
    def remove_nw_defn(self,def_id, site_id=None, op_level=None, group_id=None, node_id=None,_dc=None):
        result = self.network_controller.remove_nw_defn(def_id, site_id, op_level, group_id, node_id,_dc)
        return result

    @expose()
    def associate_nw_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None, node_id=None):
        result = self.network_controller.associate_nw_defns(def_ids, def_type, site_id, op_level, group_id, node_id)
        return result

    @expose(template='json')
    def get_server_nw_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        result = None
        result = self.network_controller.get_server_nw_def_list(def_id, defType, site_id, group_id, _dc)
        return result

    @expose(template='json')
    def get_network_models(self, _dc=None):
        result = None
        result = self.network_controller.get_network_models()
        return result
