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
from convirt.controllers.TemplateController import TemplateController

class TemplateAjaxController(BaseController):
    """

    """
    template_controller=TemplateController()
    #/template/

    @expose(template='json')
    def get_image_groups(self,store_id=None,_dc=None):
        result = self.template_controller.get_image_groups(store_id)
        return result

    @expose(template='json')
    def get_images(self, group_id):
        result = self.template_controller.get_images( group_id)
        return result

    @expose(template='json')
    def check_image_exists(self,image_name):
        result = None
        result=self.template_controller.check_image_exists(image_name)
        return result

    @expose(template='json')
    def get_image_target_nodes(self, image_id):
        result = None
        result=self.template_controller.get_image_target_nodes(image_id=image_id)
        return result

    @expose()
    def add_image_group(self, group_name,store_id):
        result = None
        #group_name=to_str(group_name)
        result = self.template_controller.add_image_group(group_name,store_id)
        return result

    @expose()
    def remove_image_group(self, group_id):
        result = None
        result = self.template_controller.remove_image_group(group_id)
        return result

    @expose()
    def rename_image_group(self, group_id, group_name):
        result = None
        result = self.template_controller.rename_image_group(group_id, group_name)
        return result

    @expose()
    def remove_image(self, image_id, group_id):
        result = None
        result = self.template_controller.remove_image(image_id, group_id)
        return result

    @expose()
    def rename_image(self, image_id, image_name, group_id):
        result = None
        #image_name=to_str(image_name)
        result = self.template_controller.rename_image(image_id, image_name, group_id)
        return result

    @expose()
    def clone_image(self, image_id, image_name, group_id,group_name):
        result = None
        #image_name=to_str(image_name)
        result = self.template_controller.clone_image(image_id, image_name, group_id, group_name)
        return result

    @expose(template='json')
    def get_image_info(self, node_id, level):
        result = self.template_controller.get_image_info(node_id,level)
        return result

    @expose()
    def save_image_desc(self, image_id, content):
        result = None
        result =self.template_controller.save_image_desc(image_id, content)
        return result

    @expose(template='json')
    def get_image_script(self, image_id):
        result =self.template_controller.get_image_script(image_id)
        return result

    @expose()
    def save_image_script(self, image_id, content):
        result = None
        result = self.template_controller.save_image_script(image_id, content)
        return result

    @expose(template='json')
    def get_imagestore_details(self, imagestore_id, _dc=None):
        result = self.template_controller.get_imagestore_details(imagestore_id)
        return result

    @expose(template='json')
    def scan_image_store(self,imagestore_id):
        result = self.template_controller.scan_image_store(imagestore_id)
        return result

    @expose(template='json')
    def get_imagestore_count(self,imagestore_id):
        result = self.template_controller.get_imagestore_count(imagestore_id)
        return result

    @expose(template='json')
    def get_imagegroup_count(self,imagegroup_id ):
        result = self.template_controller.get_imagegroup_count(imagegroup_id)
        return result

    @expose(template='json')
    def get_imagegroup_details(self,imagegroup_id, _dc=None ):
        print  "get_imagegroup_details", imagegroup_id
        result = self.template_controller.get_imagegroup_details(imagegroup_id)
        return result

    @expose(template='json')
    def get_piechart_data(self,image_id,  _dc=None ):
        result= None
        result = self.template_controller.get_piechart_data(image_id)
        return result

    @expose(template='json')
    def get_boot_info(self,image_id,_dc=None):
        result = self.template_controller.get_boot_info(image_id)
        return result

    @expose(template='json')
    def get_template_grid_info(self,image_id,type,_dc=None):
        result = self.template_controller.get_template_grid_info(image_id,type)
        return result

    @expose(template='json')
    def transfer_image(self,image_id,source_group_id,dest_group_id):
        result = None
        result=self.template_controller.transfer_image(image_id,source_group_id,dest_group_id)
        return result

    @expose(template='json')
    def get_target_images(self, node_id,image_group_id=None,**kw):
        result = None
        result=self.template_controller.get_target_images(node_id,image_group_id,**kw)
        return result

    @expose(template='json')
    def get_target_image_groups(self, node_id,**kw):
        result = None
        result=self.template_controller.get_target_image_groups(node_id,**kw)
        return result

    @expose(template='json')
    def get_image_vm_info(self,image_id, _dc=None):
        result =self.template_controller.get_image_vm_info(image_id)
        return result

    @expose(template='json')
    def get_template_version_info(self,image_id, _dc=None):
        result = self.template_controller.get_template_version_info(image_id)
        return result

    @expose(template='json')
    def get_template_details(self,image_id, _dc=None):
        result = self.template_controller.get_template_details(image_id)
        return result

    @expose(template='json')
    def get_imagestore_summary_info(self,imagestore_id, _dc=None):
        result = self.template_controller.get_imagestore_summary_info(imagestore_id)
        return result

    @expose(template='json')
    def get_imagegrp_summary_info(self,grp_id, _dc=None):
        result = self.template_controller.get_imagegrp_summary_info(grp_id)
        return result

    @expose(template='json')
    def get_vm_status(self,image_id, _dc=None):
        result = self.template_controller.get_vm_status(image_id)
        return result
