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
# VMInfo.py

#import cherrypy

from xml.dom import Node
import Basic
from convirt.core.utils.utils import randomMAC   

class VMInfo:
    def __init__(self):
        pass

    def toXml(self, xml):
        vm_info_xml = xml.createElement("VMInfo")
        vm_info_xml.setAttribute("name",   self.vm_config.name)

        # for option in self.vm_config.options:
            # cherrypy.log("option " + option)
            # cherrypy.log("value  " + str(self.vm_config.options[option])) 
        
        vm_info_xml.setAttribute("vcpus",  str(self.vm_config.options["vcpus"]))
        vm_info_xml.setAttribute("memory", str(self.vm_config.options["memory"]))
        vm_info_xml.setAttribute("nodeId", str(self.node_id))
        vm_info_xml.setAttribute("domId",  str(self.dom_id))
        
        diskEntriesXml = xml.createElement("DiskEntries")
        vm_info_xml.appendChild(diskEntriesXml)
        
        propertiesXml = xml.createElement("Properties")
        vm_info_xml.appendChild(propertiesXml)

        # vm_storage_stat = self.vm_config.get_storage_stats()
        for de in self.vm_config.getDisks():
            # disk_size,disk_dev_type = vm_storage_stat.get_disk_size(de)
 
            filename = de.filename
            type     = de.type
            device   = de.device
            mode     = de.mode

            diskEntryXml = xml.createElement("DiskEntry")
            diskEntriesXml.appendChild(diskEntryXml)

            diskXml = xml.createElement("Disk")
            diskEntryXml.appendChild(diskXml)

            # diskXml.setAttribute("size", disk_size)
            # diskXml.setAttribute("type", disk_dev_type)
            diskXml.setAttribute("filename", filename)
            diskXml.setAttribute("type", str(type))

            refDiskXml = xml.createElement("ReferenceDisk")
            diskEntryXml.appendChild(refDiskXml)

            vmDeviceXml = xml.createElement("VMDevice")
            vmDeviceXml.setAttribute("mode", str(de.mode))
            vmDeviceXml.setAttribute("device", str(de.device))
            diskEntryXml.appendChild(vmDeviceXml)


        for option in self.vm_config.options:
            if (option == "vcpus"):
                continue
            elif (option == "memory"):
                continue
            elif (option == "name"):
                continue
            elif (option == "disk"):
                continue
            
            propertyXml = xml.createElement("Property")
            
            propertiesXml.appendChild(propertyXml)
            propertyXml.setAttribute("name", str(option))
            propertyXml.setAttribute("value", str(self.vm_config.options[option]))
            
        return vm_info_xml 
    
    def fromStore(node_id, dom_id):
        vm_info = VMInfo()

        manager      = Basic.getGridManager()

        managed_node = manager.getNode(node_id)
        dom          = managed_node.get_dom(dom_id)
        vm_info.vm_config = dom.get_config()
        vm_info.node_id = node_id
        vm_info.dom_id  = dom_id
        return vm_info
    
    fromStore = staticmethod(fromStore)
    

    def fromXml(xml):

        vm_info = VMInfo()

        manager      = Basic.getGridManager()
        registry     = Basic.getPlatformRegistry()
        image_store  = Basic.getImageStore()


        node_id     = xml.getAttribute("nodeId")
        dom_id      = xml.getAttribute("domId")
        image_id    = xml.getAttribute("imageId")

        vm_info.node_id = node_id
        vm_info.dom_id  = dom_id
        vm_info.image_id = image_id

        managed_node = manager.getNode(node_id)
        dom          = managed_node.get_dom(dom_id)
        platform     = managed_node.get_platform()

        if dom is None:
            platform_object   = registry.get_platform_object(platform)
            vm_info.vm_config = platform_object.create_vm_config(managed_node)
            vm_info.vm_config.platform   = platform
            vm_info.vm_config.set_managed_node(managed_node)
        else:
            vm_info.vm_config = dom.get_config()
            vm_info.vm_config.platform   = platform
            vm_info.vm_config.set_managed_node(managed_node)
        
                
        
        vm_info.vm_config.image_id = image_id
        vm_info.parseVMInfo(xml)
        
        image = image_store.get_image(image_id)
        if image is not None:
            image_vm_config, image_config = image.get_configs()
            vm_info.image_config = image_config

