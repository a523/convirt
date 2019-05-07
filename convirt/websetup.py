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
"""Setup the convirt application"""

import logging

import transaction
import fileinput
import sys
from tg import config
from datetime import datetime
from convirt.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)
from convirt.core.utils.utils import PyConfig,getHexID
from convirt.core.utils.utils import to_unicode,to_str
from convirt.model.ManagedNode import ManagedNode
from convirt.model.PlatformRegistry import PlatformRegistry
from convirt.model.ImageStore import ImageStore,ImageGroup,Image
import convirt.core.utils.constants
constants = convirt.core.utils.constants
from convirt import model
from sqlalchemy.exc import IntegrityError
import os
import MySQLdb
from convirt import model
from convirt.model.AuthInit import initialise_auth,initialise_lookup_data
from convirt.config.ConfigSettings import ClientConfiguration
from convirt.core.utils import constants as constants
from convirt.model.Metrics import MetricsService
import tg
from convirt.model.EmailSetup import EmailSetup

#Moved from within a function : TBD : fig out if this is correct or not
from convirt.core.services.tasks import *

def setup_app(command, conf, vars):
    """Place any commands to setup convirt here"""
    load_environment(conf.global_conf, conf.local_conf)
    engin = config['pylons.app_globals'].sa_engine
    # Load the models
    
    dburl = tg.config.get("sqlalchemy.url")
    pcs = dburl.split("/")
    flag=False
    update_from_version = get_update_from_version()

    if update_from_version == None:
        print ""
        print "Doing fresh install of version " + constants._version
        if pcs[0]=='mysql:':
            (cred,con) = pcs[2].split("@")

            creds = cred.split(":")
            user = creds[0]
            passwd = None
            if len(creds)>1:
                passwd=creds[1]

            cons = con.split(":")
            host = cons[0]
            port = None
            if len(cons)>1 and cons[1]!="":
                port = int(cons[1])

            rest=pcs[3].split('?')
            db=rest[0]
            params = dict(host=host, user=user)
            if passwd is not None:
                params['passwd']=passwd
            if port is not None:
                params['port']=port

            conn = MySQLdb.connect(**params)
            try:
                cursor = conn.cursor()
                print "check if database exists"
                cursor.execute("select count(*) from information_schema.schemata where schema_name='"+db+"'")
                reslt = cursor.fetchone()
                if reslt[0] == 0:
                    print "create database"
                    cursor.execute("create database "+db+" CHARACTER SET utf8;")
                else :
                    print "database exists, check if tables exist"
                    cursor.execute("select count(*) from information_schema.tables where table_schema='"+db+"'")
                    reslt = cursor.fetchone()
                    if reslt[0] != 0:
                        raise Exception("Schema '"+db+"' already esists.")
                    else :
                        print "continue with setup"

                cursor.close()
                flag=True
            except Exception, e:
                print "Exception: ", e
                print "Drop ConVirt database and run setup again."
                # Exit and let people know.
                import sys
                sys.exit(1)
                return

        engin.execute("set storage_engine='InnoDB'")

        print "Creating tables"
        model.metadata.create_all(bind=engin)

    if flag :
        conn = MySQLdb.connect(user=user, passwd=passwd, db=db)
        cursor = conn.cursor()
        cursor.execute("show table status from "+db+" where Engine = 'MyISAM'")
        rows = cursor.fetchall()
        for row in rows:
            tname = row[0]
            cursor.execute("alter table "+tname+" ENGINE ='InnoDB'")
        cursor.close()
        conn.close()

    if update_from_version is not None:
        update_changes(update_from_version)
        return

    entity_types=initialise_auth()
    initialise_lookup_data()

    local_node = ManagedNode(hostname='localhost')
    registry = PlatformRegistry(local_node.config, {})

    tot_entities=[]
    entities=[]
    si={'id':1,'name':u'Data Center','type':'DATA_CENTER'}
    #for si in sites:
    site=model.Site(si['name'])
    s=model.Entity()
    s.name=si['name']
    s.id=si['id']
    s.entity_id=site.id
    s.type=entity_types[si['type']]
    ex_sites=model.DBSession.query(model.Site).filter(model.Site.name==si['name']).all()
    if len(ex_sites)==0:
        model.DBSession.merge(s)
        model.DBSession.merge(site)
    else:
        site=ex_sites[0]
        s.entity_id=site.id
    entities.append(s)

    locn=tg.config.get(constants.prop_image_store)
    image_store_location= to_unicode(os.path.abspath(locn))
    img_str={'id':2,'name':u'Template Library','type':'IMAGE_STORE'}
    #for img_str in image_stores:
    image_store = ImageStore(registry)
    image_store.name=img_str['name']
    image_store.location=image_store_location
    image_store._store_location=image_store_location
    image_store.id=getHexID()
    iss=model.Entity()
    iss.name=img_str['name']
    iss.id=img_str['id']
    iss.entity_id=image_store.id
    iss.type=entity_types[img_str['type']]
    ex_iss=model.DBSession.query(model.ImageStore).filter(model.ImageStore.name==img_str['name']).all()
    if len(ex_iss)==0:
        model.DBSession.merge(image_store)
        model.DBSession.merge(iss)
    else:
        image_store=ex_iss[0]
        iss.entity_id=image_store.id
    entities.append(iss)

    tot_entities.extend(entities)

    server_pools_dict={}
    server_pools=[{'id':4,'name':u'Desktops','type':'SERVER_POOL'}
    ,{'id':5,'name':u'Servers','type':'SERVER_POOL'}
    ,{'id':6,'name':u'QA Lab','type':'SERVER_POOL'}
    ]
    sp_entities=[]
    for sp in server_pools:
        grp = model.ServerGroup(sp['name'])

        e=model.Entity()
        e.name=sp['name']
        e.id=sp['id']
        e.entity_id=grp.id
        e.type=entity_types[sp['type']]
        model.DBSession.merge(model.EntityRelation(s.entity_id,grp.id,u'Children'))
        server_pools_dict[sp['name']]=e
        grps=model.DBSession.query(model.ServerGroup).filter(model.ServerGroup.name==sp['name']).all()
        if len(grps)==0:
            model.DBSession.merge(grp)
            model.DBSession.merge(e)
        else:
            grp=grps[0]
            e.entity_id=grp.id
        sp_entities.append(e)

    tot_entities.extend(sp_entities)

    img_entities=image_store._init_from_dirs()
    tot_entities.extend(img_entities)
    entities.extend(img_entities)


    #begin services code
    from convirt.core.services.task_service import TaskManager
    from convirt.core.services.execution_service import ExecutionService
    from convirt.core.services.executors import ThreadExecutor
    from convirt.core.services.tasks \
            import RefreshNodeInfoTask, RefreshNodeMetricsTask,\
            Purging, CollectMetricsForNodes, TimeBasisRollupForNodes,\
            UpdateDeploymentStatusTask, CheckForUpdateTask,\
            EmailTask, UpdateDiskSize, NodeAvailTask, VMAvailTask,\
            SendDeploymentStatsRptTask


    tasksvc = model.ServiceItem(u'Task Manager Service', \
                            TaskManager, \
                            ThreadExecutor,\
                            True)
    tasksvc.id=1
    model.DBSession.merge(tasksvc)
    execsvc = model.ServiceItem(u'Execution Service', \
                            ExecutionService, \
                            ThreadExecutor, \
                            True)
    execsvc.id=2
    execsvc.dependents = [tasksvc]
    model.DBSession.merge(execsvc)

    dc_ent = s
    refresh_task = RefreshNodeInfoTask(u'Refresh Node Information',\
                        {'quiet':True}, [], {}, None, u'admin')
    refresh_task.id = 1
    refresh_task.interval = [model.TaskInterval(720)]
    set_entity_details(refresh_task, dc_ent)
    model.DBSession.merge(refresh_task)

