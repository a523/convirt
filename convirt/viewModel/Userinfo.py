#! /usr/bin/python
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
from sqlalchemy.orm import eagerload
from sqlalchemy import func
from sqlalchemy.sql.expression import not_, or_, and_
from convirt.model.DBHelper import DBHelper
from convirt.model.auth import User,Group
from convirt.model.Operation import Operation,OperationGroup

from convirt.model.services import Task
from convirt.model.Entity import Entity,EntityType
from convirt.model.VM import VM
from convirt.model.ManagedNode import ManagedNode

from convirt.core.services.tasks import *
import simplejson as json
from datetime import datetime
from convirt.model import DBSession
from convirt.core.utils.utils import to_unicode,to_str,print_traceback,convert_to_CMS_TZ
import convirt.core.utils.constants
constants = convirt.core.utils.constants
from pylons.i18n import ugettext as _
from datetime import datetime,timedelta
import calendar
import logging
LOGGER = logging.getLogger("convirt.viewModel")

class Userinfo:
    def save_user_det(self, login,userid, username, fname, lname, displayname, password, email, phone, status):
       
        user1=DBSession.query(User).filter(User.user_name==username).first()
        
        if user1 is None:
           if not self.check_email(email):
               return 'Email_exist'
           result = []
           user=User()  
           user.password=(password)
           user.firstname=(fname)
           user.lastname=(lname)
           user.display_name=(displayname)
           user.user_name=(username)
           user.phone_number=(phone)
           user.email_address=(email)
           user.created_by=(login)
           user.modified_by=(login)
           user.created_date=datetime.now()

           if status=="InActive":
              user.status=False

#           L=(groupids).split(',')
#           if groupids !="":
#                for i in L:
#                    group=DBSession.query(Group).filter(Group.group_id==int(i)).first()
#                    user.groups.append(group);

           DBHelper().add(user)
           return result
        else:
             result='False'
             return result

    def delete_user(self,userid):
        userid=int(userid)
        user=DBSession.query(User).filter(User.user_id==userid).first()
        if user is not None:
            if user.user_name in constants.DEFAULT_USERS:
                raise Exception("Can not delete "+user.user_name+" user.")
            DBHelper().delete_all(User,[],[User.user_id==userid])

    def check_email(self, email, userid = None):
        #email = None
        query = DBSession.query(User).filter(User.email_address == email)
        if userid is not None:
            query = query.filter(User.user_id != userid)
        obj = query.first()
        if obj is None:
            return True
        else:
            return False

    def updatesave_user_det(self, login, userid, username, fname, lname, displayname,  email, phone, status,changepass,newpasswd):

        result = []

        if not self.check_email(email, userid):
            return "Email_exist"

        user=DBSession.query(User).filter(User.user_id==userid).first()
        user.user_name=(username)
        user.firstname=(fname)
        user.lastname=(lname)
        user.display_name=(displayname)
        #user.password=(password)
        user.email_address=(email)
        user.phone_number=(phone)
        user.modified_date=datetime.now()
        user.modified_by=(login)
        newpasswd = (newpasswd)
       
        if changepass == "true":
           user.password=newpasswd

        if status=="InActive":
           user.status=False

