# -*- coding: utf-8 -*-
"""Main Controller"""

__all__ = ['RootController']

import sys

sys.path.append("/usr/lib/python2.4/site-packages")
sys.path.append("/usr/lib64/python2.4/site-packages")
sys.path.append("/usr/lib64/python24.zip")
sys.path.append("/usr/lib64/python2.4/plat-linux2")
sys.path.append("/usr/lib64/python2.4/lib-tk")
sys.path.append("/usr/lib64/python2.4/lib-dynload")
sys.path.append("/usr/lib64/python2.4/site-packages/Numeric")
sys.path.append("/usr/lib64/python2.4/site-packages/gtk-2.0")

import pylons
import simplejson as json
import traceback
from convirt.lib.base import BaseController
from convirt.model import DBSession, metadata
from convirt.controllers.error import ErrorController
from convirt.model.CustomPredicates import is_user
#from convirt.controllers.SecuredAdminController import SecuredAdminController
from convirt.controllers.ApplianceAjaxController import ApplianceAjaxController
from convirt.controllers.DashboardAjaxController import DashboardAjaxController
from convirt.controllers.ModelAjaxController import ModelAjaxController
from convirt.controllers.NodeAjaxController import NodeAjaxController
from convirt.controllers.NetworkAjaxController import NetworkAjaxController
from convirt.controllers.StorageAjaxController import StorageAjaxController
from convirt.controllers.TemplateAjaxController import TemplateAjaxController
from convirt.controllers.ControllerImpl import ControllerImpl

from convirt import model
from convirt.model import *
from convirt.model.DBHelper import DBHelper
from convirt.model.Authorization import AuthorizationService
from convirt.model.UpdateManager import UIUpdateManager,AppUpdateManager
#from convirt.controllers.secure import SecureController
from tg import expose, flash, require, url, request, redirect,response,session,config
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from xml.dom import minidom
#from convirt.viewModel.Sessions import SessionManager
from convirt.core.utils.utils import to_unicode,to_str,print_traceback, get_cms_stacktrace, get_cms_stacktrace_fancy, set_or_get_perf_debug

import convirt.core.utils.constants
constants = convirt.core.utils.constants

import logging,tg
LOGGER = logging.getLogger("convirt.controllers")
#from catwalk.tg2 import Catwalk
import os
# the global session manager
#sessionManager = SessionManager()

#from tgrum import RumAlchemyController
#from convirt.model.Metrics import MetricsService

