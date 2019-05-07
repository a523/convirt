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
from convirt.viewModel.ImageService import ImageService
from convirt.viewModel.VMService import VMService
from convirt.viewModel.NodeService import NodeService
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import logging,tg,os
LOGGER = logging.getLogger("convirt.controllers")

class TemplateController(ControllerBase):
    """

    """
    image_service=ImageService()
    node_service = NodeService()
    vm_service=VMService()    
    
#    @expose(template='json')
    def get_image_groups(self,store_id=None,_dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_image_groups(session['auth'],store_id)
            result = json.dumps(dict(success=True,nodes=result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def get_images(self, group_id):
        try:
            self.authenticate()
            result = self.image_service.get_images(session['auth'], group_id)
            result = json.dumps(dict(success=True,nodes=result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def check_image_exists(self,image_name):
        result = None
        self.authenticate()
        result=self.image_service.check_image_exists(session['auth'],image_name)
        return result

#    @expose(template='json')
    def get_image_target_nodes(self, image_id):
        result = None
        self.authenticate()
        try:
            result=self.node_service.get_target_nodes(session['auth'],image_id=image_id)
        except Exception , ex:
            print_traceback()
            return dict(success='false',msg=to_str(ex).replace("'",""))
        return dict(success='true',nodes=result)

#    @expose()
    def add_image_group(self, group_name,store_id):
        result = None
        self.authenticate()       
        result = self.image_service.add_image_group(session['auth'], group_name,store_id)
        return result
    
#    @expose()
    def remove_image_group(self, group_id):
        result = None
        self.authenticate()
        result = self.image_service.remove_image_group(session['auth'], group_id)
        return result

#    @expose()
    def rename_image_group(self, group_id, group_name):
        result = None
        self.authenticate()       
        result = self.image_service.rename_image_group(session['auth'], group_id, group_name)
        return result

#    @expose()
    def remove_image(self, image_id, group_id):
        result = None
        self.authenticate()
        result = self.image_service.remove_image(session['auth'], image_id, group_id)
        return result

#    @expose()
    def rename_image(self, image_id, image_name, group_id):
        result = None
        self.authenticate()   
        result = self.image_service.rename_image(session['auth'], image_id, image_name, group_id)
        return result

#    @expose()
    def clone_image(self, image_id, image_name, group_id,group_name):
        result = None
        self.authenticate()     
        result = self.image_service.clone_image(session['auth'], image_id, image_name, group_id)
        return result

#    @expose(template='json')
    def get_image_info(self, node_id, level):
        try:
            self.authenticate()
            if level==constants.IMAGE:
                result = self.image_service.get_image_info(session['auth'], node_id)
            elif level==constants.IMAGE_GROUP:
                result = self.image_service.get_image_group_info(session['auth'], node_id)
            elif level==constants.IMAGE_STORE:
                result = self.image_service.get_image_store_info(session['auth'], node_id)
            result = json.dumps(dict(success=True,content=result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose()
    def save_image_desc(self, image_id, content):
        result = None
        self.authenticate()
        result = self.image_service.save_image_desc(session['auth'], image_id, content)
        return result

#    @expose(template='json')
    def get_image_script(self, image_id):
        try:
            self.authenticate()
            result = self.image_service.get_image_script(session['auth'], image_id)
            result = json.dumps(dict(success=True,content=result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose()
    def save_image_script(self, image_id, content):
        result = None
        self.authenticate()
        result = self.image_service.save_image_script(session['auth'], image_id, content)
        return result

#    @expose(template='json')
    def get_imagestore_details(self, imagestore_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_imagestore_details(imagestore_id)
            result = json.dumps(dict(success=True, content=result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def scan_image_store(self,imagestore_id):
        try:
            self.authenticate()
            (new_imgs,rej_imgs) = self.image_service.scan_imagestore_details(session['auth'],imagestore_id)
            return dict(success=True, new_imgs=new_imgs, rej_imgs=rej_imgs)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def get_imagestore_count(self,imagestore_id):
        try:
            result = self.image_service.get_imagestore_count(imagestore_id)
            result = json.dumps(dict(success=True,count = result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def get_imagegroup_count(self,imagegroup_id ):
        try:
            result = self.image_service.get_imagegroup_count(imagegroup_id)
            result = json.dumps(dict(success=True, info = result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def get_imagegroup_details(self,imagegroup_id, _dc=None ):
        try:
            print  "get_imagegroup_details", imagegroup_id
            result = self.image_service.get_imagegroup_details(imagegroup_id)
            print result
            result = json.dumps(dict(success=True,info = result))
            return result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def get_piechart_data(self,image_id,  _dc=None ):
        try:
            result= []
            result = self.image_service.get_piechart_data(image_id)

            returnresult = json.dumps(dict(success=True,Records = result, RecordCount = '2'))
            return returnresult
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))

#    @expose(template='json')
    def get_boot_info(self,image_id,_dc=None):
         try:
            self.authenticate()
            result = self.image_service.get_boot_info(image_id)
         except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
         return dict(success=True,rows=result)

#    @expose(template='json')
    def get_template_grid_info(self,image_id,type,_dc=None):
         try:
            self.authenticate()
            result = self.vm_service.get_template_grid_info(session['auth'],image_id,type)
         except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
         return dict(success=True,rows=result)

#    @expose(template='json')
    def transfer_image(self,image_id,source_group_id,dest_group_id):
        result = None
        self.authenticate()
        result=self.image_service.transfer_image(session['auth'],image_id,source_group_id,dest_group_id)
        return result

#    @expose(template='json')
    def get_target_images(self, node_id,image_group_id=None,**kw):
        result = None
        self.authenticate()
        result=self.image_service.get_target_images(session['auth'],node_id,image_group_id)
        return result

#    @expose(template='json')
    def get_target_image_groups(self, node_id,**kw):
        result = None
        self.authenticate()
        result=self.image_service.get_target_image_groups(session['auth'],node_id)
        return result

#    @expose(template='json')
    def get_image_vm_info(self,image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_image_vm_info(image_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,rows=result)
    
#    @expose(template='json')
    def get_template_version_info(self,image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_template_version_info(session['auth'],image_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_template_details(self,image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_template_details(image_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_imagestore_summary_info(self,imagestore_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_imagestore_summary_info(imagestore_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,rows=result)

#    @expose(template='json')
    def get_imagegrp_summary_info(self,grp_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_imagegrp_summary_info(grp_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,row=result)

#    @expose(template='json')
    def get_vm_status(self,image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_vm_status(image_id)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,rows=result)
