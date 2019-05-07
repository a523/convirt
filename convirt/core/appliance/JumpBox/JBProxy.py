#!/usr/bin/env python
#
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
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# 
#
# author : Jd <jd_jedi@users.sourceforge.net>
#

from convirt.core.appliance.ApplianceProxy import ApplianceProxy
from convirt.core.utils.utils import show_url
import pprint

# class implements ui integration and backend to the proxy.
# JumpBox Appliance

class JBProxy(ApplianceProxy):

    url_list = [ ("NAV_REGISTER_APPLIANCE", ("Register",'register')),
                 ("NAV_INFO" ,  ("Info",'info')),
                 ("NAV_NETWORK_CONFIG", ("Network",'staticip')),
                 ("NAV_PROXY_CONFIG",  ("Proxy",'proxy')),
                 ("NAV_SET_TIME_ZONE" , ("Time Zone",'timezone')),
                 ("NAV_BACKUP" , ("Backup",'backup')),
               ]

    def __init__(self):
        # initialize the UI component
        self.ui = JBUI()

    def get_path(self, in_opcode):
        for (opcode,(desc, path)) in self.url_list:
            if opcode == in_opcode:
                return path

    def getProxyIntegration(self):
        ops = []
        ops.append(("SPECIFY_DETAILS", "Specify Details"))
        ops.append(("SEPARATOR", "--"))
        ops.append(("VISIT_APPLICATION", "Application"))
        ops.append(("SEPARATOR", "--"))
        for op, details in self.url_list:
            desc, url = details
            ops.append((op,desc))
            
                
        return ops

    # Callback 
    def executeOp(self, context, opcode):
        vm = context
        if opcode.find('NAV_') == 0:
            self.ui.JumpTo(vm, self.get_path(opcode))
        elif opcode == "VISIT_APPLICATION" :
            self.ui.JumpToApp(vm)
        elif opcode == "SPECIFY_DETAILS" :
            self.ui.SpecifyDetails(vm)
        else:
            raise Exception("Invalid operation " + opcode)
        
# class that implements the UI components that would be invoked by
# convirt when a particular op is invoked.
from convirt.client.dialogs import ApplianceDetailsDlg

class JBUI:
    def __init__(self):
        self.defaults = { "default_app_protocol":"http",
                          "default_app_host":"",
                          "default_app_port": 80,
                          "default_app_path":"/",
                          "default_app_mgmt_protocol":"https",
                          "default_app_mgmt_port" : 3000 }
        
        

    def get_info(self, vm, username=None, password=None):
                     
        if vm and vm.get_config():
            config = vm.get_config()
            for vkey in ("host", "app_protocol", "app_port", "app_path",
                         "app_mgmt_protocol", "app_mgmt_port"):
                if not config.get(vkey):
                    dlg = ApplianceDetailsDlg()
                    ret = dlg.show(config, self.defaults)
                    break
                    
            host = config["host"]
            if not host:
                raise Exception("Appliance host not specified")
            
            proto = config["app_mgmt_protocol"]
            if not proto:
                raise Exception("Appliance management protocol not specified")

            if config["app_mgmt_port"]:
                port = int(config["app_mgmt_port"])
            else:
                raise Exception("Invalid appliance management port")

            app_proto= config["app_protocol"]
            
            if config["app_port"] :
                app_port = int(config["app_port"])
            else:
                raise Exception("Invalid appliance port")

            if config["app_path"] :
                app_path = config["app_path"]
            else:
                app_path = "/"

            # TBD : credential management needs to be done properly
            if username is None:
                username = "admin"
            if password is None:
                password = "password"

            return ((app_proto, host, app_port, app_path),
                    (proto, host, port),
                    (username, password))



    def get_agent(self, vm, username=None, password=None):
        return None
        return agent

    def SpecifyDetails(self, vm):
        config = vm.get_config()
        if config:
            dlg = ApplianceDetailsDlg()
            ret = dlg.show(config, self.defaults)
        else:
            raise Exception("VM config not found.")
        


    # get the web url
    def get_web_url(self, vm):
        (app_url, mgmt_url, creds) = self. get_info(vm)
        (proto, host, port, path) = app_url
        url = "%s://%s:%d/%s" % (proto, host, port, path)
        return url

    # get the web url
    def get_mgmt_web_url(self, vm, path):
        (app_url, mgmt_url, creds) = self. get_info(vm)
        (proto, host, port) = mgmt_url
        (u, p) = creds 
        url = "%s://%s:%d/%s" % (proto, host, port, path)
        return url

    # show the url in the browser
    def JumpTo(self,vm, path):
        url = self.get_mgmt_web_url(vm,path)
        show_url(url)
    

    # show the url in the browser
    def JumpToApp(self,vm):
        url = self.get_web_url(vm)
        show_url(url)




# class that implements the actual communication to the appliance agent.
#import xmlrpclib
#import time
class JBAgent:
    # Need to find out if they have a good remote APIs
    pass
    
if __name__ == '__main__':
    pass
    



