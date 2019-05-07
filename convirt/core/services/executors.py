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

from threading import Thread
from convirt.core.services.core import Service, ServiceException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
from convirt.core.utils.utils import to_unicode,to_str
import logging

logger = logging.getLogger("convirt.services")

enable_processes = True
try:
    from processing import Process
    from Pyro.core import ObjBase, Daemon, getProxyForURI, initClient
    from Pyro.naming import NameServerLocator
    from Pyro.errors import NamingError
    try:
        NameServerLocator().getNS()
    except NamingError:
        enable_processes = False
except ImportError:
    enable_processes = False

#######################
## Executor Interface
#######################
class Executor:
    """ This interface defines what an executor is supposed to do. The executor
    is responsible for maintaining a running instance of a service. Various
    methods of execution such as thread or processes are supported.

    The reason why executor and service interfaces are separate is because
    the service implementer should not have to worry about how his service
    is going to be executed. We should be able to execute services seamlessly
    whether they are in-process or out-process.
    """

    def start(self, service, service_id, dbconn, service_deps):
        """Starts a service with service_id"""
        pass

    def check(self):
        """Checks the health of each service and reboots if necessary"""
        pass
    
    def query(self, service):
        """Queries the status of a service"""
        pass
    
    def get_service(self, service):
        """Returns the running service object"""
        pass
    
    def stop(self, service):
        """Stops a service"""
        pass
    
    def stop_all(self):
        """Stops all services run by this executor"""
        pass
    
    def kill(self, service):
        """Forcefully stops a service"""
        pass

if enable_processes:
    ####################
    ## Process Executor
    ####################
    class ProcessInst(Process):
        """ The process instance is a wrapper for a service
        that is supposed to run inside a separate process.

        The process management is done using processing package.
        The communication between the main process and the service
        is achieved using Pyro. Therefore, using ProcessExecutor requires
        Pyro name server to be running.

        The pyro_object generated in this class is a portal to the actual
        service object. That is why we call the delegateTo function. Any method
        call that comes from the Pyro protocol will be searched in ObjBase first.
        If not found, the method is delegated to the service object. This allows
        the convirt process to call ANY method they like on the service object
        (as long as the inputs and outputs of the function are picklable)
        """

        def __init__(self, service, db_conn_string):
            self.service = service
            self.db_conn_string = db_conn_string
            Process.__init__(self)

        def run(self):
            #Run pyro daemon first
            self.pd = PyroRemoteDaemon(self.service)
            self.pd.configure()
            self.pd.start()
            #now setup the database
            engine = create_engine(self.db_conn_string)
            self.service.dbconn = sessionmaker(bind=engine)
            #dynamic wrapping of stop function for service
            self.stop_service_fn = self.service.stop
            self.service.stop = self.stop
            #This call should always be last
            #because the service _exec is supposed to *not* return
            self.service._exec()

        def stop(self):
            #first stop the daemon so that no further requests can come in
            self.pd.stop()
            self.stop_service_fn()

    class PyroRemoteDaemon(Thread):
        """For each process, we need a separate Daemon thread so that
        we can listen for pyro messages.

        This thread has a reference to the ProcessInst object and will
        register it under the id service.getid(). The process executor
        can then access this process (and the service running inside) via
        this registered name.

        It is important that the cleanup is called on this object as it will
        deregister the name to avoid communication errors.
        """

        def __init__(self, service_obj):
            self.service_obj = service_obj
            self.service_id = service_obj.getid()
            Thread.__init__(self)

        def configure(self):
            pyro_obj = ObjBase()
            pyro_obj.delegateTo(self.service_obj)
            #Start the Pyro Daemon and register the ProcessInst object
            self.pd = pd = Daemon()
            ns = NameServerLocator().getNS()
            pd.useNameServer(ns)
            pyro_id = "REMOTESVC" + to_str(self.service_id)
            #Remove any existing reference to this id
            try:
                ns.unregister(pyro_id)
            except NamingError:
                #the name is not found, which is fine
                pass
            pd.connect(pyro_obj, pyro_id)
            #set the pyro self reference
            self.service_obj.set_external_ref(pd.getProxyForObj(pyro_obj))

        def run(self):
            # Now we wait for requests
            self.pd.requestLoop()

        def stop(self):
            self.pd.shutdown()

    class ProcessExecutor(Executor):
        """ ProcessExecutor is the main driver for creating the 
        different processes that execute the services

        it can natively check whether process are alive using the processing
        package just like in check() and query() functions. However for any
        additional functionality (such as calling stop() on the service)
        it needs to rely on Pyro to contact the service. It does that using
        getPyroObj... functions which build a PYRO URI discoverable by the pyro
        name server.
        """

        def __init__(self):
            self.processes = []
            #check if pyro name server is runnign
            try:
                NameServerLocator().getNS()
            except NamingError:
                raise ServiceException("Pyro name server is not found. \
                                       Please run pyro-ns")
            initClient()

        def startProcess(self, process):
            process.start()
            proxy_service = None
            while True:
                try:
                    if proxy_service is None:
                        proxy_service = self.get_po_process(process)
                    if proxy_service.is_ready():
                        break
                    time.sleep(0.1)
                except NamingError:
                    #pyro object not ready yet
                    pass

        def start(self, _service, service_id, dbconn, service_deps):
            #a separate process cannot build dbconn so we need to get the url
            temp = dbconn()
            try:
                db_conn_string = to_str(temp.get_bind(None).url)
            finally:
                temp.close()
            service = _service(service_id, Service.MODE_PROCESS, None)
            service.set_dependencies(service_deps)
            process = ProcessInst(service, db_conn_string)
            self.processes.append(process)
            self.startProcess(process)
    
        def check(self):
            revived = []
            for p in self.processes[:]:
                if not p.isAlive():
                    logger.debug("dead process found")
                    newP = ProcessInst(p.service, p.db_conn_string)
                    self.processes.remove(p)
                    self.processes.append(newP)
                    self.startProcess(newP)
                    revived.append(newP.service.getid())
            return revived
        
        def find_process(self, _service):
            for p in self.processes:
                if isinstance(p.service, _service):
                    return p
            else:
                return None
        
        def query(self, _service):
            p = self.find_process(_service)
            if p:
                return t.isAlive()
            else:
                return False
        
        #the following functions need to be sent using Pyro
        def get_po_service(self, _service):
            return self.get_po_process(self.find_process(_service))
        
        def get_po_process(self, process):
            return getProxyForURI("PYRONAME://REMOTESVC" + \
                                  to_str(process.service.getid()))
        
        def get_service(self, _service):
            po = self.get_po_service(_service)
            return po
        
        def stop(self, _service):
            p = self.find_process(_service)
            po = self.get_po_process(p)
            if p:
                po._stop()
                self.processes.remove(p)
        
        def stop_all(self):
            for p in self.processes[:]:
                self.get_po_process(p)._stop()
                self.processes.remove(p)
        
        def kill(self, _service):
            p = self.find_process(_service)
            if p:
                p.get_po_process(p)._stop()
                p.terminate()
                self.processes.remove(p)
    
