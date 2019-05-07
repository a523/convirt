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

import pylons
import simplejson as json
import traceback
from convirt.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect,response,session,config
from convirt.controllers.ControllerBase import ControllerBase
from convirt.model.CustomPredicates import authenticate
from convirt.model import *
from convirt.viewModel.NetworkService import NetworkService
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import logging,tg,os
LOGGER = logging.getLogger("convirt.controllers")

class NetworkController(ControllerBase):
    
    network_service=NetworkService()

#    @expose(template='json')
    def get_new_nw(self,image_id,mode,node_id=None):
        try:
            result = None
            self.authenticate()
            result=self.network_service.get_new_nw(session['auth'],image_id,mode,node_id)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'rows':result}

#    @expose(template='json')
    def get_nw_det(self,bridge,mac,model):
        try:
            result = None
            self.authenticate()
            result=self.network_service.get_nw_det(bridge,mac,model)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'nw_det':result}


#    @expose(template='json')
    def get_nws(self,image_id=None, op_level=None, node_id=None, dom_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nws(session['auth'],image_id,dom_id,node_id, op_level)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'rows':result}

#    @expose(template='json')
    def get_available_nws(self,mode,op_level=None,node_id=None,_dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_available_nws(session['auth'],mode,node_id,op_level)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'rows':result}

#    @expose(template='json')
    def get_nw_address_space_map(self,_dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nw_address_space_map()
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'nw_address_space':result}

#    @expose(template='json')
    def get_nw_nat_fwding_map(self,node_id,_dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nw_nat_fwding_map(session['auth'],node_id)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'nw_nat':result}

    #Here passing None as a default value to node_id parameter. If node_id is not passed to this function from UI then take default value as None.
#    @expose(template='json')
    def get_nw_defns(self,site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nw_defns(session['auth'],site_id,group_id, node_id, op_level)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'rows':result}

#    @expose(template='json')
    def get_nw_dc_defns(self,site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nw_dc_defns(session['auth'],site_id,group_id, node_id)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'rows':result}

#    @expose(template='json')
    def nw_address_changed(self, ip_value,_dc=None):
        try:
            self.authenticate()
            result = self.network_service.nw_address_changed(ip_value)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return dict(success=True,range=result)

    #Here passing None as a default value to node_id parameter. If node_id is not passed to this function from UI then take default value as None.
    #Default value of group_id is taken as None to avoid the error at compilation "non-default argument follows default argument" instead of changing the parameter sequence.
#    @expose(template='json')
    def get_new_private_bridge_name(self,node_id=None,group_id=None,site_id=None, op_level=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_new_private_bridge_name(session['auth'],node_id,group_id,site_id, op_level)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return dict(success=True,bridge=result)

    #Here passing None as a default value to node_id parameter. If node_id is not passed to this function from UI then take default value as None.
#    @expose(template='json')
    def add_nw_defn(self,nw_name,nw_desc,bridge,nw_address_space,nw_dhcp_range,nat_radio,nw_nat_fwding,site_id=None, op_level=None, group_id=None,node_id=None):            
#        try:
        self.authenticate()
        result = self.network_service.add_nw_defn(session['auth'],nw_name,nw_desc,bridge,nw_address_space,nw_dhcp_range,nat_radio,nw_nat_fwding,site_id,group_id,node_id, op_level)
        return result

#    @expose(template='json')
    def get_edit_network_details(self,nw_id):
        try:
            self.authenticate()
            result = self.network_service.get_edit_network_details(nw_id)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
#            return result
        return dict(success=True,network=result)

#    @expose(template='json')
    def edit_nw_defn(self,nw_id,nw_name,nw_desc):
        self.authenticate()
        result = self.network_service.edit_nw_defn(nw_id,nw_name,nw_desc)
        return result

    #Here passing None as a default value to node_id parameter. If node_id is not passed to this function from UI then take default value as None.
    #Here adding group_id parameter to get server pool in NetworkService.py file.
#    @expose(template='json')
    def remove_nw_defn(self,def_id, site_id=None, op_level=None, group_id=None, node_id=None,_dc=None):
        self.authenticate()
        result = self.network_service.remove_nw_defn(session['auth'],def_id, site_id, group_id, node_id, op_level)
        return result

#    @expose()
    def associate_nw_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None, node_id=None):
        self.authenticate()
        try:
            self.network_service.associate_nw_defns(site_id, group_id, node_id, def_type, def_ids, session['auth'], op_level)
        except Exception, ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'","").replace("\n","") + "'}"

        return "{success: true,msg: 'Task Submitted.'}"

#    @expose(template='json')
    def get_server_nw_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        try:
            result = None
            self.authenticate()
            result = self.network_service.get_server_def_list(site_id, group_id, def_id)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

    def get_network_models(self):
        self.authenticate()
        try:
            info=self.network_service.get_network_models()
            return {'success':True,'rows':info}
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex))
