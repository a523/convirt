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
#
# ApplianceService.py
#
#   This module contains code to return Appliance Catalog
#
import re

import Basic
from TaskCreator import TaskCreator
import convirt.core.appliance.xva
from convirt.core.utils.utils import constants
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
from convirt.model.ImageStore import ImageStore,ImageUtils
xva = convirt.core.appliance.xva
import logging
import traceback
LOGGER = logging.getLogger("convirt.viewModel")

class ApplianceService:
    def __init__(self):
        self.appliance_store = Basic.getApplianceStore()

    def execute(self):
        feeds = self.appliance_store.get_appliance_feeds()
        
        list = []
        for feed_name in feeds:
            appList = self.appliance_store.get_appliances_list(feed_name)
            for appDef in appList:
                list.append(appDef)
        
        #return AppInfo(list)


    def get_appliance_providers(self):
        try:
            result=[]
            feeds = self.appliance_store.get_appliance_feeds()

            counter=0
            for feed_name in feeds:
                counter+=1
                result.append(dict(id=counter,name=feed_name,value=feed_name))

            return result
        except Exception, e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'",""))
            raise e
           
    def get_appliance_packages(self):
        try:
            result=[]
            packages = self.appliance_store.get_all_packages()
            packages.sort()

            counter=0
            for package in packages:
                counter+=1
                result.append(dict(id=counter,name=package,value=package))
            return result
        except Exception, e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'",""))
            raise e
            
    def get_appliance_archs(self):
        try:
            result=[]
            archs = self.appliance_store.get_all_archs()
            archs.sort()

            counter=0
            for arch in archs:
                counter+=1
                result.append(dict(id=counter,name=arch,value=arch))
            return result
        except Exception, e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'",""))
            raise e

    def get_appliance_list(self):
        try:
            result=[]
            feeds = self.appliance_store.get_appliance_feeds()
            for feed_name in feeds:
                a_list = self.appliance_store.get_appliances_list(feed_name)
                for a_info in a_list:
                    title = a_info["title"]

                    size = int(a_info["size"])
                    size_mb = "%6.1f" %  (size / (1024 * 1024)) + " MB"

                    package = a_info["type"]
                    arch    = a_info["arch"]
                    pae     = a_info["PAE"]
                    provider = a_info["provider"]
                    provider_logo_url=a_info["provider_logo_url"]
                    desc = a_info.get("description")
                    if not desc:
                        desc = ""

                    short_desc = a_info.get("short_description")
                    if not short_desc:
                        short_desc = ""

                    if pae == "True":
                        pae_str = 'Y'
                    else:
                        pae_str = 'N'

                    if arch == "x86_64":
                        pae_str = ""

                    a_dict={}
                    a_dict['PROVIDER']=provider
                    a_dict['PROVIDER_LOGO']=provider_logo_url
                    a_dict['TITLE']=title
                    a_dict['PACKAGE']=package
                    a_dict['ARCH']= arch
                    a_dict['PAE']= pae_str
                    a_dict['SIZE_MB']= size_mb
                    a_dict['SIZE']=size
                    a_dict['UPDATED']=a_info["updated"]
                    a_dict['DESC']= desc
                    a_dict['SHORT_DESC']= short_desc
                    a_dict['APPLIANCE_ENTRY']= a_info
                    result.append(a_dict)

            return result
        except Exception, e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'",""))
            raise e

    def refresh_appliances_catalog(self):
        self.appliance_store.refresh_appliance_catalog()
        return self.get_appliance_list()
    
    def import_appliance(self,auth,href,type,arch,pae,hvm,size,provider_id,platform,description,link,image_name,group_id,is_manual,date,time):
        try:           
            is_hvm='False'
            if hvm == 'true':
                is_hvm='True'
            is_pae='False'
            if pae == 'true':
                is_pae='True'

            image_name = re.sub(ImageStore.INVALID_CHARS_EXP,'_', image_name)
                        
            appliance_entry = {}
            appliance_entry["href"] = href
            appliance_entry["type"] = type
            appliance_entry["arch"] = arch
            appliance_entry["PAE"] = is_pae
            appliance_entry["is_hvm"] = is_hvm
            appliance_entry["size"] = size
            appliance_entry["provider_id"] = provider_id
            appliance_entry["platform"] = platform
            appliance_entry["title"] = image_name

            if appliance_entry["provider_id"].lower() == "jumpbox":
                appliance_entry["is_hvm"] = "True"

            
            p_url = self.appliance_store.get_provider_url(provider_id)
            appliance_entry["provider_url"] = p_url
            p_logo_url = self.appliance_store.get_logo_url(provider_id)
            appliance_entry["provider_logo_url"] = p_logo_url

            if is_manual=='true':
                description="Manually imported appliance. Plese use 'Edit Description' menu to put appropriate description here."
                link=""

            appliance_entry["description"] = description
            appliance_entry["link"] = link

            if self.appliance_store.get_provider(provider_id):
                appliance_entry["provider"] = self.appliance_store.get_provider(provider_id)
            else:
                appliance_entry["provider"] = provider_id

            if image_name:
                image_name = image_name.strip()

            platform = appliance_entry["platform"]
            type = appliance_entry["type"]
            if type.lower() not in ("xva", "file_system", "jb_archive"):
                raise Exception("Invalid Package type %s: supported package types are XVA, FILE_SYSTEM. JB_ARCHIVE" % type)

            image_store=Basic.getImageStore()
            
            #force = False

            #for image_group in image_store.get_image_groups(auth).values():
            if image_store.image_exists_by_name(image_name):                
                img = image_store.get_image_by_name(image_name)
                image_store.delete_image(auth,group_id, img.get_id())
                    
            #image_group = image_store.get_image_groups(auth)[group_id]
            
            # Create a new image and add it to the group.
            #img = image_store.create_image(auth,group_id, image_name, platform.lower())

            title = appliance_entry.get("title")
            if not title:
                title = ""

            tc = TaskCreator()
            tc.import_appliance(auth, appliance_entry, image_store, \
                                group_id, image_name, platform.lower(),True,date,time)
        except Exception, e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'",""))
            raise e

    def get_appliance_info(self,auth,domId,nodeId,action):
        
        provider_id=None
        manager = Basic.getGridManager()
        node=manager.getNode(auth,nodeId)
        vm = node.get_dom(domId)
        if vm and vm.is_resident() and vm.get_config():
            config = vm.get_config()
            provider_id = config["provider_id"]
        #print provider_id
        result={}
        if provider_id:
            (proxy,ops) = self.get_appliance_ops(provider_id)             
            (app_url, mgmt_url, creds) = proxy.get_info(vm)
            (app_protocol, host, app_port, app_path) = app_url
            (app_mgmt_protocol, host, app_mgmt_port) = mgmt_url
            (username, password) = creds
            result=dict(app_protocol=app_protocol,host=host,app_port=app_port,app_path=app_path,
                app_mgmt_protocol=app_mgmt_protocol,app_mgmt_port=app_mgmt_port,username=username,password=password
            )
            result['is_valid']=proxy.is_valid_info(vm)

            web_url=""
            try:
                web_url=proxy.get_web_url(vm)
            except Exception, e:
                pass
            result['web_url']=web_url
            if action:
                mgmt_web_url=""
                try:
                    mgmt_web_url=proxy.get_mgmt_web_url(vm,proxy.get_path(action))
                except Exception, e:
                    pass
                result['mgmt_web_url']=mgmt_web_url
        return result

    def save_appliance_info(self,auth,domId,nodeId,action,props):
        manager = Basic.getGridManager()
        node=manager.getNode(auth,nodeId)
        vm = node.get_dom(domId)
        if vm and vm.get_config():
            config = vm.get_config()
            provider_id = config["provider_id"]
            (proxy,ops) = self.get_appliance_ops(provider_id)
            for key in proxy.get_keys():
                config[key]=props[key]
            
        manager.save_appliance_info(auth,vm,config)
        return self.get_appliance_info(auth,domId,nodeId,action)

    def get_appliance_menu_items(self,auth,domId,nodeId):

        provider_id=None
        manager = Basic.getGridManager()
        node=manager.getNode(auth,nodeId)
        vm = None
        try:
            vm = node.get_dom(domId)
        except Exception, e:
            LOGGER.error(to_str(e))
        if vm and vm.is_resident() and vm.get_config():
            config = vm.get_config()
            provider_id = config["provider_id"]
        #print provider_id
        result=[]
        if provider_id:
            (proxy,ops) = self.get_appliance_ops(provider_id)
            for key,desc in ops:
                result.append(dict(name=desc,value=key))
        return result

    def get_appliance_ops(self,provider_id):
        appliance_providers = { "rPath" : "rPathProxyModel",
                                "JumpBox" : "JBProxyModel"}
        appliance_proxy = {}
        a_proxy = appliance_providers[provider_id]
        try:
            code = "from convirt.viewModel.%s import %s; proxy=%s(); ops = proxy.getProxyIntegration()"  % (a_proxy,a_proxy, a_proxy)
            exec(code)
            appliance_proxy[provider_id] = (proxy,ops)
            return (proxy,ops)
        except Exception, ex:
            print "Skipping Application interation for " + provider_id, ex

        
"""
AppInfo is created specifically to convert the structure to xml doc.
Right now it works on list of nested dictionary.
for example:
[{...}
 {...}
 {... { }
      { }}]
"""
class AppInfo:
    def __init__(self, data):
        self.data = data
    
    def toXml(self, doc):
        xmlNode = doc.createElement("ApplianceList")

        if self.data is None:
            pass
        else:
            for item in self.data:
                xmlNode.appendChild(self.make_info_node(item, doc))
        
        return xmlNode;

    def make_info_node(self, item, doc):
        resultNode = doc.createElement("Appliance");
        
        keys = item.keys()
        for key in keys:
            newData = item[key]
            if isinstance(newData, dict):
                resultNode.appendChild(self.make_info_node(newData, doc))
            else:
                resultNode.setAttribute(self.stripAttribute(key), to_str(newData))

        return resultNode;

    def stripAttribute(self, name):
        expr = re.compile('(\((\S*)\))');
        percentReg = re.compile('%');
        if (percentReg.search(name)):
            return expr.sub('_PERCENT', name)
        else:
            return expr.sub(r'_\2', name);
