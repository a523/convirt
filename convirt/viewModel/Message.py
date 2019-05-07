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
# Message.py
#
#    This class is a container for responses sent to the web-client it will
#    contain a SessionInfo object and a payload if the session is valid.
#    If the session is valid the payload will represent the actual response
#    for the request.  This allows the server to validate the session state
#    for any/every call.  
#
#    Also note that any object that is used as a payload MUST provide a toXml
#    method that is used to produce the marhalled version of the payload.
#

#import cherrypy
from Sessions import SessionInfo
from xml.dom import minidom

class Message:
    def __init__(self, sess, resp, tag=None):
        self.sessionInfo = sess
        self.response = resp
        self.tag = tag
        
    def toXml(self):
        # Create a new xml document*
        xml = minidom.Document()
        message = xml.createElement("message")
        message.appendChild(self.sessionInfo.toXml(xml))
        if self.response is not None:
            if isinstance(self.response, list) :
                listCtr = xml.createElement(self.tag)
                for item in self.response :
                    listCtr.appendChild(item.toXml(xml)) 
                message.appendChild(listCtr)
            else :             
                message.appendChild(self.response.toXml(xml))
        xml.appendChild(message)
        return xml