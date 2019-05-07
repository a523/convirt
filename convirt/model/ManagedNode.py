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


# All classes in thse files are required Interfaces for managing
# machines/host/nodes with virtualization technology.

from convirt.core.utils.NodeProxy import Node
from convirt.core.utils.NodePool import NodePool
from convirt.core.utils.utils import LVMProxy, PyConfig,getHexID,copyToRemote
from convirt.core.utils.IPy import *
from convirt.core.utils.constants import *
from convirt.core.utils.utils import to_unicode,to_str
from convirt.core.utils.phelper import HostValidationException,\
     AuthenticationException, CommunicationException

import sys,os,re,types, platform,traceback,tg
import threading
import logging
LOGGER = logging.getLogger("convirt.model")


class NodeException(Exception):
    def __init__(self):
	Exception.__init__(self)

from convirt.model.NodeInformation import Category,Component,Instance
from sqlalchemy import  Column, ForeignKey,PickleType
from sqlalchemy.types import *
from sqlalchemy import orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import Index
from convirt.model import DeclarativeBase,DBSession
from convirt.model.DBHelper import DBHelper
from convirt.config.ConfigSettings import NodeConfiguration
from convirt.model.Credential import Credential
from convirt.core.utils.NodeProxy import Node

from convirt.model.NodeCache import NodeCache
import convirt.core.utils.utils
constants = convirt.core.utils.constants

from convirt.model.availability import AvailState, AvailHistory

class ManagedNode(DeclarativeBase):
    UNKNOWN = -1
    UP = 0
    DOWN = 1
    """
    Interface that represents a node being managed.It defines useful APIs
    for clients to be able to do Management for a virtualized Node
    """
    __tablename__='managed_nodes'
    id=Column(Unicode(50), primary_key=True)
    hostname=Column(Unicode(255), nullable=False)
    socket=Column(Integer,default=1)
    #ssh_port=Column(Integer,default=22)
    #username=Column(Unicode(50))
    #password=Column(Unicode(50))
    isRemote=Column(Boolean,default=False)
    isHVM=Column(Boolean,default=False)
    #use_keys=Column(Boolean,default=False)
    address=Column(Unicode(255))
    type=Column(Unicode(50),default=u'NONE')
    migration_port=Column(Integer,default=8002)
    credential=relation(Credential, \
                    primaryjoin=id == Credential.entity_id,\
                    foreign_keys=[Credential.entity_id],\
                    uselist=False,cascade='all, delete, delete-orphan')
    instances = relation('Instance', backref='node')
    setup_config=relation('NodeConfiguration', uselist=False,cascade='all,\
                    delete, delete-orphan')
    current_state = relation(AvailState, \
                             primaryjoin = id == AvailState.entity_id, \
                             foreign_keys=[AvailState.entity_id],\
                             uselist=False, \
                             cascade='all, delete, delete-orphan')

    __mapper_args__ = {'polymorphic_on': type}

    def __init__(self,
                 hostname = None,
                 ssh_port = 22,
                 username=Node.DEFAULT_USER,
                 password=None,
                 isRemote=False,
                 helper = None,
                 use_keys = False,
                 address = None):

        self.hostname = hostname
        self.ssh_port = ssh_port
        self.username = username
        self.id=getHexID(hostname,[MANAGED_NODE])
        self.password = password
        self.isRemote = isRemote
        self.helper   = helper
        self.use_keys = use_keys
        self.credential=Credential(self.id,u"",ssh_port = ssh_port,\
                username = username,password = password,use_keys = use_keys)
        if not address:
            self.address  = hostname
        else:
            self.address = address
        
        self.setup_config=None
        self._node_proxy_lock = threading.RLock()
        
        self._node_proxy = None    # lazy-init self.node_proxy 
        self._lvm_proxy = None     # lazy-init self.lvm_proxy 
        self._isLVMEnabled = None  # lazy-init self.isLVMEnabled 
        self._config = None        # lazy-init self.config
        self._environ = None       # lazy-init self.environ
        self._exec_path = None     # lazy init self.exec_path

        self.metrics = None
        self.current_state = AvailState(self.id, self.UP,\
                                        AvailState.MONITORING,\
                                        description=u"Newly created node.")

        try:
            if Node.use_bash_timeout and self.isRemote:
                bash=os.path.join(tg.config.get("common_script"), "bash_timeout.sh")
                copyToRemote(bash,self,os.path.join(tg.config.get('convirt_cache_dir'),'common/scripts'))
        except Exception,e:
            raise e

    @orm.reconstructor
    def init_on_load(self):
        self.ssh_port = None
        self.username = None
        self.password = None
        self.use_keys = None
        self.helper   = None
        self._node_proxy_lock = threading.RLock()

        self._node_proxy = None    # lazy-init self.node_proxy
        self._lvm_proxy = None     # lazy-init self.lvm_proxy
        self._isLVMEnabled = None  # lazy-init self.isLVMEnabled
        self._config = None        # lazy-init self.config
        self._environ = None       # lazy-init self.environ
        self._exec_path = None     # lazy init self.exec_path

        self.metrics = None
    @property
    def node_proxy(self):
        if self._node_proxy is None:
            self._node_proxy = self._init_node_proxy()
        return self._node_proxy
    @property
    def lvm_proxy(self):
        if self._lvm_proxy is None:
            self._lvm_proxy = self._init_lvm_proxy()
        return self._lvm_proxy
    @property
    def isLVMEnabled(self):
        if self._isLVMEnabled is None:
            self._isLVMEnabled = self._init_isLVMEnabled()
        return self._isLVMEnabled
    @property
    def config(self):
        if self._config is None:
            self._config = self._init_config()
        return self._config
    @property
    def environ(self):
        if self._environ is None:
            self._environ = self._init_environ()
        return self._environ
    @property
    def exec_path(self):
        if self._exec_path is None:
            self._exec_path = self._init_exec_path()
        return self._exec_path

    # implement lazy initialization. 
