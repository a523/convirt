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
from convirt.controllers.StorageController import StorageController

class StorageAjaxController(BaseController):
    #allow_only = authenticate()
    #/storage/

    storage_controller=StorageController()

    @expose(template='json')
    def get_storage_def_list(self,site_id=None,op_level=None,group_id=None,_dc=None):
        result = None
        result = self.storage_controller.get_storage_def_list(site_id,op_level,group_id, _dc)
        return result

    @expose(template='json')
    def get_dc_storage_def_list(self,site_id=None,group_id=None,_dc=None):
        result = None
        result = self.storage_controller.get_dc_storage_def_list(site_id,group_id)
        return result

    @expose(template='json')
    def get_storage_types(self,**kw):
        result = self.storage_controller.get_storage_types(**kw)
        return result

    @expose(template='json')
    def add_storage_def(self, type, site_id=None, op_level=None, group_id=None, node_id=None, sp_ids=None, **kw):
        result = None
        result =self.storage_controller.add_storage_def(type,site_id,op_level,group_id,node_id,sp_ids,kw)
        return result

    @expose(template='json')
    def edit_storage_def(self, storage_id,type,site_id=None,group_id=None,op_level=None, sp_ids=None,**kw):
        result = None
        result = self.storage_controller.edit_storage_def(storage_id,type,site_id,group_id,op_level,sp_ids,kw)
        return result

    @expose(template='json')
    def is_storage_allocated(self, storage_id):
        result = None
        result = self.storage_controller.is_storage_allocated(storage_id)
        return result

    @expose(template='json')
    def remove_storage_def(self, storage_id,site_id=None, op_level=None, group_id=None):
        result = None
        result = self.storage_controller.remove_storage_def(storage_id,site_id,op_level,group_id)
        return result

    @expose(template='json')
    def rename_storage_def(self, storage_id,new_name,group_id=None):
        result = None
        result =self.storage_controller.rename_storage_def(storage_id,new_name,group_id)
        return result

    @expose(template='json')
    def storage_def_test(self, type,storage_id,mode, site_id=None, op_level=None, group_id=None, node_id=None, show_available="true", vm_config_action=None, disk_option=None, **kw):
        result = None
        result = self.storage_controller.storage_def_test(type,storage_id,mode,site_id,op_level,group_id,node_id,show_available, vm_config_action, disk_option, kw)
        return result

    @expose()
    def associate_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None):
        result=None
        result=self.storage_controller.associate_defns(def_ids, def_type, site_id, op_level, group_id)
        return result

    @expose(template='json')
    def get_server_storage_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        result = None
        result = self.storage_controller.get_server_storage_def_list(def_id, defType, site_id, group_id)
        return result

    @expose()
    def RemoveScanResult(self):
        result= self.storage_controller.RemoveScanResult()
        return result

    @expose()
    def SaveScanResult(self,storage_id):
        result= self.storage_controller.SaveScanResult(storage_id)
        return result

    @expose(template='json')
    def get_sp_list(self, site_id, def_id=None, _dc=None):
        result = None
        try:
            result = self.storage_controller.get_sp_list(site_id, def_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'",""))
        return result