class RootController(BaseController):

    error = ErrorController()

    appliance=ApplianceAjaxController()
    dashboard=DashboardAjaxController()
    model=ModelAjaxController()
    node=NodeAjaxController()
    network=NetworkAjaxController()
    storage=StorageAjaxController()
    template=TemplateAjaxController()
    controller_impl=ControllerImpl()

    @expose()
    def cms_trace(self):
        if config.get("enable_stack_trace_url") == "True":
            return get_cms_stacktrace()
        else:
            return "<html>Stack Trace not enabled.</html>"

    @expose()
    def cms_trace_fancy(self):
        if config.get("enable_stack_trace_url") == "True":
            return get_cms_stacktrace_fancy()
        else:
            return "<html>Stack Trace not enabled.</html>"

    @expose()
    def task_trace(self):
        if config.get("enable_stack_trace_url") == "True":
            from convirt.viewModel.TaskCreator import TaskCreator
            return TaskCreator().get_running_task_info()
        else:
            return "<html>Stack Trace not enabled.</html>"

    @expose()
    def get_used_ports_info(self):
        if config.get("enable_used_ports_url") == "True":
            return self.controller_impl.get_used_ports_info()
        else:
            return "<html>Port information url not enabled.</html>"

    @expose('convirt.templates.login')
    def login(self, came_from=url('/')):
        result=None
        result=self.controller_impl.login(came_from)
        return result

    @expose()
    def user_login(self,came_from=url('/'),**kwargs):
        result=None

        try:
            status=self.controller_impl.user_login(kwargs)

            if status.get('success'):
                user=status.get('user')
                result = self.post_login(user,came_from)
                return result
            else:
                msg=status.get('msg')
                return "{success:false,msg:'"+msg.replace("'", " ")+"'}"
        except Exception, e:
            print "Exception: ", e
            import traceback
            traceback.print_exc()
            return "{success:false,msg:'"+str(e).replace("'", " ")+"'}"

    @expose()
    def post_login(self, userid, came_from=url('/')):
        result=None
        result=self.controller_impl.post_login(userid,came_from)

        return result        

    @expose('convirt.templates.login')
    def user_logout(self, came_from=url('/')):
        return self.post_logout(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        self.controller_impl.post_logout(came_from)
#        from convirt.controllers.ControllerBase import ControllerBase
#        ControllerBase().redirect_to(url('/login'))
        return dict(page='login',came_from=came_from)

    @expose()
    def perf_debug(self, **kwargs):
        return set_or_get_perf_debug(**kwargs)

    @expose(template='convirt.templates.dashboard')
    def index(self):
        result=None
        result=self.controller_impl.index()
        return result

    @expose(template='json')
    def get_app_updates(self):
        result=None
        result=self.controller_impl.get_app_updates()
        return result 

    @expose(template='json')
    def get_nav_nodes(self):
        result=None
        result=self.controller_impl.get_nav_nodes()
        return result

    @expose(template='json')
    def get_vnc_info(self,node_id,dom_id):
        result=None
        result =self.controller_impl.get_vnc_info(node_id,dom_id)
        return result

    @expose(template='json')
    def get_ssh_info(self,node_id,client_platform):
        result=None
        result =self.controller_impl.get_ssh_info(node_id,client_platform)
        return result

    @expose(template='json')
    def get_platforms(self,**kw):
        try:
            result=None
            result = self.controller_impl.get_platforms()
            return dict(success=True,rows=result)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

    @expose(template='json')
    def get_context_menu_items(self,node_id,node_type,_dc=None,menu_combo=None):
        try:
            result=None
            result= self.controller_impl.getUserOps(node_id,node_type,menu_combo)
        except Exception,ex:
            print_traceback()
        return dict(success=True,rows=result)

    @expose('convirt.templates.login')
    def authenticate(self):
        try:
           self.controller_impl.authenticate()
        except Exception,e:
            raise Exception("SessionExpired.")

    @expose(template='json')
    def get_tasks(self,_dc=None):
        result=None
        result=self.controller_impl.get_tasks()
        return result

    @expose(template='json')
    def getNotifications(self,type,list,user,entType=None,_dc=None):
        result = None
        result=self.controller_impl.getNotifications(type,list,user,entType)
        return result

    @expose(template='json')
    def getSystemTasks(self,type,user,_dc=None):
        result = None
        result=self.controller_impl.getSystemTasks(type,user)
        return result

    @expose(template='json')
    def get_failed_tasks(self,_dc=None):
        result = None
        result=self.controller_impl.get_failed_tasks()
        return result

    @expose(template='json')
    def save_email_setup_details(self, desc, servername, port, useremail, password, secure, ** kw):
        result = None
        result = self.controller_impl.save_email_setup_details( desc, servername, port, useremail, password, secure )
        return  result

    @expose(template='json')
    def update_email_setup_details(self, desc, servername, port, useremail, password, secure, ** kw):
        result = self.controller_impl.update_email_setup_details( desc, servername, port, useremail, password, secure)
        return result

    @expose(template='json')
    def send_test_email(self, desc, servername, port, useremail, password, secure, ** kw):
        try:
            msgreceived = self.controller_impl.send_test_email(desc, servername, port, useremail, password, secure)
        except Exception, ex:
            print ex
            return dict(success=False,msg="Test Failed: "+to_str(ex).replace("'",""))
        return  {'success':True, 'msg':msgreceived}

    @expose(template='json')
    def get_emailsetupinfo(self,_dc=None):
        result= self.controller_impl.get_emailsetupinfo()
        return result

    @expose(template='json')
    def delete_emailrecord(self,emailsetup_id):
        result=self.controller_impl.delete_emailrecord(emailsetup_id)
        return result

    @expose(template='json')
    def get_emailsetup_details(self,emailsetup_id):
        result=None
        result=self.controller_impl.get_emailsetup_details(emailsetup_id)
        return result
    
    @expose()
    def fix_vm_disk_entries(self, **kwargs):
        return self.controller_impl.fix_vm_disk_entries(**kwargs)

