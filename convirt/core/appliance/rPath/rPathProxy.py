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

class rPathProxy(ApplianceProxy):

    url_list = [ ("NAV_BACKUP_CONFIG", ("Backup",'rAA/backup/Backup')),
                ("NAV_EMAIL_CONFIG" ,  ("Email",'rAA/configure/SmtpConf')),
                ("NAV_NETWORK_CONFIG", ("Network",'rAA/configure/Network')),
                ("NAV_PROXY_CONFIG",  ("Proxy",'rAA/configure/Proxy')),
                ("NAV_SET_ROOT_PASSWORD", ("Root Password",'rAA/configure/RootPw')),
                ("NAV_SET_TIME_ZONE" , ("Time Zone",'rAA/configure/SetTimeZone')),
                ("NAV_SET_SSL_CERT" , ("SSL Cert",'rAA/configure/SSLCert')),
                ("NAV_SERVICES", ("Services",'rAA/services/Services')),
                ("NAV_UPDATES", ("Updates",'rAA/updatetroves/UpdateTroves')),
                ("NAV_USERS" , ("Users",'rAA/usermanagement/UserInterface')),
                ("NAV_LOGS", ("Logs",'rAA/logs/Logs'))
               ]

    def __init__(self):
        # initialize the UI component
        self.ui = rPathUI()

    def get_path(self, in_opcode):
        for (opcode,(desc, path)) in self.url_list:
            if opcode == in_opcode:
                return path

    def getProxyIntegration(self):
        ops = [] 
        #ops =  [ ("CHECK_FOR_UPDATE" ,"Check For Updates") ,
        #         ("BACKUP_NOW" ,"Backup Now") ,
        #         ("SET_ROOT_PASSWORD" , "Set Root Password")
        #       ]
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
        if opcode == "SET_ROOT_PASSWORD":
            self.ui.SetRootPassword(vm)
        elif opcode == "BACKUP_NOW":
            self.ui.BackupNow(vm)
        elif opcode == "CHECK_FOR_UPDATE":
            self.ui.CheckForUpdade(vm)
        elif opcode.find('NAV_') == 0:
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
class rPathUI:
    def __init__(self):
        self.defaults = { "default_app_protocol":"http",
                          "default_app_host":"",
                          "default_app_port": 80,
                          "default_app_path":"/",
                          "default_app_mgmt_protocol":"https",
                          "default_app_mgmt_port" : 8003 }
        



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


    def SpecifyDetails(self, vm):
        config = vm.get_config()
        if config:
            dlg = ApplianceDetailsDlg()
            ret = dlg.show(config, self.defaults)
        else:
            raise Exception("VM config not found.")
        

    def get_agent(self, vm, username=None, password=None):
        (conn, creds) =  self.get_info(vm, username, password)
        agent = rPathAgent(conn, creds)
        return agent

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

    
    def SetRootPassword(self, vm):
        try:
            agent = self.get_agent(vm)
            new = "foo5555"
            repeat = "fff"   # user typed repeated password.
            agent.set_root_password(new, repeat)
        except Exception, ex:
            print ex
            raise


    def BackupNow(self, vm):
        try:
            agent = self.get_agent(vm)
            agent.backup_now()
        except Exception, ex:
            print ex
            raise 
                
    def CheckForUpdade(self, vm):
        try:
            agent = self.get_agent(vm)
            updates = agent.check_for_updates()
            pprint.pprint(updates)
        except Exception, ex:
            print ex
            raise




# class that implements the actual communication to the appliance agent.
import xmlrpclib
import time
class rPathAgent:
    # Status code for scheduled tasks
    TASK_SCHEDULED = 0
    TASK_PENDING   = 1
    TASK_RUNNING   = 2
    TASK_SUCCESS   = 3
    TASK_UNSCHEDULED = 4
    TASK_PREVENTED   = 5
    TASK_TEMPORARY_ERROR =16
    TASK_FATAL_ERROR     =32
    
    def __init__(self, connection_info, creds):
        self.connection_info = connection_info
        self.creds = creds

        (proto,host, port) = self.connection_info
        (username, password) = self.creds

        self.proto = proto
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.__agent = None
        self._init_agent()
        
    def disconnect(self):
        if self.__agent:
            self.__agent.close()
            
    def _init_agent(self):
        if self.__agent:
            self.__agent.close()
            
        url = "%s://%s:%s@%s:%d/rAA/xmlrpc" % (self.proto,self.username,
                                               self.password,
                                               self.host, self.port)
        self.__agent = xmlrpclib.ServerProxy(url)

    def set_root_password(self, new_password, repeat_new_password):
        res = self.__agent.configure.RootPw.changePass(new_password,
                                                       repeat_new_password)
        pprint.pprint(res)
        if len(res["errors"]) > 0:
            raise Exception(res["errors"])

    def backup_now(self):
        res = self.__agent.backup.Backup.backupNow()
        schedId = res["schedId"]
        self.wait_for_task(schedId)
        
    def check_for_updates(self):
        updater = self.__agent.updatetroves.UpdateTroves
        schedId = updater.callCheck()
        self.wait_for_trove_task(schedId)

        updates = updater.callGetAvailableUpdates()
        return updates

    def wait_for_trove_task(self, schedId):
        max_wait_sec = 60
        tick_value = 0.5
        
        updater = self.__agent.updatetroves.UpdateTroves
        max_num_ticks = max_wait_sec /  tick_value
        tick = 0
        stat = updater.callGetRunStatus()
        status, statusmsg, id = stat["status"], stat["statusmsg"],\
                                stat["schedId"]
        
        while status in (self.TASK_SCHEDULED, self.TASK_PENDING,
                         self.TASK_RUNNING) and tick < max_num_ticks \
                         and id != -1:
            tick=tick +1
            time.sleep(0.1)
            stat = updater.callGetRunStatus()
            status, statusmsg, id = stat["status"], stat["statusmsg"], \
                                    stat["schedId"]

        if tick >= max_num_ticks:
            raise Exception("Long operation : Last known schedId=%d stauts=%d statusmsg=%s", schedId, status, statusmsg)
        
        # TODO : This might need refinement..
        if id != -1:
            raise Exception("Error : stauts=%d statusmsg=%s", status, statusmsg)
        
        return True
        

    def wait_for_task(self, schedId):
        max_wait_sec = 60
        tick_value = 0.1

        max_num_ticks = max_wait_sec /  tick_value
        tick = 0
        stat = self.__agent.callGetStatus(schedId)
        status, statusmsg = stat["status"], stat["statusmsg"]
        while status in (self.TASK_SCHEDULED, self.TASK_PENDING,
                         self.TASK_RUNNING) and tick < max_num_ticks:
            tick=tick +1
            time.sleep(0.1)
            stat = self.__agent.callGetStatus(schedId)
            status, statusmsg = stat["status"], stat["statusmsg"]

        if tick >= max_num_ticks:
            raise Exception("Long operation : Last known stauts=%d statusmsg=%s", status, statusmsg)
        if status != self.TASK_SUCCESS:
            raise Exception("Error : stauts=%d statusmsg=%s", status, statusmsg)
        
        return True
    
if __name__ == '__main__':
    connection_info = ("https", "192.168.12.105", 8003)
    creds = ("admin", "password")

    agent = rPathAgent(connection_info, creds)
    print agent.set_root_password("foo", "foo")





