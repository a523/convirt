# -*- coding: utf-8 -*-
"""The application's model objects"""

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False,expire_on_commit=False,
                     extension=ZopeTransactionExtension())
zopelessmaker = sessionmaker(autoflush=True, \
                             autocommit=False, \
                             expire_on_commit=False)
DBSession = scoped_session(maker)

# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
DeclarativeBase = declarative_base()

# There are two convenient ways for you to spare some typing.
# You can have a query property on all your model classes by doing this:
# DeclarativeBase.query = DBSession.query_property()
# Or you can use a session-aware mapper as it was used in TurboGears 1:
# DeclarativeBase = declarative_base(mapper=DBSession.mapper)

# Global metadata.
# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata

# If you have multiple databases with overlapping table names, you'll need a
# metadata for each database. Feel free to rename 'metadata2'.
#metadata2 = MetaData()

#####
# Generally you will not want to define your table's mappers, and data objects
# here in __init__ but will want to create modules them in the model directory
# and import them at the bottom of this file.
#
######

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""

    DBSession.configure(bind=engine)
    zopelessmaker.configure(bind=engine)
    # If you are using reflection to introspect your database and create
    # table objects for you, your tables must be defined and mapped inside
    # the init_model function, so that the engine is available if you
    # use the model outside tg2, you need to make sure this is called before
    # you use the model.

    #
    # See the following example:

    #global t_reflected

    #t_reflected = Table("Reflected", metadata,
    #    autoload=True, autoload_with=engine)

    #mapper(Reflected, t_reflected)

# Import your model modules here.
from convirt.model.auth import User, Group, Permission
from convirt.model.Entity import EntityRelation,Entity,EntityType,EntityAttribute,entity_index
from convirt.model.Credential import Credential
from convirt.model.Operation import Operation,OperationGroup
from convirt.model.ImageStore import ImageStore,Image,ImageGroup
from convirt.model.Groups import ServerGroup
from convirt.model.Sites import Site
from convirt.model.ManagedNode import ManagedNode
from convirt.config.ConfigSettings import NodeConfiguration
from convirt.model.VM import VM, OutsideVM
from convirt.core.platforms.xen.XenNode import XenNode
from convirt.core.platforms.xen.XenDomain import XenDomain
from convirt.core.platforms.kvm.KVMNode import KVMNode
from convirt.core.platforms.kvm.KVMDomain import KVMDomain
from convirt.model.Appliance import ApplianceCatalog,ApplianceFeed,Appliance
from convirt.model.NodeInformation import Category,Component,Instance
from convirt.model.services import *
from convirt.model.availability import *
from convirt.model.Metrics import Metrics, MetricsCurr, MetricsArch, rollupStatus
# Import for Storage Pool
from convirt.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink, Storage_Stats
from convirt.model.storage import StorageDef
from convirt.model.network import NwDef
from convirt.model.notification import Notification
from convirt.model.EmailSetup import EmailSetup
from convirt.model.CustomSearch import CustomSearch
from convirt.model.LockManager import CMS_Locks
from convirt.model.deployment import Deployment