#    metrics_task=RefreshNodeMetricsTask(u'Refresh Node Metrics', {'quiet':True}, \
#                                       [], {}, None, u'admin')
#    metrics_task.id = 2
#    metrics_task.interval = [model.TaskInterval(0.5)]
#    model.DBSession.merge(metrics_task)
    #end services code

    purge_task = Purging(u'Purging',\
                 {'quiet':True}, [], {}, None, u'admin')
    purge_task.id = 2
    purge_task.interval = [model.TaskInterval(24*60)]
    set_entity_details(purge_task, dc_ent)
    model.DBSession.merge(purge_task)

    timebasis_rollup_task= TimeBasisRollupForNodes(u'TimeBasisRollupForNodes', {'quiet':True}, [],\
                    {}, None, u'admin')
    timebasis_rollup_task.id = 4
    timebasis_rollup_task.interval = [model.TaskInterval(15)]
    set_entity_details(timebasis_rollup_task, dc_ent)
    model.DBSession.merge(timebasis_rollup_task)

    collect_metrics_task= CollectMetricsForNodes(u'CollectMetricsForNodes', {'quiet':True}, [],\
                    {}, None, u'admin')
    collect_metrics_task.id = 3
    collect_metrics_task.interval = [model.TaskInterval(1)]
    set_entity_details(collect_metrics_task, dc_ent)
    model.DBSession.merge(collect_metrics_task)

    upd_dep_task = UpdateDeploymentStatusTask(u'Update Deployment Status',\
                        {'quiet':True}, [], {}, None, u'admin')
    upd_dep_task.id = 4
    upd_dep_task.interval = [model.TaskInterval(24*60)]
    set_entity_details(upd_dep_task, dc_ent)
    model.DBSession.merge(upd_dep_task)

    chk_upd_task = CheckForUpdateTask(u'Check For Update',\
                        {'quiet':True}, [], {}, None, u'admin')
    chk_upd_task.id = 5
    chk_upd_task.interval = [model.TaskInterval(24*60,datetime.utcnow())]
    set_entity_details(chk_upd_task, dc_ent)
    model.DBSession.merge(chk_upd_task)

    send_mail_task= EmailTask(u'EmailTask', {'quiet':True}, [],\
                    {}, None, u'admin')
    send_mail_task.id = 6
    send_mail_task.interval = [model.TaskInterval(2)]
    set_entity_details(send_mail_task, dc_ent)
    model.DBSession.merge(send_mail_task)

    update_disk_task = UpdateDiskSize(u'Updating the disk size',\
                 {'quiet':True}, [], {}, None, u'admin')
    update_disk_task.id = 7
    update_disk_interval = tg.config.get(constants.UPDATE_DISK_SIZE_INTERVAL)
    update_disk_task.interval = [model.TaskInterval(int(update_disk_interval))]
    set_entity_details(update_disk_task, dc_ent)
    model.DBSession.merge(update_disk_task)

    node_avail_task = NodeAvailTask(u'Update node availability',\
                                    {'quiet':True}, [], {}, None, u'admin')
    node_avail_task.id = 8
    node_avail_task.interval = [model.TaskInterval(1)]
    set_entity_details(node_avail_task, dc_ent)
    model.DBSession.merge(node_avail_task)

    vm_avail_task = VMAvailTask(u'Update VM availability',\
                                {'quiet':True}, [], {}, None, u'admin')
    vm_avail_task.id = 9
    vm_avail_task.interval = [model.TaskInterval(1)]
    set_entity_details(vm_avail_task, dc_ent)
    model.DBSession.merge(vm_avail_task)

    snd_dep_task = SendDeploymentStatsRptTask(u'Send Deployment Stats',\
                        {'quiet':True}, [], {}, None, u'admin')
    snd_dep_task.id = 10
    snd_dep_task.interval = [model.TaskInterval(7*24*60)] #weekly
    set_entity_details(snd_dep_task, dc_ent)
    model.DBSession.merge(snd_dep_task)

    model.DBSession.flush()

    transaction.commit()
    create_version_file()
    print ""
    print "ConVirt setup completed successfully!!"
    
    