#    def __getattr__(self, name):
#        if name == 'node_proxy':
#            return self._init_node_proxy()
#        if name == 'lvm_proxy':
#            return self._init_lvm_proxy()
#        if name == 'config':
#            return self._init_config()
#        if name == 'isLVMEnabled':
#            return self._init_isLVMEnabled()
#        if name == 'environ':
#            return self._init_environ()
#        if name == 'exec_path':
#            return self._init_exec_path()
#        raise AttributeError()

    def is_in_error(self):
        if self.is_authenticated():
            # The following return does not seem to work!!
            #return  self.node_proxy.get_last_error() is not None
            return  self._node_proxy.get_last_error() is not None
        else:
            return True
       

    def disconnect(self):
        if self._node_proxy is not None:
            self._node_proxy.disconnect()
            self._node_proxy = None

    def connect(self):       
        credentials=self.get_credentials()
        if self._node_proxy is not None:
            self._node_proxy.connect(self.hostname,
                                     credentials["ssh_port"],
                                     credentials["username"],
                                     credentials["password"],
                                     self.isRemote,
                                     credentials["use_keys"])

        else:
            self._init_node_proxy()

    def get_connection_port(self):
        return self.get_credentials()["ssh_port"]

    # for now simple check. Later need to go deep
    def is_authenticated(self):
        if self._node_proxy is not None:
            return self._node_proxy.n_p is not None
        return self._node_proxy

    def is_up(self):
        up=False
        if self.current_state.avail_state == self.UP:
            up=True
        return up

    # set credentials, allow credentials to be set later.
    def set_credentials(self, username, password):
        self.username = username
        self.password = password

    #get the credential from the Credential object 
    def get_credentials(self):        
        return self.credential.cred_details

    #set the Credential details
    def set_node_credentials(self,type,**cred_details):
        self.credential.cred_type=type
        self.credential.cred_details=cred_details

    def is_remote(self):
        return self.isRemote


    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address


    def get_metrics(self, refresh=False,filter=False):
        if not refresh: return self.metrics

    def get_VM_count(self):
        pass
    
    def get_console(self):
        """
        get the console for the dom
        API migght need revision...
        """
        pass

    def get_terminal(self, username, password):
        """
        return tty terminal (telnet, ssh session ?)
        """
        pass
    
    def get_vnc(self):
        """
        get VNC session for this dom. VNC would popup username/password.
        """
        pass

    def get_os_info(self):
        try:
            os_info = self.environ['os_info']
            if os_info is None:
                return {}
            return os_info
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return {}

    def get_network_info(self):
        try:
            network_info = self.environ['network_info']
            if network_info is None:
                return []
            return network_info
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return []

    def get_nic_info(self):
        try:
            nic_info = self.environ['nic_info']
            if nic_info is None:
                return {}
            return nic_info
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return {}

    def get_bridge_info(self):
        try:
            bridge_info = self.environ['bridge_info']
            if bridge_info is None:
                return {}
            return bridge_info
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return {}

    def get_default_bridge(self):
        try:
            default_bridge = self.environ['default_bridge']
            return default_bridge
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return None

    def get_cpu_info(self):
        try:
            cpu_info = self.environ['cpu_info']
            if cpu_info is None:
                return {}
            return cpu_info
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return {}

    def get_disk_info(self):
        try:
            disk_info = self.environ['disk_info']
            if disk_info is None:
                return []
            return disk_info
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return []

    def get_free_mem(self, memory_total=None):
        free_mem=None
        from convirt.model.Metrics import MetricServerCurr
        currMetricsData = DBSession.query(MetricServerCurr).\
            filter(MetricServerCurr.entity_id==self.id).\
            filter(MetricServerCurr.metric_type==SERVER_CURR).first()
        if currMetricsData is not None:
            if memory_total is None:
                memory_total = currMetricsData.server_mem
            if memory_total is None:
                return 0
            memory_total=int(memory_total)
            used_mem=(currMetricsData.host_mem*memory_total)/100
            free_mem=round(memory_total-used_mem)
            free_mem="%d"%(free_mem)
        return free_mem

    def get_memory_info(self):
        try:
            memory_info = self.environ['memory_info']
            if memory_info is None:
                return {}
            free_mem=self.get_free_mem()
            if free_mem is not None:
                 memory_info[key_memory_free]=free_mem
            return memory_info
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return {}

    def get_platform_info(self):
        try:
            platform_info= self.environ['platform_info']
            if platform_info is None:
                return {}
            return platform_info
        except Exception, e:
            LOGGER.error("Exception : "+to_str(e)+" on "+self.hostname)
            print "Exception : "+to_str(e)+" on "+self.hostname
            traceback.print_exc()
        return {}

    def get_os_info_display_names(self):
      display_dict = {key_os_release:display_os_release,key_os_machine:display_os_machine,key_os_distro_string:display_os_distro}
      return display_dict

    def get_network_info_display_names(self):
      display_dict = {key_network_interface_name:display_network_interface_name,key_network_ip:display_network_ip}
      return display_dict

    def get_cpu_info_display_names(self):
      display_dict = { key_cpu_count:display_cpu_count,key_cpu_vendor_id:display_cpu_vendor_id,key_cpu_model_name:display_cpu_model_name, key_cpu_mhz : display_cpu_mhz}
      return display_dict

    def get_memory_info_display_names(self):
      display_dict = {key_memory_total:display_memory_total,key_memory_free:display_memory_free}
      return display_dict

    def get_disk_info_display_names(self):
      display_dict = {key_disk_file_system:display_disk_file_system,key_disk_size:display_disk_size,key_disk_mounted:display_disk_mounted}
      return display_dict

    def get_cpu_db(self):
        try:
            instance=DBSession.query(Instance).filter(Instance.node_id==self.id).\
                filter(Instance.name==constants.key_cpu_count).first()
            if instance :
                return int(instance.value)
        except Exception, e:
            print "Exception: ", e
        return 1

    def get_mem_db(self):
        try:
            instance=DBSession.query(Instance).filter(Instance.node_id==self.id).\
                filter(Instance.name==constants.key_memory_total).first()
            if instance :
                return int(instance.value)
        except Exception, e:
            print "Exception: ", e
        return 0

    def _init_node_proxy(self):
        self._node_proxy_lock.acquire()
        try:
            if self._node_proxy is None:
                while True:
                    creds = None
                    try:
                        credentials=self.get_credentials()
                        self._node_proxy = NodePool.get_node(\
                            hostname = self.hostname,
                            ssh_port = credentials["ssh_port"],
                            username = credentials["username"],
                            password = credentials["password"],
                            isRemote = self.isRemote,
                            use_keys = credentials["use_keys"])
                        
                    except AuthenticationException, e:
                        creds = None
                        if self.helper and not use_keys:
                            creds = self.helper.get_credentials(self.hostname,
                                                                self.username)
                            if creds is None:
                                raise Exception("Server not Authenticated")
                            else:
                                self.username = creds.username
                                self.password = creds.password
                        else:
                            raise e
                    else:
                        break
        finally:
            self._node_proxy_lock.release()
        
        
        return self._node_proxy
        

    def _init_config(self):
        if self.setup_config is None:
            self.setup_config = NodeConfiguration(self)
        return self.setup_config

    def _init_lvm_proxy(self):
        if self._lvm_proxy is None and self.isLVMEnabled:            
                self._lvm_proxy = LVMProxy(self.node_proxy,
                                           self.exec_path)
        return self._lvm_proxy

    def _init_isLVMEnabled(self):
        if self._isLVMEnabled is None:
            conf_val = self.config.get(prop_lvm)
            if conf_val is None:
                self._isLVMEnabled = LVMProxy.isLVMEnabled(self.node_proxy,
                                                           self.exec_path)
                self.config.set(prop_lvm,self._isLVMEnabled)
            else:
                self._isLVMEnabled = eval(to_str(conf_val))                
        return self._isLVMEnabled
    
    def _init_environ(self):
        if self._environ is None:
            self._environ = self.getEnvHelper()
        return self._environ

    def getEnvHelper(self):
        return NodeEnvHelper(self.id,None)
    
    def refresh_environ(self):
        ###calling environ.refresh() may start populating values.
        ###so we are deleting the database entries directly
        ###and populating them again, if populating values fails we rollback
        #self.environ.refresh()        
        try:
            DBHelper().delete_all(Instance,[],[Instance.node_id==self.id])
            self._init_environ()
        except Exception, e:
            traceback.print_exc()
            raise e

    def remove_environ(self):
        ###calling environ.remove() may start populating values.
        ###so we are deleting the database entries directly
        ###self.environ.remove()
        DBHelper().delete_all(Instance,[],[Instance.node_id==self.id])

    def _init_exec_path(self):
        if self._exec_path is None:
            self._exec_path = self.config.get(prop_exec_path)
        return self._exec_path

    def get_socket_info(self):
        try:
            cmd = 'cat /proc/cpuinfo | grep "physical id"  | sort | uniq -c | wc -l'
            (output,exit_code) = self.node_proxy.exec_cmd(cmd)
            if output and not exit_code:
                sock = int(output)
                if sock==0:
                    sock=1
                return sock
        except Exception, e:
            LOGGER.error(to_str(e))
            traceback.print_exc()
        LOGGER.error("Unable to get Socket info. output:" + to_str(output) + "exit_code:" + to_str(exit_code))
        raise Exception("Unable to get Socket info. output:" + to_str(output) + "exit_code:" + to_str(exit_code))

    def get_unused_port(self, start, end):
        """
            Try to choose a free port within the given range.
        """
        
        used_ports = self.get_used_ports()
        nc = NodeCache()
        selected_port = nc.get_port(self.hostname, constants.PORTS, used_ports, start, end)
        return selected_port
    

    def get_used_ports(self):
        """
            Return used ports within the given range.
        """
        used_ports = []
        ports = self.netstat_local_ports()
        if ports:
           used_ports = ports
        return  used_ports

    def netstat_local_ports(self):
        """Run netstat to get a list of the local ports in use.
        """
        netstat_cmd = "netstat -nat"
        out, exit_code = self.node_proxy.exec_cmd(netstat_cmd, timeout=60)
        if exit_code != 0:
            raise Exception("Error finding the used ports. "+out)

        lines = out.split('\n')
