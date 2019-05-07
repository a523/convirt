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
# DashboardService.py
#
#   This module contains code to return Dashboard information to the Web UI
#
import Basic
from convirt.core.utils.utils import constants,getHexID,get_platform_count,get_host_os_info,get_guest_os_info,get_string_status,set_registered
from convirt.core.utils.utils import to_unicode,to_str,print_traceback, convert_to_CMS_TZ, connect_url
from convirt.viewModel.NodeService import NodeService
from convirt.viewModel.StorageService import StorageService
from convirt.viewModel.NetworkService import NetworkService
from convirt.viewModel.Userinfo import Userinfo
from convirt.model.UpdateManager import UIUpdateManager
import re,urllib
from convirt.model.DBHelper import DBHelper
from datetime import datetime,timedelta
from convirt.core.utils.phelper import AuthenticationException
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import traceback
from convirt.model.Metrics import MetricsService, MetricVMRaw, MetricVMCurr, MetricServerRaw, MetricServerCurr, DataCenterRaw, DataCenterCurr
from convirt.model import DBSession, Entity,EntityRelation
from convirt.model.ManagedNode import ManagedNode
from convirt.model.VM import VM, VMDiskManager, VMStorageLinks, VMDisks, OutsideVM
from convirt.model.SPRelations import StorageDisks, SPDefLink, DCDefLink, Storage_Stats
from convirt.model.storage import StorageManager, StorageDef
from convirt.model.ImageStore import Image
from convirt.model.NodeInformation import Component, Instance
from convirt.model.availability import AvailState
from convirt.model.CustomSearch import CustomSearch
from convirt.model.TopCache import TopCache
import logging, tg
from sqlalchemy.orm import eagerload
from sqlalchemy import func, outerjoin
LOGGER = logging.getLogger("convirt.viewModel")

class DashboardService:
    def __init__(self):
        self.manager = Basic.getGridManager()
        self.custom_search=CustomSearch()

    def execute(self, auth, type, node_id, username=None,password=None):
        managed_node = None
        infoObject = None
        result = None
        if type is not None:
            if constants.MANAGED_NODE == type:
                managed_node = self.manager.getNode(auth,node_id)
                if managed_node is not None:
#                    if not managed_node.is_authenticated():
#                        try:
#                            managed_node.connect()
#                        except AuthenticationException ,ex:
#                            raise Exception("Server not authenticated.")
#                        except Exception ,ex:
#                            traceback.print_exc()
#                            LOGGER.error(ex)
#                            raise ex

                    # added for inserting the data into the tables and displaying the data from the database
                    infoObject = self.getCurrentMetrics(auth, managed_node)
                    ovm_list=[]
                    o_vms=DBSession.query(OutsideVM).filter(OutsideVM.node_id==node_id).all()
                    for o_vm in o_vms:
                        ovm_list.append(dict(NAME=o_vm.name,NODE_NAME=o_vm.name,NODE_ID=o_vm.id,\
                            NODE_TYPE= constants.DOMAIN,DOMAIN_TYPE=constants.OUTSIDE_DOMAIN,\
                            ICONSTATE=o_vm.status,STATE=o_vm.status))
                    infoObject.extend(ovm_list)
            else:
                infoObject = self.gather_info_for_pool(auth, pool_type = type, pool_id = node_id)

        dashboardInfo = DashboardInfo(infoObject)
        return dashboardInfo

    """
    Function to get the node metrics from the managed_node and insert the metrics data in
    VM RAW/CURR tables
    """
    def collectMetrics(self, auth, managed_node):
        metrics=self.manager.getNodeMetrics(auth,managed_node)
        ms = MetricsService()
        vm_ents =[]
        ent=auth.get_entity(managed_node.id)
        child_ents=auth.get_entities(to_unicode(constants.DOMAIN),parent=ent)
        """
        loop to get the vm id to be inserted in the VM metrics table since the dictionary does not
        have VM id but VM name.
        """
        for child_ent in child_ents:
            for keys in metrics:
                if keys==child_ent.name: # if the correct vm found
                    dict_data = metrics[keys]
                    vm_metrics_obj = MetricVMRaw()
                    ms.insertMetricsData(dict_data, child_ent.entity_id, vm_metrics_obj)

    """
    Function which gets the metrics data from the VM current metrics table and returns a list of
    dictionaries to be displayed on the dashboard.
    """
    def getCurrentMetrics(self, auth, managed_node):
        ms = MetricsService()
        vmmetrics_list = []
        ent=auth.get_entity(managed_node.id)
        child_ents=auth.get_entities(to_unicode(constants.DOMAIN),parent=ent)
        for vmids in child_ents:
            dict = {}
            dict['CPU(%)'] = 0
            dict['MEM(%)'] = 0
            dict['VBDS'] = 0
            dict['VBD_OO'] = 0
            dict['VBD_RD'] = 0
            dict['VBD_WR'] = 0
            dict['NETS'] = 0
            dict['NETTX(k)'] = 0
            dict['NETRX(k)'] = 0
            dict['STATE'] = VM.SHUTDOWN
            dict['NODE_ID'] = vmids.entity_id
            dict['VM_LOCAL_STORAGE'] = 0
            dict['VM_SHARED_STORAGE'] = 0
            dict['VM_TOTAL_STORAGE'] = 0
            dict['NAME'] = vmids.name
            dict['NODE_NAME'] = vmids.name
            dict['SSID'] = 0
            dict['CPU(sec)'] = 0
            dict['MAXMEM(%)'] = 0
            dict['MEM(k)'] = 0
            dict['NODE_TYPE'] = constants.DOMAIN
            dict['MAXMEM(k)'] = 0
            dict['VCPUS'] = 0
            dict['DISPLAY'] = 0
            VMCurrInstance = ms.getVMCurrMetricsData(constants.VM_CURR, vmids, auth)
            # if data is returned from the current metrics table.
            if VMCurrInstance:
                dict.update({'CPU(%)':VMCurrInstance.cpu_util})
                dict.update({'MEM(%)':VMCurrInstance.mem_util})
                dict.update({'VBDS':VMCurrInstance.vbds})
                dict.update({'VBD_OO':VMCurrInstance.vbd_oo})
                dict.update({'VBD_RD':VMCurrInstance.vbd_rd})
                dict.update({'VBD_WR':VMCurrInstance.vbd_wr})
                dict.update({'NETS':VMCurrInstance.nets})
                dict.update({'NETTX(k)':VMCurrInstance.nets_tx})
                dict.update({'NETRX(k)':VMCurrInstance.nets_rx})
                ###commented on 25/11/09
                vm = DBSession.query(VM).filter(VM.id==vmids.entity_id).options(eagerload("current_state")).first()
                dict.update({'STATE':to_str(vm.get_state())})
                dict.update({'ICONSTATE':to_str(vm.get_state())})
                if not managed_node.is_up():
                    dict.update({'ICONSTATE':"D_"+to_str(vm.get_state())})
                ###end
                dict.update({'NODE_ID':vmids.entity_id})
                dict.update({'VM_LOCAL_STORAGE':VMCurrInstance.gb_local})
                dict.update({'VM_SHARED_STORAGE':VMCurrInstance.gb_poolused})
                dict.update({'VM_TOTAL_STORAGE':VMCurrInstance.gb_pooltotal})
                dict.update({'NAME':vmids.name})
                # added newly to test
                dict.update({'NODE_NAME': vmids.name})
                dict.update({'SSID': '0'})
                dict.update({'CPU(sec)': '1'})
                dict.update({'MAXMEM(%)': '6.3'})
                dict.update({'MEM(k)': '262068'})
                dict.update({'NODE_TYPE': constants.DOMAIN})
                dict.update({'MAXMEM(k)': '262144'})
                dict.update({'VCPUS': '1'})
                dict.update({'DISPLAY': '1'})
            vmmetrics_list.append(dict)
        return vmmetrics_list
    """
    Function retrieves the metrics data from the SERVER_POOL current metrics and returns
    a list of dictionaries to be displayed on the dashboard.
    """
    def getServerPoolCurrentMetrics(self, pool_info, metrics_type):
        serverpool_dict = {}
        #Initialize server_pool dict
        serverpool_dict['VM_TOTAL_CPU(%)'] = 0
        serverpool_dict['VM_TOTAL_MEM(%)'] = 0
        serverpool_dict['VM_TOTAL_VBD_OO'] = 0
        serverpool_dict['VM_TOTAL_VBD_WR'] = 0
        serverpool_dict['VM_TOTAL_VBD_RD'] = 0
        serverpool_dict['VM_TOTAL_VBDS'] = 0
        serverpool_dict['VM_TOTAL_NETTX(k)'] = 0
        serverpool_dict['VM_TOTAL_NETS'] = 0
        serverpool_dict['VM_TOTAL_NETRX(K)'] = 0
        serverpool_dict['VM_LOCAL_STORAGE'] = 0
        serverpool_dict['VM_SHARED_STORAGE'] = 0
        serverpool_dict['VM_TOTAL_STORAGE'] = 0
        serverpool_dict['NODE_STATUS'] = 0
        serverpool_dict['PAUSED_VMs'] = 0
        serverpool_dict['RUNNING_VMs'] = 0
        serverpool_dict['CRASHED_VMs'] = 0
        serverpool_dict['TOTAL_VMs'] = 0
        serverpool_dict['SERVER_CPUs'] = 0
        serverpool_dict['SERVER_MEM'] = 0
        serverpool_dict['NODE_ID'] = pool_info.id
        serverpool_dict['NODE_NAME'] = pool_info.name
        serverpool_dict['NODE_TYPE'] = 'SERVER_POOL'
        serverpool_dict['VM_TOTAL_MEM'] = 0
        serverpool_dict['VM_TOTAL_CPU'] = 0
        serverpool_dict['NODES_CONNECTED'] = 0
        serverpool_dict['NODE_COUNT'] = 0

        ms = MetricsService()
        serverPoolCurrInstance = ms.getServerPoolCurrMetricsData(pool_info.id,metrics_type)
        if serverPoolCurrInstance:
            serverpool_dict['VM_TOTAL_CPU(%)'] = serverPoolCurrInstance.cpu_util
            serverpool_dict['VM_TOTAL_MEM(%)'] = serverPoolCurrInstance.mem_util
            serverpool_dict['VM_TOTAL_VBDS'] = serverPoolCurrInstance.vbds
            serverpool_dict['VM_TOTAL_VBD_OO'] = serverPoolCurrInstance.vbd_oo
            serverpool_dict['VM_TOTAL_VBD_RD'] = serverPoolCurrInstance.vbd_rd
            serverpool_dict['VM_TOTAL_VBD_WR'] = serverPoolCurrInstance.vbd_wr
            serverpool_dict['VM_TOTAL_NETS'] = serverPoolCurrInstance.nets
            serverpool_dict['VM_TOTAL_NETTX(k)'] = serverPoolCurrInstance.net_tx
            serverpool_dict['VM_TOTAL_NETRX(k)'] = serverPoolCurrInstance.net_rx
            serverpool_dict['VM_LOCAL_STORAGE'] = serverPoolCurrInstance.gb_local
            serverpool_dict['VM_SHARED_STORAGE'] = serverPoolCurrInstance.gb_poolused
            serverpool_dict['VM_TOTAL_STORAGE'] = serverPoolCurrInstance.gb_pooltotal
            serverpool_dict['NODE_STATUS'] = 1
            serverpool_dict['PAUSED_VMs'] = serverPoolCurrInstance.paused_vms
            serverpool_dict['RUNNING_VMs'] = serverPoolCurrInstance.running_vms
            serverpool_dict['CRASHED_VMs'] = serverPoolCurrInstance.crashed_vms
            serverpool_dict['VM_TOTAL_MEM'] = serverPoolCurrInstance.total_mem
            serverpool_dict['VM_TOTAL_CPU'] = serverPoolCurrInstance.total_cpu
            serverpool_dict['TOTAL_VMs'] = serverPoolCurrInstance.total_vms
            serverpool_dict['SERVER_CPUs'] = serverPoolCurrInstance.server_cpus
            serverpool_dict['SERVER_MEM'] = serverPoolCurrInstance.server_mem
            serverpool_dict['NODES_CONNECTED'] = serverPoolCurrInstance.nodes_connected
            serverpool_dict['NODE_COUNT'] = serverPoolCurrInstance.server_count
            serverpool_dict['NODE_ID'] = pool_info.id
            serverpool_dict['NODE_NAME'] = pool_info.name
            serverpool_dict['NODE_TYPE'] = 'SERVER_POOL'
        return serverpool_dict

    """
    Function gets the metrics data from the SERVER current metrics table and returns a
    list of dictionaries to be displayed on the dashboard.
    """
    def getServerCurrentMetrics(self,auth,m_node):
        #Initialize server dict
        dict_data = {}
        dict_data["NODE_NAME"] = m_node.hostname
        dict_data["NODE_PLATFORM"] = m_node.platform
        if not m_node.is_up():
            dict_data["NODE_PLATFORM"] = m_node.platform+"_down"
        dict_data["NODE_TYPE"] = 'MANAGED_NODE'
        dict_data["NODE_ID"] = m_node.id

        node_componentid = DBSession.query(Component.id).filter(Component.type == to_unicode('platform_info')).first()
        idList = list(node_componentid)

        node_ver = 'NA'
        node_version = DBSession.query(Instance).filter(Instance.node_id == m_node.id).filter( Instance.component_id == (idList[0])).filter(Instance.name == to_unicode('xen_version')).first()
        if node_version:
            node_ver = node_version.value

        ms = MetricsService()
        serverCurrInstance = ms.getServerCurrMetricsData(constants.SERVER_CURR, m_node.id)
        status="Unknown"
        if m_node.current_state.avail_state==m_node.UP:
            status="Connected"
        elif m_node.current_state.avail_state==m_node.DOWN:
            status="Not Connected"
        dict_data['NODE_STATUS'] = status

        if serverCurrInstance:
            dict_data['VM_TOTAL_CPU(%)'] = serverCurrInstance.cpu_util
            dict_data['VM_TOTAL_MEM(%)'] = serverCurrInstance.mem_util
            dict_data['VM_TOTAL_VBDS'] = serverCurrInstance.vbds
            dict_data['VM_TOTAL_VBD_OO'] = serverCurrInstance.vbd_oo
            dict_data['VM_TOTAL_VBD_RD'] = serverCurrInstance.vbd_rd
            dict_data['VM_TOTAL_VBD_WR'] = serverCurrInstance.vbd_wr
            dict_data['VM_TOTAL_NETS'] = serverCurrInstance.nets
            dict_data['VM_TOTAL_NETTX(k)'] = serverCurrInstance.nets_tx
            dict_data['VM_TOTAL_NETRX(k)'] = serverCurrInstance.nets_rx
            dict_data['VM_LOCAL_STORAGE'] = serverCurrInstance.gb_local
            dict_data['VM_SHARED_STORAGE'] = serverCurrInstance.gb_poolused
            dict_data['VM_TOTAL_STORAGE'] = serverCurrInstance.gb_pooltotal
            #FIXME: Switch this to real node status
            dict_data['PAUSED_VMs'] = serverCurrInstance.paused_vms
            dict_data['RUNNING_VMs'] = serverCurrInstance.running_vms
            dict_data['CRASHED_VMs'] = serverCurrInstance.crashed_vms
            dict_data['VER'] = node_ver #result[17] # get xen version
            dict_data['VM_TOTAL_MEM'] = serverCurrInstance.total_mem
            dict_data['VM_TOTAL_CPU'] = serverCurrInstance.total_cpu
            dict_data['TOTAL_VMs'] = serverCurrInstance.total_vms
            dict_data['SERVER_CPUs'] = serverCurrInstance.server_cpus
            dict_data['SERVER_MEM'] = serverCurrInstance.server_mem
            dict_data['HOST_MEM(%)'] = serverCurrInstance.host_mem
            dict_data['HOST_CPU(%)'] = serverCurrInstance.host_cpu
            childnode=NodeService().get_childnodestatus(auth,m_node.id)
            dict_data["NODE_CHILDREN"]=childnode
        return dict_data

    """
    function implemented to showup dashboard from database. It is replacement
    for gather_info_for_pool
    """
    def gather_info_for_pool_from_database(self, auth, pool_type, pool_id):
        resultList = []
        if pool_type == constants.SERVER_POOL:
            node_list = self.manager.getNodeList(auth, pool_id)
        else:
            return resultList;

        if node_list is None:
            return

