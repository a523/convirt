#!/usr/bin/env python
#
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
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# 
#
# author : Jd <jd_jedi@users.sourceforge.net>
#

from convirt.core.utils.utils import PyConfig
import re, os,time,transaction

from convirt.model.SPRelations import StorageDisks
from convirt.core.utils.NodeProxy import Node
from convirt.model.ManagedNode import ManagedNode
from convirt.core.utils.constants import *
from convirt.core.utils.utils import getHexID
from sqlalchemy import *
from sqlalchemy import orm
from sqlalchemy.orm import relation, backref
from sqlalchemy.types import *
from sqlalchemy.schema import Index, UniqueConstraint
from convirt.model import DeclarativeBase,Entity, DBSession
from convirt.model.DBHelper import DBHelper
from convirt.model import DBSession
from convirt.model.availability import AvailState
import logging
LOGGER = logging.getLogger("convirt.model")
from convirt.core.utils.utils import to_unicode,to_str
import convirt.core.utils.constants
constants=convirt.core.utils.constants

import logging
LOGGER = logging.getLogger("convirt.model")

# Contains base classes representing
#        VM,
#        VMConfig,
#        VMStats,
#        VMOperationsException
# Also, has utility classes
#        DiskEntry
#        NetworkEntry

class VMOperationException(Exception):
   def __init__(self, message, errno = None):
      if errno:
         Exception.__init__(self, (errno, message))
      else:
         Exception.__init__(self,  message)
      self.message = message
      self.errno = errno

   def __repr__(self):
      if self.errno != None:
         return "[Error %s]: %s" % (to_str(self.errno), self.message)
      else:
         return self.message
      


class VM(DeclarativeBase):
    """
    This represent Doms. It encapsulates information about
    running virtual machine : state as well as resource stats
    """
    RUNNING  = 0
    PAUSED   = 2
    SHUTDOWN = 3
    CRASHED  = 4
    NOT_STARTED    = -1
    UNKNOWN  = -2

    __tablename__ = 'vms'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    vm_config = Column(Text)
    type=Column(Unicode(50),default='NONE')
    image_id=Column(Unicode(50))
    template_version=Column(Float)
    os_flavor=Column(Unicode(50))
    os_name=Column(Unicode(50))
    os_version=Column(Unicode(50))
    status=Column(Unicode(50))
    created_user = Column (Unicode(255))
    created_date = Column (DateTime)
    current_state = relation(AvailState, \
                             primaryjoin = id == AvailState.entity_id, \
                             foreign_keys=[AvailState.entity_id],\
                             uselist=False, \
                             cascade='all, delete, delete-orphan')


    __mapper_args__ = {'polymorphic_on': type}

    def __init__(self, node, config=None,vm_info=None):
        if not config and vm_info is None :
            raise Exception("config and vm_info both can not be None")
        self.vm_config=""
        if config:
            for name, value in config.options.iteritems():
                self.vm_config+="%s = %s\n" % (name, repr(value))
        
        self.node = node
        self._config = config
        self._vm_info= vm_info

        self.id = None
        self.name = None
        self._is_resident = False
        self.pid=None  #to keep track of the dom once it is started
        # Now call the init method that would initialized the above
        # state variables
        self.init()
        self.id = getHexID(self.name,[constants.DOMAIN]) # id is name, need to resolve this with guid
        self.current_state = AvailState(self.id, self.NOT_STARTED, \
                                        AvailState.NOT_MONITORING, \
                                        description = u'New VM')

    @orm.reconstructor
    def init_on_load(self):
        self.node=None
        self.pid=None        
        self._config = VMConfig(config=self.vm_config)
        #self._config.options = get_config(self.vm_config)
        self._vm_info= None
        self._is_resident = False


    def stop_monitoring(self):
        self.current_state.monit_state = AvailState.NOT_MONITORING

    def start_monitoring(self):
        self.current_state.monit_state = AvailState.MONITORING

    def get_state(self):
        return self.current_state.avail_state

    def get_ui_state(self):
        #this function returns a bucketed version of states
        #each RUNNING, PAUSED maps to RUNNING
        #each SHUTDOWN, CRASHED, NOT_STARTED maps to SHUTDOWN
        raw_state = self.get_state()
        if(raw_state == self.RUNNING or
           raw_state == self.UNKNOWN):
            return self.RUNNING
        elif raw_state == self.PAUSED:
            return self.PAUSED
        else:
            return self.SHUTDOWN


    def is_monitored(self):
        return (self.current_state.monit_state == AvailState.MONITORING)

    # to be provided by the derived class
    # set id, name, and _is_resident state
    def init(self):
       raise Exception("Must be implemented by derived class.")


    def get_platform(self):
       raise Exception("Platform not defined!!" + to_str(self.__class__))

    # interface methods

    def is_running(self):
        running=False
        if self.get_state() in [self.RUNNING,self.PAUSED,self.UNKNOWN]:
            running = True
        return running
    
    """ Is the vm dom0 """
    def isDom0(self):
       return False # for most platforms

    def isDomU(self):
       return True # for most platforms

    """ refresh the vm information """
    def refresh(self):
       try:          
          self._vm_info = self.node.get_vmm().refresh(self.pid)
          self.init()
       except VMOperationException, ex:
          self._vm_info = None
          self._is_resident = False

    """ Save the vm to a given file """
    def _save(self, filename):
       self.node.get_vmm().save(self.pid, filename)


    def _reboot(self):
       self.node.get_vmm().reboot(self.pid)
       self._vm_info =  None
       self._is_resident = False


    def _start(self, config = None):
       if not config:
          self.node.get_vmm().start(self._config)
       else:
          self.node.get_vmm().start(config)
