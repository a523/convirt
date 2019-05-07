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

from convirt.config.app_cfg import base_config
from convirt.model.services import ServiceItem
from convirt.core.services.tasks import *
from convirt.model.services import TaskInterval
from datetime import datetime
from convirt.model import DBSession
import Basic
import logging

from convirt.core.utils.utils import getDateTime
from convirt.core.utils.utils import to_unicode,to_str
logger = logging.getLogger("convirt.viewModel")

class TaskCreator:
    """ This is the helper function for creating various task types
    in convirt. Each new task type must add its own function here. The
    arguments to tasks must be named (given in kw_params) and dom_id, node_id
    format must be followed. This is to ensure that the Tasks GUI can
    automatically pick the entity context for your task.
    """

    def __init__(self):
        #initialize the service id from database
        s = DBSession.query(ServiceItem).\
                filter(ServiceItem.name == to_unicode('Task Manager Service')).one()
        self.task_service_id = s.id
        self.svc_central = base_config.convirt_service_central

    def get_running_task_info(self):
        task_service = self.svc_central.get_service(self.task_service_id)
        return task_service.get_running_task_info()

    def _get_username(self, auth):
        return auth.user.user_name

    def send_deployment_stats(self):
        #task_service = self.svc_central.get_service(self.task_service_id)

        t = SendDeploymentStatsTask(u'Send Deployment Stats', {'quiet':True}, [],\
                        dict(), None, u'admin')
        dc_ent = DBSession.query(Entity).filter(Entity.type_id==1).first()
        t.set_entity_info(dc_ent)
        t.set_interval(TaskInterval(interval=None,
                                       next_execution=datetime.utcnow()))
        DBSession.add(t)
        import transaction
        transaction.commit()
        logger.debug("SendDeploymentStatsTask Submitted")
        return t.task_id

    def vm_action(self, auth, dom_id, node_id, action, \
                  dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)

        # 数据库操作
        t = VMActionTask(action, {}, [], \
                         dict(dom_id=dom_id,node_id=node_id,action=action),\
                         None, user_name)
        t.set_entity_details(dom_id)

        execution_time=getDateTime(dateval,timeval)
        print execution_time
        if execution_time is None:
            task_service.submit_sync(t)   # 存数据库
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("VM Action Task Submitted")
        #self.refresh_node_metrics()

    def server_action(self, auth, node_id, action,dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ServerActionTask(action, {}, [], \
                             dict(node_id=node_id,action=action),\
                             None, user_name)
        t.set_entity_details(node_id)

        execution_time=getDateTime(dateval,timeval)
        print execution_time
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Server Action Task Submitted")

    def remove_node(self, auth, node_id, node_name, grp_id, grp_name, force, \
                                                dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveServerTask(u"Remove "+node_name, {}, [], \
                             dict(node_id=node_id,node_name=node_name,\
                             grp_id=grp_id,grp_name=grp_name,force=force),\
                             None, user_name)
        t.set_entity_details(node_id)
        #t.cancellable = True

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Remove Server Task Submitted")
        return t.task_id

    def migrate_vm(self, auth, dom_list, source_node_id,\
                    dest_node_id, live, force, all,dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        isLive = False
        isForce = False
        migrate_all = False
        if live=='true':
            isLive = True
        if force=='true':
            isForce = True
        if all=='true':
            migrate_all = True
        t = VMMigrateTask(u'Migrate VM', {}, [], \
                          dict(dom_list=dom_list, \
                               source_node_id=source_node_id,\
                               dest_node_id=dest_node_id,\
                               live=isLive, force=isForce, \
                               all=migrate_all), \
                          None, user_name)
        if all=='true':
            t.set_entity_details(dest_node_id)
        else:
             t.set_entity_details(dom_list[0])

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Migrate Task Submitted")
        #self.refresh_node_metrics()

    def config_settings(self, auth, image_id, config, mode,\
                        node_id, group_id, dom_id, vm_name,dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t= VMConfigSettingsTask(u'Provision VM', {}, [],\
                     dict(image_id=image_id, config=config, mode=mode,\
                          node_id=node_id, group_id=group_id, dom_id=dom_id,\
                          vm_name=vm_name), None, user_name)
        if mode == 'PROVISION_VM':
            t.set_entity_details(node_id)
        elif mode == 'EDIT_VM_INFO':
             manager=Basic.getGridManager()
             managed_node =manager.getNode(auth,node_id)
             if managed_node is not None:
                 dom=managed_node.get_dom(dom_id)
                 t.set_entity_details(dom.id)

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Configuration Task Submitted")

    def save_vm(self, auth, dom_id, node_id, file, directory, dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t= VMSnapshotTask(u'Hibernate', {}, [],\
                          dict(dom_id=dom_id, node_id=node_id, file=file,\
                               directory=directory), None, user_name)
        t.set_entity_details(dom_id)

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Snapshot Task Submitted")

    def restore_vm(self, auth, node_id, file,dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t= VMRestoreTask(u'Restore VM', {}, [],\
                    dict(node_id=node_id, file=file), None, user_name)
        t.set_entity_details(node_id)

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Restore Task Submitted")

    def import_appliance(self, auth, appliance_entry, image_store, \
                         group_id, image_name, platform, force,dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t= ImportApplianceTask(u'Import Appliance', {}, [],\
                               dict(appliance_entry=appliance_entry, \
                                    image_store=image_store, group_id=group_id,\
                                    image_name=image_name,platform=platform,\
                                    force=force),  None, user_name)
        t.set_entity_details(group_id)

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Import appliance task submitted")

    def refresh_node_metrics(self):
        task_service = self.svc_central.get_service(self.task_service_id)
        t = DBSession.query(Task).\
                filter(Task.name == u'Refresh Node Metrics').one()
        task_service.submit_task(t,2)
        logger.debug("Refresh Node Metrics task submitted")

    def vm_remove_action(self, auth, dom_id, node_id, force=False, \
                  dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = VMRemoveTask(u'Remove VM', {}, [], \
                         dict(dom_id=dom_id,node_id=node_id,force=force),\
                         None, user_name)
        t.set_entity_details(node_id)
        execution_time=getDateTime(dateval,timeval)
        print execution_time
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Remove VM Task Submitted")

    def populate_node_info(self, auth, node_id, dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = PopulateNodeInfoTask(u'Populate Node Information', {}, [], \
                         dict(node_id=node_id), None, user_name)
        t.set_entity_details(node_id)
        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Populate Node Information Task Submitted")


    def vm_availability(self, auth, node_id):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = VMAvailability(u'Update VM Availability : Node Up', {}, [],\
                        dict(node_ids=[node_id]), None, user_name)
        t.set_entity_details(node_id)
        task_service.submit_sync(t)
        logger.debug("VMAvailability Task Submitted")
        return t.task_id

    def import_vm_action(self, auth, node_id, directory,filenames,dateval=None,timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = VMImportTask("Import VM", {}, [], \
                             dict(node_id=node_id,directory=directory,filenames=filenames),\
                             None, user_name)
        t.set_entity_details(node_id)
        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Import VM Task Submitted")
        return t.task_id

    def associate_defns_task(self, auth, site_id, group_id, def_type, def_ids, op_level):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t= AssociateDefnsTask(u'Associate Definitions', {}, [], dict(site_id=site_id, group_id=group_id, def_type=def_type, def_ids=def_ids, op_level=op_level), None, user_name)
        t.set_entity_details(group_id)
        task_service.submit_sync(t)
        logger.debug("Associate Definitions task submitted")
        return t.task_id

    def add_storage_def_task(self, auth, site_id, group_id, node_id, type, opts, op_level, sp_ids):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        #get scan result
        scan_result = session.get(constants.SCAN_RESULT)
        t= AddStorageDefTask(u'Add Storage Definition', {}, [], dict(site_id=site_id, group_id=group_id,\
            node_id=node_id, type=type, opts=opts, op_level=op_level, sp_ids=sp_ids,\
            scan_result=scan_result), None, user_name)
        t.set_entity_details(site_id)
        task_service.submit_sync(t)
        logger.debug("Add Storage Definition task submitted")
        #remove scan result from session
        session[constants.SCAN_RESULT] = None
        session.save()
        return t.task_id

    def remove_storage_def_task(self, auth, storage_id, site_id, group_id, op_level):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t= RemoveStorageDefTask(u'Remove Storage Definition', {}, [], dict(storage_id=storage_id, site_id=site_id, group_id=group_id, op_level=op_level), None, user_name)
        if group_id:
            t.set_entity_details(group_id)
        elif site_id:
            t.set_entity_details(site_id)
        task_service.submit_sync(t)
        logger.debug("Remove Storage Definition task submitted")
        return t.task_id

    def submit_task(self, task, dateval=None, timeval=None):
        result=None
        try:
            task_service = self.svc_central.get_service(self.task_service_id)
            execution_time=getDateTime(dateval,timeval)
            if execution_time is None:
                task_service.submit_sync(task)
            else:
                task_service.submit_schedule(task, execution_time)
            logger.debug("Task : "+ task.name+ " Submitted")
            result=task.task_id
        except Exception, ex:
            traceback.print_exc()
            raise ex
        return result


    def add_annotation(self, auth, node_id,text,user,dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AddAnnotationTask(u"Add Annotation ", {}, [],
                            dict(node_id=node_id,text=text,user=user),
                             None, user_name)
        t.set_entity_details(node_id)

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Add Annotation Task Submitted")
        return t.task_id

    def edit_annotation(self, auth, node_id,text,user, dateval=None, timeval=None):

        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = EditAnnotationTask(u"Edit Annotation", {}, [],
                            dict(node_id=node_id,text=text,user=user),
                             None, user_name)
        t.set_entity_details(node_id)

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Edit Annotation  Task Submitted")
        return t.task_id

    def clear_annotation(self, auth, node_id,dateval=None, timeval=None):

        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ClearAnnotationTask(u"Remove Annotation ", {}, [],
                           dict(node_id=node_id),
                             None, user_name)
        t.set_entity_details(node_id)

        execution_time=getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug("Clear Annotation Task Submitted")
        return t.task_id