#        node_list.sort()
        i=0
        for m_node in node_list:           
            #m_node = self.manager.getNode(auth, m_name, pool_id)            
#            node_status = "Unknown"
            if m_node is None :
                continue

            #call function to read the data from server current metrics to display dashboard

            i+=1
            if (i > int(tg.config.get(constants.NODE_LIST_LIMIT))):                
                break
            else:
                data_dict = self.getServerCurrentMetrics(auth,m_node)
                resultList.append(data_dict)
                   

        dict_data={}      
        if len(node_list) > int(tg.config.get(constants.NODE_LIST_LIMIT)):
            dict_data["NODE_NAME"] = 'Too many...'
            dict_data["NODE_TYPE"] = constants.SPECIAL_NODE           
            resultList.append(dict_data)

        return resultList


    def gather_info_for_pool(self, auth, pool_type, pool_id):
        resultList = self.gather_info_for_pool_from_database(auth, pool_type, pool_id)

        ## Append the group summary if the node selection is data center
        if pool_type == constants.DATA_CENTER:
            group_list = self.manager.getGroupList(auth)
            for group in group_list:
                #group = self.manager.getGroup(auth,group_name)
                group_info = {}

                # summarize nodes within group.
                node_list = self.manager.getNodeList(auth,group.id)

                group_info["NODE_COUNT"] =  len(node_list)
                group_info["NODE_TYPE"] = constants.SERVER_POOL
                group_info["NODE_ID"]=group.id
                childnode=NodeService().get_childnodestatus(auth,group.id)
                group_info["NODE_CHILDREN"]=childnode
                connected = 0
                servers = 0
                vm_mem = 0
                vm_cpu = 0

                mem = 0
                cpu = 0

                vm_running = 0
                vm_paused = 0
                vm_crashed = 0
                vm_total = 0

                nets=0
                net_tx = 0
                net_rx =0

                vbds=0
                vbd_oo = 0
                vbd_rd = 0
                vbd_wr = 0

                for m_node in node_list:
                    #m_node = self.manager.getNode(auth, node_name, group.name)
                    if m_node is None :
                        print "m_node is None ", node_name, pool_id
                        continue

                    servers = servers + 1
                    if m_node is not None:
#                        if not m_node.is_authenticated():
#                            try:
#                                m_node.connect()
#                            except Exception, ex:
#                                traceback.print_exc()
#                                LOGGER.error(ex)
                        if True:#m_node.is_authenticated() and not m_node.is_in_error():
                            node_snapshot = None
                            dom_count = 0
                            try:
                                node_snapshot = self.getServerCurrentMetrics(auth,m_node)#m_node.get_metrics()
                                dom_count = len(self.manager.get_dom_names(auth,m_node.id))#len(m_node.get_dom_names())-1
                            except Exception, ex:
                                #print "error getting info for ", m_node.hostname, ex
                                pass

                            if node_snapshot is None:
                                continue

                            connected = connected + 1
                            # TBD : This needs to be streamlined
#                            if m_node["nr_cpus"] is not None:
#                                cpu +=  m_node["nr_cpus"]
#                                mem +=  m_node["total_memory"]
#                            else:

                            cpu +=  int(m_node.get_cpu_info().get(constants.key_cpu_count,0))
                            mem +=  int(m_node.get_memory_info().get(constants.key_memory_total,0))
                            node_snapshot["TOTAL_VMs"] = dom_count
                            if node_snapshot.get('VM_TOTAL_CPU') is not None:
                                vm_cpu += node_snapshot["VM_TOTAL_CPU"]
                            if node_snapshot.get('VM_TOTAL_MEM') is not None:
                                vm_mem += node_snapshot["VM_TOTAL_MEM"]

                            if node_snapshot.get("RUNNING_VMs") is not None:
                                vm_running += node_snapshot["RUNNING_VMs"]
                            if node_snapshot.get("PAUSED_VMs") is not None:
                                vm_paused += node_snapshot["PAUSED_VMs"]
                            if node_snapshot.get("CRASHED_VMs") is not None:
                                vm_crashed += node_snapshot["CRASHED_VMs"]
                            if node_snapshot.get("TOTAL_VMs") is not None:
                                vm_total += node_snapshot["TOTAL_VMs"]
                            if node_snapshot.get("VM_TOTAL_NETS") is not None:
                                nets += node_snapshot.get("VM_TOTAL_NETS")
                            if node_snapshot.get("VM_TOTAL_NETTX(k)") is not None:
                                net_tx += node_snapshot.get("VM_TOTAL_NETTX(k)")
                            if node_snapshot.get("VM_TOTAL_NETRX(k)") is not None:
                                net_rx += node_snapshot.get("VM_TOTAL_NETRX(k)")
                            if node_snapshot.get("VM_TOTAL_VBDS") is not None:
                                vbds += node_snapshot.get("VM_TOTAL_VBDS")
                            if node_snapshot.get("VM_TOTAL_VBD_OO") is not None:
                                vbd_oo += node_snapshot.get("VM_TOTAL_VBD_OO")
                            if node_snapshot.get("VM_TOTAL_VBD_RD") is not None:
                                vbd_rd += node_snapshot.get("VM_TOTAL_VBD_RD")
                            if node_snapshot.get("VM_TOTAL_VBD_WR") is not None:
                                vbd_wr += node_snapshot.get("VM_TOTAL_VBD_WR")


                # add group information
                group_info["NODE_NAME"] = group.name
                group_info["NODES_CONNECTED"] = connected

                # summarized stats
                group_info["SERVERS"] = servers
                group_info["SERVER_CPUs"] = cpu
                group_info["iSERVER_MEM"] = mem
                group_info["SERVER_MEM"] = to_str(mem) + "M"

                # VM stats
                group_info["RUNNING_VMs"] = vm_running
                group_info["PAUSED_VMs"] = vm_paused
                group_info["CRASHED_VMs"] = vm_crashed
                group_info["TOTAL_VMs"] = vm_total


                if connected > 0:
		    cpu_ratio=0
                    if cpu != 0:
                        cpu_ratio=vm_cpu / cpu
                        
                    group_info["VM_TOTAL_CPU(%)"] = cpu_ratio                    
                    group_info["VM_TOTAL_MEM(%)"] = (vm_mem * 100.0)/ mem
                else:
                    group_info["VM_TOTAL_CPU(%)"] = 0
                    group_info["VM_TOTAL_MEM(%)"] = 0


                group_info["VM_TOTAL_NETS"] = nets
                group_info["VM_TOTAL_NETTX(k)"] = net_tx
                group_info["VM_TOTAL_NETRX(K)"] = net_rx

                group_info["VM_TOTAL_VBDS"] = vbds
                group_info["VM_TOTAL_VBD_OO"] = vbd_oo
                group_info["VM_TOTAL_VBD_RD"] = vbd_rd
                group_info["VM_TOTAL_VBD_WR"] = vbd_wr

                resultList.append(group_info)
        return resultList

    def data_center_info(self, auth, node_id, type):
        ent=auth.get_entity(node_id)
        if ent is None:
            return []
        data_list = self.gather_info_for_pool(auth,constants.DATA_CENTER,node_id)
        info_list=[]
        cpu=0
        server_mem=0.00
        stor_avail=0.00
        nwlist=0

        if type=='DATA_CENTER_INFO':
            for data_dict in data_list:
                cpu+=data_dict.get('SERVER_CPUs',0)
                server_mem+=data_dict.get('iSERVER_MEM',0.00)/1000

