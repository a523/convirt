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
import tg
from convirt.core.utils.utils import to_str,print_traceback
import convirt.core.utils.constants
constants = convirt.core.utils.constants

class GenericCache:

    cache={}
    user_cache={}

    def check_cache_limit(self,cache_val):
        """
        checking cache limit reached or not.
        if reached deleting least used value
        """
        try:
            temp_dic={}
            if len(cache_val)>=int(tg.config.get(constants.MAX_CACHE_SIZE)):
                for val in cache_val:
                    last_accessed_time=cache_val[val].get("last_accessed")
                    if last_accessed_time is not None:
                        temp_dic[last_accessed_time]=val
#                        print val,"====",last_accessed_time
                keys = temp_dic.keys()
                if len(keys)>0:
                    keys.sort()
#                    print "\n\n=",keys[0],"==value==",temp_dic[keys[0]]
                    x=len(keys)-int(tg.config.get(constants.MAX_CACHE_SIZE))
                    for i in range(0,x+1):
                        del cache_val[temp_dic[keys[i]]]
#                    del cache_val[temp_dic[keys[0]]]
        except Exception,e:
             print_traceback()

    def metric_cache(self,node_id,metric,metric_type,rollup_type,per_type,date1,date2,period):
        """
        Overrided in the MetricCache 
        """
        pass

    def get_top_entities(self,node_id,node_type,metric,top_type,metric_type,ids,date1,date2):
        """
        Overrided in the TopCache
        """
        pass
    
    def clear_cache(self):
        """
        clears all cache details
        """
        self.cache.clear()

    def get_cache_details(self):
        """
        cache details for showing in cli
        """

        cache_det={}
        cache_det["cache_time"]=tg.config.get(constants.CACHE_TIME)
        cache_det["cache_size"]=tg.config.get(constants.MAX_CACHE_SIZE)
        cache_det["cache_curr_size"]=to_str(len(self.cache))
        cache_info=[]
        for c in self.cache:
            cache_info.append(dict(name=c,time=self.cache.get(c).get("cached_time"),\
            last_access=self.cache.get(c).get("last_accessed")))
        cache_det["cache_info"]=cache_info
        return cache_det

    def on_add_entity(self,ent_type):
        """
        removing top_cache details correspong to the entity
        """
        try:
            self.remove_top_details(ent_type)
        except Exception,e:
            print "on_add_entity==",e


    def on_delete_entity(self,node_id,ent_type):
        """
        removing cache/top_cache details correspong to the entity
        """
        keys=self.cache.keys()
        try:
            for c in keys:
                if c[0]==node_id:
                    del self.cache[c]
            self.remove_top_details(ent_type)
        except Exception,e:
            print "on_delete_entity==",e
        
    def remove_top_details(self,ent_type):
        users=self.user_cache.keys()
        type=""
        if ent_type==constants.MANAGED_NODE:
            type="topNservers"
        elif ent_type==constants.DOMAIN:
            type="topNvms"
        for user in users:
            user_det=self.user_cache.get(user,{}).keys()
            for u in user_det:
                if u[3]== type:
                    del self.user_cache[user][u]
