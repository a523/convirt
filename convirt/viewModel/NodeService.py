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

"""APIs to operate on a Managed Node."""

from tg import session
import stat, time,os
from convirt.core.utils import utils
from convirt.core.utils.utils import *
from convirt.core.utils.utils import constants,is_host_remote
from convirt.core.utils.utils import populate_node_filter,dynamic_map
from convirt.core.utils.utils import to_unicode,to_str,print_traceback,p_timing_start,p_timing_end
from convirt.model.Groups import ServerGroup
from convirt.viewModel.NodeInfoVO import NodeInfoVO
from convirt.core.utils.NodeProxy import Node
from convirt.viewModel.ResponseInfo import ResponseInfo
from convirt.core.utils.phelper import AuthenticationException
import Basic
import simplejson as json
from convirt.model.VM import vifEntry
from convirt.model.VM import ImageDiskEntry
from convirt.model.VM import VM, OutsideVM
from convirt.model.ManagedNode import ManagedNode

from sqlalchemy.orm import eagerload
from convirt.model import DBSession
from convirt.model.Entity import Entity,EntityRelation,EntityAttribute
from convirt.model.Metrics import MetricsService
from convirt.model.UpdateManager import UIUpdateManager
from convirt.model.storage import StorageManager, StorageDef
from convirt.model.SPRelations import StorageDisks
#from TaskCreator import TaskCreator
import traceback
import logging, transaction
LOGGER = logging.getLogger("convirt.viewModel")
class NodeService:

    def __init__(self):
        self.manager=Basic.getGridManager()

    def get_dom(self, auth, domId, nodeId=None):
        ''' Gets a VM object'''
        if nodeId is not None:
            node=self.get_managed_node(auth, nodeId)
            return node.get_dom(domId)
        return self.manager.get_dom(auth,domId)

    def get_managed_node(self, auth, nodeId):
        ''' Gets a Managed Node object'''
        managed_node = self.manager.getNode(auth,nodeId)
        return managed_node

    def get_nodes(self, auth, groupId):
        ''' Returns list of Managed Nodes under the group'''
        return self.manager.getNodeList(auth,groupId)

    def get_managed_nodes(self, auth, groupId, site_id=None):
        result=[]
        try:
            if site_id == 'data_center':
                site = self.manager.getSiteByGroupId(groupId)
                if site:
                    site_id = site.id
            if groupId:
                node_list=self.get_nodes(auth,groupId)
                for node in node_list:
                    tmp={}
                    tmp['hostname']=node.hostname
                    tmp['platform']=node.platform
                    tmp['group']=groupId
                    tmp['id']=node.id
                    result.append(tmp)
            elif site_id:
                group_list = self.manager.getGroupList(auth, site_id)
                if group_list:
                    for group in group_list:
                        if group:
                            node_list=self.get_nodes(auth,group.id)
                            for node in node_list:
                                tmp={}
                                tmp['hostname']=node.hostname
                                tmp['platform']=node.platform
                                tmp['group']=groupId
                                tmp['id']=node.id
                                result.append(tmp)

        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg:' "+to_str(ex).replace("'", "")+"'}"
        return dict(success=True,rows=result)

    def get_group(self,auth, groupId):
        ''' Gets a Server Pool object'''
        return self.manager.getGroup(auth, groupId)

    def get_groups(self,auth):
        ''' Returns list of groups'''
        return self.manager.getGroupList(auth)

    def get_nav_nodes(self,auth):
        dcs=self.manager.getDataCenters()
        iss=self.manager.getImageStores()
        result=[]
        if len(dcs)==0:
            raise Exception("No DataCenter Found.")
        if len(iss)==0:
            raise Exception("No ImageStore Found.")
        for dc in dcs:
            childnode=NodeService().get_childnodestatus(auth,dc.id)
            d=dict(
                NODE_NAME= dc.name,
                NODE_ID= dc.id,
                NODE_TYPE=constants.DATA_CENTER,
                NODE_CHILDREN=childnode
            )
            result.append(d)

        for store in iss:
            childnode=NodeService().get_childnodestatus(auth,store.id)
            i=dict(
                NODE_NAME= store.name,
                NODE_ID= store.id,
                NODE_TYPE=constants.IMAGE_STORE,
                NODE_CHILDREN=childnode
            )
            result.append(i)

        return result


    def get_platforms(self):
        try:
            result = []
            registry=Basic.getPlatformRegistry()
            for plat, info in registry.get_platforms().iteritems():
                result.append(dict(name=info['name'],value=plat))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        return result

    def get_platform(self, auth, nodeId, type):
        platform=""
        image=None
        managed_node=None
        if type==constants.MANAGED_NODE:
            managed_node = self.get_managed_node(auth,nodeId)
            if managed_node is None:
                raise Exception("Can not find the specified Node.")
            platform=managed_node.get_platform()

        elif type==constants.IMAGE:
            image_store=Basic.getImageStore()
            image=image_store.get_image(auth,nodeId)
            if image is None:
                raise Exception("Can not find the Image.")
            platform=image.get_platform()
        return platform

    def get_vnc_info(self,auth,nodeId,domId,address):
        result=self.manager.get_vnc_info(auth,nodeId,domId,address)
        return result
    
    def get_ssh_info(self,auth,nodeId,address,client_platform):
        result=self.manager.get_ssh_info(auth,nodeId,address,client_platform)
        return result    

    def delete(self, auth,domId, nodeId):
        self.manager.remove_vm(auth, domId, nodeId)

    def server_action(self, auth,nodeId, action):
        managed_node = self.get_managed_node(auth,nodeId)
        if managed_node is not None:
            if not managed_node.is_authenticated():
                try:
                    managed_node.connect()
                except Exception, e:
                    return "{success:false,msg: '"+to_str(e).replace("'", "")+"'}"

            try:
                self.manager.do_node_action(auth,nodeId, action)
            except Exception, e:
                return "{success: false,msg:'"+to_str(e).replace("'", "")+"'}"
            return "{success: true,msg:'Operation Completed Successfully.'}"
        else:
            return "{success:false,msg: 'Can not find the Managed Node'}"

