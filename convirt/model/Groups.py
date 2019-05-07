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
#

from convirt.model.ManagedNode import ManagedNode
import convirt.core.utils.utils
from convirt.core.utils.utils import to_unicode,to_str
from convirt.core.utils.utils import getHexID
constants = convirt.core.utils.constants
from convirt.model.DBHelper import DBHelper
from sqlalchemy import  Column,PickleType
from sqlalchemy.types import *
from sqlalchemy import orm
from sqlalchemy.schema import Index
from convirt.model import DeclarativeBase
from sqlalchemy.orm import relation, backref
from convirt.model.availability import AvailState
import logging
LOGGER = logging.getLogger("convirt.model")
class ServerGroup(DeclarativeBase):
    __tablename__='server_groups'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    groupVars = Column(PickleType)
    current_state = relation(AvailState, \
                             primaryjoin = id == AvailState.entity_id, \
                             foreign_keys=[AvailState.entity_id],\
                             uselist=False, \
                             cascade='all, delete, delete-orphan')
                             
    def __init__(self, name, node_list = None, group_vars = None):
        self.name = name
        self.id = getHexID(name,[constants.SERVER_POOL])
        self.n_list = {}   # dict()
        self.groupVars = {} # dict

        self.alloc_policy = SimpleAllocationPolicy(self) #TBD: parametrise!
        
        if node_list is not None:
            self.n_list = node_list

        if group_vars is not None:
            self.groupVars = group_vars

        self.current_state = AvailState(self.id, None, \
                                    AvailState.MONITORING, \
                                    description = u'New ServerPool')

    @orm.reconstructor
    def init_on_load(self):
        self.n_list = {}   # dict()
#        self.groupVars = {} # dict
#        if self.group_vars is not None:
#            self.groupVars = self.group_vars
        self.alloc_policy = SimpleAllocationPolicy(self)

    def getName(self):
        return self.name
                    
    def getNodeNames(self,auth):
        ent=auth.get_entity(self.id)
        nodes=auth.get_entity_names(to_unicode(constants.MANAGED_NODE),parent=ent)
        return nodes
    
    def getNodeList(self,auth):
        ent=auth.get_entity(self.id)
        nodelist={}
        if ent is not None:
            child_ents=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=ent)
            ids = [child_ent.entity_id for child_ent in child_ents]
            nodes= DBHelper().filterby(ManagedNode,[],[ManagedNode.id.in_(ids)])
            for node in nodes:
                nodelist[node.id]=node
        return nodelist

    def getNode(self,name):
        return self.n_list.get(name)
    
    def getGroupVars(self):
        return self.groupVars
    
    def getGroupVarValue(self, var):
        return self.groupVars.get( var )

    def getAllocationCandidate(self,auth, ctx):
        return self.alloc_policy.getNext(auth,ctx) 

    def setGroupVars(self, vars):
        self.groupVars = vars        
        #self.group_vars=vars
        
    # note does not update the store. Should not be called by client.
    def _addNode(self, node):
        if self.n_list.get(node.hostname) is None:
            self.n_list[node.hostname] = node
        else:
            raise Exception("Node %s already exists." %
                            (node.hostname,))


    def _removeNode(self, name):
        if name in self.getNodeNames():
            del self.n_list[name]
                    
    def __str__(self):
        return  self.name + "||" + to_str(self.n_list.keys()) + "||" + to_str(self.groupVars.keys())


Index('sp_id',ServerGroup.id)

class SimpleAllocationPolicy:
    """
    Policy for determining the best provisioning candidate
    amongst a group's members. A candidate is selected if
    it has the minimum:
        1. VM CPU utilisation
        2. VM Mem allocation
        3. number of VM's configured        
    in that order.
    """
    def __init__(self, group = None):
        self._group = group

    def setGroup(self, group):
        self._group = group

    def filter_node(self, node, ctx):
        try:
            node.connect()
        except Exception,e:
            pass
        result = node.is_authenticated()
        if ctx is not None and result and ctx.image:
            result=False
            if node.is_image_compatible(ctx.image):
                ###checking whether the node has enough free memory to allocate for the new vm
                free_mem=0
                try:
                    free_mem=int(node.get_memory_info().get(constants.key_memory_free,0))
                except Exception, e:
                    err=to_str(e).replace("'", " ")
                    LOGGER.error(err)
                mem=0
                try:
                    vm_config,image_config=ctx.image.get_configs()
                    mem=int(vm_config['memory'])
                except Exception, e:
                    err=to_str(e).replace("'", " ")
                    LOGGER.error(err)
                LOGGER.error("Memory required is "+str(mem))
                LOGGER.error("Available memory in "+node.hostname+" is "+str(free_mem))
                result = (mem<free_mem)
        #print "returning ", result, " for ", node.hostname
        return result
    
    def getNext(self, auth,ctx):
        sp=auth.get_entity(self._group.id)
        #nodenames=auth.get_entity_names(constants.MANAGED_NODE,parent=sp)
        child_ents=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=sp)
        ids = [child_ent.entity_id for child_ent in child_ents]
        nodelist= DBHelper().filterby(ManagedNode,[],[ManagedNode.id.in_(ids)])

        load_time=self._group.getGroupVarValue("SERVER_LOAD_TIME")
        
        try:
            load_time=int(load_time)
        except Exception, e:
            load_time=0
        list = []

        LOGGER.error("Begining initial placement on "+self._group.name)
        for n in nodelist:
            if self.filter_node(n, ctx):
                metrics=n.get_raw_metrics(load_time)
                cpu_info = n.get_cpu_info()
                nr_cpus = int(cpu_info.get(constants.key_cpu_count,1))
                vcpus=n.get_vcpu_count()
                free_mem=int(n.get_memory_info().get(constants.key_memory_free,0))

                list.append((metrics['VM_TOTAL_CPU(%)'],
                    metrics['VM_TOTAL_MEM(%)'],
                    (vcpus/nr_cpus),
                    n.get_VM_count(),
                    -free_mem,
                    n
                    ,n.hostname))
        #print list,"\n\n",min(list),"\n\n"
        LOGGER.error("Capable nodes:\n "+to_str(list))
        LOGGER.error("Finishing initial placement on "+self._group.name)

        if len(list) == 0:
            return None
        else:
            return min(list)[5]
        return None
        
    

