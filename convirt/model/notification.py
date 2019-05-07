#!/usr/bin/env python
#
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
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
#
#
# author : Jd <jd_jedi@users.sourceforge.net>
#

from convirt.core.utils.utils import getHexID
from sqlalchemy import  Column,ForeignKey, DateTime, PickleType, Boolean, Unicode
from sqlalchemy.types import *
from tg import session
from convirt.model import DeclarativeBase

class Notification(DeclarativeBase):
    __tablename__ = 'notification'
    id = Column(Integer, primary_key=True)
    task_id=Column(Unicode(50))
    task_name=Column(Unicode(255))
    user_name=Column(Unicode(255))
    mail_status=Column(Boolean, default=False)
    emailId = Column(Unicode(255),  nullable=False)
    error_time = Column(DateTime)
    error_msg = Column(PickleType)
    subject = Column(Unicode(255))

    def __init__(self, task_id, task_name, timestamp, results, user, email, subject =None):
        self.task_id = task_id
        self.task_name = task_name
        self.user_name = user
        self.emailId = email
        self.error_time=timestamp
        self.error_msg = results
        self.subject = subject 
        
    def __repr__(self):
        return '<Notification with id %s and timestamp %s returned %s>' % \
                (self.id, self.error_time, self.mail_status)
