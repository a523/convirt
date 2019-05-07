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
from sqlalchemy.sql.expression import not_
from convirt.viewModel.NodeService import NodeService
from convirt.viewModel.VMService import VMService
from convirt.model.VM import VM
from convirt.viewModel.TaskCreator import TaskCreator
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import logging,tg,os
LOGGER = logging.getLogger("convirt.controllers")

class NodeController(ControllerBase):
    """

    """

    #allow_only = authenticate()
    #/node/

    tc = TaskCreator()
    node_service = NodeService()
    vm_service=VMService()

#    @expose(template='json')
    def get_platform(self,node_id,type,**kw):
        try:
            self.authenticate()
            result = self.node_service.get_platform(session['auth'],node_id,type)
        except Exception, ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'","")}
        return dict(success='true',platform=result)

#    @expose(template='json')
    def get_managed_nodes(self, site_id=None, group_id=None,**kw):
        result = None
        self.authenticate()
        result = self.node_service.get_managed_nodes(session['auth'],group_id,site_id)
        return result

#    @expose(template='json')
    def get_node_info(self, node_id, level ,_dc=None):
        result = None
        self.authenticate()
        if level==constants.DOMAIN:
            result = self.node_service.get_vm_info(session['auth'], node_id)
        elif level==constants.MANAGED_NODE:
            result = self.node_service.get_node_info(session['auth'], node_id)
        return result

#    @expose(template='json')
    def refresh_node_info(self, node_id, level ,_dc=None):
        result = None
        self.authenticate()
        if level==constants.MANAGED_NODE:
            result = self.node_service.refresh_node_info(session['auth'], node_id)
        return result

#    @expose(template='json')
    def get_group_vars(self, group_id ,_dc=None):
        result = None
        self.authenticate()
        result = self.node_service.get_group_vars(session['auth'], group_id)
        return result

#    @expose(template='json')
    def save_group_vars(self, group_id ,_dc=None, **attrs):
        result = None
        self.authenticate()
        #group_id=str(group_id)
        result = self.node_service.save_group_vars(session['auth'], group_id,attrs)
        return result

#    @expose()
    def add_node(self, platform, hostname, username, password, ssh_port, use_keys, group_id, protocol=None, xen_port=8006, xen_migration_port=8002, address=None, ** kw):
        try:
            result = None
            self.authenticate()
            result = self.node_service.add_node(session['auth'], group_id, platform, hostname, ssh_port, username, password,
                                                        protocol, xen_port, xen_migration_port, use_keys, address)
            return  result
        except Exception, ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'","")}

#    @expose()
    def edit_node(self, node_id, platform, hostname, username, password, ssh_port, use_keys, protocol=None, xen_port=8006, xen_migration_port=8002, address=None, ** kw):
        try:
            result = None
            self.authenticate()
            result = self.node_service.edit_node(session['auth'], node_id, platform, hostname, ssh_port, username, password, protocol, xen_port, xen_migration_port, use_keys, address)
            return  result
        except Exception, ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'","")}

#    @expose(template='json')
    def remove_node(self,node_id,force="False"):
        result = None
        self.authenticate()
        result = self.node_service.remove_node(session['auth'],node_id,eval(force))
        return  result

#    @expose(template='json')
    def get_node_properties(self,node_id):
        try:
            self.authenticate()
            result = self.node_service.get_node_properties(session['auth'],node_id)
            return dict(success=True,node=result.toJson())
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def connect_node(self, node_id, username='root', password=None):
        try:
            result = None
            self.authenticate()
            result = self.node_service.connect_node(session['auth'],node_id, username, password)
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose()
    def vm_action(self, dom_id, node_id, action,date=None,time=None):
        self.authenticate()
        try:
            wait_time=0
            dom=DBSession().query(VM).filter(VM.id==dom_id).one()
            self.tc.vm_action(session['auth'],dom_id,node_id,action,date,time)
            if action == constants.START:
                wait_time=dom.get_wait_time('view_console')
        except Exception, ex:
            print_traceback()
            return "{success: false,msg:'"+to_str(ex).replace("'","").replace("\n","")+"'}"
        return "{success:true,msg:'"+ action.title() +" Virtual Machine Task Submitted.',wait_time:"+to_str(wait_time)+"}"

#    @expose(template='json')
    def transfer_node(self, node_id,source_group_id,dest_group_id, forcefully):
        result = None
        self.authenticate()
        result=self.node_service.transfer_node( session['auth'], node_id,source_group_id,dest_group_id,forcefully)
        return result

