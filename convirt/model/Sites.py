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

import convirt.core.utils.utils
from convirt.core.utils.utils import getHexID
constants = convirt.core.utils.constants

from sqlalchemy import  Column
from sqlalchemy.types import *
from sqlalchemy.schema import Index

from convirt.model import DeclarativeBase
class Site(DeclarativeBase):
    __tablename__='sites'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50), nullable=False)
    def __init__(self, name):
        self.name = name
        self.id = getHexID(name,[constants.DATA_CENTER])

Index('s_id',Site.id)