#    def get_nodes(self, groupId):
#        manager = Basic.getGridManager()
#        combined_node_list = []
#
#        if groupId is None:
#            group_list = [x for x in manager.getGroupList().itervalues()]
#            combined_node_list.extend(manager.getNodeList().itervalues())
#        else:
#            group_list = [x for x in manager.getGroupList().itervalues() if x.name == groupId]
#
#        group_list.sort(key=lambda(x) : x.getName())
#
#        for group in group_list:
#            combined_node_list.extend(group.getNodeList().itervalues())
#
#        return map((lambda x: NodeInfoVO(x)), combined_node_list)

    def get_node_info(self, auth,nodeId ):
        try:
            result=[]
            managed_node = self.get_managed_node(auth,nodeId)

            result.extend(self.getDictInfo(managed_node.get_platform_info(),managed_node.get_platform_info_display_names(),'Platform Info'))
            result.extend(self.getDictInfo(managed_node.get_os_info(),managed_node.get_os_info_display_names(),'OS Info'))
            result.extend(self.getDictInfo(managed_node.get_cpu_info(),managed_node.get_cpu_info_display_names(),'CPU Info'))
            result.extend(self.getDictInfo(managed_node.get_memory_info(),managed_node.get_memory_info_display_names(),'Memory Info'))

            result.extend(self.getListInfo(managed_node.get_disk_info(),managed_node.get_disk_info_display_names(),'Disk Info'))
            result.extend(self.getListInfo(managed_node.get_network_info(),managed_node.get_network_info_display_names(),'Network Info'))

        except Exception, ex:
            LOGGER.error(to_str(ex).replace("'",""))
            print_traceback()
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',rows=result)

    def refresh_node_info(self, auth, nodeId):
        try:
            result=[]
            managed_node = self.get_managed_node(auth,nodeId)
            managed_node.refresh_environ()
        except Exception, ex:
            LOGGER.error(to_str(ex).replace("'",""))
            print_traceback()
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',rows=result)

    def entity_context(self, auth, node_id):
        try:
            entity_det = auth.get_entity(node_id)
            state = VM.SHUTDOWN
            if entity_det.type.name==constants.DOMAIN:
                vm = DBSession.query(VM).filter(VM.id==entity_det.entity_id).options(eagerload("current_state")).first()
                state=vm.current_state.avail_state

            entity={"node_id":node_id,"node_text":entity_det.name,"node_type":entity_det.type.name,"state":state}
            parent=self.get_parent_id(auth,node_id)
            g_parent=self.get_parent_id(auth, parent.get("node_id"))
        except Exception, ex:
            LOGGER.error(to_str(ex).replace("'",""))
            print_traceback()
            raise ex
        return dict(entity=entity,parent=parent,g_parent=g_parent)

    def get_parent_id(self, auth, node_id):
        try:
            entity = auth.get_entity(node_id)
            parent_id = entity.parents[0].entity_id
            parent_name = entity.parents[0].name
            parent_type = entity.parents[0].type.name
#            print "result===",result
        except Exception, ex:
            LOGGER.error(to_str(ex).replace("'",""))
            print_traceback()
            raise ex
        return dict(node_id=parent_id,node_text=parent_name,node_type=parent_type)

    def get_childnodestatus(self,auth,node_id):
       try:
           childnode=False
           entity = auth.get_entity(node_id)
           if entity.children:
               childnode=True
       except Exception,ex:
            LOGGER.error(to_str(ex).replace("'",""))
            print_traceback()
            raise ex
       return childnode

    def get_updated_entities(self,user_name):
        try:
            updatemgr=UIUpdateManager()
            updated_entities=updatemgr.get_updated_entities(user_name)
            #print "\n\n\n\nupdate_nodes==="+user_name+"==",updated_entities
#            updatemgr.clear_updated_entities(user_name)
            return updated_entities
        except Exception,ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            print_traceback()
            raise ex        

    def get_vm_info(self, auth,domId):
        try:
            result=[]
            vm = self.get_dom(auth,domId)
            platform = vm.get_platform()
            registry=Basic.getPlatformRegistry()
            web_helper = registry.get_web_helper(platform)
            vm_info_helper = web_helper.get_vm_info_helper()

            result= vm_info_helper.get_vm_info(vm)

        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',rows=result)

    def get_vm_config_file(self, auth,domId, nodeId):
        text=""
        managed_node=self.get_managed_node(auth,nodeId)
        if not managed_node.is_authenticated():
            managed_node.connect()
        dom = self.get_dom(auth,domId)
#        filename=dom.get_config().filename
#        if managed_node.node_proxy.file_exists(filename):
#            file = managed_node.node_proxy.open(filename)
#            lines = file.readlines()
#            text = "".join(lines)
#            file.close()
        vmconfig=dom.vm_config
        text=to_str(vmconfig)
        return text

    def save_vm_config_file(self,auth,domId,nodeId, content):
        try:
            self.manager.save_dom_config_file(auth,domId, nodeId,content)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return "{success: true,msg: 'Success'}"

    def remove_vm_config_file(self, auth,domId, nodeId):
        try:
            self.manager.remove_dom_config_file(auth,domId, nodeId)                
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex

    def migrate_vm(self,auth, dom_name, domId, source_nodeId, dest_nodeId, \
                                                        live, force, all):
        try:
            managed_node = self.get_managed_node(auth, source_nodeId)
            dest_node = self.get_managed_node(auth, dest_nodeId)

            vm_list = []
            dom_list=[]
            if (all=='true'):
                for vm in self.manager.get_node_doms(auth,source_nodeId):