def get_update_from_version():
    """
    """
    print ""
    print "Reading version information file upgrade/" + constants.VERSION_FILE
    if not os.path.isfile("upgrade/" + constants.VERSION_FILE):
        return None

    try:
        for line in open("upgrade/" + constants.VERSION_FILE):
            line = line.strip()
            if len(line) == 0 or line.startswith("#"):
                continue
            tokens = line.split(":")
            if len(tokens) != 2:
                print "WARNING: Invalid format: " + line
                continue
            if tokens[0].strip() == constants.DATA_VERSION:
                return tokens[1].strip()
    except IOError, e:
        print "ERROR: Failed to read version information file upgrade/" + constants.VERSION_FILE + ": " + to_str(e)

    return None;

def create_version_file():
    if not os.path.isfile("upgrade/" + constants.VERSION_FILE):
        print ""
        print "Version information file upgrade/" + constants.VERSION_FILE + " does not exist. Creating..."
        try:
            vfh = open("upgrade/" +constants.VERSION_FILE, 'w')
            vfh.write(constants.SCHEMA_VERSION + ": " + constants._version + "\n")
            vfh.write(constants.CONFIG_VERSION + ": " + constants._version + "\n")
            vfh.write(constants.DATA_VERSION + ": " + constants._version + "\n")
            vfh.write(constants.APP_VERSION + ": " + constants._version + "\n")
            print "Successfully created version information file upgrade/" + constants.VERSION_FILE
            vfh.close()
        except IOError,e:
            print "ERROR: Failed to create version information file upgrade/" + constants.VERSION_FILE + ": " + to_str(e)
            sys.exit(-1)
        finally:
            if vfh is not None:
                vfh.close()
                vfh = None

