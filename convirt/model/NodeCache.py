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
from convirt.model.GenericCache import GenericCache
from convirt.core.utils.utils import to_str,print_traceback
import convirt.core.utils.utils
constants = convirt.core.utils.constants
import tg, threading, traceback
from datetime import datetime, timedelta


class NodeCache(GenericCache):
    """
        Used to hold the cache values for the managed nodes.
        lock is acquired at class level and the cache is also kept at class level

        Node name is used as the key to dictionary.
        if we discover CMS node as a managed node (using IP and as localhost)
        the current mechanism will break.
    """
    node_cache = {}
    lock = threading.RLock()

    def get_port(self, hostname, key, used_ports, start, end):
        """
            Locking system applied to this method.
        """
        selected_port=-1
        self.lock.acquire()
        try:
            try:
                self.clear_ports_cache(hostname, key)
                ports_in_cache = self.get_cache_val(hostname, key)
        
                used_ports.extend(ports_in_cache.keys())
                #print "\n\n--------used_ports--------", used_ports
                selected_port = self.get_free_port(used_ports, start, end)
                #print "selected port----", selected_port
                self.set_cache_val(hostname, key, selected_port)
            except Exception, ex:
                traceback.print_exc()
                raise ex
        finally:
            self.lock.release()
        return selected_port


    def get_free_port(self, used_ports, start, end):
        """
            Return a free port
        """
        for port in range(start, end):
            if port in used_ports:
                continue
            return port


    def get_node_cache(self, node_id):
        n_cache = self.node_cache.get(node_id)
        
        if n_cache is None:
            n_cache = {}
            self.node_cache.update({node_id:n_cache})
        return n_cache


    def get_cache_val(self, node_id, key):
        n_cache = self.get_node_cache(node_id)
        
        if key in [constants.PORTS]:
            val = n_cache.get(key, {})
            return val
        val = n_cache.get(key)
        return val


    def set_cache_val(self, node_id, key, val):
        """
        node_cache format {
                        'localhost': {
                                        'ports': {
                                                    6912: datetime.datetime(2010, 11, 15, 23, 21, 48, 413074),
                                                    6911: datetime.datetime(2010, 11, 15, 23, 21, 17, 642708)
                                                  }
                                        }
                        '192.168.1.107': {
                                        'ports': {
                                                    6922: datetime.datetime(2010, 11, 15, 23, 21, 48, 413074),
                                                    6918: datetime.datetime(2010, 11, 15, 23, 21, 17, 642708)
                                                  }
                                        }
                      }
        """
        n_cache = self.get_node_cache(node_id)
        upd_val = val
        if key in [constants.PORTS]:
            ### calling get_cache_val to get the value in proper format
            ports_dict = self.get_cache_val(node_id, key)
            ports_dict[val] = datetime.utcnow()
            upd_val = ports_dict
        n_cache.update({key:upd_val})
        self.node_cache.update({node_id:n_cache})
    
    def clear_ports_cache(self, node_id, key):
        """
            Clear old ports from ports cache, based on time it cached.
        """
        
        interval = 30
        try:
            interval = int(tg.config.get("node_ports_cache_clear_time", 30))
        except Exception, e:
            #print "Exception: ", e
            pass

        ports_dict = self.get_cache_val(node_id, key)
        for port, time in ports_dict.items():
            if time < (datetime.utcnow() - timedelta(seconds = interval)):                
                del ports_dict[port]

    def get_cache(self):
        return self.node_cache

__author__="root"
__date__ ="$Nov 3, 2010 5:51:54 PM$"

if __name__ == "__main__":
    print "Hello";



