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

from convirt.core.utils.utils import constants
from convirt.viewModel.TreeNode import TreeNode
from convirt.viewModel.DashboardInfo import DashboardInfo
import Basic

import cherrypy
import re

class DataCenterService:
    def __init__(self):
        self.manager = Basic.getGridManager()
    
    def execute(self):
        managed_node = None
        infoObject = None
        
        if type is not None:
            if constants.DATA_CENTER == type:
                infoObject = self.gatherInfoForPool(pool_type = type, pool_name = groupLabel)
            elif constants.SERVER_POOL == type:
                infoObject = self.gatherInfoForPool(pool_type = type, pool_name = groupLabel)
            elif constants.MANAGED_NODE == type:
                managed_node = self.manager.getNode(nodeLabel, groupLabel)
                if managed_node is not None:
                    infoObject = [managed_node.get_metrics()]
        
        import pprint
        if infoObject is not None: pprint.pprint(infoObject)
        dashboardInfo = DashboardInfo(infoObject)
        return dashboardInfo



"""
DashboardInfo is created specifically to convert the structure to xml doc.
Right now it works on list of nested dictionary.
for example:
[{...}
 {...}
 {... { }
      { }}]
"""
class TreeInfo:
    def __init__(self, data):
        self.data = data
    
    def toXml(self, doc):
        xmlNode = doc.createElement("TreeInfo")

        if self.data is None:
            pass
        else:
            for item in self.data:
                xmlNode.appendChild(self.makeInfoNode(item, doc))
        
        return xmlNode;

    def makeInfoNode(self, item, doc):
        resultNode = doc.createElement("InfoNode");
        
        keys = item.keys()
        for key in keys:
            newData = item[key]
            if isinstance(newData, dict):
                resultNode.appendChild(self.makeInfoNode(newData, doc))
            else:
                resultNode.setAttribute(self.stripAttribute(key), str(newData))

        return resultNode;

    def stripAttribute(self, name):
        import re
        expr = re.compile('(\(\S*\))');
        return expr.sub('', name);
