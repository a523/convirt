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
from convirt.model.DBHelper import DBHelper
from convirt.viewModel.Userinfo import Userinfo
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import logging,tg,os
LOGGER = logging.getLogger("convirt.controllers")

class ModelController(ControllerBase):
    """
    
    """
    user_info= Userinfo()

#    @expose(template='json')
    def get_users(self,_dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result = None
            result=self.user_info.get_users()
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_user_status_map(self,_dc=None):
        result = None
        self.authenticate()
        if session['auth'].is_admin() == False:
            return dict(success=False,msg=constants.NO_PRIVILEGE)
        result=self.user_info.get_user_status_map()
        return result

#    @expose(template='json')
    def save_user_det(self, userid, username, fname, lname, displayname, password, email, phone, status):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.save_user_det( session['userid'],userid, username, fname, lname, displayname, password, email, phone, status)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'user_det':result}

#    @expose(template='json')
    def delete_user(self,userid):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            self.user_info.delete_user(userid)
            return {'success':True, 'msg':'User Removed.'}
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}

#    @expose(template='json')
    def updatesave_user_det(self, userid, username, fname, lname, displayname,  email, phone, status,changepass,newpasswd):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.updatesave_user_det(session['userid'],userid, username, fname, lname, displayname,  email, phone, status,changepass,newpasswd)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'user_det':result}

#    @expose(template='json')
    def edit_user_det(self,userid):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.edit_user_det(userid)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'edit_user_det':result}

#    @expose(template='json')
    def change_user_password(self, userid, newpasswd, oldpasswd):
        try:
            result = None
            self.authenticate()
            if userid != "" and userid != session['userid']:
                if session['auth'].is_admin() == False:
                    return dict(success=False,msg=constants.NO_PRIVILEGE)
            result = self.user_info.change_user_password(userid, newpasswd, oldpasswd)
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}
        return {'success':True, 'user_det':result}

#    @expose(template='json')
    def get_opsgroups(self,_dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_opsgroups()
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_entities(self,enttype_id,_dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_entities(enttype_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_groups_map(self,userid=None,_dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_groups_map(userid)
            return {'success':True, 'group_det':result}
        except Exception, ex:
              print_traceback()
              return {'success':False,'msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def get_users_map(self,groupid=None,_dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_users_map(groupid)
            return {'success':True, 'user_det':result}
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def get_togroups_map(self,userid,_dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_togroups_map(userid)
            return {'success':True, 'togroup_det':result}
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def delete_group(self,groupid):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            self.user_info.delete_group(groupid)
            return {'success':True, 'msg':'Group Removed.'}
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}

#    @expose(template='json')
    def get_groupsdetails(self,_dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_groupsdetails()
            #print "result", result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def save_group_details(self, groupid, groupname, userids,desc):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.save_group_details(session['userid'],groupid, groupname, userids,desc)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'group_det':result}

#    @expose(template='json')
    def updatesave_group_details(self,groupid, groupname, userids,desc):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.updatesave_group_details(session['userid'],groupid, groupname, userids,desc)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'group_det':result}

#    @expose(template='json')
    def edit_group_details(self,groupid):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.edit_group_details(groupid)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'edit_group_det':result}

#    @expose(template='json')
    def get_tousers_map(self,groupid,_dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_tousers_map(groupid)
            return {'success':True, 'touser_det':result}
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def save_opsgroup_details(self, opsgroupname, opsgroupdesc, operation):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.save_opsgroup_details( session['userid'],opsgroupname, opsgroupdesc, operation)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'opsgroup_det':result}

#    @expose(template='json')
    def updatesave_opsgroup_details(self, opsgroupid, opsgroupname, opsgroupdesc, operation):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.updatesave_opsgroup_details(session['userid'],opsgroupid, opsgroupname, opsgroupdesc, operation)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'opsgroup_det':result}

#    @expose(template='json')
    def edit_opsgroup_details(self,opsgroupid):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.edit_opsgroup_details(opsgroupid)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'edit_opsgroup_det':result}

#    @expose(template='json')
    def  get_operations_map(self,opsgrpid=None,_dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info. get_operations_map(opsgrpid)
            return {'success':True, 'operation_det':result}
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def get_tooperations_map(self,opsgroupid,_dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info. get_tooperations_map(opsgroupid)
            return {'success':True, 'tooperations_det':result}
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def delete_opsgroup(self,opsgroupid):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            self.user_info.delete_opsgroup(opsgroupid)
            return {'success':True, 'msg':'Opsgroup Removed.'}
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}

#    @expose(template='json')
    def get_operations(self,_dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_operations()
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def save_oper_det(self, opname, descr, context_disp, entityid,dispname,icon):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.save_oper_det(session['userid'],opname, descr, context_disp, entityid,dispname,icon)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'operation_det':result}

#    @expose(template='json')
    def edit_op_det(self,opid,enttype):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.edit_op_det(opid,enttype)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'edit_op_det':result}

#    @expose(template='json')
    def updatesave_op_det(self, opid, opname, desc, entid, context_disp,dispname,icon):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.updatesave_op_det(session['userid'],opid, opname, desc, entid, context_disp,dispname,icon)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'operation_det':result}

#    @expose(template='json')
    def delete_operation(self,opid):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            self.user_info.delete_operation(opid)
            return {'success':True,'msg':'Operation Deleted.'}
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))

#    @expose(template='json')
    def get_entitytype_map(self,opid=None,_dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_entitytype_map(opid)
            return {'success':True, 'entitytype_det':result}
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def get_toentitytype_map(self,opid,_dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_toentitytype_map(opid)
            return {'success':True, 'toentitytype_det':result}
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def get_enttype(self,_dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_enttype()
            #print "result", result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_enttype_for_chart(self,_dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            result=self.user_info.get_enttype_for_chart()
            #print "result", result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def save_enttype_details(self, enttypename, dispname):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.save_enttype_details(session['userid'],enttypename, dispname)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'opsgroup_det':result}

#    @expose(template='json')
    def edit_enttype_details(self,enttypeid):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.edit_enttype_details(enttypeid)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'edit_enttype_det':result}

#    @expose(template='json')
    def updatesave_enttype_details(self, enttypeid, enttypename, dispname):
          try:
              result = None
              self.authenticate()
              if session['auth'].is_admin() == False:
                  return dict(success=False,msg=constants.NO_PRIVILEGE)
              result = self.user_info.updatesave_enttype_details(session['userid'],enttypeid, enttypename, dispname)
          except Exception, ex:
              print_traceback()
              return {'success':False, 'msg':to_str(ex).replace("'", "")}
          return {'success':True, 'opsgroup_det':result}

#    @expose(template='json')
    def delete_enttype(self,enttypeid):
        try:
            self.authenticate()
            if session['auth'].is_admin() == False:
                return dict(success=False,msg=constants.NO_PRIVILEGE)
            self.user_info.delete_enttype(enttypeid)
            return {'success':True, 'msg':'Entitytype Removed.'}
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}


