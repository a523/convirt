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

from convirt.core.utils.utils import getHexID
from sqlalchemy import  Column, ForeignKey,PickleType
from sqlalchemy.types import *
from sqlalchemy.schema import Index
from convirt.model import DeclarativeBase
class Credential(DeclarativeBase):
    """
    Class that stores the credentials and encryption details
    for an Entity.
    """
    __tablename__='credentials'
    id=Column(Unicode(50),primary_key=True)
    entity_id=Column(Unicode(50))
    cred_type=Column(Unicode(50))
    cred_details=Column(PickleType)

    def __init__(self,entity_id,type,**kwargs):
        self.id=getHexID()
        self.entity_id=entity_id
        self.cred_type=type
        self.cred_details=kwargs

Index("cred_eid", Credential.entity_id)