#                    if not vm.isDom0():
                    vm_list.append(vm)
                    dom_list.append(vm.id)
            else:
                dom = self.manager.get_dom(auth,domId)
                vm_list = [dom]
                dom_list.append(dom.id)

            isLive=False
            isForce=False
            e=[]
            w=[]
            if(live=='true'):
                isLive=True
            if(force=='true'):
                isForce=True
            if dest_node.is_up():
                dest_node.connect()
            if not isForce:
                (e, w) = managed_node.migration_checks(vm_list, dest_node, isLive)

            result=[]
            if not isForce and len(e)>0 or len(w)>0:
                for err in e:
                    (cat, msg) = err
                    result.append(dict(type='error',category=cat,message=msg))
                for warn in w:
                    (cat, msg) = warn
                    result.append(dict(type='warning',category=cat,message=msg))
                return dict(success=True,rows=result)

#            tc = TaskCreator()
#            tc.migrate_vm(auth, vm_list, source_node_id,\
#                               dest_node_id, live, force, all)
            result={}
            result['dom_list']=dom_list
            result['submit']=True
            return result
#            self.manager.submit_migrate_task(auth, vm_list, source_nodeId,\
#                               dest_nodeId, live, force, all)
#            if all=='true':
#                self.manager.migrateNode(auth,managed_node, dest_node, True, isForce)
#            else:
#                self.manager.migrateDomains(auth,managed_node, vm_list, dest_node, True, isForce)

        except Exception, e:
            print_traceback()
            LOGGER.error(to_str(e))
            return dict(success=False,msg=to_str(e).replace("'", ""))
        return dict(success=True,msg='Migrate Task Submitted.')

    def get_node_properties(self, auth,nodeId):
        managed_node = self.get_managed_node(auth,nodeId)
        #managed_node.connect()
        return NodeInfoVO(managed_node)

    def connect_node(self, auth,nodeId, username, password):

        result = dict(success=True,msg='Success')

        managed_node = self.get_managed_node(auth,nodeId)
        credentials=managed_node.get_credentials()
        old_pwd=credentials["password"]
        old_usr=credentials["username"]

        if username!="" and username != None:
            credentials["username"]=username
            if password == None:
                password=""
            credentials["password"] = password
            managed_node.set_node_credentials(managed_node.credential.cred_type, **credentials)
        try:
            if not managed_node.is_authenticated():
                managed_node.connect()
            managed_node.refresh_environ()
        except AuthenticationException ,ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            result = dict(success=False,msg=to_str(ex).replace("'", ""),error='Not Authenticated')            
        except Exception ,ex:
            print_traceback()
            result = dict(success=False,msg=to_str(ex).replace("'", ""))
            
        if result['success']==False:
            credentials["username"]=old_usr
            credentials["password"] = old_pwd
            managed_node.set_node_credentials(managed_node.credential.cred_type, **credentials)
            
        return result

    def disconnect_node(self, auth,nodeId):
        managed_node = self.get_managed_node(auth,nodeId)
        if managed_node is None:
            pass
        else:
            managed_node.disconnect()

    def add_node(self, auth, groupId, platform, hostname, ssh_port, username, password, protocol, xen_port,
                                        xen_migration_port, use_keys, address = None):
        factory = self.manager.getFactory(platform)

        if address is None:
            address = hostname
        if use_keys=='true':
            usekeys=True
        else:
            usekeys=False
        isRemote=is_host_remote(hostname)

        try:
            node = factory.create_node(platform = platform,
                                       hostname = hostname,
                                       username= username,
                                       password= password,
                                       is_remote= isRemote,
                                       ssh_port = int(ssh_port),
                                       use_keys = usekeys,
                                       address = address,
                                       protocol = protocol,
                                       tcp_port = int(xen_port),
                                       migration_port = int(xen_migration_port))
            node.connect();
            if usekeys:
                local_node=Basic.getManagedNode()
                setup_ssh_keys(node,local_node)
            self.manager.addNode(auth,node,groupId)
            
        except Exception , ex:
            err=to_str(ex).replace("'", " ")
            LOGGER.error(":"+err)
            print_traceback()
            return "{success: false,msg: '",err,"'}"
        else:
            return "{success: true,msg: 'Server Added'}"

    def edit_node(self, auth, node_id, platform, hostname, ssh_port, username, password, protocol, xen_port, xen_migration_port, use_keys, address = None):
        factory = self.manager.getFactory(platform)

        if address is None:
            address = hostname
        if use_keys=='true':
            usekeys=True
        else:
            usekeys=False
        isRemote=is_host_remote(hostname)
        try:
            node=self.manager.getNode(auth,node_id)
            node = factory.update_node(node,platform = platform,
                                       hostname = hostname,
                                       username= username,
                                       password= password,
                                       is_remote= isRemote,
                                       ssh_port = int(ssh_port),
                                       use_keys = usekeys,
                                       address = address,
                                       protocol = protocol,
                                       tcp_port = int(xen_port),
                                       migration_port = int(xen_migration_port)) 
            node.connect();
            if usekeys:
                local_node=Basic.getManagedNode()
                setup_ssh_keys(node,local_node)
            self.manager.editNode(auth, node)
        except Exception , ex:
            print_traceback()
            err=to_str(ex).replace("'", " ")
            LOGGER.error(":"+err)
            return "{success: false,msg: '",err,"'}"
        else:
            return "{success: true,msg: 'Server Updated'}"

    def get_migrate_target_sps(self, auth, node_id=None, sp_id=None):

        grps=self.get_groups(auth)
        result=[]
        for grp in grps:
            if grp.id!=sp_id:
                result.append(dict(name=grp.name,id=grp.id,type=constants.SERVER_POOL))
        return result

    def remove_node(self,auth,nodeId,force):
        try:
            node = self.manager.getNode(auth,nodeId)
            if node is None:
                raise Exception("Can not find the server.")
            if not force:
                domlist=node.get_all_dom_names()[0]
                runningdoms=[]
                try:
                    connected = False
                    runningdoms=self.manager.get_running_doms(auth,nodeId)
                    connected = True
                except Exception, e:
                    print "Error getting running vm info from "+\
                                    node.hostname+"\n"+ to_str(e)
                    LOGGER.error("Error getting running vm info from "+\
                                    node.hostname+"\n"+ to_str(e))
                if len(runningdoms)>0:
                    raise Exception("Can not delete the server.\
                        Running Virtual Machines exist under the Server. ")
                else:
                    node_up = node.is_up()
                    return dict(success=True,vms=len(domlist),node_up=node_up)

            node=DBSession.query(Entity).filter(Entity.entity_id==nodeId).first()
            grp=node.parents[0]
            from convirt.viewModel.TaskCreator import TaskCreator
            tid=TaskCreator().remove_node(auth,nodeId,node.name,grp.entity_id,grp.name,force)
            #self.manager.removeNode(auth,nodeId)
            return dict(success=True,msg='Remove Server Task Submitted.',taskid=str(tid))
        except Exception ,ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        #return dict(success=True,msg='Server Removed')

    def get_node_status(self, node_id=None, dom_id=None):

        if node_id is not None:
            pass
        elif dom_id is not None:
            dom_ent=DBSession.query(Entity).filter(Entity.entity_id==dom_id).first()
            node_id = dom_ent.parents[0].entity_id
        node=DBSession.query(ManagedNode).filter(ManagedNode.id==node_id).first()
        if node is None:
            raise Exception("Can not find the Server.")
        return node.is_up()

    def transfer_node(self, auth, node_id,source_group_id,dest_group_id, forcefully):
        """ transfer node  """
        try:
            self.manager.transferNode(auth, source_group_id, dest_group_id, node_id, forcefully)
        except Exception , ex:
            print_traceback()
            error_desc = to_str(ex).replace("'","")
            LOGGER.error(error_desc)
            return "{success: false, msg: '" + error_desc + "'}"
        return "{success: true, msg: 'Success'}"

    def import_vm_config(self, auth,nodeId, directory, filenames):
        try:
            file_list=[]
            file_list=filenames.split(",")
            self.manager.import_dom_config(auth,nodeId, directory, file_list)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_alloc_node(self,auth,groupId,imageId):
        try:

            group=self.manager.getGroup(auth,groupId)
            image=None
            if imageId is not None:
                image_store=Basic.getImageStore()
                image=image_store.get_image(auth,imageId)

            policy_ctx = dynamic_map()
            policy_ctx.image = image
            node = group.getAllocationCandidate(auth,policy_ctx)
            if node is None:
                raise Exception("Did not find any suitable server in "+group.name+\
                    ". Some of the reasons can be : 1.Not connected to server."+\
                    "2.Server is not capable of provisioning the image. " +\
                    "3.No server has enough free memory.")
            print dict(success='true',node=dict(name=node.hostname,nodeid=node.hostname,id=node.id))
            return dict(success='true',node=dict(name=node.hostname,nodeid=node.hostname,id=node.id))
        except Exception, ex:
            print_traceback()
            err=to_str(ex).replace("'", " ")
            LOGGER.error(err)
            return "{success: false,msg: 'Error:",err,"'}"


    def get_target_nodes(self, auth, node_id=None, image_id=None):
        platform=None
        image=None
        managed_node=None
        if node_id:
            managed_node = self.get_managed_node(auth,node_id)
            if managed_node is None:
                raise Exception("Can not find the specified Node.")
            platform=managed_node.get_platform()

        elif image_id:
            image_store=Basic.getImageStore()
            image=image_store.get_image(auth,image_id)
            
        grps=self.get_groups(auth)
        result=[]
        for grp in grps:
            list=[]
            nodes=self.get_nodes(auth,grp.id)
            for node in nodes:
                if node.id != node_id:
                    if populate_node_filter(node,platform,image):
                        list.append(dict(name=node.hostname,id=node.id,platform=node.platform,\
                                                type=constants.MANAGED_NODE,children=[]))
            if len(list) > 0:
                result.append(dict(name=grp.name,id=grp.id,type=constants.SERVER_POOL,children=list))

        return result

    def get_boot_device(self,auth,domId):
        try:
            dom = self.get_dom(auth,domId)
            vm_config = dom.get_config()

            if not vm_config:
                return "{success: false,msg: 'No configuration file associated with this VM.'}"
            boot_image = vm_config['boot']
            if boot_image is None:
                boot_image=""

            return "{success: true,msg: 'Success',boot:'"+boot_image+"'}"
        except Exception, ex:
            err=to_str(ex).replace("'", " ")
            LOGGER.error(err)
            return "{success: false,msg: 'Error:",err,"'}"

    def set_boot_device(self,auth, domId,boot):
        try:
            dom = self.get_dom(auth,domId)
            self.manager.set_dom_device(auth,dom,boot)
            msg="Success"
            running="false"
            if dom.is_resident():
                msg="The VM is running. <br/>The new Boot Location will take effect when VM is restarted."
                running="true"
            return "{success: true,msg: '"+msg+"',running:'"+running+"'}"

        except Exception, ex:
            print_traceback()
            err=to_str(ex).replace("'", " ")
            LOGGER.error(err)
            return "{success: false,msg: 'Error:",err,"'}"

    def add_group(self, auth, name,site_id):
        group = ServerGroup(name)
        self.manager.addGroup(auth,group,site_id)
        return group

    def get_group_vars(self, auth,group_id):
        result=[]
        try:
            group_vars=self.manager.getGroupVars(auth,group_id)
            id=0
            for key in group_vars:
                result.append(dict(id=id,variable=key,value=group_vars[key]))
                id=id+1
        except Exception , ex:
            print_traceback()
            return dict(success='false',msg=to_str(ex).replace("'",""))
        return dict(success='true',rows=result)

    def save_group_vars(self, auth,group_id ,group_vars):
        try:
            groupvars={}
            for (k,v) in group_vars.iteritems():
                v=group_vars[k]
                if v and v[0]=="*":
                    continue
                else:
                    groupvars[k]=v

            self.manager.setGroupVars(auth,group_id,groupvars)
        except Exception , ex:
            print_traceback()
            return dict(success='false',msg=to_str(ex).replace("'",""))
        return dict(success='true',msg='Success')

    def remove_group(self, auth, group_id):
        for node in self.manager.getNodeList(auth,group_id):
            runningdoms=self.manager.get_running_doms(auth,node.id)
            if len(runningdoms)>0:
                raise Exception("Can not delete the Server Pool.\
                    Running Virtual Machines exist under the Server Pool.")
        self.manager.removeGroup(auth, group_id,True)
        return

    def get_dir_contents(self, auth,nodeId=None, directory=None):
        managed_node =None
        if nodeId is None:
            managed_node=Basic.local_node
        else:
            managed_node = self.get_managed_node(auth,nodeId)

        if managed_node is None:
            raise Exception('Cannot find the Managed Node.')
        elif not managed_node.is_authenticated():
            managed_node.connect()

        return self.list_dir_contents(managed_node, directory)
    #should move to utils
    def list_dir_contents(self, managed_node, directory=None):

        if not directory:
            dir=managed_node.get_config_dir()
        else:
            dir=directory

        dir_entries=managed_node.node_proxy.get_dir_entries(dir)

        result=[]
        counter=1
        for entry in dir_entries:
            mod_date = time.strftime("%a %b %d %Y %H:%M:%S",time.localtime(entry['mtime']))           
            counter=counter+1
            result.append(dict(id=counter,name=entry['filename'],path=entry['path'],size=entry['size'],date=mod_date,isdir=entry['isdir']))

        return result

    #should move to utils
    def make_dir(self,auth,nodeId, directory ,dir):
        try:
            managed_node = self.get_managed_node(auth,nodeId)
            if managed_node is None:
                raise Exception('Cannot find the Managed Node.')
            elif not managed_node.is_authenticated():
                managed_node.connect()

            utils.mkdir2(managed_node,os.path.join(directory,dir))
        except Exception, ex:
            print_traceback()
            strerror=to_str(ex).replace("'", " ")
            return "{success: false,msg: '",strerror,"'}"

        return "{success: true,msg: 'Successfully created.',newdir:'",os.path.join(directory,dir),"'}"

    def getListInfo(self, value_list, display_dict, type1):
        ret_list=[]
        if value_list is None:
            return []
        display_list = ['','','']
        i = 0
        for name in display_dict:
            display_list[i] = display_dict[name]
            i = i + 1
        ret_list.append(dict(label=display_list[0],value=display_list[1],extra=display_list[2],type=type1))

        for i in range(len(value_list)):
            value_dict = value_list[i]
            column_value = ['','','']
            j=0
            for name in value_dict:
                value = value_dict[name]
                if type(value) == int:
                    value = to_str(value)
                column_value[j]=value.rstrip().lstrip()
                j = j+1
            ret_list.append(dict(id=type1+to_str(i),label=column_value[0],value=column_value[1],extra=column_value[2],type=type1))

        #print "---",ret_list
        return ret_list

    def getDictInfo(self, value_dict, display_dict,type):
        ret_list=[]
        mod_dict=self.decorateDictInfo(value_dict, display_dict)
        i=0
        for key in mod_dict:
            ret_list.append(dict(id=type+to_str(i),label=key,value=mod_dict[key],type=type,extra=''))
            i=i+1
        return ret_list

    def decorateDictInfo(self, value_dict, display_dict):
        mod_dict={}
        if value_dict is not None:
            for name in display_dict :
                value = value_dict.get(name)
                if not value:
                    continue
                if type(value) == int:
                    value = to_str(value)
                value = value.rstrip().lstrip()
                mod_dict[display_dict[name]]=value
        return mod_dict

    def vm_config_settings(self,auth,image_id,config,mode,node_id,group_id,dom_id,vm_name):
        start = p_timing_start(LOGGER, "vm_config_settings ")
        vm_config=None
        hex_id = getHexID()
        try:
              print "dom id===",dom_id
              config=json.loads(config)

              vm_name=vm_name
              image_id=image_id
              vm_config=image_config =None
              ctx = dynamic_map()
              image_store=Basic.getImageStore()
              image=image_store.get_image(auth,image_id)

              if image is not None:
                  ctx.image_name=image.name
                  ctx.image_id=image.id
                  ctx.image=image
                  vm_config,image_config = image.get_configs()
              vm_info=None
              dom=None
              
              managed_node=None
              if node_id is not None:
                    node_id=(node_id)
                    managed_node = self.get_managed_node(auth,node_id)
                    ctx.managed_node= managed_node
                    if managed_node is None:
                        raise Exception('Cannot find the Managed Node.')

              #getting storage list from existing vm config. So this list would not have newly added storage to VM.
              filename_list=[]
              if dom_id is not None:
                    dom_id=(dom_id)
                    ctx.dom_id=dom_id
                    vm = self.manager.get_dom(auth, dom_id)
                    dom = managed_node.get_dom(vm.name)
                    vm_config=dom.get_config()
                    vm_info=dom.get_info()
                    for disk in vm_config.getDisks():
                        filename_list.append(disk.filename)
                    
              else:
                  if mode=="PROVISION_VM":
                        dom_id=vm_name

              general=config.get('general_object')
              boot_params=config.get('boot_params_object')
              misc_dic=config.get('misc_object')
              provision_dic=config.get('provision_object')
              network_dic=config.get('network_object')

              storage_status=config.get('storage_status_object')

              print "STORAGE_STATUS=====",storage_status.get("disk_stat")
              disk_status=storage_status.get("disk_stat")

    # disks panel
              initial_disks=vm_config["disk"]
              if image_config is not None and initial_disks is not None:
                  for disk in initial_disks:
                      image_config=self.remove_device_entries(image_config, disk)

              disks = []
              disk_entries=[]
              template_cfg=[]
              
              for disk in disk_status:
                 disk_entry=ImageDiskEntry((disk.get("type"),disk.get("filename"),disk.get("device"),disk.get("mode")),image_config)
                 disk_entry.option = disk.get("option")
                 disk_entry.image_src = disk.get("image_src")
                 disk_entry.image_src_type = disk.get("image_src_type")
                 disk_entry.image_src_format = disk.get("image_src_format")
                 disk_entry.disk_create = disk.get("disk_create")
                 disk_entry.disk_type = disk.get("disk_type")
                 d_size=disk.get("size")
                 if d_size :
                    disk_entry.size = int(d_size)
                 else:
                     disk_entry.size = d_size               
                 disk_entries.append(disk_entry)

              for disk_entry in disk_entries:
                  if image_config is not None:
                      image_config=self.update_device_entries(image_config,disk_entry)
                  disks.append(repr(disk_entry))
              vm_config["disk"] = disks

              final_disks=disks
              s_stat = vm_config.get_storage_stats()
              for disk in disk_status:
                  is_remote = disk.get("shared")
                  s_stat.set_remote(disk.get("filename") , is_remote)
                  storage_disk_id = unicode(disk.get("storage_disk_id"))
                  s_stat.set_storage_disk_id(str(disk.get("filename")), storage_disk_id)

