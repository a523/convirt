import pylons
from convirt.model import DBSession

from convirt.model import *
from convirt.model.Authorization import AuthorizationService
from convirt.model.UpdateManager import UIUpdateManager,AppUpdateManager
from tg import url, request,session
from convirt.core.utils.utils import get_edition_string,get_version
from convirt.model.NodeCache import NodeCache
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from convirt.viewModel.NodeService import NodeService
from convirt.viewModel.TaskCreator import TaskCreator
from convirt.viewModel.Userinfo import Userinfo
from convirt.viewModel.EmailService import EmailService
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
from convirt.model.TopCache import TopCache

import convirt.core.utils.constants
constants = convirt.core.utils.constants

import logging,tg
LOGGER = logging.getLogger("convirt.controllers")
# the global session manager
#sessionManager = SessionManager()

#from tgrum import RumAlchemyController
from convirt.controllers.ControllerBase import ControllerBase
class ControllerImpl(ControllerBase):
    
    node_service=NodeService()
    user_info=Userinfo()
    tc = TaskCreator()
    email_service=EmailService()
    def login(self, came_from=url('/')):
        """Start the user login."""
        if session.get('userid') is None and request.identity is not None:
            self.redirect_to(url('/user_logout'))
#        login_counter = request.environ['repoze.who.logins']
#        if login_counter > 0:
#            flash(_('Wrong credentials'), 'warning')
        return dict(page='login',came_from=came_from)

    def user_login(self,args):
        try:
            username = args.get('login')
            password = args.get('password')
            
            user = DBSession.query(User).filter(User.user_name==username).first()
            if user:
                if user.status != True:
                    msg="User: "+username+" is not Active."
                    LOGGER.info(msg)
                    return dict(success=False,user=None,msg=msg)
                sqa_sts = user.validate_password(password)
                if not sqa_sts:
                    msg="Invalid password provided for CMS authentication."
                    LOGGER.info(msg)
                    return dict(success=False,user=None,msg=msg)
                if not len(user.groups):
                    msg="User should belongs to a group"
                    LOGGER.info(msg)
                    return dict(success=False,user=None,msg=msg)
            else:
                msg="Invalid username provided for CMS authentication."
                LOGGER.info(msg)
                return dict(success=False,user=None,msg=msg)
            return dict(success=True,user=username)
        except Exception, e:
            print "Exception", e
            LOGGER.error(e)
            return dict(success=False,user=None,msg=str(e))
        

    def post_login(self,userid,came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        """
        result=''
        if not userid:            
            result = "{success:false,msg:'session expired'}"
            return result

        u=User.by_user_name(to_unicode(userid))
        g=Group.by_group_name(to_unicode('adminGroup'))
        auth=AuthorizationService()
        auth.user=u
            
        session['username']=u.user_name
        session['user_firstname']=u.firstname
        session['has_adv_priv']=tg.config.get(constants.ADVANCED_PRIVILEGES)
        session['PAGEREFRESHINTERVAL']=tg.config.get(constants.PAGEREFRESHINTERVAL)
        session['TASKPANEREFRESH']=tg.config.get(constants.TASKPANEREFRESH)
        session['userid']=userid
        session['auth']=auth
        session['edition_string']=get_edition_string()
        session['version']=get_version()
        self.update_registerd_session()
        is_admin = u.has_group(g)
        session['is_admin']=is_admin
        session.save()
        TopCache().delete_usercache(auth)

        result = "{success:true}"
        return result
        
    def post_logout(self, came_from=url('/')):
        """Redirect the user to the initially requested page on logout and say
        goodbye as well."""
        #flash(_('We hope to see you soon!'))
#        sessionInfo = getSession()
#        sessionInfo.logout()
        try:
            if session.get('username'):
                UIUpdateManager().del_user_updated_entities(session['username'])
                UIUpdateManager().del_user_updated_tasks(session['username'])
        except Exception, e:
            print_traceback()
            LOGGER.error(to_str(e))
        session.delete()
        #self.redirect_to(url('/login'))
    def update_registerd_session(self):
        session['did'] = 0
        session['registered'] = False
        from convirt.model import DBSession,Deployment
        dep=DBSession.query(Deployment).first()
        if dep:
            session['did'] = dep.deployment_id
            session['registered'] = dep.registered
            session.save()

    def index(self):
        """Handle the front-page."""
        try:
            self.authenticate()
        except Exception, e:
            #print "Exception: ", e
            self.redirect_to(url('/login'))
        self.update_registerd_session()
        return dict(page='index',user_name=session['username'],\
                                has_adv_priv=session['has_adv_priv'],\
                                is_admin=session['is_admin'],\
                                user_firstname=session['user_firstname'],\
                                TASKPANEREFRESH=session['TASKPANEREFRESH'],\
                                page_refresh_interval=session['PAGEREFRESHINTERVAL'],\
                                version=session['version'],\
                                edition_string=session['edition_string'],\
                                registered=session['registered'],\
                                did=session['did'])

    def has_admin_role(self):
        try:
            self.authenticate()            
            return dict(success=True,result=session['is_admin'])
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))

    def get_app_updates(self):
        self.authenticate()
        try:
            updates=[]
            userid = session['userid']
            updates=AppUpdateManager().check_user_updates(userid)
            return dict(success=True,updates=updates)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        
    def get_nav_nodes(self):
        result=[]
        try:
            result=self.node_service.get_nav_nodes(session['auth'])
            return dict(success=True,nodes=result)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))

    def get_used_ports_info(self):
        try:
            nc = NodeCache().get_cache()
            print nc
            result = []
            for n, c in nc.iteritems():
                res = "\n\n Server : '%s'" %n
                for p, d in c['ports'].iteritems():
                    res += "\n\t Port : '%s' , Time : '%s'" %(p, d)

                result.append(res)

            return highlight("\n".join(result), PythonLexer(), HtmlFormatter(
                full=False,
                # style="native",
                noclasses=True,
            ))
        except Exception, ex:
            print_traceback()
            return "<html>Error getting Ports information.</html>"

    def get_vnc_info(self,node_id,dom_id):
        try:
            self.authenticate()
            host=pylons.request.headers['Host']
                        
            if host.find(":") != -1:
                (address,port)=host.split(':')
            else:
                address = host                
            
            #(address,port)=host.split(':')
            result = self.node_service.get_vnc_info(session['auth'],node_id,dom_id,address)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,vnc=result)


    def get_ssh_info(self,node_id,client_platform):
        result = []
        try:
            self.authenticate()
            host=pylons.request.headers['Host']
            if host.find(":") != -1:
                (address,port)=host.split(':')
            else:
                address = host

            #(address,port)=host.split(':')
            result = self.node_service.get_ssh_info(session['auth'],node_id,address,client_platform)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", " "))
        return dict(success=True,vnc=result)
        

    def get_platforms(self,**kw):
        try:
            self.authenticate()
            result = self.node_service.get_platforms()
        except Exception, ex:
            print_traceback()
            raise ex
        return result

    def get_context_menu_items(self,node_id,node_type,_dc=None,menu_combo=None):
        try:
            self.authenticate()
            result=self.getUserOps(node_id,node_type,menu_combo)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)
    
    def getUserOps(self,ent_id,nodeType=None,menu_combo=None):
        
        result=[]
        ent=session['auth'].get_entity(ent_id,nodeType)
        if ent is None:
            return result
        ops = session['auth'].get_ops(ent)

        for o in ops:
            if o.display==True:
                result.append(dict(value=o.display_id,text=o.display_name,id=o.id,icon=o.icon))
            if menu_combo!='True' and o.has_separator==True:
                    result.append(dict(name='--'))
        return result    
   
    def get_tasks(self,_dc=None):
        try:
            self.authenticate()
            result = None
            result=self.user_info.get_tasks(session['userid'])
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

    def getNotifications(self,type,list,user,entType=None,_dc=None):
        try:
            self.authenticate()
            result = None
            result=self.user_info.getNotifications(type,list,user,entType)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

    def getSystemTasks(self,type,user,_dc=None):
        try:
            self.authenticate()
            result = None
            result=self.user_info.getSystemTasks(type,user)
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

    def get_failed_tasks(self,_dc=None):

        try:
            self.authenticate()
            result = None
            result=self.user_info.get_failed_tasks(session['userid'])
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

    def save_email_setup_details(self, desc, servername, port, useremail, password, secure, ** kw):
        try:
            result = None
            self.authenticate()
            result = self.email_service.save_email_setup_details( desc, servername, port, useremail, password, secure )
            return  result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))

    def update_email_setup_details(self, desc, servername, port, useremail, password, secure, ** kw):
        result = None
        self.authenticate()
        result = self.email_service.update_email_setup_details( desc, servername, port, useremail, password, secure)
        return  result

    def send_test_email(self, desc, servername, port, useremail, password, secure, ** kw):   
        try:
            self.authenticate()
            msgreceived = self.email_service.send_test_email(desc, servername, port, useremail, password, secure)
            return msgreceived
        except Exception, ex:
            print_traceback()
            raise ex
#            return dict(success=False,msg=to_str(ex).replace("'",""))

    def get_emailsetupinfo(self,_dc=None):
        try:
            self.authenticate()
            result = None
            result=self.email_service.get_emailsetupinfo()
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))            
        return dict(success=True,rows=result)

    def delete_emailrecord(self,emailsetup_id):
        try:
            self.authenticate()
            self.email_service.delete_emailrecord(emailsetup_id)
            return {'success':True, 'msg':'Email Record Deleted.'}
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}

    def get_emailsetup_details(self,emailsetup_id):
        try:
            result = None
            self.authenticate()
            result = self.email_service.get_emailsetup_details(emailsetup_id)
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}
        return {'success':True, 'emailsetup_details':result}

    def fix_vm_disk_entries(self, **kwargs):
        """
        """
        msg = ""
        self.authenticate()
        try:
            msg = self.node_service.fix_vm_disk_entries(session['auth'], **kwargs)
            return msg
        except Exception, ex:
            print_traceback()
            msg = to_str(ex).replace("'","")
            return msg
    
