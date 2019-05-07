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
#
# -*- coding: utf-8 -*-

"""Sample model module."""

from sqlalchemy import *
from datetime import datetime
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Boolean
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import Index

from convirt.model import DeclarativeBase, metadata, DBSession
from convirt.model.DBHelper import DBHelper

op_groups_table = Table('operation_opgroup', metadata,
    Column('op_id', Integer, ForeignKey('operations.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('opgroup_id', Integer, ForeignKey('operation_groups.id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

class Operation(DeclarativeBase):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description=Column(Unicode(255))
    display_name=Column(Unicode(255))
    display_id=Column(Unicode(255))
    display=Column(Boolean, default=False)
    has_separator=Column(Boolean, default=False)
    display_seq=Column(Integer)
    icon=Column(Unicode(255))
    created_by=Column(Unicode(255),nullable=False)
    created_date = Column(DateTime)
    modified_by=Column(Unicode(255),nullable=False)
    modified_date= Column(DateTime,default=datetime.now)
    def __repr__(self):
        return '<Operation: name=%s>' % self.name

Index("op_id_name", Operation.id,Operation.name)

class OperationGroup(DeclarativeBase):
    __tablename__ = 'operation_groups'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False, unique=True)
    description=Column(Unicode(255))
    created_by=Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by=Column(Unicode(255))
    modified_date= Column(DateTime,default=datetime.now)
    operations = relation('Operation', secondary=op_groups_table, backref='opsGroup')
    
    def __repr__(self):
        return '<OperationGroup: name=%s>' % self.name

Index("opgrp_id", OperationGroup.id)