#   network panel
              net_list=network_dic.get("network")
              vifs = []
              for net_data in net_list:

                  mac=net_data.get("mac")
                  if  mac=="Autogenerated":
                      mac="$AUTOGEN_MAC"

                  bridge=net_data.get("bridge");
                  if bridge=="Default":
                      bridge="$DEFAULT_BRIDGE"

                  vif_entry=vifEntry('mac=%s,bridge=%s' % (mac,bridge))
                  vifs.append(repr(vif_entry))


              vm_config["vif"] = vifs

              for key in misc_dic:
                   misc_dic[key]=process_value(misc_dic.get(key))

              for key in provision_dic:
                    provision_dic[key]=process_value(provision_dic.get(key))

              err_msgs=validateVMSettings(mode,managed_node,image_store,dom_id,general.get("memory"),general.get("vcpus"))
              if len(err_msgs)>0:
                    raise Exception(err_msgs)
              
    #    boot_params panel
              if mode in ["EDIT_VM_CONFIG", "PROVISION_VM", "EDIT_IMAGE"] and  vm_config:
                  for key in boot_params.keys():
                      vm_config[key]=to_str(boot_params.get(key))
                      if boot_params.get("boot_check")==True:
                          vm_config["bootloader"]=boot_params.get("boot_loader")
                          vm_config["kernel"]=""
                          vm_config["ramdisk"]=""
                      else:
                         vm_config["bootloader"] = ""
              
        # general panel
              if mode in ["EDIT_VM_CONFIG", "PROVISION_VM","EDIT_IMAGE"] and vm_config:
                  for key in general.keys():
                        value=general.get(key)
                        if key in ["memory", "vcpus"]:
                            value = int(general.get(key))
