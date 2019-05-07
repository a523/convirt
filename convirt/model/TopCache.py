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
from datetime import datetime, timedelta
import convirt.core.utils.constants
constants = convirt.core.utils.constants
from convirt.model.Metrics import MetricsService
from convirt.model.GenericCache import GenericCache
import tg

class TopCache(GenericCache):
    service = MetricsService()

    def get_top_entities(self,node_id,node_type,metric,top_type,auth,metric_type,ids,date1,date2):
        """
        Setting value for cache by checking the conditions
        """
        now=datetime.utcnow()
        status=False
        user_id=auth.user.user_id
        top_cache=self.get_top_value(user_id)
        usage_list=[]
        cache_key = (node_id,node_type,metric,top_type)
        #checking cache's key is already exisiting
        if top_cache.has_key(cache_key):
            cache_ids=[]
            for data in top_cache[cache_key].get("value"):
                cache_ids.append(data[1])
            diff_list=[item for item in cache_ids if not item in ids]
#            print "FOUNDDDDDDDDDDTOP555555==",(node_id,node_type,metric,top_type)
            cached_time=top_cache[cache_key].get("cached_time")
            if (now>cached_time) or len(diff_list)>0:
                status=True
        else:
            status=True

        if status:
            #quering the result and set it to cache
            cache_time=now+timedelta(minutes=int(tg.config.get(constants.CACHE_TIME)))
            data_list=self.service.getRawTopMetric(ids, metric, metric_type,date1,date2, "DESC",5)
            if len(data_list)>0:
                self.check_cache_limit(top_cache)
            top_cache[cache_key]={"cached_time":cache_time,"value":data_list}

        top_cache[cache_key]["last_accessed"]=now
        self.user_cache[user_id].update({cache_key:top_cache[cache_key]})

        # making key to remove if not deleted on entity operations
        if len(ids)==0 and self.user_cache.has_key(user_id):
            user=self.user_cache[user_id]
            if user.has_key(cache_key):
                self.user_cache[user_id][cache_key]["value"]=[]
                
        usage_list=self.user_cache[user_id][cache_key].get("value",[])
        
        if len(usage_list)==0:
            del self.user_cache[user_id][cache_key]         

        return usage_list

    def get_top_value(self,user_id):
        """
        getting cache value of user
        """
        if not self.user_cache.has_key(user_id):
            self.user_cache[user_id]={}
        top_cache=self.user_cache.get(user_id,{})
        return top_cache

    def delete_usercache(self,auth):
        """
        deleting cache value of user
        """
        user_id=auth.user.user_id
        if self.user_cache.has_key(user_id):
            del self.user_cache[user_id]