#        print "\n\n=lines======\n\n",lines,"\n\n"
        port_list = []
        # Skip 2 lines of header.
        for x in lines[2:]:
            if not x:
                continue
            # Local port is field 3.
            y = x.split()[3]
            # Field is addr:port, split off the port.
            y = y.split(':')[-1]
            port_list.append(int(y))
#        print "ports===",port_list
        return port_list

Index('mnode_id',ManagedNode.id)


class NodeEnvHelper:
    """A helper for ManagedNode for retrieving and storing
    Environment/Config information for a host."""

    def __init__(self, node_id,node_proxy):
        self.node_proxy = node_proxy
        self.node_id=node_id
        self.__dict = {}
        #self.__populateDictionary()
        self.__populateInformation()

    def __iter__(self):
        return self.__dict.iterkeys()

    def keys(self):
        return self.__dict.keys()
    
    def __getitem__(self, item):
        if not item: return None
        if self.__dict.has_key(item):
            return self.__dict[item]
        else:
            return None

    def __setitem__(self, item, value):
        self.__dict[item] = value

    def refresh(self):
        DBHelper().delete_all(Instance,[],[Instance.node_id==self.node_id])
        self.__dict = None
        self.__populateDictionary()

    # try to get the network definition from ip and netmask
    def populate_network(self, n):
        if n.get("ip") and n.get("netmask"):
            try:
                ip = IP(n.get("ip"))
                mask = IP(n.get("netmask"))
                net_int = ip.int() & mask.int()
                net_ip = IP(net_int)
                net_ip_mask = IP(net_ip.strNormal() + "/" + mask.strNormal())
                net_str = net_ip_mask.strNormal()
                n["network"] = net_str
            except Exception,ex:
                pass   

    def __populateInformation(self):
        instances=DBHelper().filterby(Instance,[],[Instance.node_id==self.node_id])

        if len(instances)==0:
            self.__populateDictionary()
        else:
            for instance in instances:
                comp=instance.component
                if comp.type in ['cpu_info','memory_info','os_info','nic_info','bridge_info','platform_info']:
                    if not self.__dict.has_key(comp.type):
                        self.__dict[comp.type]={}
                    val=instance.value
                    if val[0] in ['{','[']:
                        val=eval(instance.value)
                    self.__dict[comp.type][instance.name]=val
                elif comp.type in ['disk_info']:
                    self.__dict[comp.type]=eval(instance.value)
                elif comp.type in ['network_info']:
                    if not self.__dict.has_key(comp.type):
                        self.__dict[comp.type]=[]
                    self.__dict[comp.type].append(dict(interface_name=instance.name,ip_address=instance.value))
                    pass
                elif comp.type in ['default_bridge']:
                    self.__dict[comp.type]=instance.value

    def __populateDictionary(self):
        """ retrieve environment information for the
        node and store it in the local dictionary. """

        if self.__dict is not None:
            self.__dict = None

        m_node=DBSession.query(ManagedNode).filter(ManagedNode.id==self.node_id).one()
        self.node_proxy=m_node.node_proxy

        cpu_attributes = [key_cpu_count,key_cpu_vendor_id,key_cpu_model_name, key_cpu_mhz]
        memory_attributes = [key_memory_total,key_memory_free]
        disk_attributes = [key_disk_file_system,key_disk_size,key_disk_mounted]

        cpu_values = self.node_proxy.exec_cmd( \
                'cat /proc/cpuinfo | grep "processor" | wc -l;' +
                'cat /proc/cpuinfo | grep "vendor*" | head -1 | cut -d\':\' -f2;' +
                'cat /proc/cpuinfo | grep "model na*" | head -1 | cut -d\':\' -f2;' +
                'cat /proc/cpuinfo | grep "cpu MHz*" | head -1 | cut -d\':\' -f2;'\
                )[0].split('\n')[:-1]