#
                        if key == 'filename':
                            if mode not in ["EDIT_IMAGE"]:
                                vm_config.set_filename(value)
                                vm_config["config_filename"]=value
                        else:
                            vm_config[key] = value

              elif mode in ["EDIT_VM_INFO"] and vm_info is not None:
                    for key in general.keys():
                        value = general.get(key)
#
                        if key in ("memory", "vcpus"):
                            value = int(general.get(key))
                        if key == 'filename' :
                            vm_config.set_filename(value)
                            vm_config["config_filename"]=value
                        else:
                            vm_info[key] = value

                    vm_config["os_flavor"] = general.get("os_flavor")
                    vm_config["os_name"] = general.get("os_name")
                    vm_config["os_version"] = general.get("os_version")
                    vm_config["template_cfg"] = template_cfg
         # misc panel
              if mode in ["EDIT_VM_CONFIG", "PROVISION_VM", "EDIT_IMAGE"] and vm_config:
                   vm_config=self.update_config_props(vm_config,misc_dic,self.get_exclude_list())

        # provison panel
              if mode in ["EDIT_IMAGE","PROVISION_VM"] and image_config:
                   image_config=self.update_config_props(image_config,provision_dic)

              print "after instantiate"
              if mode in ["PROVISION_VM"]:
                  group=self.manager.getGroup(auth,group_id)
                  storage_manager=Basic.getStorageManager()

                  ctx.image_store = image_store
                  ctx.image_id=image_id
                  ctx.managed_node= managed_node
                  ctx.vm = None
                  ctx.server_pool= group
                  ctx.platform = managed_node.get_platform()
                  ctx.storage_manager = storage_manager

                  if ctx.server_pool is not None:
                        grp_settings = ctx.server_pool.getGroupVars()
                        merge_pool_settings(vm_config,image_config,grp_settings, True)

                  vm_config['name']=vm_name
                  vm_config['image_name']=ctx.image_name
                  ctx.vm_config = vm_config
                  ctx.image_config = image_config
                  ctx.start=general.get("start_checked")
              #decide what to do
              if mode in ["PROVISION_VM","EDIT_VM_INFO","EDIT_VM_CONFIG"]:
                  vm_config["auto_start_vm"] = general.get('auto_start_vm')
              if mode == "PROVISION_VM":
                  vm_disks = self.manager.get_vm_disks_from_UI(dom_id, config)
                  vm_id = self.manager.provision(auth, ctx, ctx.image_name, group_id, vm_disks, hex_id)
              elif mode == "EDIT_VM_INFO":
                  vm_id = dom_id
                  vm_config.set_id(vm_id)
                  ctx.template_version=general.get('template_version')
                  vm_disks = self.manager.get_vm_disks_from_UI(dom_id, config)
                  self.manager.edit_vm_info(auth, vm_config, vm_info, dom, ctx,\
                                            initial_disks, final_disks, group_id, vm_disks, hex_id)
              elif mode == "EDIT_VM_CONFIG":
                  vm_id = dom_id
                  vm_config.set_id(vm_id)
                  vm_config['vmname'] = vm_name
                  ctx.image_id=image_id
                  ctx.template_version=general.get('template_version')
                  vm_disks = self.manager.get_vm_disks_from_UI(dom_id, config)
                  self.manager.edit_vm_config(auth, vm_config, dom, ctx, group_id, vm_disks, hex_id)
              elif mode == "EDIT_IMAGE":
                  ctx.update_template=general.get('update_version')
                  ctx.new_version=general.get('new_version')
                  ctx.os_flavor=general.get('os_flavor')
                  ctx.os_name=general.get('os_name')
                  ctx.os_version=general.get('os_version')
                  self.manager.edit_image(auth, vm_config, image_config, ctx)

              if mode not in ["EDIT_IMAGE"]:
                  #get removed storage disk list
                  removed_disk_list = self.removed_disk_list(filename_list, disk_status)
                  #manage vm disks and vm storage links here
                  self.manager.manage_vm_disks(auth, vm_id, node_id, config, mode, removed_disk_list)
                  #compute storage stats
                  storage_list_for_recompute = []
                  #disk_status will have storage list from UI grid. So this list would not have remove storages from VM.
                  for disk in disk_status:
                      storage_id = disk.get("storage_id")
                      if storage_id and storage_id != "null":
                        defn = StorageManager().get_defn(storage_id)
                        if defn:
                            if not self.check_duplicate_in_list(storage_list_for_recompute, "STORAGE_DEF", defn.name):
                                storage_list_for_recompute.append(defn)
                            else:
                                LOGGER.info(to_str(defn.name) + " storage is already marked for Recompute.")
                        
                  #filename_list will have storage list from existing vm config. So this list would not have newly added storages to VM.
                  for filename in filename_list:
                      storage_id=None
                      s_disk=DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
                      if s_disk:
                        storage_id = s_disk.storage_id
                      if storage_id and storage_id != "null":
                        defn = StorageManager().get_defn(storage_id)
                        if defn:
                            if not self.check_duplicate_in_list(storage_list_for_recompute, "STORAGE_DEF", defn.name):
                                storage_list_for_recompute.append(defn)
                            else:
                                LOGGER.info(to_str(defn.name) + " storage is already marked for Recompute.")

                  if storage_list_for_recompute:
                    for each_storage_defn in storage_list_for_recompute:
                        StorageManager().Recompute(each_storage_defn)

                  #unreserve disks
                  self.manager.unreserve_disks(vm_config, hex_id)
        except Exception, ex:
            #unreserve disks
            self.manager.unreserve_disks(vm_config, hex_id)
            print_traceback()
            err=to_str(ex).replace("'", " ")
            LOGGER.error(err)
            raise ex
        p_timing_end(LOGGER, start)

    def removed_disk_list(self, old_disk_list, new_disk_list):
        LOGGER.info("Getting removed disk list...")
        #following list is from old vm_config
        removed_file_list=[]
        for filename in old_disk_list:
            #following list is from UI grid.
            disk_removed = True
            for disk in new_disk_list:
                if filename == disk.get("filename"):
                    disk_removed = False
                    break
            
            if disk_removed:
                removed_file_list.append(filename)
        LOGGER.info("Removed disk list is " + to_str(removed_file_list))
        return removed_file_list
            
    def check_duplicate_in_list(self, item_list, list_type, item):
        return_val = False
        for each_item in item_list:
            if list_type == "STORAGE_DEF":
                each_item = each_item.name
            if each_item == item:
                #duplicate item found
                return_val = True
                return return_val
        return return_val
    
    def update_config_props(self,config,model,excluded = []):
        print "Model====  ",model
        # take misc model remove deleted props
        delete_props = []
        if config is None:
            return
        for prop in config:
            if prop not in excluded:
                # check if it exists in the misc model
                found = False
                for key in model.keys():
                    if key == prop:
                        found = True
                        break
                if not found:
                    delete_props.append(prop)

        for prop in delete_props:
            del config.options[prop]

        # now copy update values from model to the config.
        for key in model.keys():
            #key=str(key)
            value = model.get(key)
            value=to_str(value)
            # We got the string representation, guess and make it proper value
            key = key.strip()
            value = value.strip()
            value = guess_value(value)
            if key is not None and key is not '':
                config[key] = value
        return config

    def get_exclude_list(self):
        return [ "name", "memory", "kernel", "ramdisk", "root",
                 "cpus", "extra", "vcpus", "on_shutdown",
                 "os_flavor","os_name","os_version","auto_start_vm","config_filename",
                 "on_reboot", "on_crash", "bootloader", "disk", "STORAGE_STATS" ]

    def get_vm_config(self,auth,domId,nodeId):
        result={}
        try:
            if domId is not None and nodeId is not None:
                node=self.get_managed_node(auth, nodeId)
                dom = DBSession.query(VM).filter(VM.name==domId).first()
                if dom :
                    if dom.is_running() and node.is_up():
                        dom = node.get_dom(domId)
                else:
                    return
            else:
                return
            vm_config=dom.get_config()
            if vm_config is not None:
                for key in vm_config.keys():
                     result[key]=vm_config.get(key)

                result['os_flavor']=dom.os_flavor
                result['os_version']=dom.os_version
                result['os_name']=dom.os_name
                result["filename"]=""#vm_config.get("filename")

                result["template_version"]=to_str(dom.template_version)
                result["inmem_memory"]=vm_config.get("memory")
                result["inmem_vcpus"]=vm_config.get("vcpus")
                result["inmem_bootloader"]=vm_config.get("bootloader")

                try:
                    if dom["memory"] is not None:
                        result["inmem_memory"]=dom["memory"]
                    if dom["vcpus"] is not None:
                        result["inmem_vcpus"]=dom["vcpus"]
                    if dom["bootloader"] is not None:
                        result["inmem_bootloader"]=dom["bootloader"]
                except Exception, e:
                    print "Exception: ", e

                t_vers=get_template_versions(dom.image_id)
                version_list=[]
                for ver in t_vers:
                    version_list.append(ver[0])