#            info_list.append(dict(name='Name',value=ent.name))
            info_list.append(dict(name='Total CPU count',value=to_str(cpu)+"          "))
            info_list.append(dict(name='Total Memory',value=to_str("%6.2f" % (server_mem))+(' GB')))

            site_id = node_id
            ss = DBSession.query(Storage_Stats).filter_by(entity_id=site_id, storage_id=None).first()
            if ss:
                stor_avail = ss.storage_avail_in_SP
            if not stor_avail:
                stor_avail=0.00
            stor_avail=to_str("%6.2f" %(stor_avail))+"  "+" "+"GB"
            info_list.append(dict(name='Storage Available',value=stor_avail))

            nwlist=NetworkService().get_nw_defns(auth,node_id,None,None,constants.SCOPE_DC)
            info_list.append(dict(name='Networks',value=to_str(len(nwlist))+""))

#            info_list.append(dict(name='Platform',value=m_node.platform))
#            info_list.append(dict(name='Version',value=data_dict.get('VER',"")))
#            info_list.append(dict(name='CPU(s)',value=data_dict.get('SERVER_CPUs',"")))
#            info_list.append(dict(name='Memory(KB)',value=data_dict.get('SERVER_MEM',"")))
        elif type=='DATA_CENTER_SEC_INFO':
            info_list=[]

        elif type=='DATA_CENTER_VM_INFO':
             entId_list=[]

            #ent=auth.get_entity(group.id)
             node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE))
             entId_list=[x.entity_id for x in node_entities]
             vm_entities = auth.get_entities(to_unicode(constants.DOMAIN))        
             vm_ids=[x.entity_id for x in vm_entities]
             entId_list += vm_ids
             sp_entities = auth.get_entities(to_unicode(constants.SERVER_POOL))
             sp_ids = [x.entity_id for x in sp_entities]
             entId_list += sp_ids

             sps=len(sp_ids)
             srvrs=0
             total_vms=0
             running_vms=0
             paused_vms=0

             for data_dict in data_list:
                srvrs+=data_dict.get('SERVERS',0)
                total_vms+=data_dict.get('TOTAL_VMs',0)
                running_vms+=data_dict.get('RUNNING_VMs',0)
                paused_vms+=data_dict.get('PAUSED_VMs',0)

             density=0
             if srvrs>0:
                density=to_str("%6.2f" % (float(total_vms)/float(srvrs)))

             vminfo=to_str(total_vms)+"/"+to_str(running_vms)+"/"+to_str(paused_vms)+"/"+to_str(total_vms-(running_vms+paused_vms))
             total_notification = Userinfo().getNotifications('COUNT',entId_list,auth.user.user_name)
#             system_tasks = Userinfo().getSystemTasks('COUNT',auth.user.user_name)
             info_list.append(dict(name='Server Pools',value=sps))
             info_list.append(dict(name='Servers',value=srvrs))
             info_list.append(dict(name='Virtual Machines',value=vminfo ,type='vmsummary'))
             info_list.append(dict(name='Virtual Machine Density',value=density))
            #    Call ge platform count to get the Virtualizaton Platform details
             pfvalue=""
             pflist=get_platform_count()
             i=0
             for pfl in pflist:
                 if i>0:
                    pfvalue+=" , "
                 pfvalue+=to_str(pfl[1])+" "+constants.platforms[pfl[0]]
                 i+=1
             info_list.append(dict(name='Virtualization Platform',value=pfvalue))
             info_list.append(dict(name='Notifications',value=total_notification,list=entId_list,type='Notifications',entType=constants.DATA_CENTER))
#             info_list.append(dict(name='System Tasks',value=system_tasks,type='Systemtasks'))
             
             #Start-Storage information
             """
             total_allocated_size=0
             storage=""
             d_count=0
             storage_id_list=[]
             
             #get list of storage ids for the data center
             def_links = DBSession.query(DCDefLink).filter_by(site_id=node_id)
             if def_links:
                 for eachlink in def_links:
                    storage_id_list.append(eachlink.def_id)
            
#             vms=DBSession.query(VM).filter(VM.id.in_(vm_ids)).all()             
             for vmid in vm_ids:
                 allocated_size, local_size = StorageManager().get_storage_size(vmid)
                 total_allocated_size = total_allocated_size + allocated_size             

             total_size=0.00
             if storage_id_list:
                for eachid in storage_id_list:
                    defn = StorageManager().get_defn(eachid)
                    if defn:
                        stats = defn.get_stats()
                        if stats:
                            size = stats.total_size
                            if size:
                                total_size = total_size + float(size)
                            else:
                                total_size = total_size

             if float(total_size) > 0:
                 storage = (100 * float(total_allocated_size))/float(total_size)
             else:
                 storage = 0
             """
             storage=""
             ss = DBSession.query(Storage_Stats).filter_by(entity_id=node_id, storage_id=None).first()
             if ss:
                 storage = ss.storage_allocation_at_DC
             info_list.append(dict(name='Storage Allocation (%)',value=storage,type='storage'))
             #End-Storage information

        elif type=='STORAGE_INFO':
            result=StorageService().get_storage_def_list(auth,node_id,None,constants.SCOPE_DC)
            info_list=result['rows']
        elif type=='VIRT_NW_INFO':
            info_list=NetworkService().get_nw_defns(auth,node_id,None,None,constants.SCOPE_DC)
        return info_list

    def get_resources(self,auth):
        try:
            resources_url = tg.config.get("resources_url")
            resource_list = connect_url(resources_url)
        except:
            resource_list = tg.config.get("def_resources")
        
        return resource_list

    def server_pool_info(self, auth, node_id, type):
        group=self.manager.getGroup(auth, node_id)
        if group is None:
            return  []
        data_dict = self.getServerPoolCurrentMetrics(group,constants.SERVERPOOL_CURR)
        info_list=[]

        if type=='SERVER_POOL_INFO':

            info_list.append(dict(name='Name',value=group.name))
#            info_list.append(dict(name='Platform',value=m_node.platform))
#            info_list.append(dict(name='Version',value=data_dict.get('VER',"")))
#            info_list.append(dict(name='CPU(s)',value=data_dict.get('SERVER_CPUs',"")))
#            info_list.append(dict(name='Memory(KB)',value=data_dict.get('SERVER_MEM',"")))
        elif type=='SERVER_POOL_SEC_INFO':
            info_list=[]

        elif type=='SERVER_POOL_VM_INFO':
            entId_list=[]
            entId_list.append(group.id)
            total_notification=''
            ent=auth.get_entity(group.id)
            managed_nodes=ent.children
            srvrs=len(managed_nodes)
            ids=[]
            pfvalue=""
            vms=data_dict.get('TOTAL_VMs',0)
            density=0
            if srvrs>0:
                density=to_str("%6.2f" % (float(vms)/float(srvrs)))

            runn=data_dict.get('RUNNING_VMs',0)
            paused=data_dict.get('PAUSED_VMs',0)
            vminfo=to_str(vms)+"/"+to_str(runn)+"/"+to_str(paused)+"/"+to_str(vms-(runn+paused))

            info_list.append(dict(name='Servers',value=srvrs))
            info_list.append(dict(name='Virtual Machines',value=vminfo ,type='vmsummary'))
            info_list.append(dict(name='Virtual Machine Density',value=density))

            for managed_node in managed_nodes:
                entId_list.append(managed_node.entity_id)
                vmnodes=managed_node.children
                for vmnode in vmnodes:
                    entId_list.append(vmnode.entity_id)
                ids.append(managed_node.entity_id)
            pflist=get_platform_count(ids)
            i=0
            for pf in pflist:
                if i>0:
                    pfvalue+=" , "
                pfvalue+=to_str(pf[1])+" "+constants.platforms[pf[0]]
                i+=1
            total_notification = Userinfo().getNotifications('COUNT',entId_list,auth.user.user_name)
            info_list.append(dict(name='Virtualization Platform',value=pfvalue))
#            #    Call ge platform count to get the Virtualizaton Platform details

#            info_list.append(dict(name='CPU Usage',value=data_dict.get('VM_TOTAL_CPU(%)',0.00),
#                                    type='bar',chart_type='SERVER_CPU',action='chart'))
#            info_list.append(dict(name='Memory Usage',value=data_dict.get('VM_TOTAL_MEM(%)',0.00),
#                                    type='bar',chart_type='SERVER_MEM',action='chart'))

            info_list.append(dict(name='Notifications',value=total_notification,list=entId_list,type='Notifications'))
            
            #Start-Storage information
            storage=""
            group_id = node_id
            ss = DBSession.query(Storage_Stats).filter_by(entity_id=group_id, storage_id=None).first()
            if ss:
                storage = ss.storage_used_in_SP
            if not storage:
                storage=0.00

            #get storage used size
            storage = to_str(storage) + " GB"
            #now not showing the storage allocation so commenting it.
            #info_list.append(dict(name='Storage Allocation (%)',value=storage,type='storage'))
            info_list.append(dict(name='Storage Used',value=storage))
            #info_list.append(dict(name='Stoage Available',value=storage,type='storage'))
            #End-Storage information

        elif type=='STORAGE_INFO':
            result=StorageService().get_storage_def_list(auth,None,node_id,constants.SCOPE_SP)
            info_list=result['rows']

        elif type=='VIRT_NW_INFO':
