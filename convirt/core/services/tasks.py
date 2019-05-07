#!/usr/bin/env python
#
#   ConVirt   -  Copyright (c) 2009 Convirture Corp.
#   ======
#
# ConVirt is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at
#
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# 
#
# author : gizli
#    

from convirt.model.services import Task, TaskResult
from convirt.viewModel import Basic
from convirt.viewModel.NodeService import NodeService
from convirt.core.appliance import xva
from convirt.model.ImageStore import ImageUtils
from convirt.model.SyncDefinition import SyncDef
import convirt.core.utils.utils
from convirt.core.utils.constants import *
from convirt.model.Metrics import MetricsService
import logging,transaction,traceback,os,tg
from convirt.model import DBSession
from convirt.model.VM import VM
from convirt.model.Entity import Entity, EntityTasks
from convirt.model.ManagedNode import ManagedNode
import convirt.core.utils.constants as constants
from convirt.viewModel.StorageService import StorageService
from convirt.viewModel.NetworkService import NetworkService
from convirt.model.UpdateManager import AppUpdateManager        
from convirt.core.utils.utils import to_unicode,to_str, get_parent_task_status_info, \
                    get_child_task_status_info, p_task_timing_start,p_task_timing_end,notify_task_hung
from convirt.model.AvailabilityWorker import AvailabilityWorker
from convirt.model.VMAvailabilityWorker import VMAvailabilityWorker
from convirt.model.CollectMetricsWorker import CollectMetricsWorker
from datetime import datetime, timedelta


LOGGER = logging.getLogger("convirt.viewModel")
AVL_LOGGER = logging.getLogger("AVAIL_TIMING")
MTR_LOGGER = logging.getLogger("METRICS_TIMING")
WRK_LOGGER = logging.getLogger("WORKER")

def m_(string):
    return string

class NodeTask(Task):
    def get_node_id(self):
        return self.get_param('node_id')

    def get_dom_id(self):
        return self.get_param('dom_id')

    def get_dom_name(self):
        node_id = self.get_dom_id()
        name=node_id
        if node_id is not None:
            try:
                vm = DBSession.query(VM).filter(VM.id == node_id).one()
                name=vm.name
            except Exception, e:
                pass
            return name

    def get_node_name(self):
        node_id = self.get_node_id()
        name=node_id
        if node_id is not None:
            try:
                node = DBSession.query(ManagedNode).\
                        filter(ManagedNode.id == node_id).one()
                name=node.hostname
            except Exception, e:
                pass
            return name


class VMActionTask(NodeTask):
    def get_descriptions(self):
        action = self.get_param('action')
        dom_name = self.get_dom_name()
        node_name = self.get_node_name()
        short_desc = ""
        desc = ""
        if action == constants.START:
            short_desc = m_("Starting %s")
            desc = m_("Start action on %s. Managed Node is %s")
        elif action == constants.PAUSE:
            short_desc = m_("Pausing %s")
            desc = m_("Pause action on %s. Managed Node is %s")
        elif action == 'unpause':
            short_desc = m_("Resuming %s")
            desc = m_("Resume action on %s. Managed Node is %s")
        elif action == constants.REBOOT:
            short_desc = m_("Rebooting %s")
            desc = m_("Reboot action on %s. Managed Node is %s")
        elif action == constants.KILL:
            short_desc = m_("Killing %s")
            desc = m_("Kill action on %s. Managed Node is %s")
        elif action == constants.SHUTDOWN:
            short_desc = m_("Shutting down %s")
            desc = m_("Shutdown action on %s. Managed Node is %s")
        return (short_desc, (dom_name,), desc, (dom_name, node_name))

    def exec_task(self, auth, ctx, dom_id, node_id, action):
        manager = Basic.getGridManager()
        return manager.do_dom_action(auth, dom_id, node_id, action)

    def resume_task(self, auth, ctx, dom_id, node_id, action):
        try:
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            if node is None:
                raise Exception("Can not find the managed node for "+node_id)
            dom = DBSession.query(VM).filter(VM.id == dom_id).first()
            if dom is None:
                raise Exception("Can not find the virtual machine for "+dom_id)
            dom.node = node
            values=dom.get_state_dict()[action]
            status = dom.check_state(values, 1)
            if status == False:
                raise Exception(action +" failed due to timeout.")
            return status
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, dom_id, node_id, action):
        try:
            return self.resume_task(auth, ctx, dom_id, node_id, action)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)


class ServerActionTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        action = self.get_param('action')
        short_desc = ""
        if action == 'start_all':
            short_desc = m_("Starting all Virtual Machines on %s")
        elif action == 'shutdown_all':
            short_desc = m_("Shutting down all Virtual Machines on %s")
        elif action == 'kill_all':
            short_desc = m_("Killing all VMs on %s")
        return (short_desc, (node_name,), short_desc, (node_name,))


    def exec_task(self, auth, ctx, node_id, action):
        manager = Basic.getGridManager()
        managed_node = manager.getNode(auth, node_id)
        if managed_node is not None:
            if not managed_node.is_authenticated():
                managed_node.connect()
            return manager.do_node_action(auth, node_id, action)
        else:
            raise Exception("Can not find the managed node")

class RemoveServerTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_param('node_name')
        grp_name = self.get_param('grp_name')
        short_desc = ""
        desc = ""

        short_desc = m_("Remove %s")
        desc = m_("Removing Server %s on Server Pool %s.")

        return (short_desc, (node_name), desc, (node_name, grp_name))

    def exec_task(self, auth, ctx, node_id, **kw):
        manager = Basic.getGridManager()
        return manager.removeNode(auth, node_id, kw.get("force", False))

    def resume_task(self, auth, ctx, node_id, **kw):
        try:
            return self.exec_task(auth, ctx, node_id, **kw)
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, node_id, **kw):
        try:
            return self.exec_task(auth, ctx, node_id, **kw)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

class VMMigrateTask(NodeTask):
    def get_descriptions(self):
        source_node=self.get_param('source_node_id')
        dest_node=self.get_param('dest_node_id')
        migrate_vm=self.get_param('all')
        vmName=''
        if migrate_vm==False:
            doms=self.get_param('dom_list')
            dom=DBSession.query(Entity).filter_by(entity_id=doms[0]).one()
            if dom:
                vmName=dom.name
        else:
             vmName='All Virtual Machines'
        sname=source_node
        dname=dest_node
        sent=DBSession.query(Entity).filter_by(entity_id=source_node).one()
        if sent:
            sname=sent.name
        dent=DBSession.query(Entity).filter_by(entity_id=dest_node).one()
        if dent:
            dname=dent.name
        short_desc = m_("Migrate %s from %s to %s")#m_("Migrate %s")
        desc = m_("Migrate %s from %s to %s")
        return (short_desc, (vmName,sname,dname), desc, (vmName,sname,dname))

    def get_source_node_id(self):
        return self.get_param('source_node_id')

    def get_dest_node_id(self):
        return self.get_param('dest_node_id')

    def get_entity_ids(self):
        entity_ids=""
        entity_ids+=self.get_source_node_id()
        entity_ids+=","+self.get_dest_node_id()
        return entity_ids

    def exec_task(self, auth, ctx, dom_list, source_node_id,\
                   dest_node_id, live, force, all):
        manager = Basic.getGridManager()
        return manager.migrate_vm(auth, dom_list, source_node_id,\
                                  dest_node_id, live, force, all)

    def resume_task(self, auth, ctx, dom_list, source_node_id,\
                   dest_node_id, live, force, all):
        try:
            manager = Basic.getGridManager()
            return manager.resume_migrate_vm(auth, dom_list, source_node_id,\
                                      dest_node_id, live, force, all)
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, dom_list, source_node_id,\
                   dest_node_id, live, force, all):
        try:
            manager = Basic.getGridManager()
            return manager.resume_migrate_vm(auth, dom_list, source_node_id,\
                                      dest_node_id, live, force, all,\
                                      recover=True)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

class VMConfigSettingsTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        vm_name = self.get_vm_name()
        mode=self.get_param('mode')
        if mode == "PROVISION_VM":
            short_desc = m_("Provisioning %s")
            desc = m_("Provisioning %s onto %s")
        elif mode == "EDIT_VM_INFO":
            short_desc = m_("Change Settings of %s")
            desc = m_("Change In Memory Settings of %s %s")
        return (short_desc, (vm_name,), desc, (vm_name, node_name))

    def exec_task(self, auth, ctx, image_id, config, mode, node_id, group_id,\
                  dom_id, vm_name):
        return NodeService().vm_config_settings(auth, image_id, config, mode, \
                                         node_id, group_id, dom_id, vm_name)
        
    def get_vm_name(self):
        return self.get_param('vm_name')
    
    def resume_task(self, auth, ctx, image_id, config, mode, node_id, group_id,\
              dom_id, vm_name,cli,memory,vcpu):

        if mode!="PROVISION_VM":
            raise Exception(constants.INCOMPLETE_TASK)

        ###TODO:disk cleanup
        vm = DBSession.query(VM).filter(VM.name==vm_name).first()
        if vm is None:
            raise Exception(constants.INCOMPLETE_TASK)

    def recover_task(self, auth, ctx, image_id, config, mode, node_id, group_id,\
                  dom_id, vm_name,cli,memory,vcpu):

        self.resume_task(auth, ctx, image_id, config, mode, node_id, group_id,\
                  dom_id, vm_name,cli,memory,vcpu)

    def get_vm_name(self):
        return self.get_param('vm_name')

class RefreshNodeInfoTask(Task):
    def get_descriptions(self):
        short_desc = m_("Refresh Task for All Nodes")
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        manager = Basic.getGridManager()
        groups = manager.getGroupList(auth)
        for group in groups:
            nodes = manager.getNodeList(auth, group.id)
            for n in nodes:
                try:
                    transaction.begin()
                    n=DBSession.query(ManagedNode).filter(ManagedNode.id==n.id).one()
                    n.refresh_environ()
                    n.get_running_vms()
                    n.socket=n.get_socket_info()
                    if n.is_up():
                        n.isHVM = n.is_HVM()
                    DBSession.add(n)
                    transaction.commit()
                except Exception, e:
                    LOGGER.error(to_str(e))
                    DBSession.rollback()
        ungrouped_nodes = manager.getNodeList(auth)
        for n in ungrouped_nodes:
            try:
                transaction.begin()
                n=DBSession.query(ManagedNode).filter(ManagedNode.id==n.id).one()
                n.refresh_environ()
                n.get_running_vms()
                n.socket=n.get_socket_info()
                DBSession.add(n)
                transaction.commit()
            except Exception, e:
                LOGGER.error(to_str(e))
                DBSession.rollback()

class PopulateNodeInfoTask(NodeTask):
    def get_descriptions(self):
        short_desc = m_("Populate Information Task for Node")
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx, node_id):
        manager = Basic.getGridManager()
        m_node = manager.getNode(auth, node_id)
        m_node._init_environ()

class Purging(Task):
    def get_descriptions(self):
        short_desc = m_("Purge Historical Data")
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for Purging task')
        MetricsService().purging_for_all_nodes(auth)
        #purge the task results
        #no need to catch exception since task service will log
        #and rollback in case of an exception
        import tg
        from datetime import datetime, timedelta
        purge_interval = tg.config.get("task_results_purge_interval")
        cutoff_date = datetime.utcnow() + timedelta(days=-int(purge_interval))
        DBSession.query(TaskResult).\
                filter(TaskResult.timestamp <= cutoff_date).\
                delete()
        #also purge the non-repeating tasks that were submitted long time
        #ago
	limit = 5000
	try:
	    limit=int(tg.config.get(constants.TASK_PURGE_COUNT))
	except Exception, e:
            print "Exception: ", e
        offset = 0

        while True:
            tasks=DBSession.query(Task).\
                    filter(Task.submitted_on <= cutoff_date).\
                    filter(Task.interval == None).\
                    filter(Task.calendar == None).order_by(Task.submitted_on.asc()).\
                    limit(limit).offset(offset).all()

            if len(tasks) == 0:
                break

            offset += limit

            for task in tasks:
                DBSession.delete(task)
            transaction.commit()

        #purge results entries of repeating tasks
        rept_purge_interval = tg.config.get("repeating_tasks_purge_interval")
        cutoff_date = datetime.utcnow() + timedelta(days=-int(rept_purge_interval))

        rpt_tasks = ['TimeBasisRollupForNodes','EmailTask']
        rpt_prvnt_tasks = ['CollectMetricsForNodes','NodeAvailTask','VMAvailTask']

        rpt_task = DBSession.query(Task.task_id).filter(Task.task_type.in_(rpt_tasks)).all()
        rpt_prvnt_task = DBSession.query(Task.task_id).filter(Task.task_type.in_(rpt_prvnt_tasks)).all()

        rpt_task_ids = [x.task_id for x in rpt_task]
        rpt_prvnt_task_ids = [x.task_id for x in rpt_prvnt_task]
        
        print rpt_task_ids,"=========XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX=========",rpt_prvnt_task_ids
        task_ids = rpt_task_ids + rpt_prvnt_task_ids

        DBSession.query(TaskResult).\
                filter(TaskResult.task_id.in_(task_ids)).\
                filter(TaskResult.timestamp <= cutoff_date).\
                delete()
        transaction.commit()

        #purge entries of child tasks of repeating tasks
        DBSession.query(TaskResult).\
                filter(TaskResult.task_id.in_(\
                        DBSession.query(Task.task_id).\
                        filter(Task.parent_task_id.in_(rpt_prvnt_task_ids)).\
                        filter(Task.submitted_on <= cutoff_date))\
                ).\
                delete()
        transaction.commit()
        
        DBSession.query(Task).\
                filter(Task.parent_task_id.in_(rpt_prvnt_task_ids)).\
                filter(Task.submitted_on <= cutoff_date).\
                delete()

        #task engine will commit


