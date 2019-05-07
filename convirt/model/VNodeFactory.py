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

# define interface to be implemented by Plaform Factories
from convirt.core.utils.constants import *
from convirt.core.utils.utils import to_unicode,to_str
class VNodeFactory:
    def __init__(self):
        self.config = None  # later initialize this from a config file
        #self.store = store

    # create a new node
    def create_node(self, **props):
        pass

    # create a new node, given state of the node in the repository
    def create_node_from_repos(self, **props):
        pass

    # retun a bunch of props that can be used to save the state of the
    # node in the repository
    def get_props_for_repos(self, node):
        props = { prop_domfiles : to_str(node.get_managed_domfiles())}
        return props