def replace_value(key, value):
    for line in fileinput.input("upgrade/" + constants.VERSION_FILE, inplace=True):
        tokens = line.split(':')
        if tokens[0].strip() == key:
            sys.stdout.write(line.replace(line, key + ": " + value + '\n'))
        else:
            sys.stdout.write(line)


def set_entity_details(task, dc_ent):
    task.set_entity_info(dc_ent)

def update_changes(update_from_version):
    """
    """
    to_version = None
    try:
        ran_update=False
        print ""
        print "Applying upgrade changes from version " + update_from_version + " to " + constants._version + "..."

        if update_from_version in [ "2.0" ]:
            upgradeTo2_0_1(update_from_version)
            to_version = "2.0.1"
            upgradeTo2_0_2(update_from_version)
            to_version = "2.0.2"
            upgradeTo2_1(update_from_version)
            to_version = "2.1"
            upgradeTo2_2(update_from_version)
            to_version = "2.2"
            ran_update=True

        if update_from_version in [ "2.0.1" ]:
            upgradeTo2_0_2(update_from_version)
            to_version = "2.0.2"
            upgradeTo2_1(update_from_version)
            to_version = "2.1"
            upgradeTo2_2(update_from_version)
            to_version = "2.2"
            ran_update=True

        if update_from_version in [ "2.0.2" ]:
            upgradeTo2_1(update_from_version)
            to_version = "2.1"
            upgradeTo2_2(update_from_version)
            to_version = "2.2"
            ran_update=True

        if update_from_version in [ "2.1", "2.1.x" ]:
            upgradeTo2_2(update_from_version)
            to_version = "2.2"
            ran_update=True

        if ran_update == True:
            model.DBSession.flush()
            transaction.commit()
            print "Successfully completed upgrade changes from version " + update_from_version + " to " + constants._version
        else:
            print "No upgrade changes to apply from version " + update_from_version + " to " + constants._version
        to_version = constants._version
    except Exception, ex:
        import traceback
        if to_version is not None:
            print "ERROR: Failed to apply upgrade changes from version " + to_version + ": " + to_str(ex)
        else:
            print "ERROR: Failed to apply upgrade changes from version " + update_from_version + ": " + to_str(ex)
        traceback.print_exc()

    if to_version is not None:
        replace_value(constants.DATA_VERSION, to_version)

