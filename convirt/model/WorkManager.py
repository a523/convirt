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
#
from convirt.config.app_cfg import base_config
from convirt.model.services import ServiceItem
from convirt.model import DBSession
from convirt.model.Entity import Entity,EntityTasks
from convirt.model.services import Task,TaskUtil
from convirt.core.utils.utils import to_unicode,to_str
from sqlalchemy.orm import eagerload
from sqlalchemy.sql.expression import not_

import convirt.core.utils.constants
constants = convirt.core.utils.constants

from datetime import datetime,timedelta
import traceback,transaction,tg,logging
import time

LOGGER = logging.getLogger("convirt.model")
WRK_LOGGER = logging.getLogger("WORKER")

class WorkManager:
    """
    This is the availabilty worker , which creates the sub tasks
    """

    def __init__(self,auth):
        from convirt.viewModel.TaskCreator import TaskCreator
        self.max_workers = 1
        self.worker = u"DefaultWorker"
        self.worker_ids = []
        self.available_workers = self.max_workers
        self.tc = TaskCreator()
        self.auth = auth
        self.start_time=datetime.utcnow()
        self.execution_context={}
        s = DBSession.query(ServiceItem).\
                filter(ServiceItem.name == to_unicode('Task Manager Service')).one()
        self.task_service_id = s.id
        self.svc_central = base_config.convirt_service_central
        try:
            self.max_worker_wait_time=int(tg.config.get("max_worker_wait_time"))
        except Exception, e:
            print "Exception: ", e
            self.max_worker_wait_time=300


    def get_work(self):
        raise Exception("get_work needs to be implemented.")

    def get_task(self):
        pass

    def workers_in_progress(self):
        return self.worker_ids


    def make_entity_task_entries(self, task_id, entity_ids):
        """
        making entry to entity_tasks table
        """
#        estimated_time=datetime.utcnow()+timedelta(minutes=int(tg.config.get("completion_time")))
        ent_tasks = []
        WRK_LOGGER.debug("in make_entity_task_entries task_id : "+str(task_id)+ " :entity_ids :"+str(entity_ids))
        for ent_id in entity_ids:
            try:
                ###update the entity_tasks table
                ent_task=EntityTasks(self.worker,to_unicode(task_id),ent_id,False,datetime.utcnow())
                ent_tasks.append(ent_task)

            except Exception, e:
                traceback.print_exc()

#            transaction.commit()
        self.update_execution_context()
        for ent_task in ent_tasks:
            DBSession.merge(ent_task)
            
        transaction.commit()
        WRK_LOGGER.debug("in make_entity_task_entries committed task_id : "+str(task_id)+ " :entity_ids :"+str(entity_ids))


    def wait_for_workers_to_finish(self, task_ids):

        WRK_LOGGER.debug("wait_for_workers_to_finish for "+self.worker+" max_worker_wait_time: "+str(self.max_worker_wait_time))
        task_completed = False
        self.wait_start_time=datetime.utcnow()
        ###this is an infinite loop until we find a completed task
        ###we need to add some wait time to check on the status of child tasks
        while task_completed == False:
            time.sleep(5)
            completed_tasks = self.check_tasks_completed(task_ids)
            WRK_LOGGER.debug("wait_for_workers_to_finish for "+self.worker+" completed_tasks :"+str(completed_tasks))
            if len(completed_tasks) > 0:
                task_completed = True

                for task in completed_tasks:
                    self.worker_ids.remove(task['task_id'])
                    WRK_LOGGER.debug("child task completed, update EntityTasks "+self.worker+" completed_tasks :"+str(task['task_id']))
                    ets = DBSession.query(EntityTasks).\
                        filter(EntityTasks.worker_id==to_unicode(task['task_id'])).all()
                    for et in ets:
                        et.worker_id=None
                        et.finished=True
                        et.end_time=datetime.utcnow()
                        DBSession.merge(et)

                    transaction.commit()
                    WRK_LOGGER.debug("child tasks completed, updated EntityTasks "+self.worker)
            else :
