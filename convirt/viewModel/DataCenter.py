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

from xml.dom import minidom

from convirt.core.utils import constants
from convirt.model.VM import VM
import Basic

class DataCenter(object):

    def toXml(self, xml):
        data_center_xml = xml.createElement("DataCenter")

        servers_xml     = xml.createElement("Servers")

        manager = Basic.getGridManager()
        nodes = manager.getNodeList()

        for node in nodes:
            managed_node = manager.getNode(node)
            self.load_managed_node(managed_node, servers_xml, xml)

        if servers_xml.hasChildNodes():
            data_center_xml.appendChild(servers_xml)

        groups_xml = xml.createElement("ServerGroups")

        groups = manager.getGroupList()
        group_names = manager.getGroupNames()    
        for name in group_names:
            group = groups[name]
            self.load_group(group, groups_xml, xml)

        if groups_xml.hasChildNodes():
            data_center_xml.appendChild(groups_xml)

        return data_center_xml

    def load_group(self, group, parent_xml, xml):

        group_xml = xml.createElement("ServerGroup")
        group_xml.setAttribute("id", group.getName())
        group_xml.setAttribute("label", group.getName())

        parent_xml.appendChild(group_xml)

        servers_xml     = xml.createElement("Servers")

        nodes = group.getNodeList()
        for node in nodes:
            managed_node = group.getNode(node)
            self.load_managed_node(managed_node, servers_xml, xml)

        if servers_xml.hasChildNodes():
            group_xml.appendChild(servers_xml)
        

    def load_managed_node(self, managed_node, parent_xml, xml):

        node_xml = xml.createElement("Server")
        node_xml.setAttribute("id", managed_node.hostname)
        node_xml.setAttribute("label", managed_node.hostname)

        parent_xml.appendChild(node_xml)

        vms_xml = xml.createElement("VMs")

        doms = managed_node.get_dom_names()
        doms.sort()

        for dom_name in doms:
            dom = managed_node.get_dom(dom_name)
            self.load_vm(dom, vms_xml, xml)

        if vms_xml.hasChildNodes():
            node_xml.appendChild(vms_xml)

    def load_vm(self, dom, parent_xml, xml):
        
        vm_xml = xml.createElement("VM")
        vm_xml.setAttribute("id", dom.name)
        vm_xml.setAttribute("label", dom.name)
        # FIXME add state

        parent_xml.appendChild(vm_xml)



