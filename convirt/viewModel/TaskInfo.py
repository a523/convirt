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
# TaskInfo.py
#
#    This module contains all the model classes to support the cvServer
#    application.  These classes are a mix of classes that have persistent
#    counterparts in the database and those that do not.  For the sqlobject
#    ORM (with sqlite) it is possible to declare the classes and then run
#    the "tg-admin sql create" to create the schema that corresponds to these
#    classes.  This may not be the best approach, TBD.
#
#    NOTE ON IM:  this module includes some artificats related to the built-in
#    TG support for identity management, but we have not fully investigated or
#    exercised these capabilities yet.
#
#    NOTE ON SERIALIZATION: also see json.py for information on how instances
#    of these classes are serialized for delivery to the client.
#

#import cherrypy
from xml.dom import minidom

class TaskInfo:
    def __init__(self, id, type):
        self.taskId = id
        self.taskType = type
        self.taskStatus = 'undetermined'
        self.taskCompPct = 0

    def initTask(id, type):
        longRunningTask = TaskInfo(id, type)
    initTask = staticmethod(initTask)
    
    def getTask(id):
        return longRunningTask
    getTask = staticmethod(getTask)

    def toXml(self, xml):
        task = xml.createElement("taskInfo")
        task.setAttribute("taskId", str(self.taskId))
        task.setAttribute("taskType", self.taskType)
        task.setAttribute("taskStatus", self.taskStatus)
        task.setAttribute("taskCompPct", str(self.taskCompPct))
        return task

longRunningTask = TaskInfo(0, "n/a")
    