#       self.start_monitoring()
#       self.node.refresh_vm_avail()

    def _shutdown(self):       
       self.node.get_vmm().shutdown(self.pid)
       self._vm_info =  None
       self._is_resident = False
#       self.stop_monitoring()
#       self.node.refresh_vm_avail()


    def _destroy(self):
       self.node.get_vmm().destroy(self.pid)
       self._vm_info =  None
       self._is_resident = False
#       self.stop_monitoring()
#       self.node.refresh_vm_avail()


    def _pause(self):
       res = self.node.get_vmm().pause(self.pid)
#       self.node.refresh_vm_avail()
       return res

    def _unpause(self):
       res = self.node.get_vmm().unpause(self.pid)
#       self.node.refresh_vm_avail()
       return res

    def _suspend(self):
       self.node.get_vmm().suspend(self.pid)
#       self.node.refresh_vm_avail()

    def _resume(self):
       self.node.get_vmm().resume(self.pid)
#       self.node.refresh_vm_avail()

    def _migrate(self, dest,live, port):
       self.node.get_vmm().migrate(self.pid, dest, live, port)


    def is_resident(self):
       return self._is_resident

    def getVCPUs(self):
       c = self.get_config()
       if c :
           return c['vcpus']
       return 1

    # change to live running VM
    def setVCPUs(self, value):
       self.node.get_vmm().setVCPUs(self.pid, value)


    def setMem(self,value):
       self.node.get_vmm().setMem(self.pid, value)

    # attach disks in memory
    def attachDisks(self,attach_disk_list):
       self.node.get_vmm().attachDisks(self.pid,attach_disk_list)

    # detach disks in memory
    def detachDisks(self,detach_disk_list):
       self.node.get_vmm().detachDisks(self.pid,detach_disk_list)

    # Associate a config
    def get_config(self):
       return self._config 
    
    def set_config(self, config):
       self._config=config
       pass

    def get_info(self):
       return self._vm_info

    # get some metric information
    # TBD: Needs some standardization on what minimal info 
    def get_snapshot(self):
       pass


    # expose the vm details via getitem
    # Need some standardization so that UI can display it.
    def __getitem__(self, param):
       pass

    # display strings
    def get_state_string(self):
       state = self.get_state()
       if state == self.RUNNING: return "Running"
       elif state ==  self.PAUSED : return "Paused"
       elif state == self.SHUTDOWN: return "Shutdown"
       elif state == self.CRASHED: return "Crashed"
       elif state == self.UNKNOWN: return "Unknown"
        
       return "Unknown"

    # return (cmd, args) for the console
    def get_console_cmd(self):
       pass

    # get the vnc port to be used
    def get_vnc_port(self):
       return None

    # should we use the graphical display or console
    def is_graphical_console(self):
       return False


    def is_hvm(self):
       if self._config is None:
          return None
       else:
          return self._config.is_hvm()

    def get_template_info(self):
        """
        returns template name, template's current version and vm & template version match
        for imported vms template name alone is available from config file
        """
        template_info={}
        template_info["template_name"]=self._config['image_name']
        template_info["template_version"]='0.0'
        template_info["version_comment"]=''
        
        try:
            if self.image_id is not None:                
                from convirt.model.ImageStore import Image
                img=DBSession.query(Image).filter(Image.id==self.image_id).one()
                template_info["template_name"]=img.name
                template_info["template_version"]=to_str(self.template_version)
                template_info["version_comment"]=''
                if self.template_version != img.version:
                    template_info["version_comment"]="*Current version of the Template is "+\
                                                    to_str(img.version)
        except Exception, e:
            LOGGER.error(e)
            pass
        return template_info

    def get_os_info(self):
        """
        returns os name, os version
        for imported vms os name may not be available from config file
        """
        os_info={}
        os_info["name"]=self.os_name
        os_info["version"]=self.os_version
        if os_info["name"] is None:
            os_info["name"]=self._config['os_name']
            os_info["version"]=self._config['os_version']
        if os_info["name"] is None:
            os_info["name"]=''
            os_info["version"]=''
        return os_info

    def get_state_dict(self):
        state_dict = {}
        state_dict['start']=[0,1]
        state_dict['shutdown']=[3]
        state_dict['kill']=[3]
        state_dict['pause']=[2]
        state_dict['unpause']=[0,1]
        state_dict['reboot']=[0,1]
        return state_dict

    ###HAS TO BE REFACTORED
    def check_action_status(self,action,cmd_result):

        values=self.get_state_dict()[action]

        wait = self.get_wait_time(action)
        timeout_err = action+' failed due to timeout'
        
        if action == 'reboot':
            rebooted=self.check_reboot_state(wait)
            if rebooted:
                return True
            else:
                raise Exception(timeout_err)

        if action == 'pause':
            paused=self.check_pause_state(values,wait,cmd_result)
            if paused:
                self.status = constants.PAUSED
                transaction.commit()
                return True
            else:
                raise Exception(timeout_err)

        if action == 'unpause':
            unpaused=self.check_unpause_state(values,wait,cmd_result)
            if unpaused:
                self.status = constants.RESUMED
                transaction.commit()
                return True
            else:
                raise Exception(timeout_err)

        result = self.check_state(values,wait)
        if result == False :
            raise Exception(timeout_err)
        else:
            return True
        
    def check_state(self,values,wait_time):

        for counter in range(0,wait_time):
            time.sleep(1)
            self.node.refresh()
            metrics=self.node.get_metrics()
            data_dict=metrics.get(self.name)

            if data_dict is not None:
                state=data_dict.get('STATE')
            else:
                state=self.SHUTDOWN

            if state in values:
                return True
        return False
    
    def check_pause_state(self,values,wait_time,cmd_result):
        ###method to check if the vm has been paused
        ###within the wait time
        return self.check_state(values,wait_time)
        

    def check_unpause_state(self,values,wait_time,cmd_result):
        ###method to check if the vm has been unpaused
        ###within the wait time
        return self.check_state(values,wait_time)

    def check_reboot_state(self,wait_time):
        ###method to check if the vm has been rebooted
        ###within the wait time

        pass

    def status_check(self):
        ###method to decide whether to proceed with metrics collection
        if self.status==constants.MIGRATING:
            msg = "VM "+self.name+", is on migration. "+\
                        "Not updating current metrics."
            return (False,msg)
        return (True,None)

    def get_wait_time(self, action):
        config = self.get_config()

        wait_time=config[action+'_time']
        if wait_time is None:
            import tg
            wait_time = tg.config.get(action+'_time')
            wait_time=int(wait_time)

        return wait_time

    def get_attribute_value(self, name, default):
        value=self.get_config().get(name)
        if value is None:
            value=default
        return value
    
    def get_vnc_log_level(self):
        config = self.get_config()

        log_level=config.get('vnc_log_level')
        if log_level is None:
            import tg
            log_level = tg.config.get('vnc_log_level')
            log_level=int(log_level)
        if log_level>=4:
            log_level=4
        print log_level
        return log_level

