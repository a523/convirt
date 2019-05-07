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


from convirt.model import DBSession,Group
from convirt.model.EmailManager import EmailManager
from convirt.core.utils.utils import fetch_isp,getText,populate_node,to_str,to_unicode,get_product_edition
import tg
from convirt.core.utils.utils import PyConfig
import xml.dom.minidom
import os,tempfile,datetime,time,traceback
from datetime import datetime,timedelta
import logging
LOGGER = logging.getLogger("convirt.model")


class AppUpdateManager:

    def __init__(self):
        self.update_url = "http://www.convirture.com/updates/updates.xml"
        self.updates_file = "/var/cache/convirt/updates.xml"

    def check_for_updates(self,send_mail=False):

        update_items = []
        dep=None
        try:
            from convirt.model import Deployment
            deps=DBSession.query(Deployment).all()
            if len(deps) > 0:
                dep=deps[0]
                #update_items=retrieve_updates(dep.deployment_id)
                edition = get_product_edition()
                (new_updates,max_dt)=self.get_new_updates(dep.deployment_id,dep.update_checked_date, edition)

                if send_mail and new_updates :
                    self.send_update_mails(new_updates)
            else:
                LOGGER.error("Deployment table is not set. Update can not proceed.")
                return update_items
        except Exception, ex:
            traceback.print_exc()
            LOGGER.error("Error fetching updates:"+to_str(ex))
            return update_items

        #update deployment table
        try:
            dep.update_checked_date=datetime.utcnow()
            DBSession.add(dep)
        except:
            pass

        return update_items

    # every time it is called it gets new updates from last time
    # it was called.
    def get_new_updates(self,guid,update_checked_date, edition=None):
        new_updates = []
        updates = self.retrieve_updates(guid)

        r_date=update_checked_date

        max_dt = r_date
        for update in updates:
            str_p_dt = to_str(update["pubDate"])

            if str_p_dt:
                p_dt = time.strptime(str_p_dt, "%Y-%m-%d %H:%M:%S")
                dt = datetime(*p_dt[0:5])
                if dt > r_date :
                    if edition:
                        pltfom = to_str(update["platform"])
                        platforms = pltfom.split(",")
                        if edition in platforms or 'ALL' in platforms:
                            new_updates.append(update)
                            if dt > max_dt:
                                max_dt = dt

        str_max_dt = r_date.strftime("%Y-%m-%d %H:%M:%S")
        if max_dt > r_date:
            str_max_dt = max_dt.strftime("%Y-%m-%d %H:%M:%S")

        return (new_updates,str_max_dt)

    def retrieve_updates(self,guid):

        update_items = []
        try:
            # file is not writable..lets create a tmp file
            if not os.access(self.updates_file,os.W_OK):
                (t_handle, t_name) = tempfile.mkstemp(prefix="updates.xml")
                self.updates_file = t_name
                os.close(t_handle) # Use the name, close the handle.

            self.update_url+="?guid="+guid
            fetch_isp(self.update_url, self.updates_file, "/xml")
        except Exception, ex:
            traceback.print_exc()
            LOGGER.error("Error fetching updates:"+to_str(ex))
            try:
                if os.path.exists(self.updates_file):
                    os.remove(self.updates_file)
            except:
                pass
            return update_items

        if os.path.exists(self.updates_file):
            updates_dom = xml.dom.minidom.parse(self.updates_file)
            for entry in updates_dom.getElementsByTagName("entry"):
                info = {}
                for text in ("title","link","description", "pubDate",
                             "product_id", "product_version","platform"):
                    info[text] = getText(entry, text)
                populate_node(info,entry,"link",
                          { "link" : "href"})
                update_items.append(info)

        # cleanup the file
        try:
            if os.path.exists(self.updates_file):
                os.remove(self.updates_file)
        except:
            pass

        return update_items

    def send_update_mails(self,updates):

        grp=Group.by_group_name(to_unicode('adminGroup'))
        emailer=EmailManager()

        for usr in grp.users:

            for update in updates:
                sent=True
                try:
                    sent=emailer.send_email(usr.email_address,to_str(update.get('description','')),\
                                    subject=to_str(update.get('title','')),mimetype='html')
                except Exception,e:
                    traceback.print_exc()
                    LOGGER.error("Error sending update mail:"+to_str(update.get('title','')))
                    return
                if sent == False:
                    LOGGER.error("Error sending update mail:"+to_str(update.get('title','')))
                    return

    def check_user_updates(self,username):
        update_items = []
        dep=None
        try:
            from convirt.model import Deployment
            deps=DBSession.query(Deployment).all()
            if len(deps) > 0:
                dep=deps[0]
                user_config_filename=os.path.abspath(tg.config.get("user_config"))               
                if not os.path.exists(user_config_filename):
                    user_config_file=open(user_config_filename,"w")                   
                    user_config_file.close()                    
                user_config=PyConfig(filename=user_config_filename)
                date=user_config.get(username)               
                if date !=None:
                    p_r_date =  time.strptime(date, "%Y-%m-%d %H:%M:%S")                   
                    r_date =datetime(*p_r_date[0:5])
                else:
                    r_date=datetime.utcnow()
                edition = get_product_edition()
                (update_items,max_dt) = self.get_new_updates(dep.deployment_id,r_date, edition)
                user_config[username]=max_dt
                user_config.write()
            else:
                LOGGER.error("Deployment table is not set.Update can not proceed.")
                return
        except Exception, ex:
            traceback.print_exc()
            LOGGER.error("Error fetching updates:"+to_str(ex))
            return        
        return update_items

