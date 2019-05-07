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
#


from convirt.model.AvailabilityWorker import AvailabilityWorker
from convirt.model.Entity import Entity,EntityType
from convirt.model import DBSession
import traceback,logging
import convirt.core.utils.constants
constants = convirt.core.utils.constants


logger = logging.getLogger("convirt.model")
class VMAvailabilityWorker(AvailabilityWorker):

    def __init__(self,auth):
        AvailabilityWorker.__init__(self,auth)
        self.worker=constants.VM_AVAILABILITY
        
    def get_task(self, auth, node_ids):
        """
        creates a task for node_ids
        """

        try:
            from convirt.core.services.tasks import VMAvailability
            user_name = auth.user.user_name
            t= VMAvailability(u'Update vm availability', {}, [],\
                        dict(node_ids=node_ids), None, user_name)
            dc_ent=DBSession.query(Entity).filter(Entity.type_id==EntityType.DATA_CENTER).first()
            t.set_entity_info(dc_ent)
            t.repeating=True
            logger.debug("VM NodesAvailability Task Created")
            return t
        except Exception, e:
            traceback.print_exc()
            raise e