class CollectMetricsForNodes(Task):
    def get_descriptions(self):
        short_desc = m_("Collect data for all entities and update CURR and RAW tables")
        return (short_desc, (), short_desc, ())

    def get_status(self):
        return get_parent_task_status_info(self)

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec task for CollectMetricsForNodes task')
        strt = p_task_timing_start(MTR_LOGGER, "CollectMetricsForNodes", [])
        CollectMetricsWorker(auth).do_work()
        p_task_timing_end(MTR_LOGGER, strt)

    def resume_task(self, auth, ctx):
        try:
            CollectMetricsWorker(auth).resume_work(ctx)
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx):
        try:
            self.resume_task(auth, ctx)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

class WorkerTask(Task):

    def get_next_node_id(self, index):
        try:
            try:
                return self.exc_node_ids[index]
            except IndexError, e:
                return None
        finally:
            pass

    def get_running_status(self):
        max_wait_time=self.get_max_wait_time()
        
        WRK_LOGGER.debug("get_running_status : "+self.name)
        try:
            if (datetime.utcnow() - self.start_time).seconds > max_wait_time:
                WRK_LOGGER.error("Task, "+str(self.name)+":"+str(self.task_id) +\
                                " is hung on "+self.current_node.hostname)
                self.exc_node_ids = [self.current_node.id]
                
                self.mark_hung = True
                notify_task_hung(self,self.current_node)
                return (True, self.completed_nodes, self.pending_nodes )
        finally:           
            pass

        return (False, [], [])

    def check_if_hung(self):
        WRK_LOGGER.debug("Check if Task, "+self.name+" is hung? ")
        marked_hung = False
        try:
            marked_hung = self.mark_hung

            if marked_hung :
                WRK_LOGGER.debug("Task, "+self.name+"("+str(self.task_id)+") was marked hung. updating entity_tasks")
                DBSession.query(EntityTasks).\
                            filter(EntityTasks.worker_id==to_unicode(self.task_id)).\
                            update(dict(worker_id=None,finished=True, end_time=datetime.utcnow()))
#                transaction.commit()
        except AttributeError, e:
            pass

    def get_pending_node_ids(self, node_ids):
        #while resuming get node_ids which is still under process by the task
        #i.e. ignore the completed nodes and pending nodes(if the task was hung)
        ets = DBSession.query(EntityTasks.entity_id).\
                filter(EntityTasks.worker_id==to_unicode(self.task_id)).\
                filter(EntityTasks.entity_id.in_(node_ids)).all()
        node_ids=[et[0] for et in ets]
        WRK_LOGGER.debug("RESUMING CHILD WORKER . NodeIDS : "+str(node_ids))
        return node_ids
        
    def do_cleanup(self):
        #cleanup entity_tasks if any of the entries are still owned by me
        #so that next iteration will pick those up
        #make worker_id = null, finished = 1, endtime = utcnow()
        WRK_LOGGER.debug("Cleaning Up entity_tasks . task_id: "+str(self.task_id))
        r = DBSession.query(EntityTasks.entity_id).\
                filter(EntityTasks.worker_id==to_unicode(self.task_id)).\
                update(values=dict(worker_id=None,finished=True,end_time=datetime.utcnow()))
        WRK_LOGGER.debug("Cleaned Up entity_tasks . task_id:rows : "+str(self.task_id)+":"+str(r))