#        memory_values = self.node_proxy.exec_cmd( \
#                'cat /proc/meminfo | grep "Mem*" | cut -d\':\' -f2'\
#                )[0].split('\n')[:-1]
#
#        memory_values = [ int(re.search('(\d+)(\s+)(\S+)', v.strip()).group(1))/ 1000 \
#                          for v in memory_values ]

        memory_values = self.populate_mem_info()
        
        network_values = self.node_proxy.exec_cmd( \
               'ifconfig | awk \'{print $1, $2, $3, $4}\' ;'
               )[0].split("\n   \n")

        # Process networks # TODO : rewrite this.
        raw_network_list = network_values
        network_list = []
        if raw_network_list[0].find('not found') == -1:
            for i in range(len(raw_network_list)):
                split_item = raw_network_list[i].split("UP")
                if cmp('',split_item[0]) !=0 :
                    split_item = split_item[0].split('\n')
                    interface_name = split_item[0].split()[0]
                    ip_addr = ''
                    if cmp('',split_item[1]) !=0:
                        for i in range(1, len(split_item)):
                            ip_addr += split_item[i] + '\n'
                    network_list.append(dict([(key_network_interface_name, interface_name), (key_network_ip, ip_addr)]))


        disk_values = self.node_proxy.exec_cmd( \
                'df -kh -P | grep ^/dev | awk \'{print $1, $2, $6}\''\
                )[0].split('\n')[:-1]

        cpu_dict = dict((cpu_attributes[x],cpu_values[x]) \
                           for x in range(len(cpu_attributes)))
        cpu_dict[key_cpu_count] = int(cpu_dict[key_cpu_count])
        
        memory_dict = dict((memory_attributes[x],memory_values[x]) \
                           for x in range(len(memory_attributes)))


        disk_list = []
        for i in range(len(disk_values)):
          disk_values_split =disk_values[i].split(" ")
          disk_list.append(dict((disk_attributes[x],disk_values_split[x]) \
            for x in range(len(disk_values_split))))

        # os details
        os_values = self.node_proxy.exec_cmd( \
            'uname -r;uname -s; uname -m;'\
                )[0].split('\n')[:-1]
        i = 0
        os_dict = {}
        for name in [key_os_release,key_os_system,key_os_machine]:
            try:
                os_dict[name] = os_values[i]
            except ValueError:
                pass
            i = i+1

        # Augment the information gathered from setup script.
        discovery_file = '/var/cache/convirt/server_info'
        alt_discovery_file = '/var/cache/convirt/server_info'
        if not self.node_proxy.file_exists(discovery_file):
            if self.node_proxy.file_exists(alt_discovery_file):
                discovery_file = alt_discovery_file

        discovered_info = None
        if self.node_proxy.file_exists(discovery_file):
            discovered_info = PyConfig(self, discovery_file)
        
        def_bridge = ""
        if discovered_info:
            os_dict[key_os_distro] = discovered_info["DISTRO"]
            os_dict[key_os_distro_ver] = discovered_info["VER"]
            os_dict[key_os_distro_string] = discovered_info["DISTRO"] + " " + \
                discovered_info["VER"]
            def_bridge = discovered_info["DEFAULT_BRIDGE"]


        # Add some more network specific info.
        cmd = "ls -ld /sys/class/net/*/device | sed -e 's/.*\/sys\/class\/net\///' -e 's/\/device.*//'"
    
        nics = {}
        (output,exit_code) = self.node_proxy.exec_cmd( cmd)
        if output and not exit_code:
            nic_list = output.split('\n')
            for nic in nic_list:
                if nic:
                    nics[nic] = { "name":nic }

        bridges = {}
        cmd = "ls -ld /sys/class/net/*/{bridge,brif/*} | sed -e 's/.*\/sys\/class\/net\///' -e 's/\/bridge.*//' -e 's/\->.*//'"
        (output,exit_code) = self.node_proxy.exec_cmd( cmd)
        if output and not exit_code:
            base_entries = output.split('\n')
            entries=[]
            for e in base_entries:
                if e and e.find('cannot access') < 0:
                    if e and e.find('ls:') != 0:
                        entries.append(e)
            # Populate bridges
            for e in entries:
                if e and e.find("/brif/") == -1:
                    bridges[e] = { "name":e }
            # Populate interfaces for bridges.
            for e in entries:
                if e.find("/brif/") > -1:
                    (br_name,brif,ifname) = e.split("/")
                    if ifname:
                        ifname = ifname.strip()
                    if ifname and (ifname.find("vif") == 0 or \
                            ifname.find("tap")==0):
                        # ignore virtual interface conventions.
                        continue
                    bridge = bridges[br_name]
                    if bridge :
                        interfaces = bridge.get("interfaces")
                        if interfaces is not None:
                            interfaces.append(ifname)
                        else:
                            bridge["interfaces"] = [ifname,]

        # from the network info, get ip address and netmask and 
        # construct net details from it.
        # NOTE : There must be a better way of doing this.
        # Look in to ioctl 
        ipv4_re = re.compile("(.*):(.*) (.*):(.*)")
        ipv4_re1 = re.compile("(.*):(.*) (.*):(.*) (.*):(.*)")
        for n_info in network_list:
            ifname = n_info[key_network_interface_name]
            b = bridges.get(ifname)
            n = nics.get(ifname)
            if b or n:
                # we need to process
                ip_info = n_info[key_network_ip]
                if ip_info:
                    ip_list = ip_info.split('\n')
                    for ip_entry in ip_list:
                        m = ipv4_re.match(ip_entry)
                        if not m:
                            ipv4_re1.match(ip_entry)
                        if m :
                            l = len(m.groups())
                            if l > 0 and  m.group(1).find("inet addr") == 0:
                                if b: b["ip"] = m.group(2)
                                if n: n["ip"] = m.group(2)
                            if l > 2 and m.group(3).find("Mask") == 0:
                                if b: b["netmask"] = m.group(4)
                                if n: n["netmask"] = m.group(4)
                            if l > 4 and m.group(5).find("Mask") == 0:
                                if b: b["netmask"] = m.group(6)
                                if n: n["netmask"] = m.group(6)
                                
                                
        # find the network by using ip and netmask
        for n in nics.itervalues():
            self.populate_network(n)
        for b in bridges.itervalues():
            self.populate_network(b)

        platform_dict = self.populate_platform_info()

        if platform_dict is None:
            raise Exception("Cannot get server platform")

        #import pprint; pprint.pprint(bridges)
        self.__dict = dict([('cpu_info',cpu_dict),
                            ('memory_info', memory_dict),
                            ('disk_info', disk_list),
                            ('network_info',network_list),
                            ('nic_info',nics),
                            ('bridge_info',bridges),
                            ('os_info', os_dict),
                            ('default_bridge', def_bridge),
                            ('platform_info', platform_dict)])
        comp_dict={}
        components=DBHelper().get_all(Component)
        for component in components:
            comp_dict[component.type]=component
        instances=[]
        #import pprint; pprint.pprint(self.__dict)
        for key,val in self.__dict.iteritems():
            #val is of dictionary type
            if key in ['cpu_info','memory_info','os_info','nic_info','bridge_info','platform_info']:
                for k1,v1 in val.iteritems():
                    inst=Instance(to_unicode(k1))
                    inst.value=to_unicode(v1)
                    inst.display_name=to_unicode('')
                    inst.component=comp_dict[key]
                    inst.node_id=self.node_id
                    instances.append(inst)
            #val is of list type
            elif key in ['disk_info']:
                inst=Instance(to_unicode('disks'))
                inst.value=to_unicode(val)
                inst.display_name=to_unicode('')
                inst.component=comp_dict[key]
                inst.node_id=self.node_id
                instances.append(inst)
            elif key in ['network_info']:
                for i in range(len(val)):
                    k1,v1=val[i]
                    inst=Instance(to_unicode(val[i][k1]))
                    inst.value=to_unicode(val[i][v1])
                    inst.display_name=to_unicode('')
                    inst.component=comp_dict[key]
                    inst.node_id=self.node_id
                    instances.append(inst)
            #val is of string type
            elif key in ['default_bridge']:
                inst=Instance(to_unicode(key))
                inst.value=to_unicode(val)
                inst.display_name=to_unicode('')
                inst.component=comp_dict[key]
                inst.node_id=self.node_id
                instances.append(inst)

        DBHelper().add_all(instances)

    def populate_mem_info(self):
        memory_values = self.node_proxy.exec_cmd( \
                'cat /proc/meminfo | grep "Mem*" | cut -d\':\' -f2'\
                )[0].split('\n')[:-1]

        memory_values = [ int(re.search('(\d+)(\s+)(\S+)', v.strip()).group(1))/ 1000 \
                          for v in memory_values ]

        return memory_values

    def populate_platform_info(self):
        m_node=DBSession.query(ManagedNode).filter(ManagedNode.id==self.node_id).one()
        return m_node.populate_platform_info()
    