Index('vm_id',VM.id)

# Disk entry class : very generic.
class DiskEntry:
    """This class provides a structured representation of the disk
    string. The following attributes are available:

     type:     {file|phy}
     filename: the path to the VBD or device
     device:   the device to be used in the guest system
     mode:     {r|w|w!}
     """

    def __init__(self, input):
        if isinstance(input, basestring):
            # non-greedy for the disk type
            m = re.match("^((tap:)?.*?):(.*),(.*),(.*)$", input)
            if m:
                self.type = m.group(1)
                self.filename = m.group(3)
                self.device = m.group(4)
                self.mode = m.group(5)
            else:
                print "disk entry : No regexp match for", input
                raise Exception("could not parse disk "+ input)
        elif type(input) in (list, tuple):
            self.type, self.filename, self.device, self.mode = input

    def __repr__(self):
        return "%s:%s,%s,%s" % (self.type, self.filename, self.device,
                                self.mode)




# class to represent disk in an image.
class ImageDiskEntry(DiskEntry):
   CREATE_DISK = "CREATE_DISK"
   USE_DEVICE = "USE_DEVICE"
   USE_ISO = "USE_ISO"
   USE_REF_DISK = "USE_REF_DISK"
   
   def __init__(self, input, image_conf):
      DiskEntry.__init__(self, input)
      self.option = None

      self.disk_create = "no"
      self.size = None
      self.disk_type = ""

      self.image_src = None
      self.image_src_type = None
      self.image_src_format = None

      self.set_image_conf(image_conf)


   def set_image_conf(self, image_conf):
      self.image_conf = image_conf
      self.init()
      
   def init(self):
      if self.image_conf is None:
         return
      device = self.device

      # Vars
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

      self.option = self.CREATE_DISK
      self.disk_create = self.image_conf[create_var]
      self.disk_type = self.image_conf[disk_type_var]
      self.size = self.image_conf[size_var]

      if not self.disk_type :
         if self.type == "file":
            self.disk_type = "VBD"
         if self.type == "phy": # assume physical device e.g. cdrom
            self.disk_type = ""

      
      if self.image_conf[image_src_var] :
         self.option = self.USE_REF_DISK
      elif self.type == "phy" :
         self.option = self.USE_DEVICE
      elif self.type=="file" :
         if not self.size and self.filename != "":
            self.option = self.USE_ISO
            self.disk_type = "ISO"


      if self.option == self.CREATE_DISK or self.option == self.USE_REF_DISK:
         if not self.size:
            self.size = 10000
         if not self.filename:
            self.filename = "$VM_DISKS_DIR/$VM_NAME.disk.xm"
            
      self.image_src = self.image_conf[image_src_var]
      self.image_src_type = self.image_conf[image_src_type_var]
      self.image_src_format = self.image_conf[image_src_format_var]

      self.fs_type = self.image_conf[disk_fs_type_var]


class vifEntry:
   def __init__(self, vif_str, image_config=None):
      self.vif_map = {}
      if vif_str:
         self.vif_map= dict([[z.strip() for z in y.split("=")]
                             for y in [x.strip()
                                       for x in vif_str.split(",")]])
   def get_mac(self):
      return self.vif_map.get("mac")

   def set_mac(self, v):
      self.vif_map["mac"] = v


   def get_bridge(self):
      return self.vif_map.get("bridge")

   def set_bridge(self,v):
      self.vif_map["bridge"] = v

   def get_item(self,item):
      return self.vif_map.get(item,"")

   def __repr__(self):
      s = ''
      def_keys = ["mac", "bridge"]
      keys = self.vif_map.keys()
      for k in def_keys:
         if k in keys:
            keys.remove(k)

      for k in def_keys + keys:
         v=self.vif_map.get(k)
         if v is not None:
            if s != '':
               s = s + ","
            s = s + "%s=%s" %(k,v)
      return s