#            info_list.append(dict(name='nfs1',details='10.1.0.0/24',description='private nw'))
#            info_list.append(dict(name='iscsi1',details='10.2.0.0/24',description='forwarded nw'))
            info_list=NetworkService().get_nw_defns(auth,None,node_id,None,constants.SCOPE_SP)
        elif type =='SUMMARY':
            ent=auth.get_entity(group.id)
            managed_nodes=ent.children
            srvrs=len(managed_nodes)

            ids=[]
            pfvalue=""
            for managed_node in managed_nodes:
                ids.append(managed_node.entity_id)
            pflist=get_platform_count(ids)
            i=0
            for pf in pflist:
                if i>0:
                    pfvalue+=" , "
                pfvalue+=to_str(pf[1])+" "+constants.platforms[pf[0]]
                i+=1

            info_list.append(dict(name='Servers',value=srvrs))
            info_list.append(dict(name='Total CPU count',value=to_str(data_dict.get('SERVER_CPUs',0))))
            info_list.append(dict(name='Total Memory',value=to_str("%6.2f" % (data_dict.get('SERVER_MEM',0.00)/1000))+(' GB')))

            stor_avail=0.00
            group_id = node_id
            ss = DBSession.query(Storage_Stats).filter_by(entity_id=group_id, storage_id=None).first()
            if ss:
                stor_avail = ss.storage_avail_in_SP
            if not stor_avail:
                stor_avail=0.00
            stor_avail=to_str("%6.2f" %(stor_avail))+" GB"
            info_list.append(dict(name='Storage Available',value=stor_avail))
            nwlist=NetworkService().get_nw_defns(auth,None,node_id,None,constants.SCOPE_SP)

            info_list.append(dict(name='Networks',value=len(nwlist)))
            info_list.append(dict(name='Virtualization Platform',value=pfvalue))

        return info_list

    def set_registered(self,auth):
        set_registered(auth)

    def server_info(self, auth, node_id, type):
        m_node=self.manager.getNode(auth,node_id)
        if m_node is None:
            return []
        data_dict = self.getServerCurrentMetrics(auth,m_node)
        info_list=[]

        if type=='SERVER_INFO':

            info_list.append(dict(name='Name',value=m_node.hostname))
            info_list.append(dict(name='Platform',value=constants.platforms[m_node.platform]))
            info_list.append(dict(name='Version',value=data_dict.get('VER',"")))
            info_list.append(dict(name='CPUs',value=data_dict.get('SERVER_CPUs',0)))
            info_list.append(dict(name='Memory',value=to_str("%6.2f" % (data_dict.get('SERVER_MEM',0.00)))+(' MB')))
        elif type=='SERVER_SEC_INFO':
            os=m_node.get_os_info()
            cpu=m_node.get_cpu_info()

            info_list.append(dict(name='OS Kernel',value=os.get('release',"")))
            if os.get('distro_string') is not None:
                info_list.append(dict(name='OS Distribution',value=os['distro_string']))
            info_list.append(dict(name='OS Architecture',value=os.get('machine',"")))

            info_list.append(dict(name='CPU Model',value=cpu.get('model_name',"")))
            info_list.append(dict(name='CPU Vendor ID',value=cpu.get('vendor_id',"")))

        elif type=='VM_INFO':
            entId_list=[]
            total_notification=''
            ent=auth.get_entity(m_node.id)
#            et=m_node.entity_id
            entId_list.append(m_node.id)
            vmnodes=ent.children
            for vmnode in vmnodes:
                entId_list.append(vmnode.entity_id)
#                entId_list.append(vmnode.entity_id)
            runn=data_dict.get('RUNNING_VMs',0)
            paused=data_dict.get('PAUSED_VMs',0)
            os=m_node.get_os_info()
            mem=m_node.get_memory_info()
            platform=m_node.get_platform_info()            
            plt_ver=platform.get(constants.platform_version[m_node.platform],'')
#            free_mem=0
#            if mem.get("free_memory") is not None and mem.get("total_memory") is not None :
#                try:
#                    free_mem=((float(mem.get("total_memory"))-float(mem.get("free_memory")))/float(mem.get("total_memory")))*100
#                except Exception, e:
#                    LOGGER.error(e)
#                    pass

            tot=data_dict.get('TOTAL_VMs',0)
            node_down=0
            vminfo=to_str(tot)+"/"+to_str(runn)+"/"+to_str(paused)+"/"+to_str(tot-(runn+paused))
            icon="&nbsp;<img width='13' height='13' src='../icons/small_connect.png'/>"
            if not m_node.is_up():
                node_down="node_down"
                vminfo+="/"+to_str(node_down)
                icon="&nbsp;<img width='13' height='13' src='../icons/small_disconnect.png'/> "
            total_notification = Userinfo().getNotifications('COUNT',entId_list,auth.user.user_name)
            
            des=NodeService().get_annotation(auth,node_id)
            annote_icon=""
            annot=des.get("annotate")
            if annot:
                enc_value=urllib.quote(annot.get("text"))
                enc_value=enc_value.replace("%0A","<br/>").replace("%20","&nbsp;")
                en_des="<b>Annotated by : "+annot.get("user")+"<br/> Annotation : </b><br/> <br/>"+enc_value
                annote_icon="&nbsp;&nbsp;<img width='13' height='13' src='../icons/annotation_node.png' onClick='show_desc(&quot;"+en_des+"&quot;,null,null,&quot;Annotation&quot;)'/> "
            info_list.append(dict(name='Status',value=data_dict.get('NODE_STATUS',"Unknown")+icon+annote_icon))
           
            info_list.append(dict(name='Platform',value=to_str(constants.platforms[m_node.platform]+" "+plt_ver)))
            info_list.append(dict(name='Host OS',value=os.get('distro_string',"")))
            info_list.append(dict(name='CPUs',value=data_dict.get('SERVER_CPUs',0)))            
            info_list.append(dict(name='Memory',value=to_str("%6.2f" % (float(mem.get(constants.key_memory_total,0))))+(' MB')))
            #info_list.append(dict(name='Memory Usage',value=free_mem,type='bar'))
            #info_list.append(dict(name='Storage Usage',value=23.30,type='bar'))

#            info_list.append(dict(name='Total VMs',value=len(ent.children)))
#            info_list.append(dict(name='Running VMs',value=data_dict.get('RUNNING_VMs',0)))
#            info_list.append(dict(name='Paused VMs',value=data_dict.get('PAUSED_VMs',0)))
#            info_list.append(dict(name='Crashed VMs',value=data_dict.get('CRASHED_VMs',0)))
            info_list.append(dict(name='Virtual Machines',value=vminfo,type='vmsummary'))
            info_list.append(dict(name='Host CPU(%)',value=data_dict.get('HOST_CPU(%)',0.00),
                                    type='bar',chart_type='SERVER_CPU',action='chart'))
            info_list.append(dict(name='Host Memory(%)',value=data_dict.get('HOST_MEM(%)',0.0),
                                    type='bar',chart_type='SERVER_MEM',action='chart'))
            info_list.append(dict(name='Notifications',value=total_notification,list=entId_list,type='Notifications'))
            
            #Start-Storage information
            d_size=0.0
            storage=""
            d_count=0

            node_entity = auth.get_entity(node_id)
            vm_entities = auth.get_entities(to_unicode(constants.DOMAIN), node_entity)
            for eachvm in vm_entities:
                temp_size, local_size = StorageManager().get_storage_size(eachvm.entity_id)
                d_size=d_size+local_size
                    
            d_size_gb=d_size
            if d_size_gb:
                storage = to_str(float("%6.2f" %(d_size_gb))) + " GB"
            else:
                storage = 0

            info_list.append(dict(name='Storage',value=storage))
            #End-Storage information

        elif type=='DISK_INFO':
            info_list=m_node.get_disk_info()
        elif type=='INTERFACE_INFO':
            info_list=m_node.get_network_info()
        elif type=='OS_INFO':
            info_list.extend(NodeService().getDictInfo(m_node.get_os_info(),m_node.get_os_info_display_names(),'OS Info'))
        elif type=='Memory_INFO':
            info_list.extend(NodeService().getDictInfo(m_node.get_memory_info(),m_node.get_memory_info_display_names(),'Memory Info'))
        elif type=='CPU_INFO':
            info_list.extend(NodeService().getDictInfo(m_node.get_cpu_info(),m_node.get_cpu_info_display_names(),'CPU Info'))
        elif type=='Platform_INFO':
            info_list.extend(NodeService().getDictInfo(m_node.get_platform_info(),m_node.get_platform_info_display_names(),'Platform Info'))
        elif type=='STORAGE_INFO':
            info_list=StorageService().get_server_storage_def_list(auth,node_id)
