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
#
# Sessions.py
#
#   This module contains the classes related to sessions and session management
#

from tg import session

from datetime import datetime

class SessionManager(object):
    def getSession(self):
        id = session.id
        if session.has_key('sessionInfo'):
            return session['sessionInfo']
        else:
            sessionInfo = SessionInfo(id)
            session['sessionInfo'] = sessionInfo
            session.save()
            return sessionInfo
    
# container for application-specific session state
class SessionInfo(object):
    def __init__(self, id):
        self.id = id
        self.isValid = 0
        self.username = ""
        self.password = ""
        self.group = ""
        self.role = ""
        
    def login(self, username, password, id):
        self.username = username
        self.password = password
        self.role = "superUser"
        self.group = "superGroup"
        self.isValid = 1
        self.id = id
        session['sessionInfo'] = self
        session.save()
        
    def logout(self):
        self.isValid = 0
        session.delete() 

    def toXml(self, xml):
        sess = xml.createElement("sessionInfo")
        sess.setAttribute("id", str(self.id))
        sess.setAttribute("valid", str(self.isValid))
        sess.setAttribute("username", self.__getattribute__("username"))
        return sess
   