# Network class
#class NetworkEntry:

# Keep track of type and usage of each disk associated with this VM.
import stat
class VMStorageStat:
   STORAGE_STATS = "STORAGE_STATS"
   DISK_STATS = "DISK_STATS"
   LOCAL_ALLOC = "LOCAL_ALLOCATION"    # Total
   SHARED_ALLOC = "SHARED_ALLOCATION"  # Total

   DISK_NAME = "DISK_NAME"
   DISK_SIZE = "DISK_SIZE"
   DISK_DEV_TYPE = "DEV_TYPE"
   DISK_IS_LOCAL = "IS_LOCAL"

   BLOCK = "BLOCK"
   FILE = "FILE"
   UNKNOWN = "UKNOWN"

   STORAGE_DISK_ID = "STORAGE_DISK_ID"
   
   GB_BYTES = 1024.0 * 1024.0 * 1024.0
   
   def __init__(self, config):
      self.config = config
      if self.config[self.STORAGE_STATS]:
         self.storage_stats= self.config[self.STORAGE_STATS]
      else:
         self.storage_stats = {}
         self.config[self.STORAGE_STATS] = self.storage_stats

      self.disk_stats = {}
      if self.storage_stats is not None :
         ds = self.storage_stats.get(self.DISK_STATS)
         if ds is None:
            self.storage_stats[self.DISK_STATS] = self.disk_stats # initial value of {}
         else:
            self.disk_stats = ds
            
      self.local_allocation = self.storage_stats.get(self.LOCAL_ALLOC)
      if not self.local_allocation:
         self.local_allocation = 0
      self.shared_allocation = self.storage_stats.get(self.SHARED_ALLOC)
      if not self.shared_allocation:
         self.shared_allocation = 0

      self.storage_disk_id = None
      
      #def __repr__(self):
      #   return str(self.storage_stats)

   def get_storage_disk_id(self, filename):
      file_exists = False
      for de in self.config.getDisks():
          if filename == de.filename:
              file_exists = True
      
      storage_disk_id = ""
      if file_exists == True:
          de_stat = self.disk_stats.get(filename)
          if de_stat is not None :
              storage_disk_id = de_stat[self.STORAGE_DISK_ID]
              return storage_disk_id
          else:
              return storage_disk_id
      else:
          return storage_disk_id

   def set_storage_disk_id(self, filename, storage_disk_id):
      file_exists = False
      for de in self.config.getDisks():
        if filename == de.filename:
            file_exists = True
      
      if file_exists == True:
        de_stat = self.disk_stats.get(filename)
        if de_stat is not None :
            de_stat[self.STORAGE_DISK_ID] = storage_disk_id

        else:
            de_stat = { self.DISK_NAME : filename,
                         self.DISK_SIZE : 0,
                         self.DISK_DEV_TYPE : self.UNKNOWN,
                         self.DISK_IS_LOCAL : not is_remote,
                         self.STORAGE_DISK_ID : storage_disk_id
                         }

      else:
         print "disk not found in ", disk_names
         raise Exception("disk " + filename + " not found" )

       
   def set_remote(self, filename, is_remote):
      disk_names = [de.filename for de in self.config.getDisks()]
      if filename in disk_names:
          de_stat = self.disk_stats.get(filename)
          if de_stat is not None :
             de_stat[self.DISK_IS_LOCAL] = not is_remote
          else:
             de_stat = { self.DISK_NAME : filename,
                         self.DISK_SIZE : 0,
                         self.DISK_DEV_TYPE : self.UNKNOWN,
                         self.DISK_IS_LOCAL : not is_remote
                         #self.STORAGE_DISK_ID : ""
                         }
             self.disk_stats[filename] = de_stat
      else:
         print "disk not found in ", disk_names
         raise Exception("disk " + filename + " not found" )
         
   def get_remote(self, filename):
      disk_names = [de.filename for de in self.config.getDisks()]
      if filename in disk_names:
          de_stat = self.disk_stats.get(filename)
          if de_stat is not None :
             return (not de_stat[self.DISK_IS_LOCAL])
          else:
             return False
      else:
         return False
   
         
   def update_stats(self):
       for de in self.config.getDisks():
          disk_size,disk_dev_type = self.get_disk_size(de)

          de_stat = self.disk_stats.get(de.filename)
          disk_is_local = True # for now.
             
          if de_stat :
             de_stat[self.DISK_SIZE] = disk_size
             de_stat[self.DISK_DEV_TYPE] = disk_dev_type

             try:
                 storage_disk_id = de_stat[self.STORAGE_DISK_ID]
             except Exception, ex:
                de_stat[self.STORAGE_DISK_ID] = None
          else:
             storage_disk_id = self.get_storage_disk_id(de.filename)
             de_stat = { self.DISK_NAME : de.filename,
                         self.DISK_SIZE : disk_size,
                         self.DISK_DEV_TYPE : disk_dev_type,
                         self.DISK_IS_LOCAL : disk_is_local,
                         self.STORAGE_DISK_ID : storage_disk_id
                         }
             self.disk_stats[de.filename] = de_stat
       # some disks might have been deleted
       # as well as recompute totals.
       total_local = 0          
       total_shared = 0

       disk_names = [de.filename for de in self.config.getDisks()]
       to_be_deleted = []
       for ds in self.disk_stats.itervalues():
          d_size = ds[self.DISK_SIZE]
          if d_size is None:
             d_size = 0
             
          if ds[self.DISK_NAME] not in disk_names:
             to_be_deleted.append(ds[self.DISK_NAME])
          else:
             if ds[self.DISK_IS_LOCAL]:
                total_local += d_size
             else:
                total_shared += d_size


       for key in to_be_deleted:
          del self.disk_stats[key]

       #import pprint; pprint.pprint( self.disk_stats )
       
       self.storage_stats[self.LOCAL_ALLOC]= total_local
       self.storage_stats[self.SHARED_ALLOC]= total_shared
       self.config[self.STORAGE_STATS] = self.storage_stats

   def get_shared_total(self):
      total = self.storage_stats.get(self.SHARED_ALLOC)
      if total:
         total = total / (self.GB_BYTES)
      else:
         total = 0

      return total

   def get_local_total(self):
      total = self.storage_stats.get(self.LOCAL_ALLOC)
      if total:
         total = total / (self.GB_BYTES)
      else:
         total = 0
      return total


   def get_disk_size(self, de):
       size = None
       dev_type = self.UNKNOWN

       filename=de.filename
       if filename and self.config.managed_node.node_proxy.file_exists(de.filename):
          f_stat = self.config.managed_node.node_proxy.stat(filename)
          if self.config.managed_node.is_remote():
             mode = f_stat.st_mode
          else:
             mode = f_stat[stat.ST_MODE]
          dev_type = self.FILE
          if stat.S_ISREG(mode):
             dev_type=self.FILE
          else:
             dev_type = self.BLOCK
          
          if ((not stat.S_ISREG(mode)) and (not stat.S_ISBLK(mode))):
             print "unknown disk type :", de.filename, f_stat
             return (None, dev_type)

          if filename.find("/dev") == 0:
             # assume block device
             dev_type = self.BLOCK
             try:
                try:
                   cmd="""python -c "import os; filename='%s'; fd=open(filename,'r'); fd.seek(0,2); size=fd.tell() ; fd.close(); print size" """ % filename
                   (output, code) = self.config.managed_node.node_proxy.exec_cmd(cmd)
                   #print "cmd ", cmd, " code -> " , code, " out-> ", output
                   if code == 0:
                      size=eval(output)
                   else:
                      raise Exception(output)
                except Exception, ex:
                   print "error getting disk size for ", filename, ex
             finally:
                pass
          else:
             if self.config.managed_node.is_remote():
                size = f_stat.st_size
             else:
                size = f_stat[stat.ST_SIZE] # TO DO Sparse handling
       else:
          print "Error getting disk size for", filename, \
                "(filename does not exist.)"
          
       return (size, dev_type)

