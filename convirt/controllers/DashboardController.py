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
from convirt.viewModel.DashboardService import DashboardService
from convirt.viewModel.ChartService import ChartService
from convirt.core.utils.utils import to_unicode,to_str,print_traceback, performance_debug
import convirt.core.utils.constants
constants = convirt.core.utils.constants
DEBUG_CAT = constants.DEBUG_CATEGORIES
import logging,tg,os
from convirt.model.GenericCache import GenericCache
LOGGER = logging.getLogger("convirt.controllers")

class DashboardController(ControllerBase):
    """

    """
    dashboard_service=DashboardService()
    chart_service=ChartService()

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("DC_SP_SR"))
    def dashboardservice(self, type, node_id, username=None, password=None, ** kw):
        try:
            result = None
            self.authenticate()
            dashboardInfo = self.dashboard_service.execute(session['auth'], type, node_id, username, password)
            result = json.dumps(dict(success=True,nodes=dashboardInfo.toJson()))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("DC"))
    def data_center_info(self, node_id, type):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.data_center_info(session['auth'], node_id, type)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("SP"))
    def server_pool_info(self, node_id, type):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.server_pool_info(session['auth'], node_id, type)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        
#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("SP"))
    def get_resources(self):
        self.authenticate()
        try:
            info = self.dashboard_service.get_resources(session['auth'])
            return dict(success=True,info=info)
        except Exception, ex:
           print_traceback()
           return dict(success=False,msg=to_str(ex).replace("'", " "))



#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("SR"))
    def server_info(self, node_id, type):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.server_info(session['auth'], node_id, type)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("SR"))
    def set_registered(self):
        try:

            self.dashboard_service.set_registered(session['auth'])
        except Exception, ex:
            print_traceback()



#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("VM"))
    def vm_info(self, node_id, type):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.vm_info(session['auth'], node_id, type)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug()
#    @expose(template='json')
    def vm_availability(self,node_id,_dc=None):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.vm_availability(session['auth'], node_id)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug()
#    @expose(template='json')
    def vm_storage(self,node_id,_dc=None):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.vm_storage(session['auth'], node_id)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("DC_SP_SR"))
    def dashboard_vm_info(self, node_id, type, canned=None, _dc=None):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.dashboard_vm_info(session['auth'], node_id, type, canned)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("DC_SP"))
    def dashboard_server_info(self, node_id, type, canned=None, _dc=None):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.dashboard_server_info(session['auth'], node_id, type ,canned)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug()
    def dashboard_serverpool_info(self, node_id, type,_dc=None):
        self.authenticate()
        try:
            self.authenticate()
            info = self.dashboard_service.dashboard_serverpool_info(session['auth'], node_id, type)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def metrics(self):
        try:
            self.authenticate()
            info = self.chart_service.metrics(session['auth'])
            #return info
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug(DEBUG_CAT.get("DC_SP_SR_VM"))
#    @expose(template='json')
    def get_chart_data(self,node_id,node_type,metric,period,offset,\
        frmdate=None,todate=None,chart_type=None,avg_fdate=None,avg_tdate=None):
        try:
            self.authenticate()
            info = self.chart_service.get_chart_data(session['auth'],\
                node_id,node_type,metric,period,offset,frmdate,todate,\
                chart_type,avg_fdate,avg_tdate)                
            #return info
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("SR"))
    def server_usage(self,node_id,metric,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.server_usage(session['auth'],node_id,metric)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("DC_SP_SR"))
    def topNvms(self,node_id,metric,node_type,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.topNvms(session['auth'],node_id,metric,node_type)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    @performance_debug(DEBUG_CAT.get("DC_SP"))
    def topNservers(self,node_id,metric,node_type,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.topNservers(session['auth'],node_id,metric,node_type)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug(DEBUG_CAT.get("DC_SP"))
#    @expose(template='json')
    def os_distribution_chart(self,node_id,metric,node_type,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.os_distribution_chart(session['auth'],node_id,metric,node_type)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug()
#    @expose(template='json')
    def get_updated_tasks(self,user_name, _dc=None):
        try:
            result = None
            self.authenticate()
            result = self.dashboard_service.get_updated_tasks(user_name)
            return dict(success="true",tasks=result)
        except Exception , ex:            
            return "{success:false,msg:'",to_str(ex).replace("'",""),"'}"

    @performance_debug(DEBUG_CAT.get("DC_SP_SR"))
    def get_custom_search_list(self,node_level,lists_level):
        try:
            self.authenticate()
            info = self.dashboard_service.get_custom_search_list(session['auth'],node_level,lists_level)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug(DEBUG_CAT.get("DC_SP_SR"))
    def get_custom_search(self,name,lists_level):
        try:
            self.authenticate()
            info = self.dashboard_service.get_custom_search(session['auth'],name,lists_level)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug(DEBUG_CAT.get("DC_SP_SR"))
    def get_canned_custom_list(self,node_level,lists_level,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.get_canned_custom_list(session['auth'],node_level,lists_level)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
    
    @performance_debug(DEBUG_CAT.get("DC_SP_SR"))
    def get_filter_forsearch(self,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.get_filter_forsearch(session['auth'])
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug(DEBUG_CAT.get("DC_SP_SR"))
    def get_property_forsearch(self,node_id,node_type,listlevel,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.get_property_forsearch(session['auth'],node_id,node_type,listlevel)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    def save_custom_search(self,name,desc,condition,node_id,level,lists_level,max_count=200,_dc=None):        
        try:
            self.authenticate()

            info = self.dashboard_service.save_custom_search(session['auth'],name,desc,condition,node_id,level,lists_level,max_count)
            if info == True:
                return dict(success=True,info=info)
            else:
                return dict(success=False,msg=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
    

    def delete_custom_search(self,name,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.delete_custom_search(session['auth'],name)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    def edit_save_custom_search(self,name,desc,condition,max_count=200,_dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.edit_save_custom_search(session['auth'],name,desc,condition,max_count)
            return dict(success=True,info=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))


    def test_newcustom_search(self,name,value,node_id,type,listlevel):
        try:
            self.authenticate()
            info = self.dashboard_service.test_newcustom_search(session['auth'],name,value,node_id,type,listlevel)
            return dict(success=True,msg=info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @performance_debug()
    def get_cache_details(self):
        try:
            self.authenticate()
            gc=GenericCache()
            cache_info = gc.get_cache_details()
            return dict(success=True,cache_info=cache_info)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

