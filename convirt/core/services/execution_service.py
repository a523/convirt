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

from convirt.core.services.core import Service, ServiceException
from threading import Thread, Condition, Lock
import time
import tg
from convirt.core.utils.utils import to_unicode,to_str
import logging

logger = logging.getLogger("convirt.services.exec_service")

class ThreadLimitException(ServiceException):
    pass

class ExecutionService(Service):
    """ Creates a pool of workers equal to NUM_WORKERS

    This service is used for executing "works". works are submitted via
    newwork() function which takes in the work in the form of a python
    class. The class needs to have a method called do_work that would 
    accept two parameters, a parameter list and
    context. A list of processors is also passed in. These are function
    objects and each one accept a single input and outputs a dictionary.
    """

    def new_work(self, work, ctx = None, args = None, kw = None):
        #To make new_work thread-safe, we need to execute one new work
        #at a time.
        self.task_lock.acquire()
        try:
            for w in self.workers:
                if not w.busy():
                    w.do(work, args, kw, ctx)
                    w._busy = True
                    self.running_tasks[to_str(work.task_id)] = work
                    break
            else:
                raise ThreadLimitException("All workers are busy. Try again \
                                       later or increase the default \
                                       workers.")
        finally:
            self.task_lock.release()

    def init(self):
        self.workers = []
        self.running_tasks = {}
        self.task_lock = Condition(Lock())
        nw = int(tg.config.get('services.execution.num_threads', 10))
        logger.debug("Creating " + to_str(nw) + " workers")
        while nw > 0:
            w = Worker()
            w.name = "c_worker-%d" % nw
            self.workers.append(w)
            w.start()
            while not w.alive:
                time.sleep(0.1)
            nw = nw - 1
        logger.debug("Done.")

    def stop(self):
        for w in self.workers:
            w.stop()

    def get_running_tasks(self):
        result = []
        for w in self.workers:
            if w.busy() and w.work:
                task = w.work
                result.append(task)
        return result

    def get_running_task_obj(self, task_id):
        return self.running_tasks.get(to_str(task_id))

    def clear_running_task_obj(self, task_id):
        try:
            del self.running_tasks[to_str(task_id)]
        except KeyError, e:
            logger.error("KeyError on running tasks object for taskid :"+to_str(task_id))
            
class Worker(Thread):

    def __init__(self):
        self.alive = False
        Thread.__init__(self)

    def run(self):
        self.work_notify_lock = Condition(Lock())
        self.work_notify_lock.acquire()
        self.alive = True
        while True:
            self._busy = False
            self.work_notify_lock.wait()
            if not self.alive:
                break
            try:
                self.work.do_work(self.ctx, self.args, self.kw)
            except Exception, e:
                logger.exception(to_str(e))
                pass

    def busy(self):
        return self._busy

    def do(self, work, args, kw, ctx):
        self.work = work
        self.args = args
        self.kw = kw
        self.ctx = ctx
        self.work_notify_lock.acquire()
        try:
            self.work_notify_lock.notify()
        finally:
            self.work_notify_lock.release()

    def stop(self):
        self.alive = False
        self.work_notify_lock.acquire()
        try:
            self.work_notify_lock.notify()
        finally:
            self.work_notify_lock.release()

        