#            info_list.append(dict(name='nfs1',type='nfs',size='16GB',description='nfs storage on 99'))
#            info_list.append(dict(name='iscsi_11',type='iSCSI',size='160GB',description='iscsi storage on 11'))
        elif type=='VIRT_NW_INFO':
            info_list=NetworkService().get_nw_defns(auth,None,None,node_id,constants.SCOPE_S)
        return info_list

    def server_usage(self, auth, node_id, metric):
        m_node=self.manager.getNode(auth,node_id)
        if m_node is None:
            return []
        data_dict = self.getServerCurrentMetrics(auth,m_node)
        free=total=100.00
        dom0=0.00
        vm=0.00

        result= []

        if metric==constants.METRIC_CPU:
            dom0=float(data_dict.get('HOST_CPU(%)',0.00))-float(data_dict.get('VM_TOTAL_CPU(%)',0.00))
            vm=float(data_dict.get('VM_TOTAL_CPU(%)',0.00))

        elif metric==constants.METRIC_MEM:
            dom0=float(data_dict.get('HOST_MEM(%)',0.00))-float(data_dict.get('VM_TOTAL_MEM(%)',0.00))
            vm=float(data_dict.get('VM_TOTAL_MEM(%)',0.00))
        free=total-(dom0+vm)

        host="Other"
        if m_node.platform=='xen':
            host="Domain-0"
        result.append(dict(value=vm,label= 'Virtual Machines'))
        result.append(dict(value=dom0, label= host))
        result.append(dict(value=free, label= 'Free'))
        return result

    def os_distribution_chart(self,auth,node_id,metric,node_type):

        ids=list=result=[]

        ent=auth.get_entity(node_id)

        if metric==constants.MANAGED_NODE:

            if node_type==constants.DATA_CENTER:
                ids=None
            elif node_type==constants.SERVER_POOL:
                servers=ent.children
                for server in servers:
                    ids.append(server.entity_id)

            list=get_host_os_info(ids)

        elif metric==constants.DOMAIN:
            if node_type==constants.DATA_CENTER:
                ids=None
            elif node_type==constants.SERVER_POOL:
                servers=ent.children
                for server in servers:
                    vms=server.children
                    for vm in vms:
                        ids.append(vm.entity_id)

            list=get_guest_os_info(ids)

        for element in list:
            label=element[0]
            if label is None or label=='None None' or label=='None':
                label="Unknown"
            result.append(dict(value=element[1],label=label))

        if (len(result) == 0):
            result.append(dict(total="0", label= 'No Data to Display'))
        print result
        return result

    def topNvms(self, auth, node_id, metric,node_type):
        result=[]
        vms=[]
        if node_type==constants.DATA_CENTER:
            site=auth.get_entity(node_id)
            if site is None:
                return []

            for grp in site.children:
                for node in grp.children:
                    vms.extend(node.children)

        elif node_type==constants.SERVER_POOL:
            group=auth.get_entity(node_id)
            if group is None:
                return []

            for node in group.children:
                    vms.extend(node.children)

        elif node_type==constants.MANAGED_NODE:
            m_node=auth.get_entity(node_id)
            if m_node is None:
                return []

            vms.extend(m_node.children)

        vm_ids=[]
        vm_dict={}
        for vm in vms:
            vm_ids.append(vm.entity_id)
            vm_dict[vm.entity_id]=vm.name

        tc=TopCache()
        metric_type=constants.VM_RAW
        date2=datetime.utcnow()
        date1=datetime.utcnow() +timedelta(seconds=-3601)
        data_list=tc.get_top_entities(node_id,node_type,metric,"topNvms",auth,metric_type,vm_ids,date1,date2)
        for data in data_list:
            try:
                result.append(dict(vmid=data[1],vm=vm_dict[data[1]], usage=data[0],node_id=data[1]))
            except Exception,e:
                traceback.print_exc()
        return result


    def topNservers(self, auth, node_id, metric,node_type):
        result=[]
        srvrs=[]
        if node_type==constants.DATA_CENTER:
            site=auth.get_entity(node_id)
            if site is None:
                return []

            for grp in site.children:
                srvrs.extend(grp.children)

        elif node_type==constants.SERVER_POOL:
            group=auth.get_entity(node_id)
            if group is None:
                return []

            srvrs.extend(group.children)


        srvr_ids=[]
        srvr_dict={}
        for srvr in srvrs:
            srvr_ids.append(srvr.entity_id)
            srvr_dict[srvr.entity_id]=srvr.name

        tc=TopCache()
        metric_type=constants.SERVER_RAW
        date2=datetime.utcnow()
        date1=datetime.utcnow() +timedelta(seconds=-3601)
        data_list=tc.get_top_entities(node_id,node_type,metric,"topNservers",auth,metric_type,srvr_ids,date1,date2)
        for data in data_list:
            result.append(dict(serverid=data[1],server=srvr_dict[data[1]], usage=data[0],node_id=data[1]))

        return result

    def vm_info(self, auth, node_id, type):
        vm_ent=auth.get_entity(node_id)
        if vm_ent is None:
            return []
        node_ent=vm_ent.parents[0]

        m_node=self.manager.getNode(auth,node_ent.entity_id)
        
        dom=DBSession.query(VM).filter(VM.id==node_id).one()
        config=dom.get_config()
        
        info_list=[]

        os_info=dom.get_os_info()
        os=os_info.get('name',"")+" "+to_str(os_info.get('version',""))

        if type=='VM_INFO':

            cpu=0.00
            mem=0.00
            ms=MetricsService()
            state=dom.get_state()
            VMCurrInstance = ms.getVMCurrMetricsData(constants.VM_CURR, vm_ent, auth)
            if VMCurrInstance is not None:
                cpu=VMCurrInstance.cpu_util
                mem=VMCurrInstance.mem_util

            vm_status=""
            ###TBD:Checking for unknown shouldn't be  here
#            if (state in [VM.RUNNING, VM.UNKNOWN]):
#                vm_status="Up"+"&nbsp;<img width='13' height='13' src='../icons/small_started_state.png'/>"
#            elif (state == VM.PAUSED):
#                vm_status="Paused"+"&nbsp;<img width='13' height='13' src='../icons/small_pause.png'/>"
#            else:
#                vm_status="Down"+"&nbsp;<img width='13' height='13' src='../icons/small_shutdown.png'/>"

            avail_state = DBSession.query(AvailState.avail_state).filter(AvailState.entity_id==node_id).one()

            if avail_state[0] in [VM.RUNNING,VM.UNKNOWN]:
                vm_status="Up"+"&nbsp;<img width='13' height='13' src='../icons/small_started_state.png'/>"
            elif avail_state[0]==VM.PAUSED:
                vm_status="Paused"+"&nbsp;<img width='13' height='13' src='../icons/small_pause.png'/>"
            elif avail_state[0] in [VM.SHUTDOWN,VM.CRASHED,VM.NOT_STARTED]:
                vm_status="Down"+"&nbsp;<img width='13' height='13' src='../icons/small_shutdown.png'/>"

            info_list.append(dict(name='Name',value=dom.name))
            status=""
            if not m_node.is_up():
                status="&nbsp; <img width='13' height='13' src='../icons/small_shutdown.png'/> <br/>(Not Connected)"
                if avail_state[0] in [VM.SHUTDOWN,VM.CRASHED,VM.NOT_STARTED]:
                    vm_status="Down"+"&nbsp;<img width='13' height='13' src='../icons/small_shutdown_down.png'/>"
                elif avail_state[0] in [VM.RUNNING,VM.UNKNOWN]:
                    vm_status="Up"+"&nbsp;<img width='13' height='13' src='../icons/small_started_state_down.png'/>"
                elif avail_state[0]==VM.PAUSED:
                    vm_status="Paused"+"&nbsp;<img width='13' height='13' src='../icons/small_pause_down.png'/>"

            info_list.append(dict(name='Server',value=m_node.hostname+status))
            des=NodeService().get_annotation(auth,node_id)
            annote_icon=""
            annot=des.get("annotate")
            if annot:
                enc_value=urllib.quote(annot.get("text"))
                enc_value=enc_value.replace("%0A","<br/>").replace("%20","&nbsp;")
                en_des="<b>Annotated by : "+annot.get("user")+"<br/> Annotation : </b><br/><br/>"+enc_value
                annote_icon="&nbsp;&nbsp;<img width='13' height='13' src='../icons/annotation_vm.png' onClick='show_desc(&quot;"+en_des+"&quot;,null,null,&quot;Annotation&quot;)'/> "

            info_list.append(dict(name='Status',value=vm_status+annote_icon))
            template_info=dom.get_template_info()
            info_list.append(dict(name='Template',value=template_info['template_name']))

            info_list.append(dict(name='Guest OS',value=os))


            #info_list.append(dict(name='Started on',value="2009-11-5 6:38:24"))
            #info_list.append(dict(name='Uptime',value=""))
            info_list.append(dict(name='Virtual CPUs',value=config['vcpus']))
            info_list.append(dict(name='Memory',value=to_str(config['memory'])+" MB"))

#            info_list.append(dict(name='VM CPU(%)',value=cpu,
#                                    type='bar'))
#            info_list.append(dict(name='VM Memory(%)',value=mem,
#                                    type='bar'))

            #server_mem=data_dict.get('SERVER_MEM',0)

            #mem_used=(mem/100)*server_mem
            #mem=(mem_used/config['memory'])*100

#            print "---------",to_str("%6.2f" % (mem))
            info_list.append(dict(name='Host CPU Usage(%)',value=cpu,
                                    type='bar'))
            info_list.append(dict(name='Memory Utilization(%)',value=float("%6.2f" % (mem)),
                                    type='bar'))

#            image_config=None
#            if img is not None:
#                vm_config,image_config=img.get_configs()

#            disks = config.getDisks()
            """
            d_size=0.0
            storage=""
            d_count=0
            
            disk_stat=VMDiskManager(config).get_storage_stats().get("DISK_STATS")
            if disk_stat:
    #            print "DiS===",disk_stat
                for disk in disk_stat:
    #                print "===",disk_stat.get(disk)
                    disk_s=disk_stat.get(disk)
                    disk_size=disk_s.get("DISK_SIZE")
                    if disk_size is not None:
                        d_size=d_size+disk_size
                        d_count=d_count+1
            
            local_size = d_size
            """
            #Start-Storage information
            d_size=0.0
            d_count=0
            storage = None
            d_size, local_size = StorageManager().get_storage_size(dom.id)
            shared_size = d_size

            if local_size and shared_size:
                storage = to_str(local_size) + ", " + to_str(shared_size)
            elif not local_size and shared_size:
                storage = shared_size
            if local_size and not shared_size:
                storage = local_size
            if storage:
                storage = str(storage) + " GB"
            else:
                storage = None
                
            info_list.append(dict(name='Storage',value=storage))
            #End-Storage information

            vifs = config.getNetworks()
            info_list.append(dict(name='Network',value=to_str(len(vifs))))

            for vif in vifs:
                info_list.append(dict(name='',value=NetworkService().get_nw_entry(vif).get("name")))
        
        elif type=='STORAGE_INFO':
            disks = VMDiskManager(config).getDisks()
            for disk in disks:
                is_remote = config.get_storage_stats().get_remote(disk.disk_name)
                if is_remote == True:
                    sharedVal = "Yes"
                else:
                    sharedVal = "No"

                info_list.append(dict(type=disk.disk_type,filename=disk.disk_name,device=disk.dev_type,                                mode=disk.read_write,shared=sharedVal,size=disk.disk_size))
        elif type=='NW_INFO':
            vifs = config.getNetworks()

            for vif in vifs:
                info_list.append(NetworkService().get_nw_entry(vif))


        elif type=='GENERAL_INFO':
            info_list.append(dict(name='Name',value=dom.name))
            info_list.append(dict(name='Server',value=m_node.hostname))
            info_list.append(dict(name='Virtual CPUs',value=config["vcpus"]))
            info_list.append(dict(name='Memory',value=to_str(config["memory"])+" MB"))
            info_list.append(dict(name='Guest OS',value=os))