# DomConfig object, will use python config 
class VMConfig(PyConfig):
    """
    reprsents startup config object (information in the conf file)
    """
    
    # Module variable.
    imps = ["import sys",
            "import os",
            "import os.path",
            ]
    

    signature = "# Automtically generated by ConVirt\n"



    # DomConfig follows
    def __init__(self, node=None, filename = None,config=None):
        """
        read stuff from file and populate the config
        when filename is None, creates an empty config
        """
        
        self.convirt_generated = False
        self.storage_stats = None
        
        PyConfig.__init__(self,
                          node,
                          filename,
                          VMConfig.signature,config)

        if filename is None and config is None: return

        if len(self.lines) > 0:
            if self.lines[0].find(self.signature) >= 0:
                    self.convirt_generated = True
            
        if self["name"] is None:
            raise Exception("No dom name specified")

        #pick up the name from the file
        self.name = self["name"]
        self.id = self["uuid"]

    # read_config
    def read_config(self, init_glob=None, init_locs=None):
        # Leverage the fact that conf files are python syntax.
        # save on parsing code
        # Create global and local dicts for the file.
        # Initialize locals to the vars.
        globs = {}
        locs = {}
        cmd = '\n'.join(self.imps)
        # Use exec to do the standard imports and
        # define variables we are passing to the script.
        exec cmd in globs, locs
        return PyConfig.read_config(self, globs, locs)

    # read_conf
    def read_conf(self, init_glob=None, init_locs=None):
        # Leverage the fact that conf files are python syntax.
        # save on parsing code
        
        # Create global and local dicts for the file.
        # Initialize locals to the vars.
        globs = {}
        locs = {}

        cmd = '\n'.join(self.imps)  

        # Use exec to do the standard imports and
        # define variables we are passing to the script.
        exec cmd in globs, locs
        return PyConfig.read_conf(self, globs, locs)
    
    def __setitem__(self, name, item):
        self.options[name] = item
        if name == "name":
            self.name = item

    # try to keep them in sync
    def set_name(self, name):
        self.name = name
        self["name"] = name
    
    def set_id(self, id):
        self.id = id
        self["uuid"] = id

    # get the configured disks
    # NOTE: do not change this to map, the order is important
    #       and is used at the time of provisioning for mapping disk
    #       entry template name to instantiated names
    def getDisks(self, image_config=None):
        """
        This method returns a more structured version of the config file's
        disk entry
        """
        reslist = []
        if self["disk"] is not None:
            for str in self["disk"]:
                if str !="":
                    reslist.append(ImageDiskEntry(str, image_config))
        return reslist

    def getNetworks(self, image_config=None):
        """
        This method returns a more structured version of the config file's
        vif entry
        """
        reslist = []
        if self["vif"] is not None:
            for str in self["vif"]:
                if str !="":
                    reslist.append(vifEntry(str, image_config))
        return reslist

    # Assumes that the file read contains single line values
    # now preserves the comments and order
    def write(self):
        """Writes the settings out to the filename specified during
        initialization"""
        self.name = self["name"]
        PyConfig.write(self)
        self.convirt_generated = True


    def is_convirt_generated(self):
        return self.convirt_generated

    # Get raw file content    
    def get_contents(self):
        f = self.managed_node.node_proxy.open(self.filename)
        lines = f.readlines()
        f.close()
        contents = "".join(lines)
        return contents

    # Write raw contents
    def write_contents(self, contents):
        """Writes the settings out to the filename specified during
        initialization"""
        outfile = self.managed_node.node_proxy.open(self.filename, 'w')
        outfile.write(contents)
        outfile.close()



    # Validate the config. Actual details to be supplied by the
    # derived class
    
    def validate(self):
        """Attempts to validate that the settings are not going to lead to
        any errors when the dom is started, and returns a list of the
        errors as strings"""

        result = []
        return result

    def is_hvm(self):
       if self["builder"] == "hvm" :
          return True
       else:
          return False

    # assumes valid disk entries. (not tempate ones)
    # For each disk that is exposed via host system,
    # update the size.
    def update_storage_stats(self):
       storage_stat =  self.get_storage_stats()
       storage_stat.update_stats()
       #import pprint; pprint.pprint(storage_stat.storage_stats)

    # map containing disk name / filename in dom0 and if it is remote or not.
    def set_remote(self, remote_map):
       storage_stat = self.get_storage_stats()
       for d in self.getDisks():
          d_name = d.filename
          is_remote = remote_map.get(d_name)
          if is_remote is not None:
             storage_stat.set_remote(d_name, is_remote)
             

    def get_storage_stats(self):
       if self.storage_stats is None:
          self.storage_stats = VMDiskManager(self)

       return self.storage_stats
       

