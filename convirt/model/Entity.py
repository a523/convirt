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
# author : ConVirt Team

# -*- coding: utf-8 -*-

"""Sample model module."""

from sqlalchemy import *
from datetime import datetime
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import Index
from convirt.model import DeclarativeBase, metadata
from convirt.model.DBHelper import DBHelper
from convirt.model import DBSession
from convirt.core.utils.utils import to_unicode,to_str
import traceback,logging
LOGGER = logging.getLogger("convirt.model")

ops_enttypes = Table('ops_enttypes', metadata,
    Column('op_id', Integer, ForeignKey('operations.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('entity_type_id', Integer, ForeignKey('entity_types.id',
        onupdate="CASCADE", ondelete="CASCADE"))
)
class EntityRelation(DeclarativeBase):
    __tablename__ = 'entity_relations'

    id = Column(Integer, primary_key=True)
    src_id=Column(Unicode(50))
    dest_id=Column(Unicode(50))
    relation=Column(Unicode(50))
    
    def __init__(self,src_id,dest_id,relation):
        self.src_id=src_id
        self.dest_id=dest_id
        self.relation=relation
        
    def __repr__(self):
        return '<EntityRelation: name=%s>' % self.relation

Index('er_sid_did_reln',EntityRelation.src_id,EntityRelation.dest_id,EntityRelation.relation)

class Entity(DeclarativeBase):
    __tablename__ = 'entities'

    id = Column(Integer)
    name = Column(Unicode(255), nullable=False)
    created_by=Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by=Column(Unicode(255))
    modified_date= Column(DateTime,default=datetime.now)
    entity_id = Column(Unicode(50), primary_key=True)
    #parent_id=Column(Unicode(50), ForeignKey('entities.entity_id',onupdate="CASCADE", ondelete="CASCADE"))
    type_id=Column(Integer, ForeignKey('entity_types.id',onupdate="CASCADE", ondelete="CASCADE"))
    attributes = relation('EntityAttribute', backref='entity',cascade='all, delete, delete-orphan')
    #attributes = relation('EntityAttribute', backref='entity')
    #children=relation('Entity', backref=backref('parent', remote_side=[entity_id]))
    def _get_children(self):
        relns=DBSession.query(EntityRelation).filter(and_(EntityRelation.src_id==self.entity_id,\
            EntityRelation.relation==u'Children')).all()
        rels=[x.dest_id for x in relns]
        return DBSession.query(Entity).filter(Entity.entity_id.in_(rels)).all()
    def _get_parents(self):
        relns=DBSession.query(EntityRelation).filter(and_(EntityRelation.dest_id==self.entity_id,\
            EntityRelation.relation==u'Children')).all()
        rels=[x.src_id for x in relns]
        return DBSession.query(Entity).filter(Entity.entity_id.in_(rels)).all()
    children=property(_get_children)
    parents=property(_get_parents)
    def __repr__(self):
        return '<Entity: name=%s>' % self.name
    @classmethod
    def getEntityName(self,Id):
        EntityName=''
        ent=DBSession.query(Entity).filter(Entity.entity_id==Id).first()
        if ent is not None:
            EntityName=ent.name
            return EntityName
        else:
            return EntityName

    @classmethod
    def get_hierarchy(cls,entity_id):
        list=[]
        try:
            entity=DBSession.query(cls).filter(cls.entity_id==entity_id).first()
            while entity is not None:
                list.append(entity.entity_id)
                if len(entity.parents)!=0:
                    entity=entity.parents[0]
                else:
                    break
        except Exception,ex:
            LOGGER.error(to_str(ex).replace("'",""))
            traceback.print_exc()
            raise ex
        return list

entity_index=Index('ix_entities_name_type',Entity.name,Entity.type_id,unique=True)

class EntityType(DeclarativeBase):
    __tablename__ = 'entity_types'

    ###is_allowed api, state_transitions, entity states in constants
    ###depend on these values
    DATA_CENTER  = 1
    IMAGE_STORE  = 2
    SERVER_POOL  = 3
    MANAGED_NODE = 4
    DOMAIN       = 5
    IMAGE_GROUP  = 6
    IMAGE        = 7
    APPLIANCE    = 8
    EMAIL        = 9

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    display_name = Column(Unicode(255))
    created_by=Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by=Column(Unicode(255))
    modified_date= Column(DateTime,default=datetime.now)
    entities = relation('Entity', backref='type')
    ops = relation('Operation', secondary=ops_enttypes, backref='entityType')

    def __repr__(self):
        return '<EntityType: name=%s>' % self.name
    
Index('etype_name',EntityType.name)

class EntityAttribute(DeclarativeBase):
    __tablename__ = 'entity_attributes'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    value = Column(Unicode(255))
    entity_id=Column(Unicode(50), ForeignKey('entities.entity_id',onupdate="CASCADE", ondelete="CASCADE"))

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return '<EntityAttribute: name=%s>' % self.name

class EntityTasks(DeclarativeBase):
    __tablename__ = 'entity_tasks'
    worker = Column(Unicode(255), primary_key=True)
    entity_id = Column(Unicode(50), primary_key=True)
    worker_id = Column(Unicode(50))
    finished = Column(Boolean)
    start_time = Column(DateTime)
    estimated_time = Column(DateTime)
    end_time = Column(DateTime)
    last_ping_time = Column(DateTime)

    def __init__(self, worker,worker_id,entity_id,finished,start_time,estimated_time=None,last_ping_time=None):
        self.worker = worker
        self.worker_id = worker_id
        self.entity_id = entity_id
        self.finished = finished
        self.start_time = start_time
        self.estimated_time = estimated_time
        self.last_ping_time = last_ping_time


    def __repr__(self):
        return "<Entity=%s, task=%s, time=%s>" %(self.entity_id, self.worker_id, self.start_time)