#                 info_list.append(dict(name='Config File',value=""))

        elif type=='BOOT_PARAM':
                info_list.append(dict(name='Bootloader',value=config["bootloader"]))
                info_list.append(dict(name='Kernel',value=config["kernel"]))
                info_list.append(dict(name='Ramdisk',value=config["ramdisk"]))
                info_list.append(dict(name='Root Device',value=config["root"]))
                info_list.append(dict(name='Kernel Args',value=config["extra"]))
                info_list.append(dict(name='On Power off',value=config["on_shutdown"]))
                info_list.append(dict(name='On Reboot',value=config["on_reboot"]))
                info_list.append(dict(name='On Crash',value=config["on_crash"]))
                boot_device=""
                if config["boot"] =="d":
                    boot_device="CD ROM"
                else:
                    boot_device="Disk"
                info_list.append(dict(name='Boot Device',value=boot_device))
        elif type=='TEMPLATE_INFO':
                template_info=dom.get_template_info()
                info_list.append(dict(name='Name',value=template_info["template_name"]))
                info_list.append(dict(name='Version',value=template_info['template_version']+""+\
                                        template_info['version_comment']))
#                info_list.append(dict(name='Provisioned on',value="2009-11-5 6:38:24"))
#                info_list.append(dict(name='Provisioned by',value="admin"))
        elif type=='DISPLAY':
                info_list.append(dict(name='VNC',value=get_string_status(config["vnc"])))
                info_list.append(dict(name='Use Unused Display',value=get_string_status(config["vncunused"])))
                info_list.append(dict(name='SDL',value=get_string_status(config["sdl"])))
                info_list.append(dict(name='Standard Vga',value=get_string_status(config["stdvga"])))
        elif type=='USB_DEVICE':
                info_list.append(dict(name='USB Enabled',value=get_string_status(config["usb"])))
                info_list.append(dict(name='USB Device',value=config['usbdevice']))
        elif type=='ADVANCED':
                info_list.append(dict(name='Architecture Lib directory',value=config["arch_libdir"]))
                info_list.append(dict(name='UUID',value=config["uuid"]))
                info_list.append(dict(name='Platform',value=config["platform"]))
                info_list.append(dict(name='Network Mode',value=config["network_mode"]))
                info_list.append(dict(name='Shadow Memory',value=config["shadow_memory"]))

                info_list.append(dict(name='PAE',value=get_string_status(config["pae"])))
                info_list.append(dict(name='ACPI',value=get_string_status(config["acpi"])))
                info_list.append(dict(name='APIC',value=get_string_status(config["apic"])))
                info_list.append(dict(name='Architecture',value=config["arch"]))
                info_list.append(dict(name='Device Model',value=config["device_model"]))
                info_list.append(dict(name='Builder',value=config["builder"]))


        return info_list

    def vm_availability(self, auth, node_id):
        vm_ent=auth.get_entity(node_id)
        if vm_ent is None:
            return []

        result= []

        uptime=57
        downtime=38
        unknown=5
        result.append(dict(value= to_str(uptime), label= 'Up'))
        result.append(dict(value= to_str(downtime), label= 'Down'))
        result.append(dict(value= to_str(unknown), label= 'Unknown'))

        return result

    def vm_storage(self, auth, node_id):
        vm_ent=auth.get_entity(node_id)
        if vm_ent is None:
            return []

        result= []

        local=0.00
        shared=0.00
        ms=MetricsService()
        VMCurrInstance = ms.getVMCurrMetricsData(constants.VM_CURR, vm_ent, auth)
        if VMCurrInstance is not None:
            local=VMCurrInstance.gb_local
            shared=VMCurrInstance.gb_poolused
            #tot=VMCurrInstance.gb_pooltotal

        if local==0 and shared==0:
            result.append(dict(value= to_str(0), label= 'No Storage used'))
        else:
            result.append(dict(value= to_str("%6.2f" %local), label= 'Local'))
            result.append(dict(value= to_str("%6.2f" %shared), label= 'Shared'))

        return result


    def dashboard_vm_info(self, auth, node_id, type, canned ):

        result=[]        

        if canned in [constants.TOP50BYCPUVM,constants.TOP50BYMEMVM,constants.DOWNVM,constants.RUNNINGVM,None]:
            filter=canned
        else:
            filter=self.get_custom_search(auth,canned,constants.VMS)

        result=self.dashboard_vms_canned_search(auth, node_id, type,filter)
        return result
    

    def get_vm_ids(self, auth, node_id,node_type):

        vm_ids=[]
        if node_type==constants.DATA_CENTER:
            group_list = self.manager.getGroupList(auth)
            for group in group_list:
                group_entity = auth.get_entity(group.id)
                nodes=[]
                nodes=group_entity.children
                if nodes != []:
                    for node_entity in nodes:
                        vms= node_entity.children
                        if vms != []:
                            tmp_ids = [vm_ent.entity_id for vm_ent in vms]
                            vm_ids.extend(tmp_ids)


        elif node_type==constants.SERVER_POOL:
            group_entity = auth.get_entity(node_id)
            nodes=[]
            nodes=group_entity.children
            if nodes != []:
                for node_entity in nodes:
                    vms= node_entity.children
                    print vms
                    if vms != []:
                        tmp_ids = [vm_ent.entity_id for vm_ent in vms]
                        vm_ids.extend(tmp_ids)

        elif node_type==constants.MANAGED_NODE:
            node_entity=auth.get_entity(node_id)
            vms= node_entity.children
            if vms != []:
                vm_ids = [vm_ent.entity_id for vm_ent in vms]

        return vm_ids


    def dashboard_vms_canned_search(self, auth, node_id, node_type, canned):
        
        vm_ids=self.get_vm_ids(auth, node_id, node_type)
        
        ms = MetricsService()
        class_name = ms.getClassfromMetricType(constants.VM_CURR)
        query=DBSession.query(class_name).filter(class_name.entity_id.in_(vm_ids))
        
            
        if canned==constants.TOP50BYCPUVM:
            query=query.order_by(class_name.cpu_util.desc())
            

        elif canned ==constants.TOP50BYMEMVM:
            query=query.order_by(class_name.mem_util.desc())
            

        elif canned == constants.DOWNVM:
            query=query.join((AvailState,AvailState.entity_id==class_name.entity_id)).\
                    join((VM,VM.id==class_name.entity_id))
            query=query.filter(AvailState.avail_state == VM.SHUTDOWN)

        elif canned ==constants.RUNNINGVM:
            query=query.join((AvailState,AvailState.entity_id==class_name.entity_id)).\
                    join((VM,VM.id==class_name.entity_id))
            query=query.filter(AvailState.avail_state != VM.SHUTDOWN)

        elif canned is None:
           query=query.order_by(class_name.cpu_util.desc())
           

        else:            
            query=self.get_custom_query(query,class_name,canned ,constants.VMS)
            limit=canned.max_count


        try:
            if limit is None:
                limit=int(tg.config.get(constants.CUSTOM_SEARCH_LIMIT))
        except Exception, e:
            limit=50
            
        query=query.limit(limit)
        results=query.all()        
       
        info_list=[]
        for result in results:            
            dict=self.get_vm_metric_list(auth,result)
            info_list.append(dict)
         
        return info_list


    def test_vm_custom_search(self,auth,node_id,node_type,value):       
        
        vm_ids = self.get_vm_ids(auth, node_id, node_type)

        ms = MetricsService()
        class_name = ms.getClassfromMetricType(constants.VM_CURR)
        query=DBSession.query(class_name).filter(class_name.entity_id.in_(vm_ids))

        query = self.get_custom_query(query,class_name,None,constants.VMS,test_condn_val=value)
        query=query.limit(200)
        results=query.all()

        if results == []:
            msg="Custom search query executed successfully, but the resultset is empty."
        else:
            msg="Custom search query executed successfully."
        return msg

    def get_vm_metric_list(self,auth,result):
        
        metric={}

        metric['CPU(%)']=result.cpu_util
        metric['MEM(%)']=result.mem_util
        metric['VBDS']=result.vbds
        metric['VBD_OO']=result.vbd_oo
        metric['VBD_RD']=result.vbd_rd
        metric['VBD_WR']=result.vbd_wr
        metric['NETS']=result.nets
        metric['NETTX(k)']=result.nets_tx
        metric['NETRX(k)']=result.nets_rx
        metric['NODE_ID']=result.entity_id
        metric['VM_LOCAL_STORAGE']=result.gb_local
        metric['VM_SHARED_STORAGE']=result.gb_poolused
        metric['VM_TOTAL_STORAGE']=result.gb_pooltotal
        dom=self.manager.get_dom(auth,metric['NODE_ID'])
        metric['NAME']=dom.name
        # added newly to test
        metric['NODE_NAME']= dom.name
        metric['SSID']= '0'
        metric['CPU(sec)']= '1'
        metric['MAXMEM(%)']= '6.3'
        metric['MEM(k)']= '262068'
        metric['NODE_TYPE']= constants.DOMAIN
        metric['MAXMEM(k)']= '262144'
        metric['VCPUS']= '1'
        metric['DISPLAY']= '1'
        
        #-----------------------------------------------------------------------
        metric['name']=metric['NAME']
        entity = auth.get_entity(dom.id)
        metric['server']=entity.parents[0].name
        metric['cpu']=metric['CPU(%)']
        metric['mem']=metric['MEM(%)']
        (shared_usage, local_usage) = StorageManager().get_storage_size(metric['NODE_ID'])
        metric['storage'] = to_str(local_usage) + "/" + to_str(shared_usage)
        metric['network']=to_str(metric.get('NETS',0))+"/"+\
            to_str(metric.get('NETRX_k',0))+"/"+to_str(metric.get('NETTX_k',0))
        metric['io']=to_str(metric.get('VBDS',0))+"/"+\
            to_str(metric.get('VBD_OO',0))+"/"+to_str(metric.get('VBD_RD',0))+"/"+to_str(metric.get('VBD_WR',0))
        metric['node_id']=metric['NODE_ID']        
        metric['state']=to_str(dom.current_state.avail_state)
        os_info=dom.get_os_info()
        metric['os']=os_info.get('name',"")+" "+to_str(os_info.get('version',""))

        template_info=dom.get_template_info()
        metric['template']=template_info['template_name']
        metric['template_version']=template_info['template_version']
        metric['template_updates']=template_info['version_comment']
        
        return metric



    def dashboard_vm_information(self, auth, node_id, type, canned):
        info_list=[]
        metric_dict={}        

        if type==constants.DATA_CENTER:
            group_list = self.manager.getGroupList(auth)
            for group in group_list:
                node_list = self.manager.getNodeList(auth,group.id)
                for node in node_list:
                    metrics_list=self.getCurrentMetrics(auth, node)
                    metric_dict[node.hostname]=metrics_list

        elif type==constants.SERVER_POOL:
            group=self.manager.getGroup(auth, node_id)
            node_list = self.manager.getNodeList(auth,group.id)
            for node in node_list:
                metrics_list=self.getCurrentMetrics(auth, node)
                metric_dict[node.hostname]=metrics_list

        elif type==constants.MANAGED_NODE:            
            node=self.manager.getNode(auth,node_id)
            ent=auth.get_entity(node_id)
            groupId = ent.parents[0].entity_id
            metrics_list=self.getCurrentMetrics(auth, node)
            metric_dict[node.hostname]=metrics_list

        for (server,metrics_list) in metric_dict.iteritems():            
            for metric in metrics_list:                
                metric['id']=metric.get('ID',"?")
                shared_usage=0.00
                local_usage=0.00
                ss = DBSession.query(Storage_Stats).filter_by(entity_id=metric['NODE_ID']).first()
                if ss:
                    shared_usage = ss.shared_storage_at_VM
                    local_usage = ss.local_storage_at_VM

                metric['name']=metric['NAME']
                metric['server']=server
                metric['state']=metric['STATE']
                metric['cpu']=metric['CPU(%)']
                metric['mem']=metric['MEM(%)']
                metric['storage'] = to_str(local_usage) + "/" + to_str(shared_usage)
                metric['network']=to_str(metric.get('NETS',0))+"/"+\
                    to_str(metric.get('NETRX_k',0))+"/"+to_str(metric.get('NETTX_k',0))
                metric['io']=to_str(metric.get('VBDS',0))+"/"+\
                    to_str(metric.get('VBD_OO',0))+"/"+to_str(metric.get('VBD_RD',0))+"/"+to_str(metric.get('VBD_WR',0))
                metric['node_id']=metric['NODE_ID']
                dom=self.manager.get_dom(auth,metric['NODE_ID'])

                os_info=dom.get_os_info()
                metric['os']=os_info.get('name',"")+" "+to_str(os_info.get('version',""))
                
                template_info=dom.get_template_info()
                metric['template']=template_info['template_name']
                metric['template_version']=template_info['template_version']
                metric['template_updates']=template_info['version_comment']
                info_list.append(metric)
        return info_list

    def dashboard_server_info(self, auth, node_id, type,canned):

        result=[]
        if canned in [constants.TOP50BYCPU,constants.TOP50BYMEM,constants.DOWNSERVERS,constants.STANDBYSERVERS,None]:
            filter=canned
        else:
            filter=self.get_custom_search(auth,canned,constants.SERVERS)

        result=self.dashboard_server_canned_search(auth, node_id, type,filter)
        return result


    def get_server_ids(self, auth, node_id, node_type):
        srvr_ids = []
        if node_type==constants.DATA_CENTER:
            group_list = self.manager.getGroupList(auth)
            for group in group_list:
                group_entity = auth.get_entity(group.id)
                tmp_ids = [srvr_ent.entity_id for srvr_ent in group_entity.children]
                srvr_ids.extend(tmp_ids)
        elif node_type==constants.SERVER_POOL:
            group_entity = auth.get_entity(node_id)
            srvr_ids = [srvr_ent.entity_id for srvr_ent in group_entity.children]

        return srvr_ids

    def dashboard_server_canned_search(self, auth, node_id, node_type,canned):

        srvr_ids = self.get_server_ids(auth, node_id, node_type)

        ms = MetricsService()
        class_name = ms.getClassfromMetricType(constants.SERVER_CURR)
        query=DBSession.query(class_name).filter(class_name.entity_id.in_(srvr_ids))

        
        if canned==constants.TOP50BYCPU:
            query=query.order_by(class_name.host_cpu.desc())
            

        elif canned ==constants.TOP50BYMEM:
            query=query.order_by(class_name.host_mem.desc())
            

        elif canned == constants.DOWNSERVERS:
            query=query.join((AvailState,AvailState.entity_id==class_name.entity_id)).\
                    join((ManagedNode,ManagedNode.id==class_name.entity_id))
            query=query.filter(AvailState.avail_state == ManagedNode.DOWN)

        elif canned == constants.STANDBYSERVERS:
            query=query.join((ManagedNode,ManagedNode.id==class_name.entity_id))
            query=query.filter(ManagedNode.standby_status == ManagedNode.STANDBY)

        elif canned is None:
            query=query.order_by(class_name.host_cpu.desc())

        else:
            result={}
            query=self.get_custom_query(query,class_name,canned ,constants.SERVERS)
            limit=canned.max_count


        try:
            if limit is None:
                limit=int(tg.config.get(constants.CUSTOM_SEARCH_LIMIT))
        except Exception, e:
            limit=50
            
        query=query.limit(limit)
        results=query.all()

        info_list=[]
        for result in results:
            dict={}
            dict=self.get_server_metric_list(auth,result,node_type)
            info_list.append(dict)        
     
        return info_list


    def test_server_custom_search(self, auth, node_id, node_type,value):

        srvr_ids = self.get_server_ids(auth, node_id, node_type)

        ms = MetricsService()
        class_name = ms.getClassfromMetricType(constants.SERVER_CURR)
        query=DBSession.query(class_name).filter(class_name.entity_id.in_(srvr_ids))

        query = self.get_custom_query(query,class_name,None,constants.SERVERS,test_condn_val=value)

        query=query.limit(200)
        results=query.all()

        if results == []:
            msg="Custom search query executed successfully, but the resultset is empty."
        else:
            msg="Custom search query executed successfully."

        return msg


    def get_server_metric_list(self,auth,result,node_type=None):
        
        metric_dict={}
        node_entity=auth.get_entity(result.entity_id)
        group=node_entity.parents[0]