def upgradeTo2_0_1(update_from_version):
    print "Upgrading to 2.0.1..."
    from convirt.core.services.tasks \
        import RefreshNodeInfoTask, RefreshNodeMetricsTask,\
        Purging, CollectMetricsForNodes, TimeBasisRollupForNodes,\
        UpdateDeploymentStatusTask, CheckForUpdateTask,\
        EmailTask, UpdateDiskSize, NodeAvailTask, VMAvailTask
    node_avail_task = NodeAvailTask(u'Update node availability',\
                                    {'quiet':True}, [], {}, None, u'admin')
    node_avail_task.id = 8
    node_avail_task.interval = [model.TaskInterval(1)]
    model.DBSession.merge(node_avail_task)

    vm_avail_task = VMAvailTask(u'Update VM availability',\
                                {'quiet':True}, [], {}, None, u'admin')
    vm_avail_task.id = 9
    vm_avail_task.interval = [model.TaskInterval(1)]
    model.DBSession.merge(vm_avail_task)

    model.DBSession.flush()
#
    transaction.commit()

    from convirt.model.availability import AvailState
#        from convirt.model import DBSession
    from convirt.model.Groups import ServerGroup
    from convirt.model.ManagedNode import ManagedNode
    from convirt.model.VM import VM



    server_groups=model.DBSession.query(ServerGroup).all()
    for s_group in server_groups:
        s_group_avail= AvailState(s_group.id, None, \
                                 AvailState.MONITORING,\
                                description = u'New ServerPool')
        s_group.current_state=s_group_avail
        model.DBSession.add(s_group_avail)

    managed_nodes= model.DBSession.query(ManagedNode).all()

    for m_node in managed_nodes:
        m_node_avail=AvailState(m_node.id, ManagedNode.UP,\
                                    AvailState.MONITORING,\
                                    description=u"Newly created node.")

        m_node.current_state=m_node_avail
        model.DBSession.add(m_node_avail)



    vm_entities= model.DBSession.query(VM).all()

    for vm in vm_entities:
        vm_avail=AvailState(vm.id, VM.NOT_STARTED, \
                                    AvailState.NOT_MONITORING,\
                                    description = u'New VM')
        vm.current_state=vm_avail
        model.DBSession.add(vm_avail)

    print "Successfully upgraded to 2.0.1"


