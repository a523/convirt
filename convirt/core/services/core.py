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
    
from threading import Thread, Condition, Lock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, eagerload
from convirt.model.services import ServiceItem
import time
import tg
from convirt.core.utils.utils import to_unicode,to_str
import logging

logger = logging.getLogger("convirt.services")

class ServiceException(Exception):
    """ Common exception class returned by service framework 
    Services themselves can return their own exceptions
    """
    pass

class Service:
    """ Defines the minimal functionality to be implemented by services.

    Each service implementation has to override:
        init(): For one-time initialization work
        loop(): For repeated work
        stop(): For cleanup
    
    All services are defined as daemon threads.
    """
    MODE_THREAD = 0
    MODE_PROCESS = 1

    def __init__(self, id, mode, dbconn):
        """ Id: The service id from database
        mode: Whether service is running in thread or a separate process, intrnl
        dbconn: Carries the database connection maker, internal
        interval: Can be overridden by any service. Determines how often loop
                  is called
        alive: determines whether the service is running, internal
        dependencies: Holds the list of service references as identified
                      in the dependencies table, internal
        """
        self.id = id
        self.mode = mode
        self.dbconn = dbconn
        self.dep_lock = Condition(Lock())
        self.run_lock = Condition(Lock())
        self.interval = 60
        self.alive = False
        self.dependencies = {}

    def _exec(self):
        self.init()
        self.alive = True
        while self.alive:
            self.loop()
            self.run_lock.acquire()
            try:
                self.run_lock.wait(self.interval)
            finally:
                self.run_lock.release()
        self.alive = True

    def init(self):
        pass #to be implemented by service

    def loop(self):
        pass #to be implemented by service

    def _stop(self):
        self.stop()
        self.alive = False
        self.run_lock.acquire()
        try:
            self.run_lock.notify()
        finally:
            self.run_lock.release()
        max_wait = int(tg.config.get('services.core.max_wait', 2))
        cur_wait = 0
        while not self.alive and cur_wait < max_wait:
            cur_wait = cur_wait + 0.1
            time.sleep(0.1)

    def stop(self):
        pass #to be implemented by service

    def is_ready(self):
        return self.alive

    def getid(self):
        #has to be implemented by any service
        return self.id

    # Carries the proxy object information for this service
    def set_external_ref(self, external_ref):
        self.external_ref = external_ref

    def get_external_ref(self):
        return self.external_ref

    def get_database_conn(self):
        return self.dbconn()

    def get_mode(self):
        return self.mode

    def set_dependency(self, dep_name, dep_inst):
        self.dep_lock.acquire()
        try:
            self.dependencies[dep_name] = dep_inst
        finally:
            self.dep_lock.release()

    def get_bridge(self, dep_name):
        self.dep_lock.acquire()
        try:
            dep_svc = self.dependencies[dep_name]
            if self.get_mode() == Service.MODE_PROCESS or \
               dep_svc.get_mode() == Service.MODE_PROCESS:
                return (self.get_external_ref(), dep_svc)
            else:
                return (self, dep_svc)
        finally:
            self.dep_lock.release()

    def set_dependencies(self, deps):
        self.dep_lock.acquire()
        try:
            for (name, svc) in deps:
                self.dependencies[name] = svc
        finally:
            self.dep_lock.release()


