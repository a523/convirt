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

from convirt.core.utils.utils import PyConfig,getHexID
from convirt.core.utils.utils import to_unicode,to_str
from convirt.model.ManagedNode import ManagedNode
from convirt.model.PlatformRegistry import PlatformRegistry
from convirt.model.ImageStore import ImageStore,ImageGroup,Image
from datetime import datetime
import convirt.core.utils.constants
constants = convirt.core.utils.constants

import os
from convirt import model

def initialise_auth():
    admin = model.User()
    admin.user_id=1
    admin.user_name = u'admin'
    admin.display_name = u'admin'
    admin.email_address = u'admin@somedomain.com'
    admin.password = u'admin'
    admin.firstname=u'admin'
    admin.lastname=u'admin'
    admin.status=True
    admin.created_by=u""
    admin.modified_by=u""
    admin.created_date=datetime.now()
    admin.modified_date=datetime.now()
    model.DBSession.merge(admin)    

    group1 = model.Group()
    group1.group_id=1
    group1.group_name = u'adminGroup'
    group1.display_name = u'Administrator Group'
    group1.description=u'Description about administrator Group'
    group1.created_by=u""
    group1.modified_by=u""
    group1.created_date=datetime.now()
    group1.modified_date=datetime.now()
    group1.users.append(admin)
    model.DBSession.merge(group1)    

    ent_types=[{'id':1,'name':'DATA_CENTER','disp':'Data Center'},{'id':2,'name':'IMAGE_STORE','disp':'Template Library'},{'id':3,'name':'SERVER_POOL','disp':'Server Pool'},
                {'id':4,'name':'MANAGED_NODE','disp':'Server'},{'id':5,'name':'DOMAIN','disp':'Virtual Machine'},{'id':6,'name':'IMAGE_GROUP','disp':'Template Group'},
                {'id':7,'name':'IMAGE','disp':'Template'},{'id':8,'name':'APPLIANCE','disp':'Appliance'}, {'id':9,'name':'EMAIL','disp':'Email'}]
    entity_types={}
    for ent in ent_types:
        et=model.EntityType()
        et.id=ent['id']
        et.name=_(ent['name'])
        et.display_name=_(ent['disp'])
        et.created_by=_("")
        et.modified_by=_("")
        et.created_date=datetime.now()
        et.modified_date=datetime.now()
        model.DBSession.merge(et)
        entity_types[ent['name']]=et


    operations_group=[
    {'id':1,'name':'FULL_DATA_CENTER','desc':'Full Privilege on Data Center'}
    ,{'id':2,'name':'FULL_SERVER_POOL','desc':'Full Privilege on Server Pools'}
    ,{'id':3,'name':'FULL_MANAGED_NODE','desc':'Full Privilege on Managed Node'}
    ,{'id':4,'name':'FULL_DOMAIN','desc':'Full Privilege on Domains'}
    ,{'id':5,'name':'FULL_IMAGE_STORE','desc':'Full Privilege on Image Store'}
    ,{'id':6,'name':'FULL_IMAGE_GROUP','desc':'Full Privilege on Image Groups'}
    ,{'id':7,'name':'FULL_IMAGE','desc':'Full Privilege on Images'}
    ,{'id':8,'name':'OP_IMAGE_STORE','desc':'Full Privilege on Image Store'}
    ,{'id':9,'name':'OP_SERVER_POOL','desc':'Operator Privilege on Server Pools'}
    ,{'id':10,'name':'OP_MANAGED_NODE','desc':'Operator Privilege on Managed Node'}
    ,{'id':11,'name':'OP_DOMAIN','desc':'Operator Privilege on Domains'}
    ,{'id':12,'name':'OP_IMAGE_GROUP','desc':'Operator Privilege on Image Groups'}
    ,{'id':13,'name':'OP_IMAGE','desc':'Operator Privilege on Images'}
    ,{'id':14,'name':'VIEW_SERVER_POOL','desc':'View Privilege on Server Pools'}
    ,{'id':15,'name':'VIEW_MANAGED_NODE','desc':'View Privilege on Managed Node'}
    ,{'id':16,'name':'VIEW_DOMAIN','desc':'View Privilege on Domains'}
    ,{'id':17,'name':'VIEW_IMAGE_STORE','desc':'View Privilege on Image Store'}
    ,{'id':18,'name':'VIEW_IMAGE_GROUP','desc':'View Privilege on Image Groups'}
    ,{'id':19,'name':'VIEW_IMAGE','desc':'View Privilege on Images'}
    ,{'id':20,'name':'OP_DATA_CENTER','desc':'Operator Privilege on Data Center'}
    ,{'id':21,'name':'VIEW_DATA_CENTER','desc':'View Privilege on Data Center'}
    ]
    operations_group_dict={}
    for opgrp in operations_group:
        og=model.OperationGroup()
        og.name=_(opgrp['name'])
        og.id=opgrp['id']
        og.description=_(opgrp['desc'])
        og.created_by=_("")
        og.modified_by=_("")
        og.created_date=datetime.now()
        og.modified_date=datetime.now()
        model.DBSession.merge(og)
        operations_group_dict[opgrp['name']]=og

    operations_map=[
    {'id':1,'op':'ADD_SERVER_POOL','text':'Add Server Pool','display_id':'add_server_pool','entType':'DATA_CENTER',
    'separator':False,'display':True,'seq':5,'groups':['FULL_DATA_CENTER'],'icon':'add.png'}

    ,{'id':2,'op':'ADD_SERVER','text':'Add Server','display_id':'add_node','entType':'SERVER_POOL',
    'separator':False,'display':True,'seq':10,'groups':['FULL_SERVER_POOL'],'icon':'add.png'}
    ,{'id':3,'op':'CONNECT_ALL','text':'Connect All','display_id':'connect_all','entType':'SERVER_POOL',
    'opr':True,'separator':True,'display':True,'seq':15,'groups':['FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'small_connect.png'}
    ,{'id':4,'op':'PROVISION_GROUP_VM','text':'Provision Virtual Machine','display_id':'provision_vm','entType':'SERVER_POOL'
    ,'opr':True,'separator':False,'display':True,'seq':20,'groups':['FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'provision_vm.png'}
    ,{'id':5,'op':'VIEW_GROUP_PROVISIONING_SETTINGS','text':'Provisioning Settings','icon':'settings.png',
    'display_id':'group_provision_settings','entType':'SERVER_POOL','opr':True,'separator':True,'display':True,'seq':25,'groups':['FULL_SERVER_POOL','OP_SERVER_POOL']}
    ,{'id':6,'op':'STORAGE_POOL','text':'Manage Storage','display_id':'storage_pool','entType':'DATA_CENTER,SERVER_POOL',
    'opr':True,'separator':True,'display':True,'seq':30,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'storage_pool.png'}
    ,{'id':7,'op':'REMOVE_SERVER_POOL','text':'Remove Server Pool','display_id':'remove_server_pool',
    'entType':'SERVER_POOL','separator':False,'display':True,'seq':35,'groups':['FULL_SERVER_POOL'],'icon':'delete.png'}
    ,{'id':8,'op':'EDIT_GROUP_PROVISIONING_SETTINGS','display_id':'save_group_vars',
    'entType':'SERVER_POOL','opr':True,'groups':['FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'.png'}
    ,{'id':9,'op':'ADD_STORAGE_DEF','display_id':'add_storage_def','entType':'DATA_CENTER,SERVER_POOL','opr':True,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'.png'}
    ,{'id':10,'op':'UPDATE_STORAGE_DEF','display_id':'edit_storage_def','entType':'DATA_CENTER,SERVER_POOL','opr':True,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'.png'}
    ,{'id':11,'op':'UPDATE_STORAGE_DEF','display_id':'rename_storage_def','entType':'DATA_CENTER,SERVER_POOL','opr':True,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'.png'}
    ,{'id':12,'op':'REMOVE_STORAGE_DEF','display_id':'remove_storage_def','entType':'DATA_CENTER,SERVER_POOL','opr':True,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'.png'}
    ,{'id':13,'op':'UPDATE_STORAGE_DEF','display_id':'test_storage_def','entType':'DATA_CENTER,SERVER_POOL','opr':True,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL'],'icon':'.png'}

    ,{'id':14,'op':'EDIT_SERVER','text':'Edit Server','display_id':'edit_node','entType':'MANAGED_NODE','opr':True,
    'separator':False,'display':True,'seq':40,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'file_edit.png'}
    ,{'id':327,'op':'OPEN SSH','text':'Open SSH Terminal','display_id':'ssh_node','entType':'MANAGED_NODE','opr':True,
    'separator':False,'display':True,'seq':41,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'file_edit.png'}
    ,{'id':15,'op':'CONNECT_SERVER','text':'Connect Server','display_id':'connect_node','entType':'MANAGED_NODE',
    'text':'Connect Server','opr':True,'separator':True,'display':True,'seq':45,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'small_connect.png'}
    ,{'id':100,'op':'MIGRATE_SERVER','text':'Move Server','display_id':'migrate_server','entType':'MANAGED_NODE','opr':True,
    'separator':False,'display':True,'seq':47,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'small_migrate_vm.png'}
    ,{'id':16,'op':'PROVISION_VM','text':'Provision Virtual Machine','display_id':'provision_vm','entType':'MANAGED_NODE',
    'opr':True,'separator':False,'display':True,'seq':50,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'provision_vm.png'}
    ,{'id':17,'op':'RESTORE_HIBERNATED','text':'Restore Hibernated','display_id':'restore_hibernated','entType':'MANAGED_NODE','opr':True,
    'separator':False,'display':True,'seq':55,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'small_restore.png'}
    ,{'id':18,'op':'IMPORT_VM_CONFIG_FILE','text':'Import Virtual Machine Config File(s)','display_id':'import_vm_config',
    'entType':'MANAGED_NODE','separator':True,'display':True,'seq':60,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'folder.png'}
    ,{'id':19,'op':'START_ALL','text':'Start All Virtual Machines','display_id':'start_all','entType':'MANAGED_NODE',
    'opr':True,'separator':False,'display':True,'seq':65,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'small_start.png'}
    ,{'id':20,'op':'SHUTDOWN_ALL','text':'Shutdown All Virtual Machines','display_id':'shutdown_all','entType':'MANAGED_NODE',
    'opr':True,'separator':False,'display':True,'seq':70,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'small_shutdown.png'}
    ,{'id':21,'op':'KILL_ALL','text':'Kill All Virtual Machines','display_id':'kill_all','entType':'MANAGED_NODE','opr':True,
    'separator':False,'display':True,'seq':75,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'small_kill.png'}
    ,{'id':22,'op':'MIGRATE_ALL','text':'Migrate All Virtual Machines','display_id':'migrate_all','entType':'MANAGED_NODE',
    'opr':True,'separator':True,'display':True,'seq':80,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'small_migrate_vm.png'}
    ,{'id':23,'op':'MANAGE_VIRTUAL_NETWORKS','text':'Manage Virtual Networks','display_id':'manage_virtual_networks'
    ,'entType':'DATA_CENTER,SERVER_POOL,MANAGED_NODE','opr':True,'separator':True,'display':True,'seq':85,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE','FULL_SERVER_POOL','OP_SERVER_POOL','FULL_DATA_CENTER','OP_DATA_CENTER'],'icon':'manage_virtual_networks.png'}
    ,{'id':24,'op':'REMOVE_SERVER','text':'Remove Server','display_id':'remove_node','entType':'MANAGED_NODE',
    'separator':False,'display':True,'seq':90,'groups':['FULL_MANAGED_NODE'],'icon':'delete.png'}
    ,{'id':25,'op':'TRANSFER_SERVER','display_id':'transfer_node','entType':'MANAGED_NODE','opr':True,
    'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':26,'op':'ADD_VM','display_id':'','entType':'MANAGED_NODE','opr':True,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':27,'op':'VIEW_NODE_INFO','display_id':'get_node_info','entType':'MANAGED_NODE','opr':True,'view':True,
    'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE','VIEW_MANAGED_NODE'],'icon':'.png'}
    ,{'id':28,'op':'VIEW_NODE_PROPERTIES','display_id':'get_node_properties','entType':'MANAGED_NODE',
    'opr':True,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':29,'op':'VIEW_TARGET_IMAGES','display_id':'get_target_images','entType':'MANAGED_NODE','opr':True,
    'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':30,'op':'VIEW_TARGET_IMAGE_GROUPS','display_id':'get_target_image_groups',
    'entType':'MANAGED_NODE','opr':True,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':31,'op':'VIEW_DIRECTORY_CONTENTS','display_id':'get_dir_contents','entType':'MANAGED_NODE',
    'opr':True,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':32,'op':'MAKE_DIRECTORY','display_id':'make_dir','entType':'MANAGED_NODE','opr':True,
    'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':33,'op':'MIGRATE_TARGET_NODES','display_id':'get_target_nodes','entType':'MANAGED_NODE',
    'opr':True,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}

    ,{'id':9,'op':'ADD_NETWORK_DEF','display_id':'add_network_def','entType':'DATA_CENTER,SERVER_POOL,MANAGED_NODE'
    ,'opr':True,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL','FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':10,'op':'UPDATE_NETWORK_DEF','display_id':'edit_network_def','entType':'DATA_CENTER,SERVER_POOL,MANAGED_NODE'
    ,'opr':True,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL','FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}
    ,{'id':12,'op':'REMOVE_NETWORK_DEF','display_id':'remove_network_def','entType':'DATA_CENTER,SERVER_POOL,MANAGED_NODE'
    ,'opr':True,'groups':['FULL_DATA_CENTER','OP_DATA_CENTER','FULL_SERVER_POOL','OP_SERVER_POOL','FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'.png'}


    ,{'id':34,'op':'CHANGE_VM_SETTINGS','text':'Edit Settings','display_id':'change_vm_settings','entType':'DOMAIN',
    'opr':True,'separator':True,'display':True,'seq':95,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'file_edit.png'}
    ,{'id':35,'op':'EDIT_VM_CONFIG_FILE','text':'Edit Virtual Machine Config File','display_id':'edit_vm_config_file',
    'entType':'DOMAIN','opr':True,'display':True,'seq':100,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'file_edit.png'}
    ,{'id':34,'op':'VIEW_CONSOLE','text':'View Console','display_id':'view_console','entType':'DOMAIN',
    'opr':True,'separator':False,'display':True,'seq':102,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'view_console.png'}
    ,{'id':36,'op':'MIGRATE_VM','text':'Migrate Virtual Machine','display_id':'migrate','entType':'DOMAIN','opr':True,'separator':False,'display':True,
    'seq':105,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'small_migrate_vm.png'}
    ,{'id':37,'op':'START','text':'Start','display_id':'start','entType':'DOMAIN','opr':True,'separator':False,'display':True,'seq':110,
    'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'small_start.png'}

    ,{'id':74,'op':'START_VIEW_CONSOLE','text':'Start and View Console','display_id':'start_view_console','entType':'DOMAIN','opr':True,
    'separator':False,'display':True,'seq':113,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'start_siew_console.png'}

    ,{'id':38,'op':'PAUSE','text':'Pause','display_id':'pause','entType':'DOMAIN','opr':True,'separator':False,'display':True,'seq':115,
    'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'small_pause.png'}
    ,{'id':39,'op':'UNPAUSE','text':'Resume','display_id':'unpause','entType':'DOMAIN','opr':True,'separator':False,'display':True,
    'seq':125,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'small_pause.png'}
    ,{'id':40,'op':'REBOOT','text':'Reboot','display_id':'reboot','entType':'DOMAIN','opr':True,'separator':False,'display':True,
    'seq':120,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'small_reboot.png'}
    ,{'id':41,'op':'SHUTDOWN','text':'Shutdown','display_id':'shutdown','entType':'DOMAIN','opr':True,'separator':False,'display':True,
    'seq':125,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'small_shutdown.png'}
    ,{'id':42,'op':'KILL','text':'Kill','display_id':'kill','entType':'DOMAIN','opr':True,'separator':False,'display':True,'seq':130,
    'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'small_kill.png'}
    ,{'id':43,'op':'HIBERNATE_VM','text':'Hibernate','display_id':'hibernate','entType':'DOMAIN','opr':True,'separator':False,'display':True,
    'seq':135,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'small_snapshot.png'}
    ,{'id':44,'op':'SET_BOOT_DEVICE','text':'Set Boot Device','display_id':'set_boot_device','entType':'DOMAIN',
    'opr':True,'separator':True,'display':True,'seq':140,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'file_edit.png'}
    ,{'id':45,'op':'REMOVE_VM_CONFIG','text':'Remove Virtual Machine Config','display_id':'remove_vm_config',
    'entType':'DOMAIN','opr':True,'separator':False,'display':True,'seq':145,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'vm_delete.png'}
    ,{'id':46,'op':'REMOVE_VM','display_id':'delete','text':'Remove Virtual Machine','entType':'DOMAIN','opr':True,'separator':False,'display':True,
    'seq':150,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'delete.png'}
    ,{'id':47,'op':'VIEW_VM_CONFIG_FILE','display_id':'get_vm_config_file','entType':'DOMAIN','opr':True,
    'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'.png'}
    ,{'id':48,'op':'VIEW_VM_INFO','display_id':'get_vm_info','entType':'DOMAIN','opr':True,'view':True,
    'groups':['FULL_DOMAIN','OP_DOMAIN','VIEW_DOMAIN'],'icon':'.png'}

    ,{'id':49,'op':'ADD_IMAGE_GROUP','text':'Add Template Group','display_id':'add_image_group',
    'entType':'IMAGE_STORE','separator':False,'display':True,'seq':155,'groups':['FULL_IMAGE_STORE'],'icon':'add.png'}
    ,{'id':50,'op':'VIEW_IMAGE_STORE_INFO','display_id':'get_image_store_info','entType':'IMAGE_STORE',
    'opr':True,'view':True,'groups':['FULL_IMAGE_STORE','OP_IMAGE_STORE','VIEW_IMAGE_STORE'],'icon':'.png'}

    ,{'id':51,'op':'RENAME_IMAGE_GROUP','text':'Rename Template Group','display_id':'rename_image_group',
    'entType':'IMAGE_GROUP','opr':True,'separator':False,'display':True,'seq':160,'groups':['FULL_IMAGE_GROUP','OP_IMAGE_GROUP'],'icon':'rename.png'}
    ,{'id':52,'op':'REMOVE_IMAGE_GROUP','text':'Remove Template Group','display_id':'remove_image_group',
    'entType':'IMAGE_GROUP','separator':False,'display':True,'seq':165,'groups':['FULL_IMAGE_GROUP'],'icon':'delete.png'}
    ,{'id':53,'op':'IMPORT_APPLIANCE','text':'Create Template ','display_id':'import_appliance',
    'entType':'IMAGE_GROUP,IMAGE_STORE','separator':False,'display':True,'seq':170,'groups':['FULL_IMAGE_GROUP','FULL_IMAGE_STORE'],'icon':'add_appliance.png'}
    ,{'id':54,'op':'VIEW_IMAGE_GROUP_INFO','display_id':'get_image_group_info','entType':'IMAGE_GROUP',
    'opr':True,'view':True,'seq':175,'groups':['FULL_IMAGE_GROUP','OP_IMAGE_GROUP','VIEW_IMAGE_GROUP'],'icon':'.png'}
    ,{'id':55,'op':'CREATE_IMAGE','display_id':'','text':'Add Template','entType':'IMAGE_GROUP','opr':True
    ,'groups':['FULL_IMAGE_GROUP','OP_IMAGE_GROUP'],'icon':'.png'}

    ,{'id':56,'op':'PROVISION_IMAGE','display_id':'provision_image','text':'Provision','entType':'IMAGE',
    'opr':True,'separator':True,'display':True,'seq':180,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'provision_vm.png'}
    ,{'id':57,'op':'EDIT_IMAGE_SETTINGS','display_id':'edit_image_settings','text':'Edit Settings',
    'entType':'IMAGE','opr':True,'separator':False,'display':True,'seq':185,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'file_edit.png'}
    ,{'id':58,'op':'EDIT_IMAGE_SCRIPT','text':'Edit Template Script','display_id':'edit_image_script',
    'entType':'IMAGE','opr':True,'separator':False,'display':True,'seq':190,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'file_edit.png'}
    ,{'id':59,'op':'EDIT_IMAGE_DESCRIPTION','text':'Edit Template Description','display_id':'edit_image_desc',
    'entType':'IMAGE','opr':True,'separator':True,'display':True,'seq':195,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'file_edit.png'}
    ,{'id':60,'op':'CREATE_LIKE','text':'Create Like','display_id':'clone_image','entType':'IMAGE','separator':False,'display':True,
    'seq':200,'groups':['FULL_IMAGE'],'icon':'clone.png'}
    ,{'id':61,'op':'RENAME_IMAGE','text':'Rename Template','display_id':'rename_image','entType':'IMAGE','opr':True,
    'separator':False,'display':True,'seq':205,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'rename.png'}
    ,{'id':62,'op':'REMOVE_IMAGE','text':'Remove Template','display_id':'remove_image','entType':'IMAGE','separator':False,'display':True,
    'seq':210,'groups':['FULL_IMAGE'],'icon':'delete.png'}
    ,{'id':63,'op':'TRANSFER_IMAGE','display_id':'transfer_image','entType':'IMAGE','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':64,'op':'EDIT_IMAGE_DESCRIPTION','display_id':'get_image_info','entType':'IMAGE','opr':True,'view':True
    ,'groups':['FULL_IMAGE','OP_IMAGE','VIEW_IMAGE'],'icon':'.png'}
    ,{'id':65,'op':'IMAGE_TARGET_NODES','display_id':'get_target_nodes','entType':'IMAGE','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':66,'op':'EDIT_IMAGE_SCRIPT','display_id':'get_image_script','entType':'IMAGE','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':67,'op':'VIEW_APPLIANCE_INFO','display_id':'get_appliance_info','entType':'DOMAIN','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':68,'op':'SAVE_APPLIANCE_INFO','display_id':'save_appliance_info','entType':'DOMAIN','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':69,'op':'VIEW_APPLIANCE_MENU','display_id':'','entType':'APPLIANCE','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':70,'op':'VIEW_APPLIANCE_LIST','display_id':'','entType':'APPLIANCE','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':71,'op':'VIEW_APPLIANCE_ARCHS','display_id':'','entType':'APPLIANCE','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':72,'op':'VIEW_APPLIANCE_PACKAGES','display_id':'','entType':'APPLIANCE','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}
    ,{'id':73,'op':'VIEW_APPLIANCE_PROVIDERS','display_id':'','entType':'APPLIANCE','opr':True
    ,'groups':['FULL_IMAGE','OP_IMAGE'],'icon':'.png'}


     ,{'id':74,'op':'ANNOTATE','text':'Annotate','display_id':'annotate','entType':'DOMAIN','opr':True,
    'separator':False,'display':True,'seq':146,'groups':['FULL_DOMAIN','OP_DOMAIN'],'icon':'annotation_vm.png'}

    ,{'id':75,'op':'ANNOTATE','text':'Annotate','display_id':'annotate','entType':'MANAGED_NODE','opr':True,
    'separator':False,'display':True,'seq':147,'groups':['FULL_MANAGED_NODE','OP_MANAGED_NODE'],'icon':'annotation_node.png'}



    ]

    i=0
    for opmap in operations_map:
        #opmap=operations_map[ops]
        i+=1
        o=model.Operation()
        o.id=i
        o.name=_(opmap['op'])
        o.icon=_(opmap['icon'])
        o.description=_(opmap['op'])
        o.created_by=_("")
        o.modified_by=_("")
        o.created_date=datetime.now()
        o.modified_date=datetime.now()
        if opmap.has_key('text'):
            o.display_name=_(opmap['text'])
        if opmap.has_key('display_id'):
            o.display_id=_(opmap['display_id'])
        for entType in opmap['entType'].split(","):
            o.entityType.append(entity_types[entType])
        if opmap.has_key('display'):
            o.display=opmap['display']
        if opmap.has_key('seq'):
            o.display_seq=opmap['seq']
        if opmap.has_key('separator'):
            o.has_separator=opmap['separator']
        grps=opmap['groups']
        for grp in grps:
            og=operations_group_dict[grp]
            o.opsGroup.append(og)
        model.DBSession.merge(o)

    
    return entity_types

def initialise_lookup_data():
    app_catalog=model.ApplianceCatalog(u'convirt')
    app_catalog.url=u'http://www.convirture.com/catalogs/convirt_catalog.conf'
    if model.DBSession.query(model.ApplianceCatalog).filter(model.ApplianceCatalog.name==app_catalog.name).first() is None:
        model.DBSession.merge(app_catalog)

    categories_dict={}
    nodeinfo_categories=[
    {"name":"general","display_name":"General"},
    {"name":"disk","display_name":"Disk"},
    {"name":"network","display_name":"Network"}]
    for xx in nodeinfo_categories:
        category=model.Category(_(xx['name']))
        category.display_name=_(xx['display_name'])
        categories_dict[category.name]=category
        if model.DBSession.query(model.Category).filter(model.Category.name==category.name).first() is None:
            model.DBSession.merge(category)
        

    nodeinfo_components=[
    {"type":"cpu_info","display_name":"CPU Info","category":"general"},
    {"type":"os_info","display_name":"OS Info","category":"general"},
    {"type":"memory_info","display_name":"Memory Info","category":"general"},
    {"type":"platform_info","display_name":"Platform Info","category":"general"},
    {"type":"disk_info","display_name":"Disk Info","category":"disk"},
    {"type":"network_info","display_name":"Interface Name","category":"network"},
    {"type":"nic_info","display_name":"NIC Info","category":"network"},
    {"type":"bridge_info","display_name":"Bridge Info","category":"network"},
    {"type":"default_bridge","display_name":"Default Bridge","category":"network"}]
    for xx in nodeinfo_components:
        comp=model.Component(_(xx['type']))
        comp.display_name=_(xx['display_name'])
        comp.category=categories_dict[_(xx['category'])]
        if model.DBSession.query(model.Component).filter(model.Component.type==comp.type).first() is None:
            model.DBSession.merge(comp)

def _(name):
    return to_unicode(name)