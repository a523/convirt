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


from convirt.model import DeclarativeBase, metadata, DBSession

from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.types import Text
from sqlalchemy import ForeignKey, DateTime, PickleType, Boolean, Unicode
from sqlalchemy.orm import relation, backref, eagerload
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.schema import Index,Sequence
try:
    import sqlalchemy
    MSBigInteger=eval("sqlalchemy.types.BigInteger")
except Exception,e   :
    from sqlalchemy.databases.mysql import MSBigInteger
from datetime import datetime, timedelta
from convirt.model.Authorization import AuthorizationService
from convirt.model.Entity import Entity
from convirt.model.auth import User,Group
from convirt.model.UpdateManager import UIUpdateManager
from convirt.model.notification import Notification
import transaction
from convirt.core.utils.utils import to_unicode,to_str
import convirt.core.utils.utils
constants = convirt.core.utils.constants
import logging

logger = logging.getLogger("convirt.services.model")

ImmutablePickleType = PickleType(mutable=False)
from sqlalchemy.databases.mysql import MSMediumBlob
class MediumPickle(PickleType):
    impl = MSMediumBlob

class PolymorphicSetter(DeclarativeMeta):
    def __new__(cls, name, bases, dictionary):
        if '__mapper_args__' in dictionary.keys():
            dictionary['__mapper_args__']['polymorphic_identity'] = to_unicode(name)
        else:
            dictionary['__mapper_args__'] = dict(polymorphic_identity=to_unicode(name))
        return DeclarativeMeta.__new__(cls, name, bases, dictionary)


##############################
## TASKS TABLES
##############################
#Processor interface
class Processor:
    def process_output(self, results):
        pass

