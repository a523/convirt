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

from convirt.core.utils.NodeProxy import Node, NodeWrapper
from convirt.core.utils.utils import to_unicode,to_str

import socket, threading

# Pool and share the instances of Node classes. (nodeproxies)
class NodePool:

    _node_pool_lock = threading.RLock()
    nodes = {}

    @classmethod
    def get_key(cls, hostname, port, username, password, is_remote, use_keys):
        key = "%s:%d:%s:%s:%s:%s" % (hostname, port, username, password,
                                     to_str(is_remote), to_str(use_keys))
        return key

    @classmethod
    def get_node(cls,
                 hostname = None,
                 ssh_port = 22,
                 username = Node.DEFAULT_USER,
                 password=None,
                 isRemote=False,
                 use_keys = False):

        # construct the key
        key = cls.get_key(hostname, ssh_port, username, password, isRemote,
                          use_keys)

        # bug fix : unsynchronized check
        if cls.nodes.get(key) is not None:
           return cls.nodes[key]

        try:
            # TODO : Look in to removing Node Wrapper.
            import time, datetime
            start = datetime.datetime.now()
            print "NODE_PROXY : START ", hostname, \
                                         socket.getdefaulttimeout(), start
            node = NodeWrapper(hostname,
                               ssh_port,
                               username,
                               password,
                               isRemote,
                               use_keys)
        finally:
            now = datetime.datetime.now()
            print "NODE_PROXY : END ", hostname, socket.getdefaulttimeout(), \
                                       (now - start).seconds

        cls._node_pool_lock.acquire()
        try:
            if cls.nodes.get(key) is None:
                cls.nodes[key] = node
            else:
                # two threads created the entry.. we lost.
                node.cleanup()

            return cls.nodes[key]
        finally:
            cls._node_pool_lock.release()

    # cleanup all entries
    # TODO: Hook it up to app shutdown
    @classmethod
    def cleanup(cls, entry=None):
        if entry is not None:
            for n in cls.nodes.itervalues():
                if n is not None and n == entry:
                    n.cleanup()
                    return
            print "ERROR : NodePool.cleanup : node not found.", entry
            return

        for n in cls.nodes.itervalues():
            if n is not None:
                n.cleanup()

    @classmethod
    def clear_node(cls,
                 hostname = None,
                 ssh_port = 22,
                 username = Node.DEFAULT_USER,
                 password=None,
                 isRemote=False,
                 use_keys = False):
        # construct the key
        key = cls.get_key(hostname, ssh_port, username, password, isRemote,
                          use_keys)
        cls._node_pool_lock.acquire()
        try:
            if cls.nodes.get(key) is not None:
                node = cls.nodes[key]
                node.cleanup()
                cls.nodes[key] = None
        finally:
            cls._node_pool_lock.release()



if __name__ == "__main__":
    print "Hello";