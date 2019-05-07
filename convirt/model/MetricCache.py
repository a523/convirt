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
from convirt.viewModel.ChartService import ChartService
from datetime import datetime, timedelta
import convirt.core.utils.constants
constants = convirt.core.utils.constants
from convirt.model.GenericCache import GenericCache
from convirt.model.Entity import Entity
from convirt.model import DBSession
import tg

class MetricCache(GenericCache):
    chart_service=ChartService()

    def metric_cache(self,node_id,metric,metric_type,rollup_type,per_type,date1,date2,period):
        """
        Setting value for cache by checking the conditions
        """
        now=datetime.utcnow()
        status=False
        ent=DBSession.query(Entity).filter(Entity.entity_id==node_id).one()
        cache_key = (node_id,ent.type.name,metric,period)
        #checking cache's key is already exisiting
        if self.cache.has_key(cache_key):
#            print "FOUNDDDDDDDDDDDDDDDDDD==",(node_id[0],ent.type.name,period,metric)
            cached_time=self.cache[cache_key].get("cached_time")
            if (now>cached_time):
                status=True
        else:
            self.check_cache_limit(self.cache)
            status=True
        
        if status:
            #quering the result and set it to cache
            result=self.chart_service.get_metrics_specific_value([node_id],metric,metric_type,rollup_type,per_type,date1,date2)
            cache_time=now+timedelta(minutes=int(tg.config.get(constants.CACHE_TIME)))
            self.cache[cache_key]={"cached_time":cache_time,"value":result}

        self.cache[cache_key]["last_accessed"]=now
        return self.cache[cache_key].get("value")