class Task(DeclarativeBase):
    __tablename__ = 'tasks'
    __metaclass__ = PolymorphicSetter

    SHORT_DESC_KEY = "shortDesc"
    DESC_KEY = "description"
    SHORT_DESC_PARAMS_KEY = "shortDescParams"
    DESC_PARAMS_KEY = "descParams"

    IDLE = 0
    STARTED = 1
    FAILED = 2
    SUCCEEDED = 3
    CANCELED = 4

    TASK_STATUS={
        IDLE:"Not Started",
        STARTED:"Started",
        FAILED:"Failed",
        SUCCEEDED:"Succeeded",
        CANCELED:"Canceled"
    }

    #FUTURE: When we introduce steps, they need to live in a separate table
    #since it does not make sense to introduce a relationship across the
    #rows of Tasks table. E.g. every step that belongs to a single task should
    #have the same calendar since they execute in the task context.
    task_id = Column(Integer,Sequence('task_id_seq'), primary_key=True)
    task_type = Column(Unicode(50), default=to_unicode('Task'))
    name = Column(Unicode(256))
    entity_id = Column(Unicode(50))
    entity_name = Column(Unicode(255))
    entity_type = Column(Integer)
    short_desc = Column(Text)
    long_desc = Column(Text)
    context = Column(PickleType)
    params = Column(PickleType)
    kw_params = Column(PickleType)
    processors = Column(ImmutablePickleType)
    user_name = Column(Unicode(255))
    submitted_on = Column(DateTime)
    repeating = Column(Boolean)
    cancellable = Column(Boolean, default=False)
    parent_task_id = Column(Integer)

    __mapper_args__ = {'polymorphic_on': task_type}

    def __init__(self, name, context, \
                 params, kw_params, processors, user_name):
        self.name = name
        self.context = context
        self.params = params
        self.kw_params = kw_params
        self.processors = processors
        self.user_name = user_name
        self.submitted_on = datetime.utcnow()
        descriptions = self.get_descriptions()
        if descriptions is not None:
            (short_desc, short_desc_params, \
             desc, desc_params) = descriptions
            self.set_short_desc(short_desc, short_desc_params)
            self.set_desc(desc, desc_params)
        self.repeating = False

    def __repr__(self):
        return '<Task: name=%s>' % self.name

    def get_param(self, name):
        if self.kw_params is not None and \
           name in self.kw_params:
            return self.kw_params[name]

    def get_context_param(self, name):
        if self.context is not None and \
           name in self.context:
            return self.context[name]

    def set_short_desc(self, desc, desc_params):
        self.context[self.SHORT_DESC_KEY] = desc
        self.context[self.SHORT_DESC_PARAMS_KEY] = desc_params
        self.short_desc = desc%desc_params

    def set_desc(self, desc, desc_params):
        self.context[self.DESC_KEY] = desc
        self.context[self.DESC_PARAMS_KEY] = desc_params
        self.long_desc = desc%desc_params

    def get_short_desc(self):
        if self.context is not None and \
           self.SHORT_DESC_KEY in self.context:
            return (self.context[self.SHORT_DESC_KEY],\
                    self.context[self.SHORT_DESC_PARAMS_KEY])
        return None

    def is_cancellable(self):
        return self.cancellable

    def is_finished(self):
        results=self.result
        if results:
            res=results[0]
            if res.status in [self.FAILED,self.SUCCEEDED,self.CANCELED]:
                return True
        return False

    def is_failed(self):
        results=self.result
        if results:
            res=results[0]
            if res.status in [self.FAILED,self.CANCELED]:
                return True
        return False
    
    def is_cancel_requested(self):
        result=self.get_running_instance()
        if result:
            return result.cancel_requested
        return False

    def request_cancel(self):
        result=self.get_running_instance()
        if result:
            result.cancel_requested=True
            return True
        else:
            raise Exception("Task is not running. Can not cancel the task.")

    def get_running_instance(self):
        result=DBSession.query(TaskResult).filter(TaskResult.status==self.STARTED).\
                filter(TaskResult.task_id==self.task_id).first()
        return result

    def set_entity_details(self, ent_id):
        ent=DBSession.query(Entity).filter(Entity.entity_id==ent_id).first()
        if ent is not None:
            self.entity_id = ent.entity_id
            self.entity_type = ent.type_id
            self.entity_name = ent.name

    def set_entity_info(self, ent):
        if ent is not None:
            self.entity_id = ent.entity_id
            self.entity_type = ent.type_id
            self.entity_name = ent.name

    def get_task_result_instance(self):
        return DBSession.query(TaskResult).filter(TaskResult.task_id==self.task_id).first()
        
    @classmethod
    def get_task(cls,task_id):
        task=None
        try:
            transaction.begin()
            # Bug : 993 : high cpu : removing eager load
            #task=DBSession.query(cls).filter(cls.task_id==task_id).\
            #        options(eagerload("result")).first()
            task=DBSession.query(cls).filter(cls.task_id==task_id).first()
        except Exception,ex:
            logger.error(to_str(ex).replace("'",""))
            traceback.print_exc()
            transaction.abort()
        else:
            transaction.commit()
        return task
    
    def get_desc(self):
        if self.context is not None and \
           self.DESC_KEY in self.context:
            return (self.context[self.DESC_KEY],\
                    self.context[self.DESC_PARAMS_KEY])
        return None

    def cancel(self):
        pass

    def exec_task(self, auth, context, *args, **kw):
        raise Exception("exec_task needs to be implemented")

    def resume_task(self, auth, context, *args, **kw):
        raise Exception(constants.INCOMPLETE_TASK+\
                        "resume not implemented.")

    def recover_task(self, auth, context, *args, **kw):
        raise Exception(constants.INCOMPLETE_TASK+\
                        "recover not implemented.")

    def get_descriptions(self):
        raise Exception("get_descriptions needs to be implemented")

    def get_entity_ids(self):
        return self.entity_id

    def do_work(self, runtime_context, args = None, kw = None):
        self.task_manager = runtime_context.pop()
        self.curr_instance = datetime.utcnow()
        args = self.params
        recover = resume = False
        visible = False
        if kw:
            resume = kw.get('resume',False)
            recover= kw.get('recover',False)
        
        kw = self.kw_params
        self.quiet = (self.get_context_param('quiet') == True)

        if not self.quiet and resume==False and recover==False :
            self.task_started()

        try:
            try:
                task_result_running_instance = True
                if not args:
                    args = []
                if not kw:
                    kw = {}
                #build auth object
                auth = AuthorizationService()
                auth.email_address = ""
                user = User.by_user_name(self.user_name)
                auth.user = user
                if user is None:
                    u = User.by_user_name(u'admin')
                    auth.email_address = u.email_address
                    logger.info("User: "+str(self.user_name)+" does not exist in CMS.")
                    raise Exception("User: "+str(self.user_name)+" does not exist in CMS.")
                else:
                    auth.user = user
                    auth.user_name = user.user_name
                    auth.email_address = user.email_address

                TaskUtil.set_task_context(self.task_id)
                if recover != True and resume != True:
                    raw_result = self.exec_task(auth, self.context, *args, **kw)
                else:
                    runn = self.get_running_instance()
                    if runn:
                        self.curr_instance = runn.timestamp
                    else:
                        task_result = self.get_task_result_instance()
                        if isinstance(task_result.results, str):
                            task_result.results += "can not resume task. No running instance"
                        elif not task_result.results:
                            task_result.results = "can not resume task. No running instance"
                        task_result_running_instance = False

                    if task_result_running_instance:
                        if recover == True :
                            raw_result = self.recover_task(auth, self.context, *args, **kw)
                        elif resume == True:
                            raw_result = self.resume_task(auth, self.context, *args, **kw)
                if task_result_running_instance:
                    cancelled=False
                    results = raw_result
                    if isinstance(raw_result,dict):
                        if raw_result.get('status')==constants.TASK_CANCELED:
                            e=raw_result.get('msg')+"\n"+raw_result.get('results')
                            transaction.abort()
                            cancelled=True
                            if not self.quiet:
                                self.task_fail(e, auth, cancelled=True)
                        elif raw_result.get('status')==Task.SUCCEEDED:
                            results = raw_result.get('results')
                            visible = raw_result.get('visible',False)

                    else:
                        #get processed results
                        if raw_result is not None and self.processors is not None:
                            results = [raw_result,]
                            for p in self.processors:
                                if issubclass(p, Processor):
                                    p().process_output(results)
                        else:
                            results = raw_result

                        if results is None:
                            desc_tuple = self.get_short_desc()
                            if desc_tuple is None:
                                results = 'Task Completed Successfully.'
                            else:
                                (short_desc, short_desc_params) = desc_tuple
                                desc = (short_desc)%short_desc_params
                                results = desc+' Completed Successfully.'
                        #commit changes done by exec_task
                        transaction.commit()
            except Exception, e:
                #rollback any changes made in thread session
                logger.exception(to_str(e))
                transaction.abort()
                if not self.quiet:
                    self.task_fail(e, auth)
            else:
                if not self.quiet and cancelled==False:
                    self.task_success(results,visible)
        finally:
            DBSession.remove()

    def task_started(self):
        conn = self.task_manager.get_database_conn()
        try:
            res = TaskResult(self.task_id, \
                             self.curr_instance, \
                             self.STARTED, \
                             None)
            conn.add(res)
            conn.commit()
            if not self.repeating and self.entity_id!=None:
                UIUpdateManager().set_updated_tasks(self.task_id, \
                                                    self.user_name)

        finally:
            conn.close()

    #the following flavor of fail function is called
    #when the task fails without even starting. Therefore, we do not have
    #a start time or connection context. We expect the connection to be
    #passed in.
    def task_fail_start(self, exception, conn):
        results = to_str(exception)
        self.curr_instance = datetime.utcnow()
        res = TaskResult(self.task_id, \
                         self.curr_instance, \
                         self.FAILED, \
                         results)
        u = User.by_user_name(self.user_name)
        if u is None:
            u = User.by_user_name(u'admin')
        email=u.email_address
        notification=Notification(to_unicode(self.task_id), \
                                  self.name, \
                                  self.curr_instance, \
                                  results, \
                                  self.user_name, \
                                  email)
        conn.merge(res)
        conn.add(notification)
        if not self.repeating and self.entity_id!=None:
            UIUpdateManager().set_updated_tasks(self.task_id,\
                                                self.user_name)

    def task_fail(self, exception, auth, cancelled=False):
        conn = self.task_manager.get_database_conn()
        try:
            fail_status=self.FAILED
            if cancelled==True:
                fail_status=self.CANCELED

            results = to_str(exception)
            res = TaskResult(self.task_id, \
                             self.curr_instance, \
                             fail_status, \
                             results, \
                             cancel_requested=cancelled)