class VMStats:
    """
    represents statatistics/measurements for a dom. (CPU, I/O etc)
    This is abstracted out so we can cut over to some other source for
    runtime statastics/measurements
    """

    def __init__(self, vm):
        """
        constructor, dom for which the stats are to be obtained.
        """
        self.vm = vm
        self.stat = {}

    def get_snapshot(self):
        # to be implemented by derived class
        return self.stat

class VMDisks(DeclarativeBase):
    __tablename__ = 'vm_disks'

    #Columns
    id = Column(Unicode(50), primary_key=True)
    vm_id = Column(Unicode(50), ForeignKey('vms.id'))
    disk_name = Column(Unicode(300))
    disk_size = Column(Float)
    dev_type = Column(Unicode(50))
    read_write = Column(Unicode(50))
    disk_type = Column(Unicode(50))
    is_shared = Column(Boolean)
    file_system = Column(Unicode(50))
    vm_memory = Column(Float)
    sequence = Column(Integer)
    
    #Relation
    fk_VMDisks_VM = relation('VM', backref='VMDisks')

    #Index
    #create index VMDisks_diskName on VMDisks(disk_name)
    
    def __init__(self):pass

class VMStorageLinks(DeclarativeBase):
    __tablename__ = 'vm_storage_links'

    #Composite unique constraint
    __table_args__ = (UniqueConstraint('vm_disk_id', 'storage_disk_id', name='ucVMStorageLinks'), {})

    #Columns
    id = Column(Unicode(50), primary_key=True)
    vm_disk_id = Column(Unicode(50), ForeignKey('vm_disks.id'))
    storage_disk_id = Column(Unicode(50), ForeignKey('storage_disks.id'))

    #Relation
    fk_VMStorageLinks_VMDisks = relation('VMDisks', backref='VMStorageLinks')
    fk_VMStorageLinks_StorageDisks = relation('StorageDisks', backref='VMStorageLinks')

    def __init__(self):pass
    