class CollectMetrics(WorkerTask):
    def get_descriptions(self):
        short_desc = m_("Collect data for all entities and update CURR and RAW tables")
        return (short_desc, (), short_desc, ())

    def get_status(self):        
        return get_child_task_status_info(self)

    def exec_task(self, auth, ctx,node_ids,sp_id):
        LOGGER.debug('entered in excec task for CollectMetricsForNodes task')
        strt = p_task_timing_start(MTR_LOGGER, "CollectMetrics", node_ids)
        try:
            manager = Basic.getGridManager()
            self.completed_nodes = []
            self.pending_nodes = [node_id for node_id in node_ids]
            self.exc_node_ids = [node_id for node_id in node_ids]
            index = 0
            node_id = self.get_next_node_id(index)
            while node_id is not None:
                self.pending_nodes.remove(node_id)
                m_node=DBSession.query(ManagedNode).filter(ManagedNode.id==node_id).one()
                index+=1
                node_id = self.get_next_node_id(index)
                if m_node is None :
                    continue
                self.current_node = m_node
                self.start_time = datetime.utcnow()
                try:
                    try:
                        strt1 = p_task_timing_start(MTR_LOGGER, "NodeGetMterics", m_node.id)
                        #call function to store the Server metrics into the database
                        node_snapshot=manager.collectServerMetrics(auth, m_node,filter=True)

                        #call function to store the VM metrics into the database table
                        manager.collectVMMetrics(auth, m_node.id, node_snapshot)
                        #collect metrics at serverpool level
                        manager.collectServerPoolMetrics(auth, sp_id)
                        DBSession.flush()
                        transaction.commit()
                        p_task_timing_end(MTR_LOGGER, strt1)
                    except Exception, e:
                        LOGGER.error("Error updating metrics . Server :"+m_node.hostname)
                        traceback.print_exc()
                finally:
                    self.completed_nodes.append(m_node.id)
        finally:
            self.check_if_hung()
            p_task_timing_end(MTR_LOGGER, strt)

    def resume_task(self, auth, ctx, node_ids,sp_id):
        try:
            self.do_cleanup()
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx,node_ids,sp_id):
        try:
            self.resume_task( auth, ctx,node_ids, sp_id)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

    def get_max_wait_time(self):
        try:
            max_node_metrics_wait_time=int(tg.config.get("max_node_metrics_wait_time"))
        except Exception, e:
            LOGGER.error("Exception: "+str(e))
            max_node_metrics_wait_time=90

        return max_node_metrics_wait_time

class TimeBasisRollupForNodes(Task):
    def get_descriptions(self):
        short_desc = m_("Metric Rollup")
        return (short_desc, (), short_desc, ())
    
    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec task for TimeBasisRollupForNodes task')
        MetricsService().timebasis_rollup_for_all_nodes(auth)


class VMSnapshotTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        short_desc = m_("Snapshot vm %s")
        return (short_desc, (node_name,), short_desc, (node_name))

    def exec_task(self, auth, ctx, dom_id, node_id, file, directory):
        manager = Basic.getGridManager()
        return manager.save_dom(auth, dom_id, node_id, file, directory)

class VMRestoreTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        short_desc = m_("Restoring vm to %s")
        return (short_desc, (node_name,), short_desc, (node_name))

    def exec_task(self, auth, ctx, node_id, file):
        manager = Basic.getGridManager()
        return manager.restore_dom(auth, node_id, file)    

class ImportApplianceTask(Task):
    def get_descriptions(self):
        pass

    def get_group_id(self):
        return self.get_param('group_id')

    def exec_task(self, auth, ctx, appliance_entry, image_store, group_id, \
                                image_name, platform, force):
        local_node = Basic.local_node
        if appliance_entry["type"].lower() == "xva":
            return xva.import_appliance(auth,local_node, appliance_entry, \
                                        image_store, group_id, image_name, \
                                        platform, force, None)
        else:
            return ImageUtils.import_fs(auth,local_node, appliance_entry, \
                                        image_store, group_id, image_name, \
                                        platform, force, None)

    def resume_task(self, auth, ctx, appliance_entry, image_store, group_id, \
                                image_name, platform, force):

        ###TODO:disk cleanup
        img = DBSession.query(Image).filter(Image.name==image_name).first()
        if img is None:
            raise Exception(constants.INCOMPLETE_TASK)

    def recover_task(self, auth, ctx, appliance_entry, image_store, group_id, \
                                image_name, platform, force):

        self.resume_task(auth, ctx, appliance_entry, image_store, group_id, \
                                image_name, platform, force)

class RefreshNodeMetricsTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        manager = Basic.getGridManager()
        groups = manager.getGroupList(auth)
        for group in groups:
            nodes = manager.getNodeList(auth, group.id)
            for n in nodes:
                manager.refreshNodeMetrics(auth,n)

        ungrouped_nodes = manager.getNodeList(auth)
        for n in ungrouped_nodes:
            manager.refreshNodeMetrics(auth,n)

class UpdateDeploymentStatusTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for UpdateDeploymentStatus Task')
        from convirt.core.utils.utils import update_deployment_status
        update_deployment_status()

class SendDeploymentStatsTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for SendDeploymentStats Task')
        from convirt.core.utils.utils import send_deployment_stats
        send_deployment_stats(True)

class SendDeploymentStatsRptTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for SendDeploymentStatsRptTask Task')
        from convirt.core.utils.utils import send_deployment_stats
        send_deployment_stats(False)

class CheckForUpdateTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for CheckForUpdate Task')
        AppUpdateManager().check_for_updates(True)

class NodeAvailTask(Task):
    def get_descriptions(self):
        pass

    def get_status(self):
        return get_parent_task_status_info(self)

    def exec_task(self, auth, ctx):
        LOGGER.debug('node availability task is running')

        strt = p_task_timing_start(AVL_LOGGER, "NodeAvailTask", [])
        AvailabilityWorker(auth).do_work()
        p_task_timing_end(AVL_LOGGER, strt)

    def resume_task(self, auth, ctx):
        try:
            AvailabilityWorker(auth).resume_work(ctx)
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx):
        try:
            self.resume_task(auth, ctx)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

class NodesAvailability(WorkerTask):
    def get_descriptions(self):
       pass

    def get_status(self):
        return get_child_task_status_info(self)

    def do_nmap_ping(self, node_names, port=22):
        try:
            src_script_dir = os.path.abspath(tg.config.get('common_script'))
            ping_script_file = tg.config.get('nmap_script')

            src_script_file = os.path.join(src_script_dir,ping_script_file)
            cmd = src_script_file + " " + str(port) + " " + node_names

            local = Basic.getManagedNode()
            (output, exit_code) = local.node_proxy.exec_cmd(cmd, timeout=30)

            return (output, exit_code)
        except Exception, e:
            return ("", -1)

    def exec_task(self, auth, ctx,node_ids):
        try:
            LOGGER.debug('entered in exec task for NodesAvailability task')
            nodes=DBSession.query(ManagedNode).filter(ManagedNode.id.in_(node_ids)).all()
            node_names = ""
            port=0
            for node in nodes:
                node_names += node.hostname + " "
                nport=node.get_connection_port()
                if port == 0:
                    port=nport
                else:
                    if port > 0 and nport != port:
                        port=-1

            strt = p_task_timing_start(AVL_LOGGER, "NodesAvailability", node_names.strip().split(' '))
            strt1 = p_task_timing_start(AVL_LOGGER, "PreProcess", node_names.strip().split(' ')[0])
            
            self.completed_nodes = []
            self.pending_nodes = [node_id for node_id in node_ids]
            self.exc_node_ids = [node_id for node_id in node_ids]
            index = 0
            node_id = self.get_next_node_id(index)

            use_nmap = eval(tg.config.get("use_nmap_for_heartbeat", "False"))

            if use_nmap == True and port > 0:
                strt2 = p_task_timing_start(AVL_LOGGER, "NodesNmap", node_names)
                (output, exit_code) = self.do_nmap_ping(node_names=node_names, port=port)
                p_task_timing_end(AVL_LOGGER, strt2)
            else:
                (output, exit_code) = ("", -1)
            p_task_timing_end(AVL_LOGGER, strt1)

            while node_id is not None:
                self.pending_nodes.remove(node_id)
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
                index+=1
                node_id = self.get_next_node_id(index)

                strt1 = p_task_timing_start(AVL_LOGGER, "NodeRefreshAvail", node.hostname)
                if node:
                    self.current_node = node
                    self.start_time = datetime.utcnow()

                    try:
                        try:
                            node.refresh_avail(auth, exit_code=exit_code, isUp="(" + node.hostname + ")" in output)
                        except Exception, e:
                            LOGGER.error("Error updating Node availability . Server :"+node.hostname)
                            traceback.print_exc()
                    finally:
                        self.completed_nodes.append(node.id)
                p_task_timing_end(AVL_LOGGER, strt1)
        finally:
            self.check_if_hung()
            p_task_timing_end(AVL_LOGGER, strt)

    def resume_task(self, auth, ctx, node_ids):
        try:
            self.do_cleanup()
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx,node_ids):
        try:
            self.resume_task( auth, ctx,node_ids)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

    def get_max_wait_time(self):
        try:
            max_node_avail_wait_time=int(tg.config.get("max_node_avail_wait_time"))
        except Exception, e:
            LOGGER.error("Exception: "+str(e))
            max_node_avail_wait_time=45

        return max_node_avail_wait_time