#        site_id = group.parents[0].entity_id
#        strge_size = StorageService().get_total_storage(auth,site_id,group.id,constants.SCOPE_DC)
        node=DBSession.query(ManagedNode).filter(ManagedNode.id==result.entity_id).first()
#                metric_dict=self.getServerCurrentMetrics(auth,node)

        metric_dict['VM_TOTAL_CPU(%)'] = result.cpu_util
        metric_dict['VM_TOTAL_MEM(%)'] = result.mem_util
        metric_dict['VM_TOTAL_VBDS'] = result.vbds
        metric_dict['VM_TOTAL_VBD_OO'] = result.vbd_oo
        metric_dict['VM_TOTAL_VBD_RD'] = result.vbd_rd
        metric_dict['VM_TOTAL_VBD_WR'] = result.vbd_wr
        metric_dict['VM_TOTAL_NETS'] = result.nets
        metric_dict['VM_TOTAL_NETTX(k)'] = result.nets_tx
        metric_dict['VM_TOTAL_NETRX(k)'] = result.nets_rx
        metric_dict['VM_LOCAL_STORAGE'] = result.gb_local
        metric_dict['VM_SHARED_STORAGE'] = result.gb_poolused
        metric_dict['VM_TOTAL_STORAGE'] = result.gb_pooltotal
        metric_dict['PAUSED_VMs'] = result.paused_vms
        metric_dict['RUNNING_VMs'] = result.running_vms
        metric_dict['CRASHED_VMs'] = result.crashed_vms
#        metric_dict['VER'] = node_ver #result[17] # get xen version
        metric_dict['VM_TOTAL_MEM'] = result.total_mem
        metric_dict['VM_TOTAL_CPU'] = result.total_cpu
        metric_dict['TOTAL_VMs'] = result.total_vms
        metric_dict['SERVER_CPUs'] = result.server_cpus
        metric_dict['SERVER_MEM'] = result.server_mem
        metric_dict['HOST_MEM(%)'] = result.host_mem
        metric_dict['HOST_CPU(%)'] = result.host_cpu
        childnode=NodeService().get_childnodestatus(auth,node.id)
        metric_dict["NODE_CHILDREN"]=childnode
        #-------------------------------------------------------------
        metric_dict['serverpool']=group.name
        metric_dict['name']=node.hostname    
        metric_dict['mem']=result.host_mem
        """
        usage = StorageManager().get_storage_usage_for_server(node_entity)
        if strge_size:
            metric_dict['storage']=(100 * float(usage))/float(strge_size)
        else:
            metric_dict['storage']=0
        """
        strg_allocation = 0
        ss = DBSession.query(Storage_Stats).filter_by(entity_id=node_entity.entity_id, storage_id=None).first()
        if ss:
            if node_type == constants.DATA_CENTER:
                strg_allocation = ss.allocation_at_S_for_DC
            elif node_type == constants.SERVER_POOL:
                strg_allocation = ss.allocation_at_S_for_SP
        if strg_allocation:
            metric_dict['storage']=strg_allocation
        else:
            metric_dict['storage']=0

        metric_dict['NODE_STATUS']=result.state
        metric_dict['NODE_NAME']=node.hostname
        vm_ids=auth.get_entity_ids(to_unicode(constants.DOMAIN),parent= node_entity)
        avail_state = DBSession.query(func.count(AvailState.entity_id),AvailState.avail_state).\
                    filter(AvailState.entity_id.in_(vm_ids)).group_by(AvailState.avail_state).all()
        tot=0
        runn=0
        paused=0
        crshed=0
        for avm in avail_state:
            tot+=avm[0]
            if avm[1] in [VM.RUNNING,VM.UNKNOWN]:
                runn+=avm[0]
            elif avm[1]==VM.PAUSED:
                paused+=avm[0]
            elif avm[1] in [VM.CRASHED]:
                crshed+=avm[0]

        metric_dict['vmsummary']=to_str(tot)+"/"+to_str(runn)+"/"+to_str(paused)+"/"+to_str(crshed)
        metric_dict['platform']=constants.platforms[node.platform]
        metric_dict['NODE_TYPE']=constants.MANAGED_NODE
        metric_dict['NODE_ID']=node.id
        metric_dict['io']=to_str(self.check_none(metric_dict.get('VM_TOTAL_VBDS',0)))+"/"+\
                to_str(self.check_none(metric_dict.get('VM_TOTAL_VBD_OO',0)))+"/"+to_str(self.check_none(metric_dict.get('VM_TOTAL_VBD_RD',0)))+\
                "/"+to_str(self.check_none(metric_dict.get('VM_TOTAL_VBD_WR',0)))
        metric_dict['NODE_PLATFORM']=constants.platforms[node.platform]
        os=node.get_os_info()
        metric_dict['os']=os.get('distro_string',"")
        metric_dict['cpu']=result.host_cpu
        metric_dict['node_id']=node.id
        metric_dict['network']=to_str(self.check_none(metric_dict.get('VM_TOTAL_NETS',0)))+"/"+\
            to_str(self.check_none(metric_dict.get('VM_TOTAL_NETRX_k',0)))+"/"+to_str(self.check_none(metric_dict.get('VM_TOTAL_NETTX_k',0)))

        return metric_dict


    def check_none(self,value):
        if value is None:
            value="?"
        return value

    def dashboard_serverpool_info(self, auth, node_id, type):
        info_list=[]
        metric_dict={}
        if type==constants.DATA_CENTER:
            group_list = self.gather_info_for_pool(auth,type,node_id)
            metric_dict[constants.DATA_CENTER]=group_list

        for (dc,metrics_list) in metric_dict.iteritems():
            for metric in metrics_list:
                metric['name']=metric['NODE_NAME']
                #metric['dc']=dc
                metric['vmsummary']=to_str(metric.get('TOTAL_VMs',0))+"/"+\
                    to_str(metric.get('RUNNING_VMs',0))+"/"+to_str(metric.get('PAUSED_VMs',0))+"/"+to_str(metric.get('CRASHED_VMs',0))
                metric['cpu']=metric['VM_TOTAL_CPU(%)']
                metric['mem']=metric['VM_TOTAL_MEM(%)']
                metric['storage']=to_str(metric.get('VM_SHARED_STORAGE',0.00))+"/"+\
                    to_str(metric.get('POOL_STORAGE_TOTAL',0.00))
                metric['network']=to_str(metric.get('VM_TOTAL_NETS',0))+"/"+\
                    to_str(metric.get('VM_TOTAL_NETRX_k',0))+"/"+to_str(metric.get('VM_TOTAL_NETTX_k',0))
                metric['io']=to_str(metric.get('VM_TOTAL_VBDS',0))+"/"+\
                    to_str(metric.get('VM_TOTAL_VBD_OO',0))+"/"+to_str(metric.get('VM_TOTAL_VBD_RD',0))+\
                    "/"+to_str(metric.get('VM_TOTAL_VBD_WR',0))
                metric['node_id']=metric['NODE_ID']
                info_list.append(metric)
        return info_list

    def get_updated_tasks(self,user_name):
        try:
            updatemgr=UIUpdateManager()
            updated_tasks=updatemgr.get_updated_tasks(user_name)
