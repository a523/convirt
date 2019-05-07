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
# ApplianceEntryVO.py
#
#   This module contains code to decode the appliance entry information from XML
#
import Basic
from xml.dom import minidom
    
class ApplianceEntryVO:
    def __init__(self, xml_string):
        self.image_store = Basic.getImageStore()
        self.xml_string = xml_string
#        import pprint; print "xml_string:",;pprint.pprint(str(xml_string))
#        print "xml_string is ", type(xml_string), str(xml_string).upper()
        self.xml_dom = minidom.parseString(self.xml_string)

    """
        <Appliance 
            PAE="True" 
            arch="x86" 
            archive="false" 
            compressed="gzip" 
            description="..."
            filename="asterisk-0.9.6.5-x86.img.gz" href="http://www.convirture.com/cgi-bin/download.cgi?provider=rPath&fileId=18951&filename=asterisk-0.9.6.5-x86.img.gz"
            id="http://www.rpath.org/rbuilder/project/asterisk/" installed_size="-1" is_hvm=""
            link="http://www.rpath.org/rbuilder/project/asterisk/" platform="Xen" popularity_score="100"
            provider="rPath Appliances" provider_id="rPath"
            provider_logo_url="http://wiki.rpath.com/wiki/images/thumb/e/e7/Rpath-vert.gif/30px-Rpath-vert.gif"
            provider_url="http://www.rpath.com" short_description="" size="285115596"
            title="AsteriskNOW" 
            type="FILE_SYSTEM" 
            updated="2007-07-26 18:51:19"/>
    """
    def entry_map(self):
        nodeList = self.xml_dom.getElementsByTagName("Appliance")
        appliance_entry = {}
        if (nodeList._get_length() > 0):
            xmlNode = nodeList.item(0)
            appliance_entry["PAE"]                  = xmlNode.getAttribute("PAE")
            appliance_entry["arch"]                 = xmlNode.getAttribute("arch") 
            appliance_entry["archive"]              = xmlNode.getAttribute("archive")
            appliance_entry["compressed"]           = xmlNode.getAttribute("compressed")
            appliance_entry["description"]          = xmlNode.getAttribute("description")
            appliance_entry["filename"]             = xmlNode.getAttribute("filename") 
            appliance_entry["href"]                 = xmlNode.getAttribute("href")
            appliance_entry["id"]                   = xmlNode.getAttribute("id") 
            appliance_entry["installed_size"]       = xmlNode.getAttribute("installed_size") 
            appliance_entry["is_hvm"]               = xmlNode.getAttribute("is_hvm")
            appliance_entry["link"]                 = xmlNode.getAttribute("link") 
            appliance_entry["platform"]             = xmlNode.getAttribute("platform") 
            appliance_entry["popularity_score"]     = xmlNode.getAttribute("popularity_score")
            appliance_entry["provider"]             = xmlNode.getAttribute("provider") 
            appliance_entry["provider_id"]          = xmlNode.getAttribute("provider_id")
            appliance_entry["provider_logo_url"]    = xmlNode.getAttribute("provider_logo_url")
            appliance_entry["provider_url"]         = xmlNode.getAttribute("provider_url") 
            appliance_entry["short_description"]    = xmlNode.getAttribute("short_description") 
            appliance_entry["size"]                 = xmlNode.getAttribute("size")
            appliance_entry["title"]                = xmlNode.getAttribute("title") 
            appliance_entry["type"]                 = xmlNode.getAttribute("type") 
            appliance_entry["updated"]              = xmlNode.getAttribute("updated")
        
        import pprint
        print "appliance_entry in parsing", ; pprint.pprint(appliance_entry)
        return appliance_entry

"""
ServiceInfo Return object
"""
class ServiceInfo:
    def __init__(self, return_code, svc_name):
        self.return_code = return_code
        self.svc_name = svc_name
    
    def toXml(self, doc):
        xmlNode = doc.createElement(self.svc_name)
        xmlNode.setAttribute("returnCode", str(self.return_code))
        return xmlNode;