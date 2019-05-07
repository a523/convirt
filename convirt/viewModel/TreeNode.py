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

from convirt.client.dialogs import ApplianceLogos
import cherrypy
from xml.dom import minidom

from convirt.core.utils import constants
from convirt.model.VM import VM
import Basic

class TreeNode(object):
    def __init__(self, id, type, label, icon, branch="false"):
        self.id = id
        self.type = type
        self.label = label
        self.icon = icon
        self.branch = branch
        self.children = []
        
    def addChild(self, child):
        self.children.append(child)        

   
    def load_managed_node(managed_node, parent):
        tnode = TreeNode(managed_node.hostname, constants.MANAGED_NODE, managed_node.hostname, 
                TreeNode.get_state_pixbuf(constants.MANAGED_NODE), "true")

        parent.addChild(tnode)

        if (managed_node.is_authenticated() or not managed_node.is_remote()):
            snapshot = managed_node.get_metrics()
            if snapshot is not None:
                snapshot_keys = snapshot.keys()
                snapshot_len = len(snapshot_keys)
            else:
                snapshot_keys = []
                snapshot_len = 0

            #self.adjust_columns(self.NODE_SUMMARY, snapshot_len > 0)            
            doms = managed_node.get_dom_names()
            doms.sort()
    
            # the list of domains below each node
            for dom_name in doms:
                dom = managed_node.get_dom(dom_name)
                if dom and dom.is_resident():
                    print "  ... "+dom_name 
                    if snapshot_len > 0 and dom_name in snapshot_keys:
                        snapshot_dom = snapshot[dom_name]
                    else:
                        snapshot_dom = None

                domnode = TreeNode(dom_name, constants.DOMAIN, 
                                   dom_name, 
                                   TreeNode.get_state_pixbuf(constants.DOMAIN, dom), 
                                   "false")
                tnode.addChild(domnode)
#                      iter = self.statmodel.insert_before(None, None)
#                      self.statmodel.set(iter,
#                                         self.M_NODE, managed_node,
#                                         self.DOM_INFO, dom,
#                                         self.SNAPSHOT, snapshot_dom,
#                                         self.MODE, self.NODE_SUMMARY
#                                             )
    load_managed_node = staticmethod(load_managed_node)
 
    def load_server_group(group, parent):
        tnode = TreeNode(group.getName(), constants.SERVER_POOL, group.getName(), 
                         TreeNode.get_state_pixbuf(constants.SERVER_POOL), "true")
        parent.addChild(tnode)
        nodes = group.getNodeList()
        for node_name in nodes:
            managed_node = nodes[node_name]
            TreeNode.load_managed_node(managed_node, tnode)

    load_server_group = staticmethod(load_server_group)

    def load_image_group(group, parent):
        tnode = TreeNode(group.id, constants.IMAGE_GROUP, group.name, 
                         TreeNode.get_state_pixbuf(constants.IMAGE_GROUP), "true")
        parent.addChild(tnode)    

        images = group.get_images()
        # Sort the images
        if images:
            image_list = [ x for x in images.itervalues() ]
            image_list.sort(key=lambda(x) : x.get_name())
        else:
            image_list = []            

        for image in image_list:            
            inode = TreeNode(image.id, constants.IMAGE, image.name, 
                             TreeNode.get_state_pixbuf(constants.IMAGE), "true")
            tnode.addChild(inode)
    load_image_group = staticmethod(load_image_group)

    def loadAll():        
        manager = Basic.getGridManager()
        
        # The data center "root" node                
        dcNode = TreeNode("Data Center", constants.DATA_CENTER, "Data Center", 
                          TreeNode.get_state_pixbuf(constants.DATA_CENTER), "true")
        
        # The list of managed nodes appear 1st
        nodes = manager.getNodeList()
        for node in nodes:
            managed_node = manager.getNode(node)
            TreeNode.load_managed_node(managed_node, dcNode)

        # now the list of server groups
        groups = manager.getGroupList()
        groupNames = manager.getGroupNames()    
        for name in groupNames:
            group = groups[name]
            TreeNode.load_server_group(group, dcNode)

        # the image store
        image_store = Basic.getImageStore()
        isNode = TreeNode("Image Store", constants.IMAGE_STORE, "Image Store", 
                          TreeNode.get_state_pixbuf(constants.IMAGE_STORE), "true")
        image_groups = image_store.get_image_groups()    
               
        # now the list of images
        for group in image_groups.itervalues():
            TreeNode.load_image_group(group, isNode)
                       
        return [dcNode, isNode]
    loadAll = staticmethod(loadAll)

