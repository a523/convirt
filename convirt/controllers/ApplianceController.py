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
from convirt.viewModel.ApplianceService import ApplianceService
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import logging,tg,os
LOGGER = logging.getLogger("convirt.controllers")


class ApplianceController(ControllerBase):
    """

    """
    appliance_service=ApplianceService()
#    @expose(template='json')
    def get_appliance_providers(self,**kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_providers()
        except Exception, ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'","")}
        return dict(success='true',rows=result)

#    @expose(template='json')
    def get_appliance_packages(self,**kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_packages()
        except Exception, ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'","")}
        return dict(success='true',rows=result)

#    @expose(template='json')
    def get_appliance_archs(self,**kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_archs()
        except Exception, ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'","")}
        return dict(success='true',rows=result)

#    @expose(template='json')
    def get_appliance_list(self,**kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_list()
        except Exception, ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'","")}
        return dict(success='true',rows=result)

#    @expose(template='json')
    def refresh_appliances_catalog(self,**kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.refresh_appliances_catalog()
        except Exception, ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'","")}
        return dict(success='true',rows=result)

#    @expose(template='json')
    def import_appliance(self,href,type,arch,pae,hvm,size,provider_id,platform,description,link,image_name,group_id,is_manual,date=None,time=None,**kw):
        try:
            result = None
            self.authenticate()    
            result = self.appliance_service.import_appliance(session['auth'],href,type,arch,pae,hvm,size,provider_id,platform,
                                                                description,link,image_name,group_id,is_manual,date,time)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_appliance_menu_items(self,dom_id,node_id):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_menu_items(session['auth'],dom_id,node_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_appliance_info(self,dom_id,node_id,action=None):
        try:
            self.authenticate()
            result = self.appliance_service.get_appliance_info(session['auth'],dom_id,node_id,action)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,appliance=result)

#    @expose(template='json')
    def save_appliance_info(self,dom_id,node_id,action=None,**kw):
        try:
            self.authenticate()
            result = self.appliance_service.save_appliance_info(session['auth'],dom_id,node_id,action,kw)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'","")) 
        return dict(success=True,appliance=result)