#    @expose()
    def server_action(self, node_id, action,date=None,time=None):
        self.authenticate()
        try:
            self.tc.server_action(session['auth'], node_id, action, date,time)
        except Exception, ex:
            print_traceback()
            return "{success: false,msg:'"+to_str(ex).replace("'","").replace("\n","")+"'}"
        return "{success: true,msg:'" + action.title()[:-4] + " All Virtual Machine Task Submitted.'}"

#    @expose()
    def import_vm_config(self, node_id,directory,filenames,date=None,time=None):
        self.authenticate()
        try:
            result=self.tc.import_vm_action(session['auth'], node_id, directory,filenames, date,time)
#            doms=self.node_service.import_vm_config(session['auth'],node_id, directory, filenames)
        except Exception, ex:
            print_traceback()
            err=to_str(ex).replace("'", " ")
            LOGGER.error(err)
            return "{success: false,msg: '",err,"'}"
        return "{success: true,msg: 'Import Virtual Machine Task Submitted.'}"

#    @expose()
    def restore_vm(self, node_id,directory,filenames,date=None,time=None):
        self.authenticate()
        try:
            file = os.path.join(directory, filenames)
            self.tc.restore_vm(session['auth'], node_id, file,date,time)
        except Exception, ex:
            print_traceback()
            return "{success: false,msg:'"+to_str(ex).replace("'","").replace("\n","")+"'}"
        return "{success: true,msg: 'Restore Virtual Machine Task Submitted'}"

#    @expose()
    def save_vm(self, dom_id, node_id,directory,filenames,date=None,time=None):
        self.authenticate()
        try:
            file = os.path.join(directory, filenames)
            self.tc.save_vm(session['auth'], dom_id, node_id, \
                            file, directory,date,time)
        except Exception, ex:
            print_traceback()
            return "{success: false,msg:'"+to_str(ex).replace("'","").replace("\n","")+"'}"
        return "{success: true,msg: 'Snapshot Virtual Machine Task Submitted'}"

#    @expose(template='json')
    def migrate_vm(self, dom_name, dom_id, source_node_id, dest_node_id, live='true', force='false', all='false',date=None,time=None):
        self.authenticate()
        result=self.node_service.migrate_vm(session['auth'], dom_name, dom_id, \
                            source_node_id, dest_node_id, live, force, all)
        try:
            if result.get('submit',None)==True:
                self.tc.migrate_vm(session['auth'], result['dom_list'], source_node_id,\
                                   dest_node_id, live, force, all,date,time)
                return dict(success=True,msg='Migrate Virtual Machine Task Submitted.')
            else:
                return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'","").replace("\n",""))
        return result

#    @expose(template='json')
    def get_migrate_target_sps(self, node_id,sp_id):
        result = None
        self.authenticate()
        try:

            result=self.node_service.get_migrate_target_sps(session['auth'],node_id=node_id,sp_id=sp_id)
        except Exception , ex:
            print_traceback()
            return dict(success='false',msg=to_str(ex).replace("'",""))
        return dict(success='true',nodes=result)