#This is going to run in a thread in the main convirt process
class ServiceCentral(Thread):
    """ Responsible for maintaining and executing services.

    Service central reads a list of services, dependencies 
    from database, then starts the services according to the dependencies
    order. Then it falls into a loop waking up once in a while
    to check on services and restart those which died.

    Service central is also the public API of starting/stopping/killing
    individual services. It also provides an API to stop all of them and exit.
    """

    def __init__(self, dbconn):
        #store executor instances
        self.executors = []
        self.dbconn = dbconn
        session = dbconn()
        try:
            self.services = session.query(ServiceItem).\
                    options(eagerload('dependents')).all()
            self.dependencies = {}
            for s in self.services:
                for d in s.dependents:
                    self.dependencies[(d.id, s.id)] = s.name
        finally:
            session.close()
        self.run_lock = Condition(Lock())
        Thread.__init__(self)
        Thread.setDaemon(self, True)
    
    def run(self):
        logger.debug("Service Central is initializing...")
        #start services first
        for svc in self._order(self.services[:], self.dependencies.keys()):
            if svc.enabled:
                e = self._get_executor(svc.executor)
                e.start(svc.type, svc.id, self.dbconn, \
                        self._find_dependencies(svc.id))

        #monitor services and manage dependencies
        self.alive = True
        logger.debug("Service Central is ready")
        
        while self.alive:
            revived_svcs = []
            for e in self.executors:
                revived_svcs.append(e.check())
            for service_id in revived_svcs:
                svc = self.get_service(service_id)
                for (name, d) in self._find_dependents(service_id):
                    d.set_dependency(name, svc)
            self.run_lock.acquire()
            try:
                self.run_lock.wait(10)
            finally:
                self.run_lock.release()
        logger.debug("Service Central is dead")
        self.alive = True

    def _find_dependents(self, service_id):
        the_list = []
        for (dependent, parent) in self.dependencies.keys():
            if parent == service_id:
                name = self.dependencies[(dependent, parent)]
                the_list.append((name, self.get_service(dependent)))
        return the_list

    def _find_dependencies(self, service_id):
        the_list = []
        for (dependent,parent) in self.dependencies.keys():
            if dependent == service_id:
                name = self.dependencies[(dependent, parent)]
                the_list.append((name, self.get_service(parent)))
        return the_list

    def _get_executor(self, _executor):
        for e in self.executors:
            if isinstance(e, _executor):
                return e
        else:
            e = _executor()
            self.executors.append(e)
            return e
    
    def _get_executor_service(self, service_id):
        for svc in self.services:
            if svc.id == service_id:
                return (self._get_executor(svc.executor), svc.type)
    
    def query(self, service_id):
        """ Returns the status of the service. Alive (TRUE) or dead (FALSE) 
        """
        e = self._get_executor_service(service_id)
        if e:
            return e[0].query(e[1])
    
    def quit(self):
        """ Stops all services and kills itself """
        # First set alive to false otherwise, the service central can attempt
        # to restart stopped services
        self.alive = False
        for e in self.executors:
            e.stop_all()
        self.run_lock.acquire()
        try:
            self.run_lock.notify()
        finally:
            self.run_lock.release()
        while not self.alive:
            time.sleep(0.1)
    
    def get_service(self, service_id):
        """ Gets a handle to the actual service object.
        
        The convirt process can then call any method defined 
        on the service just like its any other instance (even if 
        the service is running in a separate process
        """
        e = self._get_executor_service(service_id)
        if e:
            return e[0].get_service(e[1])
    
    #
    #information functions below
    #
    
    def get_num_executors(self):
        return len(self.executors)
    
    def get_num_services(self):
        return len(self.services)

    #
    #internal functions below
    #
    
    #Checks to see if a service is independent
    def _is_independent(self, svcToBeChecked, services, dependencies):
        for svc in services:
            if (svcToBeChecked.id, svc.id) in dependencies:
                return False
        else:
            return True

    #Removes all dependencies where row is the parent
    def _remove_deps(self, svc, dependencies):
        for d in dependencies[:]:
            (dependent,parent) = d
            if parent == svc.id:
                dependencies.remove(d)
    
    #Given a list of services and dependencies returns either:
    # i.  An ordered list of services which does not violate the dependencies
    # ii. An exception that a cycle has been detected in the dependencies
    def _order(self, services, dependencies):
        count = 0
        ordered = []
        while len(services) != 0:
            count = count + 1
            if count > len(services):
                raise ServiceException("Cycle detected in dependencies" + to_str(dependencies))
            svc = services.pop(0)
            #if s does not have a dependency start it
            if self._is_independent(svc, services, dependencies):
                self._remove_deps(svc, dependencies)
                count = 0
                ordered.append(svc)
            else:
                services.append(svc)
        return ordered