####################
## Thread Executor
####################
class ThreadInst(Thread):
    """ The thread instance object encapsulates a service running in a thread
    Since we are running within the same process, data communication is very
    easy, just calling the methods on the service object would suffice
    """

    def __init__(self, service):
        self.service = service
        Thread.__init__(self)
    
    def run(self):
        self.service._exec()
    
    def stop(self):
        self.service._stop()

if enable_processes:
    class PyroLocalDaemon(Thread):
        ##Only one instance of this should be running since all threads that
        ##ThreadExecutor runs is under the same process
    
        def register_service(self, service_obj):
            pyro_obj = ObjBase()
            pyro_obj.delegateTo(service_obj)
            service_id = service_obj.getid()
            pyro_id = "LOCALSVC" + to_str(service_id)
            ns = self.pd.getNameServer()
            #Remove any existing reference to this id
            try:
                ns.unregister(pyro_id)
            except NamingError:
                #the name is not found, which is fine
                pass
            self.pd.connect(pyro_obj, pyro_id)
            service_obj.set_external_ref(self.pd.getProxyForObj(pyro_obj))
            service_obj.__pyro_obj = pyro_obj

        def unregister_service(self, service_obj):
            self.pd.disconnect(service_obj.__pyro_obj)
    
        def configure(self):
            #Start the Pyro Daemon and register the ProcessInst object
            self.pd = pd = Daemon()
            ns = NameServerLocator().getNS()
            pd.useNameServer(ns)
            logger.debug("Local Pyro started")
    
        def run(self):
            # Now we wait for requests
            self.pd.requestLoop()
    
        def stop(self):
            self.pd.shutdown()

class ThreadExecutor(Executor):
    """ This class is responsible for starting a service inside a thread
    using the ThreadInst object

    Check() function walks the thread array and restarts any dead threads

    Query() returns the status of a thread given a service class

    The rest of the functions are straight-forward.
    
    Naming Convention
    _service means service CLASS.
    service means service INSTANCE.
    """
    
    def __init__(self):
        self.threads = []
        if enable_processes:
            self.pyro_daemon = PyroLocalDaemon()
            self.pyro_daemon.configure()
            self.pyro_daemon.start()

    def start(self, _service, service_id, dbconn, service_deps):
        service = _service(service_id, Service.MODE_THREAD, dbconn)
        service.set_dependencies(service_deps)

        if enable_processes:
            self.pyro_daemon.register_service(service)

        threadInst = ThreadInst(service)
        self.threads.append(threadInst)
        threadInst.start()
        while not service.is_ready():
            time.sleep(0.1)
    
    def check(self):
        revived = []
        for t in self.threads[:]:
            if not t.isAlive():
                logger.debug("dead thread found. restarting")
                #FIXME: TEST if this gels with the local pyro
                #should we reinstantiate local pyro copy? the service instance
                #is the same..
                newT = ThreadInst(t.service)
                self.threads.remove(t)
                self.threads.append(newT)
                newT.start()
                while not newT.service.is_ready():
                    time.sleep(0.1)
                revived.append(newT.service.getid())
        return revived
    
    def find_thread(self, _service):
        for t in self.threads:
            if isinstance(t.service, _service):
                return t
    
    def query(self, _service):
        t = self.find_thread(_service)
        if t:
            return t.isAlive()
        else:
            return False
    
    def get_service(self, _service):
        t = self.find_thread(_service)
        if t:
            return t.service
    
    def stop(self, _service):
        t = self.find_thread(_service)
        if t:
            if enable_processes:
                self.pyro_daemon.unregister_service(t.service)
            t.stop()
            self.threads.remove(t)
    
    def stop_all(self):
        if enable_processes:
            self.pyro_daemon.stop()
        for t in self.threads[:]:
            t.stop()
            self.threads.remove(t)