# get the icon to use for a particular node.. this could be cleaned up some
    def get_state_pixbuf(node_type = None, node = None):   
        appliance_store = Basic.getApplianceStore()
        
        if node_type is None :
            return
        
        # need to fix these...
        managed_node = None
        provider_id = None
        g_name = None
        dom_name = None
        
        pb = unknown_pb
    
        if node_type == constants.MANAGED_NODE:
            pb = node_pb
        elif node_type == constants.IMAGE_STORE:
            pb = dc_pb
        elif node_type == constants.IMAGE_GROUP:
            pb = image_store_pb
        elif node_type == constants.IMAGE:
            pb = image_pb
            if g_name:
                #provider_id = g_name
                ppb = None
                if provider_id:
                    ppb = ApplianceLogos.get_provider_logo(appliance_store,
                                                           provider_id)
                if ppb:
                    pb = ppb
    
#        elif managed_node is not None and node_type == constants.DOMAIN: # dom
#            dom = managed_node.get_dom(dom_name)
        elif node_type == constants.DOMAIN: # dom
            dom = node
    
            if dom and dom.is_resident():
                try:
                    state = dom.get_state()
                except xmlrpclib.Fault :
                    state = None
    
                if state is not None and state == VM.PAUSED:
                    pb = paused_pb
                else:                                
                    pb = resident_pb
            else:
                #print "constants.get_state_pixbuf not_resident_pb DOMAIN"
                pb = not_resident_pb
                
        elif node_type == constants.SERVER_POOL:
            pb = pool_pb
        elif node_type == constants.DATA_CENTER:
            pb = dc_pb
        
        return pb
    get_state_pixbuf = staticmethod(get_state_pixbuf)

    def toXml(self, xml):
        node = xml.createElement("treeNode")
        node.setAttribute("id", str(self.id))
        node.setAttribute("type", str(self.type))
        node.setAttribute("label", self.label)
        node.setAttribute("icon", str(self.icon))
        node.setAttribute("branch", str(self.branch))
        if self.children is not None :
            node.setAttribute("numChildren", str(len(self.children)))
            for child in self.children :
                node.appendChild(child.toXml(xml))         
            
# Flex throws away children if there is only a single child... have verified
# that the children are there if you access the same URL directly.  Somewhere
# in the code under HttpService, the ArrayCollection that is formed throws
# out children if there is only a single child.  So for how we add a "NullNode"
# if there is only a single child and the client has to ignore it...
            if len(self.children) == 1 :
                node.appendChild(NullNode().toXml(xml))
        else :
            node.setAttribute("numChildren", "0")
        return node    

class NullNode(TreeNode):
    def __init__(self):
        TreeNode.__init__(self, 0,0,"_NullNode_","")

paused_pb   = "small_pause"
resident_pb = "small_started_state"
not_resident_pb = "small_shutdown"
node_pb = "small_node"
dc_pb = "small_pool"
pool_pb = "group"
unknown_pb = "small_unknown_state"
image_store_pb = "small_image_store"
image_pb = "small_image"
connected_pb = "small_connect_blue"
disconnected_pb = "small_disconnect_yellow"
appliance_pb = "small_appliance"
convirt_pb = "convirt"

## error_img = gtk.Image()
## error_img.set_from_stock(gtk.STOCK_DIALOG_ERROR,
##                          gtk.ICON_SIZE_MENU)
## error_pb = error_img.get_pixbuf()

## warn_img = gtk.Image()
## warn_img.set_from_stock(gtk.STOCK_DIALOG_WARNING,
##                         gtk.ICON_SIZE_MENU)

## warn_pb = warn_img.get_pixbuf()

warn_pb = connected_pb
error_pb = disconnected_pb
    
