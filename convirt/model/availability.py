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


from convirt.model import DeclarativeBase, DBSession,Entity
from convirt.core.utils.utils import to_unicode,to_str,getHexID,notify_node_down,node_up_action,p_task_timing_start,p_task_timing_end
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy import DateTime, PickleType, Boolean, Unicode
from sqlalchemy.schema import Index
from datetime import datetime
import logging
import transaction

logger = logging.getLogger("convirt.availability.model")
ImmutablePickleType = PickleType(mutable=False)
availability_event_type = u'Availability'
import convirt.core.utils.constants
constants = convirt.core.utils.constants
#Generic function for updating availability
#Assumptions;
#1. Node must have a current_state relation which maps to AvailState
#2. Node must have an id field which determines the entity_id
#3. Currently only used by VNode and VM which fit to both requirements.
def update_avail(node, new_state, monit_state, timestamp, reason, logger, update=True, auth=None):
    sv_point = transaction.savepoint()
    try:
        strt = p_task_timing_start(logger, "UpdateAvailability", node.id, log_level="DEBUG")
        #there is a status change, update and send event
        #update current availability,
        #we only update avail-state, monit_state is updated
        #only by user actions
        node.current_state.avail_state = new_state
        node.current_state.timestamp = timestamp
        node.current_state.description = reason
        avh=DBSession.query(AvailHistory).filter(AvailHistory.entity_id==node.id).\
            order_by(AvailHistory.timestamp.desc()).first()
        if avh is not None:
            avh.endtime=timestamp
            time_diff=timestamp-avh.timestamp
            avh.period=time_diff.days*24*60+time_diff.seconds/60
            DBSession.add(avh)
        #insert availability history
        ah = AvailHistory(node.id, new_state, monit_state, timestamp, reason)
        DBSession.add(ah)
        if update==True:
            ent = DBSession.query(Entity).filter(Entity.entity_id==node.id).first()
            from convirt.model.ManagedNode import ManagedNode
            if ent.type.name == constants.MANAGED_NODE:
                if new_state == ManagedNode.DOWN:
                    notify_node_down(ent.name, reason)
                else:
                    node_up_action(auth, node.id)
    except Exception, e:
        #defer to next time
        import traceback
        traceback.print_exc()
        logger.error(e)
        sv_point.rollback()

    p_task_timing_end(logger, strt)    

class AvailState(DeclarativeBase):
    MONITORING = 1
    NOT_MONITORING = 0

    __tablename__ = 'avail_current'

    entity_id =   Column(Unicode(50), primary_key = True)
    avail_state = Column(Integer)
    monit_state = Column(Integer)
    timestamp =   Column(DateTime)
    description = Column(Unicode(256))

    def __init__(self, entity_id, avail_state, \
                 monit_state, timestamp = None, description = None):
        self.entity_id = entity_id
        self.avail_state = avail_state
        self.monit_state = monit_state
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp
        self.description = description

    def __repr__(self):
        return 'Current availability State of %s is %s since %s' % \
                (self.entity_id, self.avail_state, self.timestamp)

class AvailHistory(DeclarativeBase):
    __tablename__ = 'avail_history'

    id = Column(Unicode(50), primary_key = True)
    entity_id = Column(Unicode(50))
    state = Column(Integer)
    timestamp = Column(DateTime)
    monit_state=Column(Integer)
    endtime=Column(DateTime)
    period=Column(Integer)
    description = Column(Unicode(256))

    def __init__(self, entity_id, state, monit_state, timestamp, description,endtime=None,period=None):
        self.id = getHexID()
        self.entity_id = entity_id
        self.state = state
        self.timestamp = timestamp
        self.description = description
        self.monit_state=monit_state
        self.endtime=endtime
        self.period=period

    def __repr__(self):
        return 'Availability State of %s at time %s was %s' % \
                (self.entity_id, self.timestamp, self.state)

Index("ah_eid_st_time", AvailHistory.entity_id, AvailHistory.state, AvailHistory.timestamp)

