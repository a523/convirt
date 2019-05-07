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

class ApplianceCatalog(DeclarativeBase):
    __tablename__='appliance_catalogs'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50), nullable=False)
    url = Column(Unicode(255), nullable=False)

    def __init__(self, name):
        self.name = name
        self.id = getHexID(name,[constants.APPLIANCE_CATALOG])

class ApplianceFeed(DeclarativeBase):
    __tablename__='appliance_feeds'
    id = Column(Unicode(50), primary_key=True)
    provider_id = Column(Unicode(50), nullable=False)
    provider_name = Column(Unicode(255))
    feed_name = Column(Unicode(255), nullable=False)
    provider_url = Column(Unicode(255))
    provider_logo_url = Column(Unicode(255))
    feed_url = Column(Unicode(255), nullable=False)
    
    def __init__(self, provider_id):
        self.provider_id = provider_id
        self.id = getHexID(provider_id,[constants.APPLIANCE_FEED])


class Appliance(DeclarativeBase):
    __tablename__='appliances'
    id = Column(Unicode(50), primary_key=True)
    catalog_id=Column(Unicode(255))
    provider_id = Column(Unicode(50))
    title = Column(Unicode(255))
    link_href=Column(Unicode(255))
    download_href=Column(Unicode(255))
    type =  Column(Unicode(50))
    description = Column(Text)
    short_description = Column(Text)
    popularity_score=Column(Unicode(5))
    updated_date=Column(Unicode(50))
    platform=Column(Unicode(50))
    arch=Column(Unicode(50))
    PAE=Column(Boolean, default=False)
    is_hvm=Column(Boolean, default=False)
    filename=Column(Unicode(255))
    compression_type=Column(Unicode(50))
    version=Column(Unicode(50))
    archive=Column(Unicode(50))
    size=Column(Integer)
    installed_size=Column(Integer)

    def __init__(self, title):
        self.title = title
        self.id = getHexID()

Index("app_prvdrid", Appliance.provider_id)