#        vm_info.instantiate_configs(managed_node,
#                                    image_store,
#                                    vm_info.vm_config.image_name,
#                                    vm_info.vm_config.image_location,
#                                    vm_info.vm_config,
#                                    vm_info.image_config)
        
        cherrypy.log(vm_info.vm_config.filename)
        return vm_info
        
    fromXml = staticmethod(fromXml)
    
    # parses a <VMInfo/> node
    def parseVMInfo(self, xml):
        self.vm_config["name"]           = xml.getAttribute("name").encode("utf8")
        # self.vm_config.name              = xml.getAttribute("name").encode("utf8")       
        self.vm_config["filename"]       = "/etc/xen/" + self.vm_config.name
        self.vm_config.filename          = "/etc/xen/" + self.vm_config.name

        # self.vm_config.options    = {}
        self.vm_config.options["vcpus"]  = int(xml.getAttribute("vcpus").encode("utf8"))
        self.vm_config.options["memory"] = int(xml.getAttribute("memory").encode("utf8"))
        # self.vm_config.options["name"]   = xml.getAttribute("name").encode("utf8")
        
        self.vm_config.options["image_name"]     = xml.getAttribute("image_name").encode("utf8")
        self.vm_config.options["image_id"]       = xml.getAttribute("imageId").encode("utf8")
        self.vm_config.options["image_location"] = xml.getAttribute("image_location").encode("utf8")
       
#        if self.vm_config.image_location:
#            self.vm_config.image_location = os.path.basename(self.vm_config.image_location)
        
        self.vm_config.disk = []
        
        for diskEntryNode in xml.getElementsByTagName("DiskEntry"):
            self.vm_config.disk.append(self.parseDiskEntry(diskEntryNode))
        self.vm_config.options["disk"] =self.vm_config.disk 
        
        for propertyNode in xml.getElementsByTagName("Property"):
            self.parseProperty(self.vm_config.options, propertyNode)
    
    def parseProperty(self, options, xml):
        name = xml.getAttribute("name").encode("utf8")
        value= xml.getAttribute("value").encode("utf8")
        options[name] = value
        
    # parses a <DiskEntry/> node
    def parseDiskEntry(self, xml):
        diskEntry = {}
        for node in xml.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.tagName == 'Disk':
                    self.parseDisk(node, diskEntry)
                elif node.tagName == 'ReferenceDisk':
                    self.parseReferenceDisk(node, diskEntry)
                elif node.tagName == 'VMDevice':
                    self.parseVMDevice(node, diskEntry)
                    
        result = diskEntry["type"] + ":" + diskEntry["filename"] + "," + diskEntry["device"] + "," + diskEntry["mode"]
        return result
    
    def parseDisk(self, xml, diskEntry):
        diskEntry["type"] = xml.getAttribute("type").encode("utf8")
        diskEntry["filename"] = xml.getAttribute("location").encode("utf8")
    
    def parseReferenceDisk(self, xml, diskEntry):
        pass
    
    def parseVMDevice(self, xml, diskEntry):
        diskEntry["device"] = xml.getAttribute("device").encode("utf8")
        diskEntry["mode"]   = xml.getAttribute("mode").encode("utf8")

    def instantiate_configs(self,
                            managed_node,
                            image_store, 
                            image_name, 
                            image_location,
                            vm_config, image_config):
     
        # get prepare template map
        template_map = {} 

        store_location = image_store.get_remote_location(managed_node)
     
        template_map["IMAGE_STORE"]    = store_location
        template_map["IMAGE_NAME"]     = image_name
        template_map["IMAGE_LOCATION"] = image_location
        template_map["VM_NAME"]        = vm_config["name"]

        # Auto generated MAC address
        # TODO: keep track of generated MAC's
        template_map["AUTOGEN_MAC"] = randomMAC()

        # image_config.instantiate_config(template_map)

        # instantiate vm_config with image configuration
        vm_config.instantiate_config(template_map)
        if image_config is not None:
            vm_config.instantiate_config(image_config)