#            u = User.by_user_name(self.user_name)
            email=auth.email_address
            if email:
                notification=Notification(to_unicode(self.task_id), \
                                      self.name, \
                                      self.curr_instance, \
                                      results, \
                                      self.user_name, \
                                      email)
                conn.add(notification)
            conn.merge(res)            
            conn.commit()

            if not self.repeating and self.entity_id!=None:
                UIUpdateManager().set_updated_tasks(self.task_id,\
                                                    self.user_name)

        finally:
            self.clear_running_task_obj()
            conn.close()

    def task_success(self, results, visible):
        conn = self.task_manager.get_database_conn()
        try:
            res = TaskResult(self.task_id, \
                             self.curr_instance, \
                             self.SUCCEEDED, \
                             results, \
                             visible=visible)
            conn.merge(res)
            conn.commit()

            if (not self.repeating and self.entity_id!=None) or (visible==True):
                UIUpdateManager().set_updated_entities(self.get_entity_ids())
                UIUpdateManager().set_updated_tasks(self.task_id,
                                                    self.user_name)

        finally:
            self.clear_running_task_obj()
            conn.close()


    def update_exec_context(self, key, context):
        conn = self.task_manager.get_database_conn()
        try:
            res = conn.query(TaskResult).\
                    filter(TaskResult.task_id == self.task_id).\
                    filter(TaskResult.timestamp == self.curr_instance).one()
            if res.exec_context is None:
                res.exec_context = {}
            res.exec_context[key] = context
            conn.commit()
        finally:
            conn.close()

    def set_interval(self, interval):
        if self.interval is None:
            self.interval = []
        self.interval.append(interval)
        self.repeating = (interval.interval is not None and interval.interval > 0)

    def set_calendar(self, calendar):
        if self.calendar is None:
            self.calendar = []
        self.calendar.append(calendar)
        self.repeating = True

    def set_frequency(self, frequency):
        if self.interval:
            self.interval[0].interval = frequency

    def get_status(self):
        stat = ""
        stat+="\n# TaskName: %s" % self.name
        now = datetime.utcnow()
        res = self.get_running_instance()
        stat+='\nID: "%s", ParentTask: "%s" SubmittedTime: "%s"' \
                        % (self.task_id, self.parent_task_id, self.submitted_on)

        if res:
            durn = str((now-res.timestamp).seconds)+"."+str((now-res.timestamp).microseconds)
            stat+='\nStartTime: "%s", RunningFor: "%s"' % (res.timestamp, durn)
        return stat

    def clear_running_task_obj(self):
        try:
            self.task_manager.clear_running_task_obj(self.task_id)
        except Exception, e:
            logger.error("Error clearing task obj from memory. "+str(e))

