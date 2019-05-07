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
from convirt.controllers.ApplianceController import ApplianceController

class ApplianceAjaxController(BaseController):
    """

    """

    appliance_controller=ApplianceController()

    @expose(template='json')
    def get_appliance_providers(self,**kw):
        result = self.appliance_controller.get_appliance_providers(**kw)
        return result

    @expose(template='json')
    def get_appliance_packages(self,**kw):
        result = self.appliance_controller.get_appliance_packages(**kw)
        return result

    @expose(template='json')
    def get_appliance_archs(self,**kw):
        result = self.appliance_controller.get_appliance_archs(**kw)
        return result

    @expose(template='json')
    def get_appliance_list(self,**kw):
        result = self.appliance_controller.get_appliance_list(**kw)
        return result

    @expose(template='json')
    def refresh_appliances_catalog(self,**kw):
        result = self.appliance_controller.refresh_appliances_catalog(**kw)
        return result

    @expose(template='json')
    def import_appliance(self,href,type,arch,pae,hvm,size,provider_id,platform,\
                        description,link,image_name,group_id,is_manual,date=None,time=None,**kw):
        result = self.appliance_controller.import_appliance(href,type,arch,pae,hvm,\
                            size,provider_id,platform,description,link,image_name,\
                            group_id,is_manual,date,time,**kw)
        return result

    @expose(template='json')
    def get_appliance_menu_items(self,dom_id,node_id):
        result = self.appliance_controller.get_appliance_menu_items(dom_id,node_id)
        return result

    @expose(template='json')
    def get_appliance_info(self,dom_id,node_id,action=None):
        result = self.appliance_controller.get_appliance_info(dom_id,node_id,action)
        return result

    @expose(template='json')
    def save_appliance_info(self,dom_id,node_id,action=None,**kw):
        result = self.appliance_controller.save_appliance_info(dom_id,node_id,action,**kw)
        return result