#        for group in user.groups:
#            user.groups.remove(group)
#
#        groupids = groupids[0:-1]
#        L=(groupids).split(',')
#        print L,"**************",groupids
#        if groupids !="":
#            for i in L:
#                group=DBSession.query(Group).filter(Group.group_id==int(i)).first()
#                user.groups.append(group);

        DBHelper().update(user)

        return result

    def edit_user_det(self,userid):
        result=[]
        gnames=""
        user=DBSession.query(User).filter(User.user_id==userid).first()
        for g in user.groups:
            gnames+=g.group_name+","
        if user.status==True:
            status="Active"
        else:
            status="InActive"

        result.append(dict(userid=user.user_id,username=user.user_name,fname=user.firstname,\
                        lname=user.lastname,displayname=user.display_name,password=user._password,\
                        repass=user._password,phone=user.phone_number,email=user.email_address,\
                        status=status,createdby=user.created_by,modifiedby=user.modified_by,\
                        createddate=user.created_date,modifieddate=user.modified_date,groupname=gnames))
        return result

    def change_user_password(self, userid, newpasswd, oldpasswd):
        result = []
        user=DBSession.query(User).filter(User.user_name==userid).first()
        if(user.validate_password(oldpasswd)):
            user.password=newpasswd
            DBHelper().update(user)
            return result
        else:
            raise Exception('Old Password is not valid.<br>Please enter valid Password.')

    def get_togroups_map(self,userid):
         result= []
         user=DBSession.query(User).filter(User.user_id==userid).first()
         groups=user.groups
         for g in groups:
               gid=g.group_id
               gname=(g.group_name)
               result.append(dict(groupid=gid,groupname=gname))
         return result

    def get_users(self):
        result= []
        users=DBHelper().get_all(User)
        for u in users:
            strgroup=''
            uid=u.user_id
            uname=u.user_name
            name=""
            if u.firstname is not None:
                name=u.firstname+" "+u.lastname
            for g in u.groups:
                strgroup += g.group_name + ","
            strgroup = strgroup[0:-1]
            result.append(dict(userid=uid,username=uname,name=name,group=strgroup))
        return result

    def save_group_details(self,login,groupid, groupname, userids,desc):

        dupGrp=None
        group=Group()
        db=DBHelper()
        session=DBHelper().get_session()
        dupGrp=session.query(Group).filter(Group.group_name==groupname).first()
        if dupGrp is None:
           result = []
           group.group_name=groupname           
           group.created_by=(login)
           group.modified_by=(login)
           group.created_date=datetime.now()
           group.description=desc

           L=(userids).split(',')
           if userids !="":
              for i in L:
                  user=session.query(User).filter(User.user_id==int(i)).first()
                  group.users.append(user);

           db.add(group)
           return result
        else:
            result="False"
            return result

    def delete_group(self,groupid):
        groupid=int(groupid)
        group=DBSession.query(Group).filter(Group.group_id==groupid).first()
        if group is not None:
            if group.group_name in constants.DEFAULT_GROUPS:
                raise Exception("Can not delete "+group.group_name+" group.")
            DBHelper().delete_all(Group,[],[Group.group_id==groupid])

    def updatesave_group_details(self,login,groupid, groupname, userids,desc):

        result = []
        group=Group()
        session=DBHelper().get_session()
        if groupname in constants.DEFAULT_GROUPS:
            user=session.query(User).filter(User.user_name==constants.DEFAULT_USERS[0]).first()
            new_ids =[]
            if userids !="":
                new_ids=(userids).split(',')
            new_ids = [int(id) for id in new_ids]
            if user.user_id not in new_ids:
                raise Exception("Can not remove user "+user.user_name+" from "+groupname)
       
        group=session.query(Group).filter(Group.group_id==groupid).first()
        group.group_name=groupname        
        group.description=desc
        group.modified_date=datetime.now()
        group.modified_by=(login)

        for user in group.users:
            group.users.remove(user)

        if userids !="":
            L=(userids).split(',')
            for i in L:
                user=session.query(User).filter(User.user_id==int(i)).first()
                group.users.append(user)

        DBHelper().update(group)

        return result

    def get_groupsdetails(self):
        result= []
        groups=DBHelper().get_all(Group)
        for g in groups:
            groupid=g.group_id
            groupname = g.group_name
            groupdesc = g.description
            result.append(dict(groupid=groupid,groupname=groupname,desc=groupdesc))
        return result

    def edit_group_details(self,groupid):
        result=[]
        group=Group()
        session=DBHelper().get_session()
        group=session.query(Group).filter(Group.group_id==groupid).first()
        result.append(dict(groupid=group.group_id,groupname=group.group_name,createdby=group.created_by,modifiedby=group.modified_by,createddate=group.created_date,modifieddate=group.modified_date,desc=group.description))
        return result

    def get_tousers_map(self,groupid):
         result= []
         session=DBHelper().get_session()
         group=session.query(Group).filter(Group.group_id==groupid).first()
         users=group.users
         for u in users:
               uid=u.user_id
               uname=(u.user_name)
               result.append(dict(userid=uid,username=uname))
         return result

    def get_groups_map(self,userid=None):
         result= []
         session=DBHelper().get_session()
         groups=DBHelper().get_all(Group)
         user=session.query(User).filter(User.user_id==userid).first()


         for g in groups:
             gid=g.group_id
             gname=(g.group_name)
             result.append(dict(groupid=gid,groupname=gname))

         if userid is None:
             return result
         else:
             for grp in user.groups:
                 i = 0
                 for group in result:
                     if grp.group_id == group['groupid']:
                         del result[i]
                         break
                     i += 1
         return result
    def get_users_map(self,groupid=None):
         result= []
         users=DBHelper().get_all(User)
         session=DBHelper().get_session()
         group=session.query(Group).filter(Group.group_id==groupid).first()
         for u in users:
             uid=u.user_id
             uname=(u.user_name)
             result.append(dict(userid=uid,username=uname))

         if groupid is None:
             return result
         else:
             for grp in group.users:
                 i = 0
                 for user in result:
                     if grp.user_id == user['userid']:
                         del result[i]
                         break
                     i += 1

         return result

    def get_tooperations_map(self,opsgroupid):
         result= []
         session=DBHelper().get_session()
         opsgroup=session.query(OperationGroup).filter(OperationGroup.id==opsgroupid).first()
         operatiions=opsgroup.operations
         for o in operatiions:
               oid=o.id
               oname=(o.name)
               result.append(dict(operationid=oid,operationname=oname))
         return result

    def  get_operations_map(self,opsgrpid=None):
         result= []
         operation=DBHelper().get_all(Operation)
         session=DBHelper().get_session()
         opsgroup=session.query(OperationGroup).filter(OperationGroup.id==opsgrpid).first()

         for o in operation:
             opid=o.id
             opname=(o.name)
             result.append(dict(operationid=opid,operationname=opname))

         if opsgrpid is None:
             return result
         else:
             for oprs in opsgroup.operations:
                 i = 0
                 for operation in result:
                     if oprs.id == operation['operationid']:
                         del result[i]
                         break
                     i += 1

         return result


    def save_opsgroup_details(self,login, opsgroupname, opsgroupdesc, operation):
        dupOpsgrp=None
        db=DBHelper()
        session=DBHelper().get_session()
        dupOpsgrp=session.query(OperationGroup).filter(OperationGroup.name==opsgroupname).first()
        opsgroup=OperationGroup();
        if dupOpsgrp is None:
           result=[]
           opsgroup.name=(opsgroupname)
           opsgroup.description=(opsgroupdesc)
           opsgroup.created_by=(login)
           opsgroup.modified_by=(login)
           opsgroup.created_date=datetime.now()
           L=((operation)).split(',')
           for i in L:
               oper=session.query(Operation).filter(Operation.id==int(i)).first()
               opsgroup.operations.append(oper);

           db.add(opsgroup);
           return result
        else:
            result="False"
            return result

    def updatesave_opsgroup_details(self, login,opsgroupid ,opsgroupname, opsgroupdesc,operation):

        result = []
        opsgroup=OperationGroup();
        db=DBHelper()
        session=DBHelper().get_session()
        opsgroup=session.query(OperationGroup).filter(OperationGroup.id==opsgroupid).first()
        opsgroup.name=opsgroupname
        opsgroup.description=opsgroupdesc
        opsgroup.modified_date=datetime.now()
        opsgroup.modified_by=(login)     

        operation = operation[0:-1]
        L=(operation).split(',')
        for i in L:
                operation=session.query(Operation).filter(Operation.id==int(i)).first()
                opsgroup.operations.append(operation);
        db.update(opsgroup);
        return result
    
    def edit_opsgroup_details(self,opsgroupid):
        result=[]
        session=DBHelper().get_session()
        opsgroup=session.query(OperationGroup).filter(OperationGroup.id==opsgroupid).first()
        opsgrpid=opsgroup.id
        opsgrpname=opsgroup.name
        opsgrpdesc=opsgroup.description        

        result.append(dict(opsgroupid=opsgrpid,opsgroupname=opsgrpname,opsgroupdesc=opsgrpdesc,createdby=opsgroup.created_by,modifiedby=opsgroup.modified_by,createddate=opsgroup.created_date,modifieddate=opsgroup.modified_date))
        return result

    def get_opsgroups(self):
        result= []
        strent=''
        opsgrp=DBHelper().get_all(OperationGroup)
        for og in opsgrp:
            i=0
            sname=og.name
            opsgroupid=og.id
            strop=''
            stropid=''
            for o in og.operations:
                strop=o.name
                desc=o.description
                opsgroupname=""
                stropid=o.id
                if i == 0:
                   opsgroupname=og.name
                i+=1
                for e in o.entityType:
                    strent = e.display_name
                result.append(dict(opsgroupid=opsgroupid,opsgrpname=opsgroupname,opname=strop, opid=stropid, desc=desc,entitytype=strent,searchName=sname))
        return result

    def delete_opsgroup(self,opsgroupid):
        opsgroupid=int(opsgroupid)
        #opgroup=DBHelper().filterby(OperationGroup,[],[OperationGroup.id==opsgroupid])[0]
        DBHelper().delete_all(OperationGroup,[],[OperationGroup.id==opsgroupid])


    def get_entities(self,enttype_id):
        result= []

        entities=DBSession.query(Entity).filter(Entity.type_id==enttype_id)
        for ent in entities:
            result.append(dict(entid=ent.entity_id, entname=ent.name))
        return result

    def get_user_status_map(self):
        try:
            result=[]

            dic={ "Active": "Active",
                 "InActive" : "InAactive",
                }
            for key in dic.keys():
                  result.append(dict(id=dic[key],value=key))
        except Exception, ex:
            LOGGER.error((ex).replace("'",""))
            print_traceback()
            return "{success: false,msg: '",(ex).replace("'",""),"'}"
        return dict(success='true',user_status=result)
       
    def get_operations(self):
        result= []
        operations=DBHelper().get_all(Operation)
        for op in operations:
            strname=''
            opname=op.name
            desc=op.description
            ctxdisp=op.display
            opid=op.id

            for e in op.entityType:
                disp_name=''
                if e.display_name is not None:
                   disp_name=e.display_name
                   strname +=disp_name + " ,"
                else:
                   strname +=disp_name + " ,"

            strname = strname[0:-1]
            result.append(dict(opname=opname,description=desc,cd=ctxdisp,enttype=strname,opid=opid))
        return result

    def save_oper_det(self, login,opname, descr, context_disp, entityid,dispname,icon):
        result = []
        dupOp=None
        operation=Operation()
        db=DBHelper()
        session=DBHelper().get_session()
        dupOp=session.query(Operation).filter(Operation.name==opname).first()
        if dupOp is None:
           operation.name=(opname)
           operation.description=(descr)
           operation.display_name=(dispname)
           operation.icon=(icon)
           operation.created_by=(login)
           operation.modified_by=(login)
           operation.created_date=datetime.now()

           if context_disp=="true":
              operation.display=True
           else:
              operation.display=False

           L=(entityid).split(',')
           for i in L:
                ent=session.query(EntityType).filter(EntityType.id==int(i)).first()
                operation.entityType.append(ent);

           db.add(operation)
           return result
        else:
            result="False"
            return result

    def edit_op_det(self,opid,enttype):
        result=[]
        op=Operation()
        session=DBHelper().get_session()
        op=session.query(Operation).filter(Operation.id==opid).first()
        entitytype=(enttype)
        result.append(dict(opid=op.id,opname=op.name,desc=op.description,contextdisplay=op.display,enttype=entitytype,createdby=op.created_by,modifiedby=op.modified_by,createddate=op.created_date,modifieddate=op.modified_date,dispname=op.display_name,icon=op.icon))
        return result

    def updatesave_op_det(self, login,opid, opname, desc, entid, context_disp,dispname,icon):

        result = []
        op=Operation()
        db=DBHelper()
        session=DBHelper().get_session()
        op=session.query(Operation).filter(Operation.id==opid).first()
        op.name=(opname)
        op.description=(desc)
        op.modified_date=datetime.now()
        op.modified_by=(login)
        op.display_name=(dispname)
        op.icon=(icon)

        if context_disp=="true":
            op.display=True
        else:
            op.display=False


        for i in op.entityType:
                op.entityType.remove(i);

        L=(entid).split(',')
        if entid !="":
             for i in L:
                ent=session.query(EntityType).filter(EntityType.id==int(i)).first()
                op.entityType.append(ent);
               

        db.update(op)
        return result
    def delete_operation(self,opid):
         opid=int(opid)
         #operation=DBHelper().find_by_id(Operation,opid)
         DBHelper().delete_all(Operation,[],[Operation.id==opid])


    def get_entitytype_map(self,opid=None):
         result= []
         session=DBHelper().get_session()
         enty=DBHelper().get_all(EntityType)
         operation=session.query(Operation).filter(Operation.id==opid).first()
        
         for e in enty:
             eid=e.id
             ename=(e.display_name)
             result.append(dict(entid=eid,entname=ename))

         if opid is None:
             return result
         else:
             for ent in operation.entityType:
                 i = 0
                 for enttype in result:
                     if ent.id == enttype['entid']:
                         del result[i]
                         break
                     i += 1
         return result
    def get_toentitytype_map(self,opid):
         result= []
         op=DBSession.query(Operation).filter(Operation.id==opid).first()
         ents=op.entityType
         for e in ents:
               oid=e.id
               oname=(e.display_name)
               result.append(dict(entid=oid,entname=oname))
         return result
    def get_enttype(self):
        result= []
        enttype=DBHelper().get_all(EntityType)
        for e in enttype:
            ent_id=e.id
            ent_name=e.name
            disp_name=e.display_name
            result.append(dict(entid=ent_id,entname=ent_name, dispname=disp_name))
        return result

    def get_enttype_for_chart(self):
        result= []
        enttype=DBHelper().get_all(EntityType)
        for e in enttype:
            if e.name in [constants.DATA_CENTER,constants.SERVER_POOL,\
                    constants.MANAGED_NODE,constants.DOMAIN]:
                ent_id=e.id
                ent_name=e.name
                disp_name=e.display_name
                result.append(dict(entid=ent_id,entname=ent_name, dispname=disp_name))
        return result

    def save_enttype_details(self,login,enttypename,dispname):
        dupEnt=None
        db=DBHelper()
        session=DBHelper().get_session()
        dupEnt=session.query(EntityType).filter(EntityType.name==enttypename).first()
        if dupEnt is None:
           result=[]
           ent=EntityType();
           ent.name=(enttypename)
           ent.display_name=(dispname)
           ent.created_by=(login)
           ent.created_date=datetime.now()
           ent.modified_by=(login)

           db.add(ent);
           return result
        else:
           result="False"
           return result

    def edit_enttype_details(self,enttypeid):
        result=[]
        session=DBHelper().get_session()
        ent=session.query(EntityType).filter(EntityType.id==enttypeid).first()
        enttypeid=ent.id
        entname=ent.name
        entdisp=ent.display_name

        result.append(dict(enttypeid=enttypeid,entname=entname,entdisp=entdisp,createdby=ent.created_by,modifiedby=ent.modified_by,createddate=ent.created_date,modifieddate=ent.modified_date))
        return result

    def updatesave_enttype_details(self, login, enttypeid ,enttypename, dispname):

        result = []
        ent=EntityType();
        db=DBHelper()
        session=DBHelper().get_session()
        ent=session.query(EntityType).filter(EntityType.id==enttypeid).first()
        ent.name=enttypename
        ent.display_name=dispname
        ent.modified_by=(login)
        ent.modified_date=datetime.now()

        db.update(ent);
        return result

    def delete_enttype(self,enttypeid):
        enttypeid=int(enttypeid)
        #ent=DBHelper().filterby(EntityType,[],[EntityType.id==enttypeid])[0]
        #DBHelper().delete_all(EntityType,[],[EntityType.id==enttypeid])

    def get_tasks(self,uid):
        result= []
        lim=tg.config.get(constants.TaskPaneLimit)
        ago=datetime.utcnow() +timedelta(days=-long(lim))

        limit = 200
        try:
            limit = int(tg.config.get(constants.task_panel_row_limit,"200"))
        except Exception, e:
            print "Exception: ", e

        LOGGER.debug("get_tasks query start : "+to_str(datetime.utcnow()))
        tasks=DBSession.query(Task.task_id, Task.name, Task.user_name, Task.entity_name, Task.cancellable, \
                                TaskResult.timestamp, TaskResult.endtime, TaskResult.status, TaskResult.results, \
                                Task.entity_type, Task.short_desc).\
             join(TaskResult).\
             filter(or_(and_(Task.repeating == True,TaskResult.visible == True),\
             and_(Task.repeating == False,Task.entity_id != None))).\
             filter(Task.submitted_on >= ago).\
             order_by(TaskResult.timestamp.desc()).limit(limit).all()
        LOGGER.debug("get_tasks query end   : "+to_str(datetime.utcnow()))
        result = self.format_task_result_details(tasks)
        return result

    def get_task_details(self,task_ids):
        result= []
        LOGGER.debug("get_task_details query start : "+to_str(datetime.utcnow()))
        task=DBSession.query(Task).filter(Task.task_id.in_(task_ids)).\
                                options(eagerload("result")).all()
        LOGGER.debug("get_task_details query end   : "+to_str(datetime.utcnow()))
        result = self.format_task_details(task)
        return result

    def getNotifications(self,type,ids,user,entType=None):
        date2=datetime.utcnow()
        date1=date2 +timedelta(days=-1)
        tasks=[]
        notify_limit = 200
        try:
            notify_limit=int(tg.config.get(constants.NOTIFICATION_ROW_LIMIT))
        except Exception, e:
            print "Exception: ", e
        x = Task
        if type == "COUNT":
           x = func.count(Task.task_id)
        q = DBSession.query(x).join(TaskResult).filter(TaskResult.status == Task.FAILED).\
                        filter(Task.submitted_on > date1).filter(Task.submitted_on < date2)
        if not isinstance(ids,list):
            ids=ids.split(',')
        q=q.filter(Task.entity_id.in_(ids))
        if type == "DETAILS":
            q = q.options(eagerload("result"))
        tasks = q.order_by(Task.submitted_on.desc()).limit(notify_limit).all()
        if type == "COUNT":
           return tasks[0][0]
        elif type == "DETAILS":
            result= []
            result=self.format_task_details(tasks)
            return result
        
    def getSystemTasks(self,type,user):
        date2=datetime.utcnow()
        date1=date2 +timedelta(days=-1)
        if type == "COUNT":
           total=0
           task=DBSession.query(Task).filter(Task.entity_id == None).\
                filter(Task.submitted_on > date1).filter(Task.submitted_on < date2).all()

           for t in task:
               for tr in t.result:
                   status=tr.status
                   if status==2:
                      total+=1
           return total

        elif type == "DETAILS":            
            result= []            
            task=DBSession.query(Task).filter(Task.entity_id == None).\
                filter(Task.submitted_on > date1).filter(Task.submitted_on < date2).\
                order_by(Task.submitted_on.desc()).all()
            for t in task:                
                desc_tuple=t.get_short_desc()
                if desc_tuple is not None:
                    (short_desc, short_desc_params) = desc_tuple
                    tname = _(short_desc)%short_desc_params
                else:
                    tname = t.name
                username=t.user_name 
                startime=''
                endtime=''                
                for tr in t.result:
                    status=tr.status
                    ts=tr.timestamp
                    startime=to_str(ts)
                    startime=startime.split('.')
                    startime=startime[0]
                    if status==2:
                       status="Failed"
                       err=tr.results
                       tend=tr.endtime
                       endtime=to_str(tend)
                       endtime=endtime.split('.')
                       endtime=endtime[0]
                       result.append(dict(tname=tname,status=status,\
                                    st=startime,errmsg=err,user=username))
            return result

    ###SHOULD BE USED FOR GETNOTIFICATIONS ALSO
    def format_task_details(self, tasks):
        result=[]
        ent_type_txt_map = self.get_entity_type_id_text_map()
        LOGGER.debug("start format_task_details : "+to_str(datetime.utcnow()))
        for t in tasks:
            tid=t.task_id
            task_name = t.name
            if t.short_desc is not None:
                task_name = t.short_desc
            username=t.user_name
            entityName=t.entity_name
            entity_type=ent_type_txt_map.get(to_str(t.entity_type),"")
               
            startime=''
            endtime=''
            err=''
            for tr in t.result:
                status=tr.status
                startime=convert_to_CMS_TZ(tr.timestamp)
