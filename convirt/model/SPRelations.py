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
# author : ConVirt Team
#
# -*- coding: utf-8 -*-

from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.orm import relation, backref

from convirt.model import DeclarativeBase, metadata, DBSession
from convirt.model.Groups import ServerGroup
from convirt.model.Sites import Site
from convirt.model.ManagedNode import ManagedNode

from sqlalchemy.schema import UniqueConstraint,Index
from convirt.core.utils.utils import uuidToString, randomUUID, dynamic_map

class Upgrade_Data(DeclarativeBase):
    __tablename__ = 'upgrade_data'

    #Columns
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50))  #name for upgrading.
    version = Column(Unicode(50))   #version for upgrading
    description = Column(Unicode(100))  #some description
    upgraded = Column(Boolean)  #True/False. Whether it is upgraded or not.

    def __init__(self):pass

class Storage_Stats(DeclarativeBase):
    __tablename__ = 'storage_stats'

    #Columns
    id = Column(Unicode(50), primary_key=True)
    entity_id = Column(Unicode(50)) #This would be site_id, group_id, node_id, vm_id...
    storage_id = Column(Unicode(50), ForeignKey('storage_definitions.id'))
    total_size = Column(Float)          #shown in Storage Resources
    used_size = Column(Float)
    available_size = Column(Float)
    allocation_in_DC = Column(Float)    #shown in Storage Resources at DC level
    allocation_in_SP = Column(Float)    #shown in Storage Resources at SP level
    storage_used_in_SP = Column(Float)  #shown in Summary at SP (Overview tab)
    storage_avail_in_SP = Column(Float) #shown in Summary at DC, SP (Config tab)
    allocation_at_S_for_DC = Column(Float)  #shown on Server tab at DC level
    allocation_at_S_for_SP = Column(Float)  #shown on Server tab at SP level
    local_storage_at_VM = Column(Float)     #shown on Server tab for VM table
    shared_storage_at_VM = Column(Float)    #shown on Server tab for VM table
    storage_allocation_at_DC = Column(Float)   #shown on Overview tab for DC level
    locked = Column(Boolean)

    #Relation
    fk_sd_ss = relation('StorageDef', backref='Storage_Stats')

    def __init__(self):pass

Index("idx_ss_entid_sid", Storage_Stats.entity_id, Storage_Stats.storage_id)

#Would establish Server and Storage/Network Definition link
class ServerDefLink(DeclarativeBase):
    __tablename__ = 'serverdeflinks'
    
    #Composite unique constraint
    __table_args__ = (UniqueConstraint('server_id', 'def_id', name='ucServerDefLink'), {})

    #Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    server_id = Column(Unicode(50), ForeignKey('managed_nodes.id'))    #From ManagedNode
    def_type = Column(Unicode(50))
    def_id = Column(Unicode(50))
    status = Column(Unicode(50))
    details = Column(Unicode(500))
    dt_time = Column(DateTime)

    #Relation
    mng_node = relation('ManagedNode', backref='ServerDefLink')

    def __init__(self):pass

Index("sdef_sid_dtype_did", ServerDefLink.server_id,ServerDefLink.def_type,ServerDefLink.def_id)

#Would establish ServerPool and Definition link
class SPDefLink(DeclarativeBase):
    __tablename__ = 'spdeflinks'

    #Composite unique constraint
    __table_args__ = (UniqueConstraint('group_id', 'def_id', name='ucSPDefLink'), {})

    #Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    group_id = Column(Unicode(50), ForeignKey('server_groups.id'))    #From ServerGroup
    def_type = Column(Unicode(50))
    def_id = Column(Unicode(50))# this would be the def id either from Storage definition or from network definition
    status = Column(Unicode(50)) #not sure of what status
    oos_count = Column(Integer) #would display the count of servers which are out of Sync
    dt_time = Column(DateTime)

    #Relation
    svr_grp = relation('ServerGroup', backref='SPDefLink')

    def __init__(self):pass

Index("spdef_gid_dtype_did", SPDefLink.group_id,SPDefLink.def_type,SPDefLink.def_id)

#Would establish ServerPool and Definition link
class DCDefLink(DeclarativeBase):
    __tablename__ = 'dcdeflinks'

    #Composite unique constraint
    __table_args__ = (UniqueConstraint('site_id', 'def_id', name='ucDCDefLink'), {})

    #Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    site_id = Column(Unicode(50), ForeignKey('sites.id'))    #From Site
    def_type = Column(Unicode(50))
    def_id = Column(Unicode(50))# this would be the def id either from Storage definition or from network definition
    status = Column(Unicode(50)) #not sure of what status
    oos_count = Column(Integer) #would display the count of servers which are out of Sync
    dt_time = Column(DateTime)

    #Relation
    site_grp = relation('Site', backref='DCDefLink')

    def __init__(self):pass

Index("dcdef_sid_dtype_did", DCDefLink.site_id,DCDefLink.def_type,DCDefLink.def_id)

class StorageDisks(DeclarativeBase):
    __tablename__ = 'storage_disks'

    #Columns
    id = Column(Unicode(50), primary_key=True)
    storage_id = Column(Unicode(50), ForeignKey('storage_definitions.id'))
    storage_type = Column(Unicode(50))
    disk_name = Column(Unicode(100))
    mount_point = Column(Unicode(50))
    file_system = Column(Unicode(50))
    actual_size = Column(Float)
    size = Column(Float)
    unique_path = Column(Unicode(300))
    current_portal = Column(Unicode(50))
    target = Column(Unicode(50))
    state = Column(Unicode(50))
    lun = Column(Integer)
    storage_allocated = Column(Boolean)
    transient_reservation = Column(Unicode(50))

    #Relation
    fk_StorageDisks_StorageDef = relation('StorageDef', backref='StorageDisks')
    
    #Index
    #create index StorageDisks_uniquePath on StorageDisks(unique_path)
    #create index StorageDisks_diskName on StorageDisks(disk_name)

    def __init__(self):pass
