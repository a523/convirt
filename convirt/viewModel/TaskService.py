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
# Metric.py
#
#   This module contains a list of numeric values with timestaps
#
from convirt.viewModel.Basic import Basic
from convirt.core.utils.Util import constants
from convirt.model.Groups import ServerGroup

import cherrypy


    
class TaskService:
    def __init__(self):
        self.manager = Basic.getGridManager()
    
    def execute(self, taskType, domId, nodeId):
        cherrypy.log ("start type="+ taskType+ "domId="+ domId)
        managed_node = self.manager.getNode(nodeId)

        dom = managed_node.get_dom(domId)
        cherrypy.log ("dom id " + dom.id)

        """Start the selected domain"""
        if taskType == constants.START:
            if not dom.is_resident():
                cherrypy.log("start")
                dom._start()
        elif taskType == constants.PAUSE:
            if dom.is_resident():
                cherrypy.log("pause")
                dom._pause();
        elif taskType == constants.REBOOT:
            if dom.is_resident():
                cherrypy.log("rebooting" + dom.id)
                dom._reboot();
        elif taskType == constants.SHUTDOWN:
            if dom.is_resident():
                cherrypy.log("shutdown" + dom.id)
                dom._shutdown();
        elif taskType == constants.KILL:
            if dom.is_resident():
                cherrypy.log("kill")
                dom._destroy();
        else:
            pass

    def connect_node(self, nodeId, username, password):
        managed_node = self.manager.getNode(nodeId)

        if managed_node is None:
            pass
        else:
            managed_node.set_credentials(username, password)
            managed_node.connect()

    def disconnect_node(self, nodeId):
        managed_node = self.manager.getNode(nodeId)

        if managed_node is None:
            pass
        else:
            managed_node.disconnect()

        

    def add_node(self, platform, hostname, ssh_port, username, password, is_remote, use_keys, address = None):

        factory = self.manager.getFactory(platform)

        if address is None:
            address = hostname

        node = factory.create_node(platform = platform,
                                   hostname = hostname,
                                   username= username,
                                   password= password,
                                   isRemote= is_remote,
                                   ssh_port = ssh_port,
                                   use_keys = use_keys,
                                   address = address)
        self.manager.addNode(node)
        return node

    def add_group(self, name):
        group = ServerGroup(name)
        self.manager.addGroup(group)
        return group


    def status(self, taskId):
        pass