class VMAvailTask(Task):
    def get_descriptions(self):
        pass

    def get_status(self):
        return get_parent_task_status_info(self)

    def exec_task(self, auth, ctx):
        LOGGER.debug('vm availability task is running')
        try:
            strt = p_task_timing_start(AVL_LOGGER, "VMAvailTask", [])
            VMAvailabilityWorker(auth).do_work()
            p_task_timing_end(AVL_LOGGER, strt)
        except Exception, e:
            LOGGER.debug('error while checking license.\n'+to_str(e))

    def resume_task(self, auth, ctx):
        try:
            VMAvailabilityWorker(auth).resume_work(ctx)
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx):
        try:
            self.resume_task( auth, ctx)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

class VMAvailability(WorkerTask):
    def get_descriptions(self):
        node_ids = self.get_param('node_ids')
        if node_ids:
            node_id = node_ids[0]
            name=node_id
            try:
                node = DBSession.query(ManagedNode).\
                        filter(ManagedNode.id == node_id).first()
                name=node.hostname
            except Exception, e:
                pass
        short_desc = m_("VMAvailability %s")
        desc = m_("VMAvailability on %s started on Node Up ")

        return (short_desc, (name,), desc, (name))

    def get_status(self):
        return get_child_task_status_info(self)

    def exec_task(self, auth, ctx,node_ids):
        LOGGER.debug('entered in exec task for VMAvailability task')
        strt = p_task_timing_start(AVL_LOGGER, "VMAvailability", node_ids)
        try:
            self.completed_nodes = []
            self.pending_nodes = [node_id for node_id in node_ids]
            self.exc_node_ids = [node_id for node_id in node_ids]
            index = 0
            node_id = self.get_next_node_id(index)
            while node_id is not None:
                self.pending_nodes.remove(node_id)
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
                index+=1
                node_id = self.get_next_node_id(index)
                if node and node.is_up():
                    self.current_node = node
                    self.start_time = datetime.utcnow()

                    try:
                        try:
                            strt1 = p_task_timing_start(AVL_LOGGER, "RefreshVMAvail", node.id)
                            node.refresh_vm_avail()
                            p_task_timing_end(AVL_LOGGER, strt1)
                        except Exception, e:
                            LOGGER.error("Error updating VM availability . Server :"+node.hostname)
                            traceback.print_exc()
                    finally:
                        self.completed_nodes.append(node.id)
        finally:
            self.check_if_hung()
            p_task_timing_end(AVL_LOGGER, strt)

    def resume_task(self, auth, ctx, node_ids):
        try:
            self.do_cleanup()
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx,node_ids):
        try:
            self.resume_task( auth, ctx,node_ids)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

    def get_max_wait_time(self):
        try:
            max_vm_avail_wait_time=int(tg.config.get("max_vm_avail_wait_time"))
        except Exception, e:
            LOGGER.error("Exception: "+str(e))
            max_vm_avail_wait_time=60

        return max_vm_avail_wait_time

class VMRemoveTask(NodeTask):
    def get_descriptions(self):
        dom_name = self.get_dom_name()
        node_name = self.get_node_name()
        short_desc = ""
        desc = ""

        short_desc = m_("Deleting %s")
        desc = m_("Remove action on %s. Managed Node is %s")

        return (short_desc, (dom_name,), desc, (dom_name, node_name))

    def exec_task(self, auth, ctx, dom_id, node_id, force):
        manager = Basic.getGridManager()
        return manager.remove_vm(auth, dom_id, node_id, force)

    def resume_task(self, auth, ctx, dom_id, node_id, force):
        try:
            vm=DBSession.query(VM).filter(VM.id==dom_id).first()
            LOGGER.debug('resuming remove vm')
            if vm is None:
                LOGGER.debug('vm is already removed')
            else:
                manager = Basic.getGridManager()
                return manager.remove_vm(auth, dom_id, node_id, force)
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, dom_id, node_id, force):
        try:
            self.resume_task( auth, ctx, dom_id, node_id, force)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