#    @expose(template='json')
    def get_vm_config_file(self,dom_id,node_id):
        result = None
        self.authenticate()
        try:
            result=self.node_service.get_vm_config_file(session['auth'],dom_id, node_id )
            result = json.dumps(dict(success=True,content=result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose()
    def save_vm_config_file(self,dom_id,node_id,content):
        result = None
        self.authenticate()
        result = self.node_service.save_vm_config_file(session['auth'],dom_id,node_id, content)
        return result

#    @expose(template='json')
    def remove_vm_config_file(self,dom_id,node_id):
        self.authenticate()
        try:
            self.node_service.remove_vm_config_file(session['auth'], dom_id,node_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,msg='VM config removed.')

#    @expose()
    def remove_vm(self,dom_id,node_id,date=None,time=None,force="False"):
        self.authenticate()
        try:
            self.tc.vm_remove_action(session['auth'],dom_id,node_id,eval(force),date,time)
        except Exception, ex:
            print_traceback()
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return "{success: true,msg: 'Remove Virtual Machine Task Submitted.'}"

#    @expose(template='json')
    def get_node_status(self, node_id=None, dom_id=None):
        try:
            node_up = self.node_service.get_node_status(node_id=node_id,dom_id=dom_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg= to_str(ex))
        return dict(success=True,node_up=node_up)

#    @expose(template='json')
    def get_migrate_target_nodes(self, node_id):
        result = None
        self.authenticate()
        try:
            result=self.node_service.get_target_nodes(session['auth'],node_id=node_id)
        except Exception , ex:
            print_traceback()
            return dict(success='false',msg=to_str(ex).replace("'",""))
        return dict(success='true',nodes=result)

#    @expose(template='json')
    def vm_config_settings(self,image_id,config,mode,node_id=None,group_id=None,dom_id=None,vm_name=None,date=None,time=None,_dc=None):
        self.authenticate()
        try:
            if mode in ['PROVISION_VM', 'EDIT_VM_INFO']:
                self.tc.config_settings(session['auth'], image_id, config, \
                                      mode, node_id, group_id, dom_id, vm_name,date,time)
                result = None
            else:
                result = self.node_service.vm_config_settings(session['auth'],\
                               image_id,config,mode,node_id,group_id,\
                               dom_id,vm_name)
        except Exception, e:
            print_traceback()
            return dict(success=False,msg='Error:'+to_str(e).replace("'", " "))
        return dict(success=True,vm_config=result)

#    @expose(template='json')
    def check_vm_name(self, vm_name, vm_id):
        from convirt.model import DBSession
        from convirt.model.VM import VM
        query = DBSession.query(VM)
        if vm_id:
            query = query.filter(not_(VM.id==vm_id))
        vm = query.filter(VM.name==vm_name).first()
        if vm :
            return dict(success=False,msg='VM <b>'+vm_name+'</b> already exists.')
        return dict(success=True,msg='')

#    @expose(template='json')
    def get_vm_config(self,domId,nodeId,_dc=None):
        self.authenticate()
        try:
            result=self.node_service.get_vm_config(session['auth'],domId,nodeId)
        except Exception, e:
            print_traceback()
            return dict(success=False,msg='Error:'+to_str(e).replace("'", " "))
        return dict(success=True,vm_config=result)

#    @expose(template='json')
    def get_shutdown_event_map(self,_dc=None):
        self.authenticate()
        result=self.node_service.get_shutdown_event_map()
        return result

#    @expose(template='json')
    def get_miscellaneous_configs(self,image_id=None,dom_id=None,node_id=None,group_id=None,action=None,_dc=None):
        try:
            self.authenticate()
            result=self.vm_service.get_miscellaneous_configs(session['auth'],image_id,dom_id,node_id,group_id,action)
            return result
        except Exception, e:
            print_traceback()
            return dict(success=False,msg='Error:'+to_str(e).replace("'", " "))

#    @expose(template='json')
    def get_provisioning_configs(self,image_id=None,_dc=None):
        try:
            self.authenticate()
            result=self.vm_service.get_provisioning_configs(session['auth'],image_id)
            return result
        except Exception, e:
            print_traceback()
            return dict(success=False,msg='Error:'+to_str(e).replace("'", " "))

#    @expose(template='json')
    def get_initial_vmconfig(self,image_id=None,mode=None,_dc=None):
        try:
            self.authenticate()
            result=self.vm_service.get_initial_vmconfig(session['auth'],image_id,mode)
            return dict(success=True,vm_config=result)
        except Exception, e:
            print_traceback()
            return dict(success=False,msg='Error:'+to_str(e).replace("'", " "))

#    @expose(template='json')
    def get_disks(self,image_id=None,mode=None,dom_id=None,node_id=None,group_id=None,action=None,_dc=None):
        result = None
        self.authenticate()
        try:
            result=self.vm_service.get_disks(session['auth'],image_id,mode,dom_id,node_id,group_id,action)
        except Exception, e:
            print_traceback()
            return dict(success=False,msg=to_str(e))
        return dict(success=True,disks=result)

#    @expose(template='json')
    def get_disks_options_map(self,_dc=None):
        result = None
        self.authenticate()
        result=self.vm_service.get_disks_options_map()
        return result

#    @expose(template='json')
    def get_disks_type_map(self,type,mode,_dc=None):
        result = None
        self.authenticate()
        result=self.vm_service.get_disks_type_map(type,mode)
        return result

#    @expose(template='json')
    def get_vmdevice_map(self,platform,_dc=None):
        result = None
        self.authenticate()
        result=self.vm_service.get_vmdevice_map(platform)
        return result

#    @expose(template='json')
    def get_device_mode_map(self,_dc=None):
        result = None
        self.authenticate()
        result=self.vm_service.get_device_mode_map()
        return result

#    @expose(template='json')
    def get_ref_disk_format_map(self,format_type,_dc=None):
        result = None
        self.authenticate()
        result=self.vm_service.get_ref_disk_format_map(format_type)
        return result
    
#    @expose(template='json')
    def get_disk_fs_map(self,_dc=None):
        result = None
        self.authenticate()
        result=self.vm_service.get_disk_fs_map()
        return result

#    @expose(template='json')
    def get_ref_disk_type_map(self,_dc=None):
        result = None
        self.authenticate()
        result=self.vm_service.get_ref_disk_type_map()
        return result

#    @expose(template='json')
    def list_dir_contents(self, node_id=None, directory=None, _dc=None):
        result = None
        self.authenticate()
        try:
            result=self.node_service.get_dir_contents(session['auth'],node_id,directory)
        except Exception , ex:
            print_traceback()
            x=to_str(ex)
            err=''
            if x.startswith('[Errno 2] No such file or directory:'):
                err='NoDirectory'
            return {'success':'false','msg':to_str(ex).replace("'",""),'err':err}
        return dict(success='true',rows=result)

#    @expose()
    def make_dir(self, node_id, parent_dir, dir, _dc=None):
        result = None
        self.authenticate()
        result=self.node_service.make_dir(session['auth'],node_id,parent_dir, dir)
        return result

#    @expose()
    def add_group(self,group_name,site_id):
        self.authenticate()
        try:
            self.node_service.add_group(session['auth'],group_name,site_id)
        except Exception , ex:
            print_traceback()
            return "{success:false,msg:'",to_str(ex).replace("'",""),"'}"
        return "{success: true,msg:'Server Pool ",group_name," Added.'}"

#    @expose()
    def remove_group(self,group_id):
        self.authenticate()
        try:
            self.node_service.remove_group(session['auth'],group_id)
        except Exception , ex:
            print_traceback()
            return "{success:false,msg:'",to_str(ex).replace("'",""),"'}"
        return "{success: true,msg:'Server Pool Removed.'}"

#    @expose(template='json')
    def get_alloc_node(self, group_id, image_id=None):
        result = None
        self.authenticate()
        result=self.node_service.get_alloc_node(session['auth'],group_id,image_id)
        return result

#    @expose(template='json')
    def get_boot_device(self,dom_id):
        result = None
        self.authenticate()
        result=self.node_service.get_boot_device(session['auth'],dom_id)

        return result

#    @expose(template='json')
    def set_boot_device(self,dom_id,boot):
        self.authenticate()
        result=self.node_service.set_boot_device(session['auth'],dom_id,boot)
        return result
    
#    @expose(template='json')
    def get_parent_id(self, node_id):
        try:
            result = None
            self.authenticate()
            result = self.node_service.get_parent_id(session['auth'],node_id)
        except Exception , ex:
            return "{success:false,msg:'",to_str(ex).replace("'",""),"'}"
        return dict(success="true",node_details=result)

#    @expose(template='json')
    def entity_context(self,node_id):
        try:
            result = None
            self.authenticate()
            result =self.node_service.entity_context(session['auth'],node_id)
        except Exception , ex:
            return "{success:false,msg:'",to_str(ex).replace("'",""),"'}"
        return dict(success="true",node_details=result)

#    @expose(template='json')
    def get_updated_entities(self,user_name, _dc=None):
        try:
            result = None
            self.authenticate()
            result = self.node_service.get_updated_entities(user_name)
        except Exception , ex:
            return "{success:false,msg:'",to_str(ex).replace("'",""),"'}"
        return dict(success="true",node_ids=result)

#    def get_vnc_log_content(self,file):
#        result = None
#        result = self.vm_service.get_vnc_log_content(file)
#        return result

    def get_command_list(self):
         result = None
         result = self.vm_service.get_command_list()
         return result

    def get_command(self,node_id,dom_id,cmd):
         result = None
         result = self.vm_service.get_command(session['auth'],node_id,dom_id,cmd)
         return result

    def process_annotation(self,node_id,text=None,user=None):
        self.authenticate()
        try:
            if user is None and text is None:
                result = self.node_service.get_annotation(session['auth'],node_id)
                if result.get("annotate"):
                    result=to_str(self.tc.clear_annotation(session['auth'], node_id))
                else:
                    return dict(success=False,msg= 'No annotations defined.')
            else:
                if user is not None:
                    result=to_str(self.tc.edit_annotation(session['auth'], node_id,text,user))
                else:
                    result=to_str(self.tc.add_annotation(session['auth'], node_id,text,user))
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg= to_str(ex))
        return dict(success=True,msg= 'Annotation Task Submitted.',taskid=result)

    def get_annotation(self,node_id):
        self.authenticate()
        result = None
        result = self.node_service.get_annotation(session['auth'],node_id)
        return result