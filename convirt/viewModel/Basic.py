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
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# author : Jd <jd_jedi@users.sourceforge.net>

from convirt.core.utils import constants 

from convirt.model.ImageStore import ImageStore
from convirt.model.ApplianceStore import ApplianceStore
from convirt.model.PlatformRegistry import PlatformRegistry
from convirt.model.GridManager import GridManager
from convirt.model.ManagedNode import ManagedNode
from convirt.model.storage import StorageManager
from convirt.model.network import NwManager
from convirt.model.DBHelper import DBHelper
from convirt.config.ConfigSettings import ClientConfiguration
local_node = None
client_config = ClientConfiguration()
store = None
registry = None
image_store = None
manager = None
storage_manager = None
nw_manager = None
appliance_store = None

def basic_initialize():
    global local_node, client_config, store, registry, image_store, manager, storage_manager
    global nw_manager, appliance_store
    try:
        local_node = ManagedNode(hostname = constants.LOCALHOST, isRemote = False, helper = None)
        #client_config = local_node.config
        #store = client_config
        registry = PlatformRegistry(client_config, {})

        #image_store = ImageStore(local_node.config, registry)
        image_stores=DBHelper().get_all(ImageStore)
        if len(image_stores)>0:
            image_store =image_stores[0]
            image_store.set_registry(registry)
        manager = GridManager( client_config,registry, None)
        storage_manager = StorageManager()
        nw_manager = NwManager()

        appliance_store = ApplianceStore(local_node, client_config)
    except Exception, e:
        import traceback
        traceback.print_exc()
        raise e

def getGridManager():
    if not manager:
        basic_initialize()
    return manager

def getImageStore():
    if not image_store:
        basic_initialize()
    return image_store

def getApplianceStore():
    if appliance_store is None:
        basic_initialize()
    return appliance_store

def getPlatformRegistry():
    if not registry:
        basic_initialize()
    return registry

def getStorageManager():
    if not storage_manager:
        basic_initialize()
    return storage_manager

def getNetworkManager():
    if not nw_manager:
        basic_initialize()
    return nw_manager

def getManagedNode():
    if not local_node:
        basic_initialize()
    return local_node
