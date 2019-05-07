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
from convirt.viewModel.TaskCreator import TaskCreator
from convirt.viewModel.StorageService import StorageService
from convirt.viewModel import Basic
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import logging,tg,os
LOGGER = logging.getLogger("convirt.controllers")

class StorageController(ControllerBase):
    
    tc = TaskCreator()
    manager=Basic.getGridManager()
    storage_service=StorageService()
#    @expose(template='json')
    def get_storage_def_list(self,site_id=None,op_level=None,group_id=None,_dc=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.get_storage_def_list(session['auth'],site_id,group_id, op_level)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

#    @expose(template='json')
    def get_dc_storage_def_list(self,site_id=None,group_id=None,_dc=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.get_dc_storage_def_list(session['auth'],site_id,group_id)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

#    @expose(template='json')
    def get_storage_types(self,**kw):
        try:
            self.authenticate()
            result = self.storage_service.get_storage_types()
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

#    @expose(template='json')
    def add_storage_def(self, type, site_id=None, op_level=None, group_id=None, node_id=None, sp_ids=None, opts=None):
        try:
            result = None
            self.authenticate()
            #result = self.storage_service.add_storage_def(session['auth'],site_id,group_id,node_id,type,opts,op_level,sp_ids, added_manually)
            self.tc.add_storage_def_task(session['auth'],site_id,group_id,node_id,type,opts,op_level,sp_ids)
            result = "{success: true,msg: 'Task Submitted.'}"
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result
    
#    @expose(template='json')
    def edit_storage_def(self, storage_id,type,site_id=None,group_id=None, op_level=None, sp_ids=None, kw=None):
        try:
            result = None
            self.authenticate()           
            result = self.storage_service.edit_storage_def(session['auth'],storage_id,site_id,group_id,type, op_level, sp_ids, kw)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

    def is_storage_allocated(self, storage_id):
        try:
            result = None
            result = self.storage_service.is_storage_allocated(storage_id)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

#    @expose(template='json')
    def remove_storage_def(self, storage_id,site_id=None, op_level=None, group_id=None):
        try:
            result = None
            self.authenticate()
            #result = self.storage_service.remove_storage_def(session['auth'],storage_id,site_id,group_id, op_level)
            self.tc.remove_storage_def_task(session['auth'],storage_id,site_id,group_id, op_level)
            result = "{success: true,msg: 'Task Submitted.'}"
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

#    @expose(template='json')
    def rename_storage_def(self, storage_id,new_name,group_id=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.rename_storage_def(session['auth'],new_name,storage_id,group_id)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

#    @expose(template='json')
    def storage_def_test(self, type,storage_id,mode, site_id=None, op_level=None, group_id=None, node_id=None, show_available="true", vm_config_action=None, disk_option=None, kw=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.storage_def_test(session['auth'],storage_id,node_id,group_id,site_id,type,mode,kw, op_level, show_available, vm_config_action, disk_option)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result

#    @expose()
    def associate_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None):
        self.authenticate()
        try:
            self.tc.associate_defns_task(session['auth'], site_id, group_id, def_type, def_ids, op_level)
        except Exception, ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'","").replace("\n","") + "'}"
        return "{success: true,msg: 'Task Submitted.'}"

#    @expose(template='json')
    def get_server_storage_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.get_server_def_list(site_id, group_id, def_id)            
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return result
    
#    @expose(template='json')
    def get_sp_list(self, site_id, def_id=None, _dc=None):
        result = None
        try:
            result = self.manager.get_sp_list(site_id, def_id, session['auth'])
        except Exception, ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'",""))
        return result

#    @expose()
    def RemoveScanResult(self):
        result=self.storage_service.RemoveScanResult()
        return result
    
#    @expose()
    def SaveScanResult(self,storage_id):
        result=self.storage_service.SaveScanResult(storage_id)
        return result