class EmailTask(Task):
    def get_descriptions(self):
        short_desc = m_("Sending E-mail for failed task")
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec task E-mail sending task')
        manager = Basic.getGridManager()
        manager.send_notifications(auth)
        
class UpdateDiskSize(Task):
    def get_descriptions(self):
        short_desc = m_("Updating the actual size of the disk")
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for Updating the size task')
        StorageService().update_disks_size(auth)

class VMImportTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        action = self.get_param('action')
        short_desc = m_("Importing Virtual Machine on %s")
        return (short_desc, (node_name,), short_desc, (node_name,))


    def exec_task(self, auth, ctx, node_id, directory,filenames):
        manager = Basic.getGridManager()
        managed_node = manager.getNode(auth, node_id)
        if managed_node is not None:
            if not managed_node.is_authenticated():
                managed_node.connect()
                NodeService().import_vm_config(auth,node_id, directory,filenames)
#            return manager.do_node_action(auth, node_id, action)
        else:
            raise Exception("Can not find the managed node")

    def resume_task(self, auth, ctx, node_id, action,paths):
        try:
            return self.exec_task(auth, ctx, node_id, action,paths)
        except Exception, e:
            msg=constants.RESUME_TASK+to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, node_id, action,paths):
        try:
            return self.exec_task(auth, ctx, node_id, action,paths)
        except Exception, e:
            msg=constants.RECOVER_TASK+to_str(e)
            raise Exception(msg)

class AssociateDefnsTask(Task):
    def get_descriptions(self):
        pass
        
    def exec_task(self, auth, ctx, site_id, group_id, def_type, def_ids, op_level):
        LOGGER.debug('entered in excec_task for associate definitions task')
        StorageService().associate_defns(site_id, group_id, def_type, def_ids, auth, op_level)

class AddStorageDefTask(Task):
    def get_descriptions(self):
        pass
        
    def exec_task(self, auth, ctx, site_id, group_id, node_id, type, opts, op_level, sp_ids, scan_result):
        LOGGER.debug('entered in excec_task for add storage definition task')
        StorageService().add_storage_def(auth, site_id, group_id, node_id, type, opts, op_level,\
            sp_ids, scan_result)

class RemoveStorageDefTask(Task):
    def get_descriptions(self):
        pass
        
    def exec_task(self, auth, ctx, storage_id, site_id, group_id, op_level):
        LOGGER.debug('entered in excec_task for remove storage definition task')
        StorageService().remove_storage_def(auth, storage_id, site_id, group_id, op_level)
        
class AddAnnotationTask(Task):
    def get_descriptions(self):
        short_desc = m_("Add Annotation Task" )
        desc = m_("Add Annotation Task at "+to_str(self.submitted_on) )
        return (short_desc, (), desc, ())
    def exec_task(self, auth, ctx, node_id,text,user):
        LOGGER.debug('Entered in excec_task for AddAnnotationTask')
        msg=NodeService().process_annotation(auth,node_id,text,user)
        return dict(results=msg, visible=True, status=Task.SUCCEEDED)
class EditAnnotationTask(Task):
    def get_descriptions(self):
        short_desc = m_("Edit Annotation Task" )
        desc = m_("Edit Annotation Task at "+to_str(self.submitted_on) )
        return (short_desc, (), desc, ())
    def exec_task(self, auth, ctx, node_id,text,user):
        LOGGER.debug('Entered in excec_task for EditAnnotationTask')
        msg=NodeService().process_annotation(auth,node_id,text,user)
        return dict(results=msg, visible=True, status=Task.SUCCEEDED)
class ClearAnnotationTask(Task):
    def get_descriptions(self):
        short_desc = m_("Clear Annotation Task" )
        desc = m_("Clear Annotation Task at "+to_str(self.submitted_on) )
        return (short_desc, (), desc, ())
    def exec_task(self, auth, ctx, node_id):
        LOGGER.debug('Entered in excec_task for ClearAnnotationTask')
        msg=NodeService().clear_annotation(auth,node_id)
        return dict(results=msg, visible=True, status=Task.SUCCEEDED)