#########################
# SELF TEST
#########################

if __name__ == '__main__':

    REMOTE_HOST = '192.168.123.155'
    REMOTE_USER = 'root'
    REMOTE_PASSWD = ''

    REMOTE = False 
    
    local_node = ManagedNode(hostname=LOCALHOST)
    if not REMOTE:
        remote_node = local_node  # for local-only testing
    else:        
        remote_node = ManagedNode(hostname=REMOTE_HOST,
                           username=REMOTE_USER,
                           password = REMOTE_PASSWD,
                           isRemote = True)    

    #
    # lvm_proxy  tests
    #

    print '\nManagedHost.LVMProxy interface test STARTING'

    print 'Local Node LVM enabled?:' , local_node.isLVMEnabled
    print 'Remote Node LVM enabled?:' , remote_node.isLVMEnabled
    
    for lvm in (local_node.lvm_proxy,remote_node.lvm_proxy):
        if lvm:
            vgs =  lvm.listVolumeGroups()
            for g in vgs:
                print g
                print lvm.listLogicalVolumes(g)
                print '\t Creating test LV'
                lvm.createLogicalVolume('selfTest',0.1,g)
                print '\t Deleting test LV'
                lvm.removeLogicalVolume('selfTest',g)            
    print 'ManagedHost.LVMPRoxy interface test COMPLETED\n'
   

    #
    # environment tests
    #
    print '\nManagedHost.Environment access  test STARTING'

    for nd in (local_node, remote_node):
        print "\n%s's environment:" % nd.hostname
        print 'Available attributes:', nd.environ.keys()
        for attr in nd.environ:
            print attr, ':',nd.environ[attr]

    print 'ManagedHost.Environment access  test COMPLETED\n'

    network_values = remote_node.node_proxy.exec_cmd( \
               'ifconfig | awk \'{print $1, $2, $3}\' ;'
               )[0].split("\n  \n")


    print network_values
    for item in network_values:
      print item.split("UP")


    disk_values = remote_node.node_proxy.exec_cmd( \
               'df  -kh -P | grep ^/dev')[0].split('\n')
    for item in disk_values:
      print item

    disk_values = ('Filesystem            Size  Used Avail Use% Mounted on\n'
                  '/dev/mapper/VG_Fedora-LV2\n29G   19G  8.2G  70% /\n'
                  '/dev/sda1             3.8G  100M  3.5G   3% /boot\n'
                  'tmpfs                 1.9G     0  1.9G   0% \n'
                  'dev/shm\n/dev/mapper/VG_PL1-home\n'
                  '20G   16G  3.1G  84% /mnt/home\n'
                  'dev/mapper/VG_PL1-vm_disks\n'
                  '40G   23G   15G  61% /vm_disks\n'
                  'dev/mapper/VG_PL1-images\n'
                  '79G   68G  7.1G  91% /mnt/images')

    disk_values = disk_values.splitlines()
    print disk_values
    sys.exit(0)
    




    
    
    