#                startime=startime[0]
                if status==1:
                   status="Started"
                elif status==2:
                     status="Failed"
                     endtime=convert_to_CMS_TZ(tr.endtime)
#                     endtime=endtime[0]
                     err=tr.results
                elif status==3:
                     status="Succeeded"
                     endtime=convert_to_CMS_TZ(tr.endtime)
#                     endtime=endtime[0]
                     err=task_name+" "+entity_type+" "+'Completed Successfully'

#                serr=wrap(err,30)
                result.append(dict(taskid=tid,entname=entityName,enttype=entity_type,\
                                name=task_name,username=username,status=status,\
                                errmsg=err,timestamp=startime,\
                                endtime=endtime))
        LOGGER.debug("end   format_task_details : "+to_str(datetime.utcnow()))
        return result
    
    def get_entity_type_id_text_map(self):
        map={}
        ent_types=DBSession.query(EntityType).all()
        for type in ent_types:
            map[to_str(type.id)] = type.display_name
        return map
        
    def format_task_result_details(self, task_results):
        result=[]
        ent_type_txt_map = self.get_entity_type_id_text_map()
        LOGGER.debug("start format_task_result_details : "+to_str(datetime.utcnow()))
        for tpl in task_results:
            tid=tpl.task_id
            task_name = tpl.name
            username=tpl.user_name
            entityName=tpl.entity_name
            cancellable=tpl.cancellable

            startime=tpl.timestamp
            endtime=""
            stat=tpl.status

            enttype = ent_type_txt_map.get(to_str(tpl.entity_type),"")
            short_desc = tpl.short_desc

            if short_desc:
                task_name = short_desc

            err=''
            if stat in [Task.FAILED,Task.SUCCEEDED,Task.CANCELED]:
                endtime=convert_to_CMS_TZ(tpl.endtime)
                err=tpl.results

            status=Task.TASK_STATUS[stat]
            startime=convert_to_CMS_TZ(startime)

            result.append(dict(taskid=tid,entname=entityName,enttype=enttype,\
                            name=task_name,username=username,status=status,\
                            errmsg=err,timestamp=startime,cancellable=cancellable,\
                            endtime=endtime))
        LOGGER.debug("end   format_task_result_details : "+to_str(datetime.utcnow()))
        return result

