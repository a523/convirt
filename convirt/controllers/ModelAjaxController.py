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
from convirt.controllers.ModelController import ModelController

class ModelAjaxController(BaseController):
    """

    """
    #allow_only = authenticate()
    #/model/

    model_controller=ModelController()

    @expose(template='json')
    def get_users(self,_dc=None):
        result = self.model_controller.get_users(_dc)
        return result
    
    @expose(template='json')
    def get_user_status_map(self,_dc=None):
        result = self.model_controller.get_user_status_map(_dc)
        return result

    @expose(template='json')
    def save_user_det(self, userid, username, fname, lname, displayname, password, email, phone, status):
        result = self.model_controller.save_user_det(userid, username, fname, lname, displayname, password, email, phone, status)
        return result

    @expose(template='json')
    def delete_user(self,userid):
        result = self.model_controller.delete_user(userid)
        return result

    @expose(template='json')
    def updatesave_user_det(self, userid, username, fname, lname, displayname,  email, phone, status,changepass,newpasswd):
        result = self.model_controller.updatesave_user_det(userid, username, fname, lname, displayname,  email, phone, status, changepass, newpasswd)
        return result

    @expose(template='json')
    def edit_user_det(self,userid):
        result = self.model_controller.edit_user_det(userid)
        return result

    @expose(template='json')
    def change_user_password(self, userid, newpasswd, oldpasswd):
        result = self.model_controller.change_user_password(userid, newpasswd, oldpasswd)
        return result

    @expose(template='json')
    def get_opsgroups(self,_dc=None):
        result = self.model_controller.get_opsgroups(_dc)
        return result

    @expose(template='json')
    def get_entities(self,enttype_id,_dc=None):
        result = self.model_controller.get_entities(enttype_id, _dc)
        return result

    @expose(template='json')
    def get_groups_map(self,userid=None,_dc=None):
        result = self.model_controller.get_groups_map(userid,_dc)
        return result

    @expose(template='json')
    def get_users_map(self,groupid=None,_dc=None):
        result = self.model_controller.get_users_map(groupid, _dc)
        return result

    @expose(template='json')
    def get_togroups_map(self,userid,_dc=None):
        result = self.model_controller.get_togroups_map(userid, _dc)
        return result

    @expose(template='json')
    def delete_group(self,groupid):
        result = self.model_controller.delete_group(groupid)
        return result

    @expose(template='json')
    def get_groupsdetails(self,_dc=None):
        result = self.model_controller.get_groupsdetails(_dc)
        return result

    @expose(template='json')
    def save_group_details(self, groupid, groupname, userids,desc):
        result = self.model_controller.save_group_details(groupid, groupname, userids, desc)
        return result

    @expose(template='json')
    def updatesave_group_details(self,groupid, groupname, userids,desc):
        result = self.model_controller.updatesave_group_details(groupid, groupname, userids,desc)
        return result

    @expose(template='json')
    def edit_group_details(self,groupid):
        result = self.model_controller.edit_group_details(groupid)
        return result

    @expose(template='json')
    def get_tousers_map(self,groupid,_dc=None):
        result = self.model_controller.get_tousers_map(groupid, _dc)
        return result

    @expose(template='json')
    def save_opsgroup_details(self, opsgroupname, opsgroupdesc, operation):
        result = self.model_controller.save_opsgroup_details(opsgroupname, opsgroupdesc, operation)
        return result

    @expose(template='json')
    def updatesave_opsgroup_details(self, opsgroupid, opsgroupname, opsgroupdesc, operation):
        result = self.model_controller.updatesave_opsgroup_details(opsgroupid, opsgroupname, opsgroupdesc, operation)
        return result

    @expose(template='json')
    def edit_opsgroup_details(self,opsgroupid):
        result = self.model_controller.edit_opsgroup_details(opsgroupid)
        return result

    @expose(template='json')
    def  get_operations_map(self,opsgrpid=None,_dc=None):
        result = self.model_controller.get_operations_map(opsgrpid,_dc)
        return result

    @expose(template='json')
    def get_tooperations_map(self,opsgroupid,_dc=None):
        result = self.model_controller.get_tooperations_map(opsgroupid,_dc)
        return result

    @expose(template='json')
    def delete_opsgroup(self,opsgroupid):
        result = self.model_controller.delete_opsgroup(opsgroupid)
        return result

    @expose(template='json')
    def get_operations(self,_dc=None):
        result = self.model_controller.get_operations(_dc)
        return result

    @expose(template='json')
    def save_oper_det(self, opname, descr, context_disp, entityid,dispname,icon):
        result = self.model_controller.save_oper_det(opname, descr, context_disp, entityid, dispname, icon)
        return result

    @expose(template='json')
    def edit_op_det(self,opid,enttype):
        result = self.model_controller.edit_op_det(opid, enttype)
        return result

    @expose(template='json')
    def updatesave_op_det(self, opid, opname, desc, entid, context_disp,dispname,icon):
        result = self.model_controller.updatesave_op_det(opid, opname, desc, entid, context_disp, dispname, icon)
        return result

    @expose(template='json')
    def delete_operation(self,opid):
        result = self.model_controller.delete_operation(opid)
        return result

    @expose(template='json')
    def get_entitytype_map(self,opid=None,_dc=None):
        result = self.model_controller.get_entitytype_map(opid, _dc)
        return result

    @expose(template='json')
    def get_toentitytype_map(self,opid,_dc=None):
        result = self.model_controller.get_toentitytype_map(opid, _dc)
        return result

    @expose(template='json')
    def get_enttype(self,_dc=None):
        result = self.model_controller.get_enttype(_dc)
        return result

    @expose(template='json')
    def get_enttype_for_chart(self,_dc=None):
        result = self.model_controller.get_enttype_for_chart(_dc)
        return result

    @expose(template='json')
    def save_enttype_details(self, enttypename, dispname):
        result = self.model_controllersave_enttype_details(enttypename, dispname)
        return result

    @expose(template='json')
    def edit_enttype_details(self,enttypeid):
        result = self.model_controller.edit_enttype_details(enttypeid)
        return result

    @expose(template='json')
    def updatesave_enttype_details(self, enttypeid, enttypename, dispname):
        result = self.model_controller.updatesave_enttype_details(enttypeid, enttypename, dispname)
        return result

    @expose(template='json')
    def delete_enttype(self,enttypeid):
        result = self.model_controller.delete_enttype(enttypeid)
        return result