#                print "\n\n\n\n===",version_list
                result["template_versions"]=version_list
                result["filename"]=vm_config["config_filename"]

        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        return result

    def get_shutdown_event_map(self):
        try:
            result=[]
            result.append(dict(id="destroy",value="Destroy"))
            result.append(dict(id="preserve",value="Preserve"))
            result.append(dict(id="rename-restart",value="Rename-Restart"))
            result.append(dict(id="restart",value="Restart"))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',shutdown_event_map=result)

    def remove_device_entries(self, image_config, device):
        if not device:
            return
        if device:
            print "## Device change detected from ", device, device

            old_create_var = device + "_disk_create"
            old_image_src_var = device + "_image_src"
            old_image_src_type_var = device + "_image_src_type"
            old_image_src_format_var = device + "_image_src_format"
            old_size_var = device + "_disk_size"
            old_disk_fs_type_var = device + "_disk_fs_type"
            old_disk_type_var = device + "_disk_type"

            # device changed. lets clear values for old device
            # ASSUME : Uniq devices
            for var, value in ((old_create_var, ""),
                               (old_size_var, 0),
                               (old_disk_fs_type_var, ""),
                               (old_disk_type_var, ""),
                               (old_image_src_var, ""),
                               (old_image_src_type_var, ""),
                               (old_image_src_format_var, "")
                           ):
                print "delting ", var
                del image_config[var]
        return image_config

    def update_device_entries(self, image_config, disk_entry, old_device = None):
        if not disk_entry:
            return

        device = disk_entry.device
        # Vars
        # Strip :cdrom from the device.
        pos = device.find(":cdrom")
        if pos > -1:
            device=device[0:pos]

        create_var = device + "_disk_create"
        image_src_var = device + "_image_src"
        image_src_type_var = device + "_image_src_type"
        image_src_format_var = device + "_image_src_format"
        size_var = device + "_disk_size"
        disk_fs_type_var = device + "_disk_fs_type"
        disk_type_var = device + "_disk_type"

        create_value = None
        if disk_entry.option == disk_entry.CREATE_DISK:
            create_value = "yes"
        if disk_entry.option == disk_entry.USE_REF_DISK:
            if disk_entry.type == "phy" and disk_entry.disk_type == "":
                create_value = ""
            else:
                create_value = "yes"