#                if True:
#                    continue
                wait_time_sec=(datetime.utcnow()-self.wait_start_time).seconds
                WRK_LOGGER.debug("No completed child tasks for "+self.worker+". waiting for "+str(wait_time_sec))
                if wait_time_sec > self.max_worker_wait_time:
                    task_service = self.svc_central.get_service(self.task_service_id)
                    past_time = self.start_time-timedelta(minutes=1)

                    for task_id in task_ids:
                        task_obj = task_service.get_running_task_obj(task_id)
                        if task_obj:
                            (hung, completed, pending) = task_obj.get_running_status()
                            WRK_LOGGER.debug("HUNG STATUS for "+self.worker+":"+str(hung)+":"+str(task_id)+\
                                ":"+str(completed)+":"+str(pending))
                            if hung:
                                task_completed = True
                                self.worker_ids.remove(task_id)

                                WRK_LOGGER.debug("Hung task. Cleanup EntityTask for "+self.worker+". task id : "+str(task_id))
                                DBSession.query(EntityTasks).filter(EntityTasks.worker==self.worker).\
                                    filter(EntityTasks.entity_id.in_(completed)).\
                                    update(dict(worker_id=None,finished=True, end_time=datetime.utcnow()))
                                DBSession.query(EntityTasks).filter(EntityTasks.worker==self.worker).\
                                    filter(EntityTasks.entity_id.in_(pending)).\
                                    update(dict(worker_id=None,finished=True, start_time=past_time))

                                transaction.commit()
                                WRK_LOGGER.debug("Hung task. Cleaned up EntityTask for "+self.worker+". task id : "+str(task_id))
                    

    def check_tasks_completed(self, task_ids):
        """
        checking tasks completed
        """

        transaction.begin()
        tasks=DBSession.query(Task).filter(Task.task_id.in_(task_ids)).\
                                options(eagerload("result")).all()
        completed_tasks = []
        for task in tasks:
            if task.is_finished():
                completed_tasks.append(dict(task_id=task.task_id, status=task.result[0].status))

        transaction.commit()
        return completed_tasks


    def do_work(self):
        """
        main function calling from CollectMetrics,NodeAvail and VMAvail for creatin sub tasks
        """
        WRK_LOGGER.debug("GETTING WORK for "+self.worker)
        (new_work, entity_ids) = self.get_work()
        wip = self.workers_in_progress()

        while new_work or wip:

            if new_work and len(wip) < self.max_workers:
                WRK_LOGGER.debug("Submitting new WORK for "+self.worker)
                work_id = self.tc.submit_task(new_work)
                self.worker_ids.append(work_id)
                WRK_LOGGER.debug("Submitting new WORK for "+self.worker +" : child task id : "+str(work_id))

                self.make_entity_task_entries(work_id, entity_ids)
#                self.update_execution_context()

            else:
                if len(wip) > 0:
                    WRK_LOGGER.debug("WAIT for "+self.worker)
                    self.wait_for_workers_to_finish(wip)
                    LOGGER.debug("WAIT OVER for "+self.worker)
                    WRK_LOGGER.debug("WAIT OVER for "+self.worker)

            WRK_LOGGER.debug("GETTING WORK new for "+self.worker)
            (new_work, entity_ids) = self.get_work()
            wip = self.workers_in_progress()

    def update_execution_context(self):
        """
        storing context in task for resume process
        """
        tid = TaskUtil.get_task_context()
        WRK_LOGGER.debug("in update_execution_context Parent task : "+str(tid)+" : child tasks :"+str(self.worker_ids))
        task=Task.get_task(tid)
        if task is not None:
            self.execution_context["start_time"]=self.start_time
            self.execution_context["worker_ids"]=self.worker_ids
            task.context["execution_context"]=self.execution_context
            DBSession.add(task)
            WRK_LOGGER.debug("in update_execution_context updated Parent task : "+str(tid))
#            transaction.commit()

    def resume_work(self,context):
        """
        on resume setting value from task context
        """
        execution_context=context["execution_context"]
        WRK_LOGGER.debug("RESUMING WORKER for :"+self.worker )
        if execution_context:
            self.start_time=execution_context.get("start_time",datetime.utcnow())
            self.worker_ids=execution_context.get("worker_ids",[])
            self.sp_list=execution_context.get("sp_list",[])
            ##validate all the worker ids are taken care of
            ets = DBSession.query(EntityTasks).filter(EntityTasks.worker==self.worker).\
                                    filter(not_(EntityTasks.worker_id.in_(self.worker_ids))).all()
            if len(ets) > 0:
                xtra_work_ids = [et.worker_id for et in ets]
                WRK_LOGGER.error("GOT ENT Tasks different from execution_context :"+self.worker+\
                ": CONTEXT WORKERS : "+str(self.worker_ids) +": XTRA WORKERS :"+str(xtra_work_ids))
                r = DBSession.query(EntityTasks.entity_id).\
                        filter(EntityTasks.worker_id.in_(xtra_work_ids)).\
                        filter(EntityTasks.worker==self.worker).\
                        update(values=dict(worker_id=None,finished=True,end_time=datetime.utcnow()))
                transaction.commit()
                WRK_LOGGER.debug("Cleaned Up entity_tasks . worker:rows : "+self.worker+":"+str(r))
                
        WRK_LOGGER.debug("RESUMING WORKER for :"+self.worker+":"+str(self.start_time)+":"+str(self.worker_ids) )
        self.do_work()



