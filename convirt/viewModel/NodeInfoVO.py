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
# NodeInfoVO.py
from convirt.core.utils import utils
from convirt.core.utils.utils import to_unicode,to_str
from convirt.core.utils.constants import *
class NodeInfoVO:
    def __init__(self, node):
        self.node = node

    def toXml(self, xml):
        node_info_xml = xml.createElement("NodeInfo")
        credentials=self.node.get_credentials()
        node_info_xml.setAttribute("hostname",self.node.hostname)
        node_info_xml.setAttribute("platform", self.node.platform)
        node_info_xml.setAttribute("username",credentials["username"])
        node_info_xml.setAttribute("configdir",self.node.get_config_dir())
        node_info_xml.setAttribute("isRemote",to_str(self.node.is_remote()))
        node_info_xml.setAttribute("snapshotdir",self.node.config.get(prop_snapshots_dir))
        if(self.node.platform=='xen'):
            node_info_xml.setAttribute("xen_port",to_str(self.node.tcp_port))
            node_info_xml.setAttribute("protocol",self.node.protocol)
        node_info_xml.setAttribute("migration_port",to_str(self.node.migration_port))
        node_info_xml.setAttribute("use_keys",to_str(credentials["use_keys"]))
        node_info_xml.setAttribute("ssh_port",to_str(credentials["ssh_port"]))
        node_info_xml.setAttribute("address",self.node.address)

        return node_info_xml

    def toJson(self):
        if self.node is None:
            return {}
        node_info = {}
        credentials=self.node.get_credentials()
        node_info["hostname"]=self.node.hostname
        node_info["platform"]=self.node.platform
        node_info["username"]=credentials["username"]
        node_info["configdir"]=self.node.get_config_dir()
        node_info["isRemote"]=to_str(self.node.is_remote())
        node_info["snapshotdir"]=self.node.config.get(prop_snapshots_dir)
        if(self.node.platform=='xen'):
            node_info["xen_port"]=to_str(self.node.tcp_port)
            node_info["protocol"]=self.node.protocol
        node_info["migration_port"]=to_str(self.node.migration_port)
        node_info["use_keys"]=to_str(credentials["use_keys"])
        node_info["ssh_port"]=to_str(credentials["ssh_port"])
        node_info["address"]=self.node.address

        return node_info

