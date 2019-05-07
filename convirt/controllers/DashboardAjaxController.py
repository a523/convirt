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
# author : SAJU M <sajuptpm@gmail.com>

from tg import expose, flash, require, url, request, redirect,response,session,config
from convirt.lib.base import BaseController
from convirt.controllers.DashboardController import DashboardController

class DashboardAjaxController(BaseController):
    """

    """

    dashboard_controller=DashboardController()

    @expose(template='json')
    def dashboardservice(self, type, node_id, username=None, password=None, **kw):
        result = self.dashboard_controller.dashboardservice(type, node_id, username, password, **kw)
        return result

    @expose(template='json')
    def data_center_info(self, node_id, type):
        result = self.dashboard_controller.data_center_info(node_id, type)
        return result

    @expose(template='json')
    def server_pool_info(self, node_id, type):
        result = self.dashboard_controller.server_pool_info(node_id, type)
        return result
    
    @expose(template='json')
    def get_resources(self):
        result = self.dashboard_controller.get_resources()
        return result

    @expose(template='json')
    def server_info(self, node_id, type):
        result = self.dashboard_controller.server_info(node_id, type)
        return result

    @expose(template='json')
    def set_registered(self):
        self.dashboard_controller.set_registered()

    @expose(template='json')
    def vm_info(self, node_id, type):
        result = self.dashboard_controller.vm_info(node_id, type)
        return result

    @expose(template='json')
    def vm_availability(self,node_id,_dc=None):
        result = self.dashboard_controller.vm_availability(node_id,_dc)
        return result

    @expose(template='json')
    def vm_storage(self,node_id,_dc=None):
        result = self.dashboard_controller.vm_storage(node_id,_dc)
        return result

    @expose(template='json')
    def dashboard_vm_info(self, node_id, type, canned=None, _dc=None):
        result = self.dashboard_controller.dashboard_vm_info(node_id, type, canned, _dc)
        return result

    @expose(template='json')
    def dashboard_server_info(self, node_id, type, canned=None, _dc=None):
        result = self.dashboard_controller.dashboard_server_info(node_id, type, canned, _dc)
        return result

    @expose(template='json')
    def dashboard_serverpool_info(self, node_id, type,_dc=None):
        result = self.dashboard_controller.dashboard_serverpool_info(node_id, type,_dc)
        return result

    @expose(template='json')
    def metrics(self):
        result = self.dashboard_controller.metrics()
        return result

    @expose(template='json')
    def get_chart_data(self,node_id,node_type,metric,period,offset,\
                frmdate=None,todate=None,chart_type=None,avg_fdate=None,avg_tdate=None):
        result = self.dashboard_controller.get_chart_data(node_id,node_type,metric,period,offset,\
                frmdate,todate,chart_type,avg_fdate,avg_tdate)
        return result

    @expose(template='json')
    def server_usage(self,node_id,metric,_dc=None):
        result = self.dashboard_controller.server_usage(node_id,metric,_dc)
        return result

    @expose(template='json')
    def topNvms(self,node_id,metric,node_type,_dc=None):
        result = self.dashboard_controller.topNvms(node_id,metric,node_type,_dc)
        return result

    @expose(template='json')
    def topNservers(self,node_id,metric,node_type,_dc=None):
        result = self.dashboard_controller.topNservers(node_id,metric,node_type,_dc)
        return result

    @expose(template='json')
    def os_distribution_chart(self,node_id,metric,node_type,_dc=None):
        result = self.dashboard_controller.os_distribution_chart(node_id,metric,node_type,_dc)
        return result

    @expose(template='json')
    def get_updated_tasks(self,user_name, _dc=None):
        result = self.dashboard_controller.get_updated_tasks(user_name, _dc)
        return result

    @expose(template='json')
    def get_custom_search_list(self,node_level,lists_level, _dc=None):
        result = self.dashboard_controller.get_custom_search_list(node_level,lists_level)
        return result

    @expose(template='json')
    def get_custom_search(self,name,lists_level):
        result = self.dashboard_controller.get_custom_search(name,lists_level)
        return result

    @expose(template='json')
    def get_canned_custom_list(self,node_level,lists_level,_dc=None):
        result = self.dashboard_controller.get_canned_custom_list(node_level,lists_level,_dc)
        return result

    @expose(template='json')
    def get_filter_forsearch(self,_dc=None):
        result = self.dashboard_controller.get_filter_forsearch(_dc)
        return result

    @expose(template='json')
    def get_property_forsearch(self,node_id,node_type,listlevel,_dc=None):
        result = self.dashboard_controller.get_property_forsearch(node_id,node_type,listlevel,_dc)
        return result

    @expose(template='json')
    def save_custom_search(self,name,desc,condition,node_id,level,lists_level,max_count=200,_dc=None):
        result = self.dashboard_controller.save_custom_search(name,desc,condition,node_id,level,lists_level,max_count,_dc)
        return result

    @expose(template='json')
    def delete_custom_search(self,name,_dc=None):
        result = self.dashboard_controller.delete_custom_search(name,_dc)
        return result

    @expose(template='json')
    def edit_save_custom_search(self,name,desc,condition,max_count=200,_dc=None):
        result = self.dashboard_controller.edit_save_custom_search(name,desc,condition,max_count,_dc)
        return result

    @expose(template='json')
    def test_newcustom_search(self,name,value,node_id,type,listlevel):
        result = self.dashboard_controller.test_newcustom_search(name,value,node_id,type,listlevel)
        return result

    @expose(template='json')
    def get_cache_details(self):
        result = self.dashboard_controller.get_cache_details()
        return result