#        if disk_entry.option == disk_entry.USE_DEVICE and disk_entry.disk_type=="LVM":
#                create_value = "yes" 
        if not create_value or create_value != "yes":
            disk_entry.size = 0
            if disk_entry.option != disk_entry.USE_REF_DISK:
                disk_entry.image_src = ""
                disk_entry.image_src_type = ""
                disk_entry.image_src_format = ""

        for var, value in ((create_var, create_value),
                           (size_var, disk_entry.size),
                           (disk_fs_type_var, disk_entry.fs_type),
                           (disk_type_var, disk_entry.disk_type),
                           (image_src_var, disk_entry.image_src),
                           (image_src_type_var, disk_entry.image_src_type),
                           (image_src_format_var, disk_entry.image_src_format),
                           ):
            if value and value!='None':
                print "*** updating ", var, value
                image_config[var] = value
            else:
                del image_config[var]
        return image_config

    def process_annotation(self,auth,node_id,text,user=None):
        ent=auth.get_entity(node_id)

        msg="Annotated by :  '"+auth.user.user_name+"'\nAnnotation :\n\n"+text+"\n"
        if user is not None:
            result=self.get_annotation(auth,node_id)
            annotate=result.get("annotate")
            msg+="\nPreviously Annotated by : '"+annotate.get("user")+"'\nPrevious Annotation :\n\n"+annotate.get("text")

        attribs=filter(lambda atr:atr.name in ["user","text"],ent.attributes)
        for attr in attribs:
            DBSession.delete(attr)

        ent.attributes.append(EntityAttribute(u"user",auth.user.user_name))
        ent.attributes.append(EntityAttribute(u"text",text))
        DBSession.add(ent)
        self.notify_users(ent,msg)
        transaction.commit()
        return msg

    def get_annotation(self,auth,node_id):
        ent=auth.get_entity(node_id)

        attribs=filter(lambda atr:atr.name in ["user","text"],ent.attributes)
        dic={}
        for attr in attribs:
            dic.update({attr.name:attr.value})

        return dict(success=True,annotate=dic)

    def clear_annotation(self,auth,node_id):
        ent=auth.get_entity(node_id)
        result=self.get_annotation(auth,node_id)
        annotate=result.get("annotate")

        attribs=filter(lambda atr:atr.name in ["user","text"],ent.attributes)
        for attr in attribs:
            DBSession.delete(attr)
        msg="Annotation cleared. \n\nPreviously Annotated by : '"+annotate.get("user")+"'\nPrevious Annotation :\n\n"+annotate.get("text")
        self.notify_users(ent,msg)
        transaction.commit()
        return msg


    def notify_users(self,node_ent,message):
        from convirt.model.notification import Notification
        from convirt.model.auth import User
        users = DBSession.query(User).all()

        subject=u"ConVirt :Annotation Status- "+node_ent.type.display_name+" : "+node_ent.name
        now=datetime.utcnow()
        entity_details=node_ent.type.display_name+" : "+node_ent.name+"\n\n"
        message=entity_details+message
        message=message.replace("\n","<br/>").replace(" ","&nbsp;")
        for user in users:
            notifcn = Notification(None, \
                      None, \
                      now, \
                      to_unicode(message), \
                      user.user_name, \
                      user.email_address,\
                      subject)
            DBSession.add(notifcn)

    def fix_vm_disk_entries(self, auth, **kwargs):
        """
        """
        msg = ""
        try:
            msg = self.manager.fix_vm_disk_entries(auth, **kwargs)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            raise ex
        return msg