#class Singleton(object):
#    _instance = None
#    def __new__(cls, *args, **kwargs):
#        if not cls._instance:
#            print "*****************"
#            cls._instance = super(Singleton, cls).__new__(
#                                cls, *args, **kwargs)
#        return cls._instance
#
#

from convirt.model.Entity import Entity
import threading

class UIUpdateManager:
    """
        UI Update manager for Tasks Panel and Left Nav.
    """
    __dict={}
    __dicttask={}
    lock = threading.RLock()

    def __init__(self):
        """
            ---------__dict and self.updated_entities format---------
            {'user_name':{'session_id':[entity_ids]}
             'group_name':{'session_id':[entity_ids]}
            }
            
            {u'username': {'e9a4ce5f1cf5ddcc64ab0162e46d9973':
                    [u'1500cfe9-57b2-3521-770f-2b8b52596085',
                    u'efc4d05d-2577-89e0-6a6c-d4a7aeaeca9f']
                },
            u'adminGroup': {'e9a4ce5f1cf5ddcc64ab0162e46d9973':
                [u'1500cfe9-57b2-3521-770f-2b8b52596085',
                    u'efc4d05d-2577-89e0-6a6c-d4a7aeaeca9f']
                }
            }
            ---------__dicttask and self.updated_tasks format---------
            {'user_name':{'session_id':[task_ids]}}
            
            {u'username': {'e9a4ce5f1cf5ddcc64ab0162e46d9973': [1421L, 1420L]}}

        """
        self.updated_entities=self.__dict
        self.updated_tasks=self.__dicttask

    def set_updated_entities(self,entity_ids):

        node_ids=[]
        for entity_id in entity_ids.split(','):
            node_ids=self.merge_lists(node_ids,Entity.get_hierarchy(entity_id))

        self.lock.acquire()
        try:
            for user in self.updated_entities.keys():

                up_sessions = self.updated_entities.get(user,{})
                for session,nodes in up_sessions.iteritems():

                    if len(nodes)>35:
                        nodes=[]

                    updated_nodes = self.merge_lists(nodes,node_ids)
                    self.updated_entities[user][session] = updated_nodes
        finally:
            self.lock.release()

    def get_updated_entities(self,user_name):
        up_ents=[]
        self.lock.acquire()
        try:
            session = self.get_session()
            up_sessions = self.updated_entities.get(user_name,None)
            if up_sessions == None:
                up_sessions={}
                self.updated_entities[user_name]=up_sessions

            up_ents = up_sessions.get(session,None)
            if up_ents == None:
                up_ents=[]
                self.updated_entities[user_name][session]=up_ents
            else:
                up_ents=[]
                for x in range(len(self.updated_entities[user_name][session])):
                    up_ents.append(self.updated_entities[user_name][session].pop())
        finally:
            self.lock.release()
        return up_ents

    def clear_updated_entities(self,user_name):
        session = self.get_session()
        self.updated_entities[user_name][session] = []

    def del_user_updated_entities(self,user_name):
        session = self.get_session()
        if self.updated_entities.get(user_name,None) is not None:
            if self.updated_entities.get(user_name).get(session) is not None:
                del self.updated_entities[user_name][session]


    def set_updated_tasks(self,task_id,user_name):
        self.lock.acquire()
        try:
            up_sessions = self.updated_tasks.get(user_name,{})
            for session,tasks in up_sessions.iteritems():

                if len(tasks)>35:
                    tasks=[]

                updated_tasks=self.merge_lists(tasks,[task_id])
                self.updated_tasks[user_name][session] = updated_tasks
        finally:
            self.lock.release()

    def get_updated_tasks(self,user_name):
        up_tasks=[]
        self.lock.acquire()
        try:
            session = self.get_session()
            up_sessions = self.updated_tasks.get(user_name,None)
            if up_sessions == None:
                up_sessions={}
                self.updated_tasks[user_name]=up_sessions

            up_tasks = up_sessions.get(session,None)
            if up_tasks == None:
                up_tasks=[]
                self.updated_tasks[user_name][session]=up_tasks
            else:
                up_tasks=[]
                for x in range(len(self.updated_tasks[user_name][session])):
                    up_tasks.append(self.updated_tasks[user_name][session].pop())
        finally:
            self.lock.release()
        return up_tasks

    def clear_updated_tasks(self,user_name):
        session = self.get_session()
        self.updated_tasks[user_name][session] = []

    def del_user_updated_tasks(self,user_name):
        session = self.get_session()
        if self.updated_tasks.get(user_name,None) is not None:
            if self.updated_tasks.get(user_name).get(session) is not None:
                del self.updated_tasks[user_name][session]


    def merge_lists(self,list1,list2):

        for item in list2:
            if item not in list1:
                list1.append(item)

        return list1

    def get_session(self):
        from tg import session
        return session.id
    

#update_details_dic={}
#
#def set_update_dict(user,node_id):
#    update_details_dic["user"]=user
#    update_details_dic["node_id"]=node_id
#
#def get_update_dic():
#    return update_details_dic
    
if __name__ == '__main__':

    set_update_dict("user","node_id")

    d2=get_update_dic()

    print "uptdat==\n",d2,"\n\n\n"

#    if(id(d1)==id(d2)):
#        print "&&&&&&&&&&&&&&&&&&&"
#    if(id(s1)==id(s2)):
#        print "Same ",s1,"--",s2
#    else:
#        print "Different ",s1,"--",s2