class VMDiskManager:
    STORAGE_STATS = "STORAGE_STATS"
    DISK_STATS = "DISK_STATS"
    LOCAL_ALLOC = "LOCAL_ALLOCATION"    # Total
    SHARED_ALLOC = "SHARED_ALLOCATION"  # Total
    
    DISK_NAME = "DISK_NAME"
    DISK_SIZE = "DISK_SIZE"
    DISK_DEV_TYPE = "DEV_TYPE"
    DISK_IS_LOCAL = "IS_LOCAL"
    
    BLOCK = "BLOCK"
    FILE = "FILE"
    UNKNOWN = "UKNOWN"
    
    STORAGE_DISK_ID = "STORAGE_DISK_ID"
    
    GB_BYTES = 1024.0 * 1024.0 * 1024.0

    def __init__(self, config):
        self.config = config
        self.storage_stats={}
        self.vm_id=None
        if self.config:
            vm = DBSession.query(VM).filter_by(id = to_unicode(config.id)).first()
            if vm:
                self.vm_id = vm.id
                self.storage_stats = self.get_storage_stats(vm.id)
            
        self.disk_stats = {}
        if self.storage_stats is not None :
            ds = self.storage_stats.get(self.DISK_STATS)
            if ds is None:
                self.storage_stats[self.DISK_STATS] = self.disk_stats # initial value of {}
            else:
                self.disk_stats = ds
            
        self.local_allocation = self.storage_stats.get(self.LOCAL_ALLOC)
        if not self.local_allocation:
            self.local_allocation = 0
        self.shared_allocation = self.storage_stats.get(self.SHARED_ALLOC)
        if not self.shared_allocation:
            self.shared_allocation = 0
        
        self.storage_disk_id = None

    def update_stats(self):
        vm = DBSession.query(VM).filter_by(id=self.config.id).first()
        if vm:
            disks = self.getDisks(vm.id)
        else:
            disks = self.config.getDisks()
        
        if disks:
            for de in disks:
                if vm:
                    filename = de.disk_name
                else:
                    filename = de.filename
                    
                disk_size,disk_dev_type = self.get_disk_size(de)
                de_stat = self.disk_stats.get(filename)
                disk_is_local = True # for now.
                    
                if de_stat :
                    de_stat[self.DISK_SIZE] = disk_size
                    de_stat[self.DISK_DEV_TYPE] = disk_dev_type
        
                    try:
                        storage_disk_id = de_stat[self.STORAGE_DISK_ID]
                    except Exception, ex:
                        de_stat[self.STORAGE_DISK_ID] = None
                else:
                    storage_disk_id = self.get_storage_disk_id(filename)
                    de_stat = { self.DISK_NAME : filename,
                                self.DISK_SIZE : disk_size,
                                self.DISK_DEV_TYPE : disk_dev_type,
                                self.DISK_IS_LOCAL : disk_is_local,
                                self.STORAGE_DISK_ID : storage_disk_id
                                }
                    self.disk_stats[filename] = de_stat
            
        # some disks might have been deleted
        # as well as recompute totals.
        total_local = 0          
        total_shared = 0
        
        if vm:
            disk_names = [de.disk_name for de in disks]
        else:
            disk_names = [de.filename for de in disks]
            
        
        to_be_deleted = []
        for ds in self.disk_stats.itervalues():
            d_size = ds[self.DISK_SIZE]
            if d_size is None:
                d_size = 0
                
            if ds[self.DISK_NAME] not in disk_names:
                to_be_deleted.append(ds[self.DISK_NAME])
            else:
                if ds[self.DISK_IS_LOCAL]:
                    total_local += d_size
                else:
                    total_shared += d_size
    
    
        for key in to_be_deleted:
            del self.disk_stats[key]
    
        #import pprint; pprint.pprint( self.disk_stats )
        
        self.storage_stats[self.LOCAL_ALLOC]= total_local
        self.storage_stats[self.SHARED_ALLOC]= total_shared
        self.config[self.STORAGE_STATS] = self.storage_stats

    def get_shared_total(self):
        total = self.storage_stats.get(self.SHARED_ALLOC)
        if total:
            total = total / (self.GB_BYTES)
        else:
            total = 0
        return total

    def get_local_total(self):
        total = self.storage_stats.get(self.LOCAL_ALLOC)
        if total:
            total = total / (self.GB_BYTES)
        else:
            total = 0
        return total


    def get_disk_size(self, de, filename=None):
        size = None
        dev_type = self.UNKNOWN
        
        try:
            if not filename:
                try:
                    filename=de.disk_name
                except Exception, ex:
                    filename=de.filename
                
            if filename == "/dev/cdrom":
                return (0, self.UNKNOWN)
    
            if filename and self.config.managed_node.node_proxy.file_exists(filename):
                f_stat = self.config.managed_node.node_proxy.stat(filename)
                if self.config.managed_node.is_remote():
                    mode = f_stat.st_mode
                else:
                    mode = f_stat[stat.ST_MODE]
                dev_type = self.FILE
                if stat.S_ISREG(mode):
                    dev_type=self.FILE
                else:
                    dev_type = self.BLOCK
                
                if ((not stat.S_ISREG(mode)) and (not stat.S_ISBLK(mode))):
                    print "unknown disk type :", filename, f_stat
                    return (None, dev_type)
        
                if filename.find("/dev") == 0:
                    # assume block device
                    dev_type = self.BLOCK
                    try:
                        try:
                            cmd="""python -c "import os; filename='%s'; fd=open(filename,'r'); fd.seek(0,2); size=fd.tell() ; fd.close(); print size" """ % filename
                            (output, code) = self.config.managed_node.node_proxy.exec_cmd(cmd)
                            #print "cmd ", cmd, " code -> " , code, " out-> ", output
                            if code == 0:
                                size=eval(output)
                            else:
                                raise Exception(output)
                        except Exception, ex:
                            print "error getting disk size for ", filename, ex
                    finally:
                        pass
                else:
                    if self.config.managed_node.is_remote():
                        size = f_stat.st_size
                    else:
                        size = f_stat[stat.ST_SIZE] # TO DO Sparse handling
            else:
                print "Error getting disk size for", filename, \
                        "(filename does not exist.)"
        except Exception, ex:
                import traceback
                traceback.print_exc()
                error_msg = to_str(ex).replace("'", "")
                LOGGER.error("Error getting disk size for " + to_str(filename) + ". Error description: " + to_str(error_msg))
                return (size, dev_type)
        return (size, dev_type)
       
    #Starts new functions from here
    def get_new_disk_entry(self):
        vm_disk = VMDisks()
        return vm_disk
    
    def getDisks(self, vm_id=None):
        vm_disks=[]
        if not vm_id:
            vm_id = self.vm_id
        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
        return vm_disks
    
    def get_storage_stats(self, vm_id=None):
        storage_stats={}
        disk_stats={}
        disk_detail={}
        if not vm_id:
            vm_id = self.vm_id

        if vm_id:
            vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
            for vm_disk in vm_disks:
                disk_detail={}
                disk_detail["DEV_TYPE"] = vm_disk.dev_type
                disk_detail["IS_LOCAL"] = self.get_remote(vm_disk.disk_name)
                disk_detail["DISK_SIZE"] = vm_disk.disk_size
                disk_detail["DISK_NAME"] = vm_disk.disk_name
                storage_disk_id=None
                vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=vm_disk.id).first()
                if vm_storage_link:
                    storage_disk_id = vm_storage_link.storage_disk_id
                    
                disk_detail["STORAGE_DISK_ID"] = storage_disk_id
                disk_stats[vm_disk.disk_name] = disk_detail
                
            storage_stats["LOCAL_ALLOCATION"] = 0
            storage_stats["SHARED_ALLOCATION"] = 0
            storage_stats["DISK_STATS"] = disk_stats
        return storage_stats
    
    def get_disk_stat(self, vm_id, filename):
        disk_detail={}

        storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
        if storage_disk:
            vm_disk = DBSession.query(VMDisks).filter_by(vm_id=vm_id, disk_name=filename).first()
            if vm_disk:
                disk_detail={}
                disk_detail["DEV_TYPE"] = vm_disk.dev_type
                disk_detail["IS_LOCAL"] = self.get_remote(vm_disk.disk_name)
                disk_detail["DISK_SIZE"] = vm_disk.disk_size
                disk_detail["DISK_NAME"] = vm_disk.disk_name
                disk_detail["STORAGE_DISK_ID"] = storage_disk.id
        return disk_detail
                
    def get_remote(self, filename):
        isLocal=True
        vm_disk = DBSession.query(VMDisks).filter_by(disk_name=filename).first()
        if vm_disk:
            isLocal = vm_disk.is_shared
        return isLocal
                    
    def set_remote(self, filename, is_remote):
        try:
            disk_names=[]
            vm = DBSession.query(VM).filter_by(name=self.config.name).first()
            if vm:
                disk_names = [de.disk_name for de in self.getDisks(vm.id)]
            
                if filename in disk_names:
                    de_stat = self.get_disk_stat(vm.id, filename) #self.disk_stats.get(filename)
                    if de_stat is not None :
                        de_stat[self.DISK_IS_LOCAL] = not is_remote
                    else:
                        de_stat = { self.DISK_NAME : filename,
                                    self.DISK_SIZE : 0,
                                    self.DISK_DEV_TYPE : self.UNKNOWN,
                                    self.DISK_IS_LOCAL : not is_remote
                                    #self.STORAGE_DISK_ID : ""
                                    }
                        self.disk_stats[filename] = de_stat
        except Exception, ex:
            LOGGER.error("Error in set_remote(): " + str(ex))
            #raise Exception("disk " + filename + " not found" )

    def get_storage_disk_id(self, filename):
        storage_disk_id=None
        storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
        if storage_disk:
            storage_disk_id = storage_disk.id
        return storage_disk_id

    def set_storage_disk_id(self, filename, storage_disk_id):
        try:
            file_exists = False
            vm = DBSession.query(VM).filter_by(name=self.config.name).first()
            if vm:
                for de in self.getDisks(vm.id):
                    if filename == de.disk_name:
                        file_exists = True
            
                if file_exists == True:
                    de_stat = self.get_disk_stat(vm.id, filename)  #self.disk_stats.get(filename)
                    if de_stat is not None :
                        de_stat[self.STORAGE_DISK_ID] = storage_disk_id
            
                    else:
                        de_stat = { self.DISK_NAME : filename,
                                    self.DISK_SIZE : 0,
                                    self.DISK_DEV_TYPE : self.UNKNOWN,
                                    self.DISK_IS_LOCAL : not is_remote,
                                    self.STORAGE_DISK_ID : storage_disk_id
                                    }
        except Exception, ex:
            LOGGER.error("Error in set_storage_disk_id(): " + str(ex))
            #raise Exception("disk " + filename + " not found" )
        
    def get_storage_id(self, filename):
        storage_id=None
        storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
        if storage_disk:
            storage_id = storage_disk.storage_id
        return storage_id

class OutsideVM(DeclarativeBase):
    __tablename__ = 'outside_vms'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50), nullable=False)
    node_id = Column(Unicode(50), nullable=False)
    status = Column(Integer)

    def __init__(self, name,node_id,status):
        self.id = getHexID(name,[constants.DOMAIN])
        self.name = name
        self.node_id = node_id
        self.status = status

    @classmethod
    def onRemoveNode(cls, node_id):
        DBSession.query(OutsideVM).filter(OutsideVM.node_id==node_id).delete()

Index('ovm_nid_name',OutsideVM.node_id,OutsideVM.name)

