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
from convirt.controllers.NodeController import NodeController

class NodeAjaxController(BaseController):
    """

    """

    #allow_only = authenticate()
    #/node/

    node_controller=NodeController()

    @expose(template='json')
    def get_platform(self,node_id,type,**kw):
        result = self.node_controller.get_platform(node_id, type, **kw)
        return result

    @expose(template='json')
    def get_managed_nodes(self, site_id=None, group_id=None,**kw):
        result = self.node_controller.get_managed_nodes(site_id, group_id, **kw)
        return result

    @expose(template='json')
    def get_node_info(self, node_id, level ,_dc=None):
        result = self.node_controller.get_node_info(node_id, level ,_dc)
        return result

    @expose(template='json')
    def refresh_node_info(self, node_id, level ,_dc=None):
        result = self.node_controller.refresh_node_info(node_id, level ,_dc)
        return result        

    @expose(template='json')
    def get_group_vars(self, group_id ,_dc=None):
        result = self.node_controller.get_group_vars(group_id ,_dc)
        return result

    @expose(template='json')
    def save_group_vars(self, group_id ,_dc=None, **attrs):
        result = self.node_controller.save_group_vars(group_id , _dc, **attrs)
        return result

    @expose()
    def add_node(self, platform, hostname, username, password, ssh_port, use_keys, group_id, protocol=None, xen_port=8006, xen_migration_port=8002, address=None, **kw):
        result = self.node_controller.add_node(platform, hostname, username, password, ssh_port, use_keys, group_id, protocol, xen_port, xen_migration_port, address, **kw)
        return result

    @expose()
    def edit_node(self, node_id, platform, hostname, username, password, ssh_port, use_keys, protocol=None, xen_port=8006, xen_migration_port=8002, address=None, **kw):
        result = self.node_controller.edit_node(node_id, platform, hostname, username, password, ssh_port, use_keys, protocol, xen_port, xen_migration_port, address, **kw)
        return result

    @expose(template='json')
    def remove_node(self,node_id,force="False"):
        result = self.node_controller.remove_node(node_id, force)
        return result

    @expose(template='json')
    def get_node_properties(self,node_id):
        result = self.node_controller.get_node_properties(node_id)
        return result

    @expose(template='json')
    def connect_node(self, node_id, username='root', password=None):
        result = self.node_controller.connect_node(node_id, username, password)
        return result

    @expose()
    def vm_action(self, dom_id, node_id, action,date=None,time=None):
        result = self.node_controller.vm_action(dom_id, node_id, action,date,time)
        return result

    @expose(template='json')
    def transfer_node(self, node_id,source_group_id,dest_group_id, forcefully):
        result = self.node_controller.transfer_node(node_id,source_group_id,dest_group_id, forcefully)
        return result

    @expose()
    def server_action(self, node_id, action,date=None,time=None):
        result = self.node_controller.server_action(node_id, action, date, time)
        return result

    @expose()
    def import_vm_config(self, node_id,directory,filenames,date=None,time=None):
        result = self.node_controller.import_vm_config(node_id, directory, filenames, date, time)
        return result

    @expose()
    def restore_vm(self, node_id,directory,filenames,date=None,time=None):
        result = self.node_controller.restore_vm(node_id,directory,filenames,date,time)
        return result

    @expose()
    def save_vm(self, dom_id, node_id,directory,filenames,date=None,time=None):
        result = self.node_controller.save_vm(dom_id, node_id, directory, filenames, date, time)
        return result

    @expose(template='json')
    def migrate_vm(self, dom_name, dom_id, source_node_id, dest_node_id, live='true', force='false', all='false',date=None,time=None):
        result = self.node_controller.migrate_vm(dom_name, dom_id, source_node_id, dest_node_id, live, force, all,date,time)
        return result

    @expose(template='json')
    def get_migrate_target_sps(self, node_id,sp_id):
        result = self.node_controller.get_migrate_target_sps(node_id, sp_id)
        return result

    @expose(template='json')
    def get_vm_config_file(self,dom_id,node_id):
        result = self.node_controller.get_vm_config_file(dom_id, node_id)
        return result

    @expose()
    def save_vm_config_file(self,dom_id,node_id,content):
        result = self.node_controller.save_vm_config_file(dom_id, node_id, content)
        return result

    @expose(template='json')
    def remove_vm_config_file(self,dom_id,node_id):
        result = self.node_controller.remove_vm_config_file(dom_id, node_id)
        return result

    @expose()
    def remove_vm(self,dom_id,node_id,date=None,time=None,force="False"):
        result = self.node_controller.remove_vm(dom_id, node_id, date, time, force)
        return result

    @expose(template='json')
    def get_node_status(self, node_id=None, dom_id=None):
        result = self.node_controller.get_node_status(node_id, dom_id)
        return result

    @expose(template='json')
    def get_migrate_target_nodes(self, node_id):
        result = self.node_controller.get_migrate_target_nodes(node_id)
        return result

    @expose(template='json')
    def vm_config_settings(self,image_id,config,mode,node_id=None,group_id=None,dom_id=None,vm_name=None,date=None,time=None,_dc=None):
        result = self.node_controller.vm_config_settings(image_id, config, mode, node_id, group_id, dom_id, vm_name, date, time, _dc)
        return result

    @expose(template='json')
    def check_vm_name(self, vm_name, vm_id):
        result = self.node_controller.check_vm_name(vm_name, vm_id)
        return result

    @expose(template='json')
    def get_vm_config(self,domId,nodeId,_dc=None):
        result = self.node_controller.get_vm_config(domId, nodeId,_dc)
        return result

    @expose(template='json')
    def get_shutdown_event_map(self,_dc=None):
        result = self.node_controller.get_shutdown_event_map(_dc)
        return result

    @expose(template='json')
    def get_miscellaneous_configs(self,image_id=None,dom_id=None,node_id=None,group_id=None,action=None,_dc=None):
        result = self.node_controller.get_miscellaneous_configs(image_id, dom_id, node_id, group_id, action, _dc)
        return result

    @expose(template='json')
    def get_provisioning_configs(self,image_id=None,_dc=None):
        result = self.node_controller.get_provisioning_configs(image_id, _dc)
        return result

    @expose(template='json')
    def get_initial_vmconfig(self,image_id=None,mode=None,_dc=None):
        result = self.node_controller.get_initial_vmconfig(image_id, mode, _dc)
        return result

    @expose(template='json')
    def get_disks(self,image_id=None,mode=None,dom_id=None,node_id=None,group_id=None,action=None,_dc=None):
        result = self.node_controller.get_disks(image_id, mode, dom_id, node_id, group_id, action, _dc)
        return result

    @expose(template='json')
    def get_disks_options_map(self,_dc=None):
        result = self.node_controller.get_disks_options_map(_dc)
        return result

    @expose(template='json')
    def get_disks_type_map(self,type,mode,_dc=None):
        result = self.node_controller.get_disks_type_map(type, mode, _dc)
        return result

    @expose(template='json')
    def get_vmdevice_map(self,platform,_dc=None):
        result = self.node_controller.get_vmdevice_map(platform, _dc)
        return result

    @expose(template='json')
    def get_device_mode_map(self,_dc=None):
        result = self.node_controller.get_device_mode_map(_dc)
        return result

    @expose(template='json')
    def get_ref_disk_format_map(self,format_type,_dc=None):
        result = self.node_controller.get_ref_disk_format_map(format_type, _dc)
        return result

    @expose(template='json')
    def get_disk_fs_map(self,_dc=None):
        result = self.node_controller.get_disk_fs_map(_dc)
        return result

    @expose(template='json')
    def get_ref_disk_type_map(self,_dc=None):
        result = self.node_controller.get_ref_disk_type_map(_dc)
        return result

    @expose(template='json')
    def list_dir_contents(self, node_id=None, directory=None, _dc=None):
        result = self.node_controller.list_dir_contents(node_id, directory, _dc)
        return result

    @expose()
    def make_dir(self, node_id, parent_dir, dir, _dc=None):
        result = self.node_controller.make_dir(node_id, parent_dir, dir, _dc)
        return result

    @expose()
    def add_group(self,group_name,site_id):
        result = self.node_controller.add_group(group_name, site_id)
        return result

    @expose()
    def remove_group(self,group_id):
        result = self.node_controller.remove_group(group_id)
        return result

    @expose(template='json')
    def get_alloc_node(self, group_id, image_id=None):
        result = self.node_controller.get_alloc_node(group_id, image_id)
        return result

    @expose(template='json')
    def get_boot_device(self,dom_id):
        result = self.node_controller.get_boot_device(dom_id)
        return result

    @expose(template='json')
    def set_boot_device(self,dom_id,boot):
        result = self.node_controller.set_boot_device(dom_id, boot)
        return result

    @expose(template='json')
    def get_parent_id(self, node_id):
        result = self.node_controller.get_parent_id(node_id)
        return result

    @expose(template='json')
    def entity_context(self,node_id):
        result = self.node_controller.entity_context(node_id)
        return result

    @expose(template='json')
    def get_updated_entities(self,user_name, _dc=None):
        result = self.node_controller.get_updated_entities(user_name, _dc)
        return result

#    @expose(template='json')
#    def get_vnc_log_content(self,file,_dc=None):
#        result = None
#        result = self.node_controller.get_vnc_log_content(file)
#        return result

    @expose(template='json')
    def get_command(self,node_id,dom_id,cmd,_dc=None):
        result = None
        result = self.node_controller.get_command(node_id,dom_id,cmd)
        return result

    @expose(template='json')
    def get_command_list(self,_dc=None):
        result = None
        result = self.node_controller.get_command_list()
        return result

    @expose(template='json')
    def process_annotation(self,node_id,text=None,user=None,_dc=None):
        result = None
        result = self.node_controller.process_annotation(node_id,text,user)
        return result
    
    @expose(template='json')
    def get_annotation(self,node_id,_dc=None):
        result = None
        result = self.node_controller.get_annotation(node_id)
        return result