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

import tg
import os, platform
from convirt.core.utils import constants as constants
from convirt.core.utils.utils import getHexID
class ClientConfiguration:
    """
    Client Configuration info and default values

    check_updates_on_startup = True
    paramiko_log_file = paramiko.log
    gnome_vfs_enabled = False
    html_browser = /usr/bin/yelp
    log_file = convirt.log
    enable_log = True
    enable_paramiko_log = False
    http_proxy =
    default_ssh_port = 22

    default_computed_options = ['arch', 'arch_libdir', 'device_model']
    use_3_0_api = True
    """
    def __init__(self):
        pass
    
    def get(self,key):

        value=None
        if key==constants.prop_chk_updates_on_startup:
            value=eval(tg.config.get(key,'True'))

        elif key==constants.prop_enable_paramiko_log:
            value=eval(tg.config.get(key,'False'))

        elif key==constants.prop_paramiko_log_file:
            value=tg.config.get(key,'paramiko.log')

        elif key==constants.prop_gnome_vfs_enabled:
            value=eval(tg.config.get(key,'False'))

        elif key==constants.prop_enable_log:
            value=eval(tg.config.get(key,'True'))

        elif key==constants.prop_log_file:
            value=tg.config.get(key,'convirt.log')

        elif key=='html_browser':
            value=tg.config.get(key,'/usr/bin/yelp')

        elif key==constants.prop_default_computed_options:
            value=tg.config.get(key,"['arch', 'arch_libdir', 'device_model']")

        elif key=='use_3_0_api':
            value=tg.config.get(key,'/usr/bin/yelp')

        elif key==constants.prop_http_proxy:
            value=tg.config.get(key,"")

        elif key==constants.prop_default_ssh_port:
            value=tg.config.get(key,22)

        elif key==constants.prop_appliance_store:
            value=tg.config.get(key,'/var/cache/convirt/appliance_store/')
            value=os.path.abspath(value)
            
        elif key==constants.prop_image_store:
            value='/var/cache/convirt/image_store/'
            value=os.path.abspath(value)

        elif key==constants.prop_log_dir:
            value='/var/log/convirt/'
            value=os.path.abspath(value)

        elif key==constants.prop_snapshots_dir:
            value='/var/cache/convirt/vm_snapshots/'
            value=os.path.abspath(value)

        elif key==constants.prop_snapshot_file_ext:
            value=tg.config.get(key,'.snapshot.xm')

        elif key==constants.prop_cache_dir:
            value='/var/cache/convirt/'
            value=os.path.abspath(value)

        elif key==constants.prop_exec_path:
            value=tg.config.get(key,'$PATH:/usr/sbin')

        elif key==constants.prop_updates_file:
            value=tg.config.get(key,'/var/cache/convirt/updates.xml')
            value=os.path.abspath(value)

        elif key==constants.prop_vnc_host:
            value=tg.config.get(key)

        elif key==constants.prop_vnc_port:
            value=tg.config.get(key)
        
        elif key==constants.prop_vnc_user:
            value=tg.config.get(key)

        elif key==constants.prop_vnc_password:
            value=tg.config.get(key)

        elif key in( constants.prop_ssh_log_level,constants.ssh_file,constants.prop_ssh_forward_host,constants.prop_ssh_forward_port,constants.prop_ssh_forward_user,constants.prop_ssh_forward_password):
            value = tg.config.get(key)
            
        elif key in (constants.prop_ssh_tunnel_setup,constants.prop_ssh_forward_key,constants.prop_use_vnc_proxy):
            value = eval(tg.config.get(key,'False'))
             
        return value

from sqlalchemy import  Column, ForeignKey,PickleType
from sqlalchemy.types import *
from sqlalchemy import orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import Index
from convirt.model import DeclarativeBase
from convirt.model.DBHelper import DBHelper

class NodeConfiguration(DeclarativeBase):
    """
    Class that stores the configuration details for a ManagedServer.
    """
    __tablename__='node_config'
    id=Column(Unicode(50),primary_key=True)
    node_id=Column(Unicode(50),ForeignKey('managed_nodes.id',onupdate="CASCADE",\
                ondelete="CASCADE"))
    config=Column(PickleType)

    def __init__(self,node):
        self.id=getHexID()
        self.node_id=node.id
        self.node=node
        self.config={}
        self.__populateDefaultEntries()

    def set(self,key,value=None):
        self.config[key]=value

    def get(self,key):
        return self.config.get(key) 

    def __populateDefaultEntries(self):        
        base_dir=None
        if not self.node.isRemote:
            base_dir = os.path.expanduser('~/.convirt/')
            if not os.path.exists(base_dir):
                os.mkdir(base_dir)
        
        client_config=ClientConfiguration()
        if base_dir is not None:
            base=base_dir
            log_dir = os.path.join(base,"log")
            i_store = os.path.join(base, 'image_store')
            a_store = os.path.join(base, 'appliance_store')
            updates_file = os.path.join(base, 'updates.xml')
        else:
            base='/var/cache/convirt'
            log_dir = client_config.get(constants.prop_log_dir)
            i_store = client_config.get(constants.prop_image_store)
            a_store = client_config.get(constants.prop_appliance_store)
            updates_file = client_config.get(constants.prop_updates_file)
        

        self.set(constants.prop_snapshots_dir, \
                            client_config.get(constants.prop_snapshots_dir))
        self.set(constants.prop_snapshot_file_ext,\
                            client_config.get(constants.prop_snapshot_file_ext))
        self.set(constants.prop_cache_dir,\
                            client_config.get(constants.prop_cache_dir))
        self.set(constants.prop_exec_path,\
                            client_config.get(constants.prop_exec_path))
        self.set(constants.prop_image_store, i_store)
        self.set(constants.prop_appliance_store, a_store)
        self.set(constants.prop_updates_file, updates_file)

        self.set(constants.prop_log_dir,log_dir)
        
        # set localhost specific properties
        if not self.node.isRemote:
            #self.add_section(constants.LOCALHOST)
            self.set(constants.prop_dom0_kernel,platform.release())

Index("config_nid", NodeConfiguration.node_id)

#class UserPreferences(DeclarativeBase):
#    """
#    Class that stores the configuration details for a ManagedServer.
#    """
#    __tablename__='user_preferences'
#    id=Column(Unicode(50),primary_key=True)
#    user_id=Column(Unicode(50))
#    preferences=Column(PickleType)
#
#    def __init__(self,user_id):
#        self.id=getHexID()
#        self.user_id=user_id
#        self.preferences={}



