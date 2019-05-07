#!/usr/bin/env python 
#
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
# author : gizli
#    

import commands
from convirt.core.services.task_service import Task

class TaskManagerWorkSample(Task):
    def exec_task(self, ctx, location):
        return commands.getoutput('ls -l ' + location)

import re
from convirt.core.services.task_service import Processor

class GetSizeProcessor(Processor):
    def process_output(self, value, results):
        array = value.split('\n')[1:]
        size_re = re.compile(".* .* .* .* (.*) .* .* (.*)")
        res = {}
        for i in array:
            m = size_re.match(i)
            if m:
                l = len(m.groups())
                if l == 2:
                    res[m.groups(2)] = m.groups(1)
        results.append(res)

class GetOwnerProcessor(Processor):
    def process_output(self, value, results):
        array = value.split('\n')[1:]
        size_re = re.compile(".* .* (.*) .* .* .* .* (.*)")
        res = {}
        for i in array:
            m = size_re.match(i)
            if m:
                l = len(m.groups())
                if l == 2:
                    res[m.groups(2)] = m.groups(1)
        results.append(res)

from convirt.model.services import TaskItem, TaskResultItem, CalendarItem,\
                                   IntervalItem
def simple_test(session):
    list_of_processors = [GetSizeProcessor, GetOwnerProcessor]
    t = TaskItem('Sample Work', [], TaskManagerWorkSample, \
                 ['/tmp/'], {}, list_of_processors, u'admin')
    t2 = TaskItem('Sample Work2', [], TaskManagerWorkSample, \
                  ['/home/'], {}, list_of_processors, u'admin')
    t.interval = [IntervalItem(interval=5),]
    t2.calendar = [CalendarItem(dow=[], month=[], day=[], hour=[], \
                                minute=[0,5,10,15,20,25,30,35,40,45,50,55]),]
    session.add(t)
    session.add(t2)
    session.commit()

def concurrency_test(session):
    list_of_processors = [GetSizeProcessor, GetOwnerProcessor]
    total = 1000
    count = 0
    while count < total:
        count = count + 1
        t = TaskItem('Task ' + str(count), [], TaskManagerWorkSample, \
                     ['/tmp/'], {}, list_of_processors, u'admin')
        tinterval = 1
        t.interval = [IntervalItem(interval=tinterval),]
        session.add(t)
    session.commit()

def check_task_results(session):
    for tr in session.query(TaskResultItem):
        print tr