#            updatemgr.clear_updated_tasks(user_name)
            
            if updated_tasks:
                task=Userinfo().get_task_details(updated_tasks)
                return task

        except Exception,ex:
            LOGGER.error(to_str(ex).replace("'",""))
            print_traceback()
            raise ex

    def get_custom_search_list(self,auth,node_level,lists_level):
       
        try:
            result=[]
            
            customs=DBSession.query(CustomSearch).filter(CustomSearch.node_level==node_level).\
                        filter(CustomSearch.lists_level==lists_level).order_by(CustomSearch.name.asc()).all()
                            
            for custom in customs:
                if node_level == constants.DATA_CENTER:
                    level="Data Center"
                elif node_level==constants.SERVER_POOL:
                    level="Server Pool"
                else:
                    level="Server"
                result.append(dict(id=custom.id,name=custom.name,user_name=custom.user_name,\
                            created_date=convert_to_CMS_TZ(custom.created_date),\
                            modified_date=convert_to_CMS_TZ(custom.modified_date),\
                            desc=custom.description,condition=custom.condition,level=level,max_count=custom.max_count))
            return result
            
        except Exception, ex:
            traceback.print_exc()
            raise ex

    def get_custom_search(self,auth,name,lists_level):
        try:
            
            custom=DBSession.query(CustomSearch).filter(CustomSearch.name==name).\
                        filter(CustomSearch.lists_level==lists_level).first()
            return custom
        except Exception, ex:
            traceback.print_exc()
            raise ex    

    def get_canned_custom_list(self,auth,node_level,lists_level):
        try:
            info=[]

            if lists_level == constants.VMS:
                info.append(dict(value=constants.DOWNVM))
                info.append(dict(value=constants.RUNNINGVM))
                info.append(dict(value=constants.TOP50BYCPUVM))
                info.append(dict(value=constants.TOP50BYMEMVM))                
            elif lists_level == constants.SERVERS:
                info.append(dict(value=constants.DOWNSERVERS))
#                info.append(dict(value=constants.STANDBYSERVERS))
                info.append(dict(value=constants.TOP50BYCPU))
                info.append(dict(value=constants.TOP50BYMEM))               

#            info.append(dict(value="------------------------------------"))

            custom_list=self.get_custom_search_list(auth,node_level,lists_level)
            for custom in custom_list:
                info.append(dict(value=custom['name']))
            return info

        except Exception, ex:
            traceback.print_exc()
            raise ex

    def get_filter_forsearch(self,auth):
        try:
            info=[]            
            info.append(dict(value='=='))
            info.append(dict(value='<='))
            info.append(dict(value='>='))
            info.append(dict(value='<'))
            info.append(dict(value='>'))
            info.append(dict(value='like'))
            return info
      
        except Exception, ex:
            traceback.print_exc()
            raise ex


    def get_property_forsearch(self,auth,node_id,node_type,listlevel):
        try:
            info=[]          
#            info.append(dict(value=constants.CPUUTIL_VALUE,text=constants.CPUUTIL_TEXT))
#            info.append(dict(value=constants.MEMUTIL_VALUE,text=constants.MEMUTIL_TEXT))
#            info.append(dict(value=constants.STRGUTIL_VALUE,text=constants.STRGUTIL_TEXT))

            if listlevel == constants.VMS:
                info.append(dict(value=constants.CPUUTIL_VALUE,text=constants.VM_CPUUTIL_TEXT))
                info.append(dict(value=constants.MEMUTIL_VALUE,text=constants.VM_MEMUTIL_TEXT))
                info.append(dict(value=constants.STRGUTIL_VALUE,text=constants.VM_STRGUTIL_TEXT))
                if node_type in [constants.DATA_CENTER,constants.SERVER_POOL]:
                    info.append(dict(value=constants.SRVR_NAME_VALUE,text=constants.SRVR_NAME_TEXT))
                if node_type in [constants.DATA_CENTER]:
                    info.append(dict(value=constants.SP_VALUE,text=constants.SP_TEXT))
                info.append(dict(value=constants.OS_VALUE,text=constants.OS_TEXT))
                info.append(dict(value=constants.TEMPLATE_VALUE,text=constants.TEMPLATE_TEXT))
                info.append(dict(value=constants.VM_NAME_VALUE,text=constants.VM_NAME_TEXT))
                info.append(dict(value=constants.VM_STATUS_VALUE,text=constants.VM_STATUS_TEXT))
            elif listlevel == constants.SERVERS:
                info.append(dict(value=constants.CPUUTIL_VALUE,text=constants.CPUUTIL_TEXT))
                info.append(dict(value=constants.MEMUTIL_VALUE,text=constants.MEMUTIL_TEXT))
                info.append(dict(value=constants.STRGUTIL_VALUE,text=constants.STRGUTIL_TEXT))
                if node_type == constants.DATA_CENTER:
                    info.append(dict(value=constants.SP_VALUE,text=constants.SP_TEXT))
                info.append(dict(value=constants.PLTFM_VALUE,text=constants.PLTFM_TEXT))
                info.append(dict(value=constants.SRVR_NAME_VALUE,text=constants.SRVR_NAME_TEXT))
                info.append(dict(value=constants.SRVR_STATUS_VALUE,text=constants.SRVR_STATUS_TEXT))
#                info.append(dict(value=constants.SB_VALUE,text=constants.SB_TEXT))


            return info

        except Exception, ex:
            traceback.print_exc()
            raise ex

    def save_custom_search(self,auth,name,desc,condition,node_id,level,lists_level,max_count):      

        try:
            custom_search=DBSession.query(CustomSearch).filter(CustomSearch.name==name).first()
            if custom_search == None:
                custom=CustomSearch()
                custom.name=name
                custom.user_name=auth.user.user_name
                custom.description=desc
                custom.condition=condition
                custom.node_level=level
                custom.lists_level=lists_level
                if max_count:
                    custom.max_count=max_count
                custom.created_date=datetime.utcnow()
                custom.modified_date=datetime.utcnow()

                DBHelper().add(custom)

                return True
            else:
                raise Exception("Custom Search with name "+name+" already exists.")

        except Exception, ex:
            traceback.print_exc()
            raise ex


    def edit_save_custom_search(self,auth,name,desc,condition,max_count):

        try:
            custom=DBSession.query(CustomSearch).filter(CustomSearch.name==name).first()
            custom.description=desc
            custom.condition=condition
            custom.max_count=max_count
            custom.modified_date=datetime.utcnow()
            DBHelper().update(custom)

            return True
        except Exception, ex:
            traceback.print_exc()
            raise ex


    def delete_custom_search(self,auth,name):
        try:
            custom_search=DBSession.query(CustomSearch).filter(CustomSearch.name==name).first()
            if custom_search:
                DBHelper().delete_all(CustomSearch,[],[CustomSearch.name==name])

        except Exception, ex:
            traceback.print_exc()
            raise ex

    def test_newcustom_search(self,auth,name,value, node_id, type ,listlevel):

        if listlevel == constants.SERVERS:
            result=self.test_server_custom_search(auth,node_id, type,value)
        elif listlevel == constants.VMS:
            result=self.test_vm_custom_search(auth,node_id, type,value)
        return result

    def get_custom_query(self,query,class_name,custom,lists_level,test_condn_val=""):

        if custom:
            description=custom.condition
        else:
            description=test_condn_val

        joins=[]
        filters=[]
        DESC=description.split(',')
        for dsc in DESC:
            dsc=to_str(dsc)
            if dsc == "\n":
                pass
            else:
                DEC=dsc.split(' ')                
                if DEC !=['']:                            
                    conditions=self.custom_search.make_query(class_name,DEC,DEC[0],lists_level)

                    for filter in conditions['filters']:
                        filters.append(filter)

                    for join in conditions['joins']:
                        if join not in joins:
                            joins.append(join)                   

                    
        for filter in filters:
            query=query.filter(filter)

        for join in joins:
             query=query.join(join)
        return query
        
"""
DashboardInfo is created specifically to convert the structure to xml doc.
Right now it works on list of nested dictionary.
for example:
[{...}
 {...}
 {... { }
      { }}]
"""
class DashboardInfo:
    def __init__(self, data):
        self.data = data

    def toXml(self, doc):
        xmlNode = doc.createElement("DashboardInfo")

        if self.data is None:
            pass
        else:
            for item in self.data:
                xmlNode.appendChild(self.make_info_node(item, doc))

        return xmlNode;

    def make_info_node(self, item, doc):
        resultNode = doc.createElement("InfoNode");

        keys = item.keys()
        for key in keys:
            newData = item[key]
            if isinstance(newData, dict):
                resultNode.appendChild(self.make_info_node(newData, doc))
            else:
                resultNode.setAttribute(self.strip_attribute(key), to_str(newData))

        return resultNode;

    def strip_attribute(self, name):
        expr = re.compile('(\((\S*)\))');
        percentReg = re.compile('%');
        if (percentReg.search(name)):
            return expr.sub('_PERCENT', name)
        else:
            return expr.sub(r'_\2', name);

    def toJson(self):
        result=[]
        if self.data is None:
            pass
        else:
            for item in self.data:
                result.append(self.createDict(item))
        return result

    def createDict(self,item):
        for key in item.keys():
            newData = item[key]
            if isinstance(newData, dict):
                self.createDict(newData)
            else:
                item[self.strip_attribute(key)]=newData
        return item