def upgradeTo2_0_2(update_from_version):
    print "Upgrading to 2.0.2..."

    limit = 5000
    offset = 0

    from convirt.model.services import Task
    #from convirt.core.services.tasks import *

    dc_ent = model.DBSession.query(model.Entity).\
        filter(model.Entity.type_id==model.EntityType.DATA_CENTER).first()

    while True:
        start = datetime.now()
        print "Fetching next batch", start
        tasks = model.DBSession.query(Task).order_by(Task.task_id.asc()).\
                limit(limit).offset(offset).all()

        now = datetime.now()
        print "Processing next batch", start, now, (now-start).seconds
        if len(tasks) == 0:
            break

        offset += limit

        if tasks[0].entity_type is not None:
            print "Skipping batch"
            continue

        for t in tasks:
            sh_desc = t.name
            lng_desc = ""
            desc_tuple=t.get_short_desc()
            if desc_tuple is not None:
                (short_desc, short_desc_params) = desc_tuple
                sh_desc=short_desc
                try:
                    sh_desc = short_desc%short_desc_params
                except Exception,ex:
                    print "short :", short_desc, short_desc_params

            desc_tuple=t.get_desc()
            if desc_tuple is not None:
                (desc, desc_params) = desc_tuple
                lng_desc = desc
                try:
                    lng_desc = desc%desc_params
                except Exception, ex:
                    print "long ", desc, desc_params

            enttype=''
            if isinstance(t, VMConfigSettingsTask) or isinstance(t, VMRemoveTask) \
                    or isinstance(t, VMSnapshotTask) or isinstance(t, VMActionTask):
                enttype=model.EntityType.DOMAIN
            elif isinstance(t, AssociateDefnsTask):
                enttype=model.EntityType.SERVER_POOL
            elif isinstance(t, ServerActionTask) or isinstance(t, RemoveServerTask)\
                    or isinstance(t, PopulateNodeInfoTask) or isinstance(t, VMRestoreTask)\
                    or isinstance(t, VMImportTask):
                enttype=model.EntityType.MANAGED_NODE
            elif isinstance(t, ImportApplianceTask):
                enttype=model.EntityType.IMAGE_GROUP
            elif isinstance(t, AddStorageDefTask):
                enttype=model.EntityType.DATA_CENTER
            elif isinstance(t, RemoveStorageDefTask) or isinstance(t, VMMigrateTask):
                enttype=get_entity_type(t.entity_name)
            elif isinstance(t, RefreshNodeInfoTask) or isinstance(t, Purging)\
                    or isinstance(t, CollectMetricsForNodes) or isinstance(t, CollectMetrics)\
                    or isinstance(t, TimeBasisRollupForNodes) or isinstance(t, RefreshNodeMetricsTask)\
                    or isinstance(t, UpdateDeploymentStatusTask) or isinstance(t, CheckForUpdateTask)\
                    or isinstance(t, NodeAvailTask) or isinstance(t, NodesAvailability)\
                    or isinstance(t, VMAvailTask) or isinstance(t, VMAvailability)\
                    or isinstance(t, EmailTask) or isinstance(t, UpdateDiskSize):
                enttype=dc_ent.type_id
                t.set_entity_info(dc_ent)
                t.repeating=True

            t.entity_type = enttype
            t.short_desc = sh_desc
            t.long_desc = lng_desc
            model.DBSession.add(t)
            entry_end = datetime.now()

        model.DBSession.flush()
        transaction.commit()
        commit_end = datetime.now()

        print "updated "+str(offset)+" rows...total batch time", (commit_end - start).seconds

    print "Successfully upgraded to 2.0.1"
    return


def upgradeTo2_1(update_from_version):

    print "Upgrading to 2.1..."
    dc_ent = model.DBSession.query(model.Entity).filter(model.Entity.type_id==1).first()
    from convirt.core.services.tasks import SendDeploymentStatsRptTask
    snd_dep_task = SendDeploymentStatsRptTask(u'Send Deployment Stats',\
                    {'quiet':True}, [], {}, None, u'admin')
    snd_dep_task.id = 10
    snd_dep_task.interval = [model.TaskInterval(7*24*60)] #weekly
    set_entity_details(snd_dep_task, dc_ent)
    model.DBSession.merge(snd_dep_task)

    model.DBSession.flush()

    transaction.commit()

    print "Successfully upgraded to 2.1"
    return

def upgradeTo2_2(update_from_version):
    print "Upgrading to 2.2..."
    mgd_nodes = model.DBSession.query(model.ManagedNode).all()
    for node in mgd_nodes:
        if node.is_up():
            node.isHVM = node.is_HVM()
            model.DBSession.add(node)

        model.DBSession.flush()

    print "Successfully updated to 2.2"
    return



def get_entity_type(entity_name):
    ent_type=1
    ent=model.DBSession.query(model.Entity).filter_by(name=entity_name).first()
    if ent:
        ent_type=ent.type_id
    else:
        print "WARNING : Entity ", entity_name , " not found! May have been deleted. "
    return ent_type