Index("task_eid_time_uname", Task.entity_id, Task.submitted_on, Task.user_name)


class TaskResult(DeclarativeBase):
    __tablename__ = 'task_results'

    task_id = Column(Integer, ForeignKey('tasks.task_id'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    endtime = Column(DateTime)
    status = Column(Integer)
    results = Column(MediumPickle)
    exec_context = Column(PickleType)
    cancel_requested = Column(Boolean, default=False)
    visible = Column(Boolean, default=False)

    task = relation(Task, backref=backref('result'))

    def __init__(self, task_id, timestamp, \
                 status, results, exec_context = {}, cancel_requested=False, visible=False):
        self.task_id = task_id
        self.timestamp = timestamp
        self.endtime=datetime.utcnow()
        self.status = status
        self.results = results
        self.exec_context = exec_context
        self.cancel_requested = cancel_requested
        self.visible = visible

    def is_finished(self):
        if self.status in [Task.FAILED,Task.SUCCEEDED,Task.CANCELED]:
            return True
        return False

    def __repr__(self):
        return '<Task with id %s and timestamp %s returned %s>' % \
                (self.task_id, self.timestamp, self.status)

Index("tr_composite", TaskResult.task_id,TaskResult.timestamp,TaskResult.status,TaskResult.visible)

class TaskInterval(DeclarativeBase):
    """ The TaskInterval entity defines regularly scheduled
    items which execute at intervals. It can also optionally define
    one time execution by passing an interval value of <= 0. Such interval
    objects will be deleted after the first execution.
    """
    __tablename__ = "task_intervals"

    cal_id = Column(Integer,Sequence('cal_id_seq'), primary_key=True)
    task_id = Column(Integer, ForeignKey(Task.task_id,ondelete = "CASCADE"))
    interval = Column('task_interval',Integer)
    next_execution = Column(DateTime)

    task = relation(Task, backref=backref('interval'))

    def __init__(self, interval, next_execution=None):
        self.interval = interval
        if next_execution:
            self.next_execution = next_execution
        elif interval is not None and interval > 0:
            self.next_execution = datetime.utcnow() \
                    + timedelta(minutes = interval)
        else:
            raise Exception("Either define a non-zero interval \
                            or a next execution timestamp")

Index("ti_ne", TaskInterval.next_execution)

class TaskCalendar(DeclarativeBase):
    __tablename__ = 'task_calendars'

    cal_id = Column(Integer,Sequence('cal_id_seq'), primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    dow = Column(Integer)
    month = Column(Integer)
    day = Column(MSBigInteger)
    hour = Column(Integer)
    minute = Column(MSBigInteger)

    task = relation(Task, backref=backref('calendar'))
  
    def create_bits(self, numbers):
        k = 0
        for n in numbers:
            if n > 60 or n < 0:
                continue
            k = k | (1 << n)
        return k

    def reverse_bits(self, number):
        ret_val = []
        if number == 0:
            return ret_val
        for n in range(0,60):
            if (number & (1 << n)) != 0:
                ret_val.append(n)
        return ret_val

    def get_dow(self):
        return self.reverse_bits(self.dow)

    def get_month(self):
        return self.reverse_bits(self.month)

    def get_day(self):
        return self.reverse_bits(self.day)

    def get_hour(self):
        return self.reverse_bits(self.hour)

    def get_minute(self):
        return self.reverse_bits(self.minute)

    def __init__(self, dow, month, day, hour, minute):
        #assume all variables are lists
        self.dow = self.create_bits(dow)
        self.month = self.create_bits(month)
        self.day = self.create_bits(day)
        self.hour = self.create_bits(hour)
        self.minute = self.create_bits(minute)

Index("tc_ne", TaskCalendar.dow, TaskCalendar.month, TaskCalendar.day,\
            TaskCalendar.hour, TaskCalendar.minute)

#######################
## SERVICES TABLES
#######################
Dependencies_table = Table("dependencies", metadata,
  Column('dependent_id', Integer, ForeignKey('services.id'), primary_key=True),
  Column('parent_id', Integer, ForeignKey('services.id'), primary_key=True))

class ServiceItem(DeclarativeBase):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    type = Column(ImmutablePickleType)
    executor = Column(ImmutablePickleType)
    enabled = Column(Boolean)

    dependents = relation("ServiceItem", secondary=Dependencies_table,\
                   primaryjoin=id == Dependencies_table.c.parent_id,\
                   secondaryjoin=Dependencies_table.c.dependent_id == id)

    parents = relation("ServiceItem", secondary=Dependencies_table,\
                   primaryjoin=id == Dependencies_table.c.dependent_id,\
                   secondaryjoin=Dependencies_table.c.parent_id == id)


    def __init__(self, name, type, executor, enabled):
        self.name = name
        self.type = type
        self.executor = executor
        self.enabled = enabled

    def __repr__(self):
        return '<Service: %s>' % self.name

Index('ser_name',ServiceItem.name)

import threading
class TaskUtil:
    local = threading.local()

    @classmethod
    def set_task_context(cls,task_id):
        cls.local.task_id = task_id

    @classmethod
    def get_task_context(cls):
        try:
            return cls.local.task_id
        except Exception, e:
#            print "Exception: ", e
#            logger.error(to_str(e))
            pass
        return None

    @classmethod
    def is_cancel_requested(cls):
        tid=cls.get_task_context()
        if tid:
            task=Task.get_task(tid)
            if task:
                return task.is_cancel_requested()
        return False


