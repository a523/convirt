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

# Base class for all Appliance proxies.
# An Appliance proxy will typically expose operations that can be invoked
# on an appliance.
# Examples : Check for update, Take a back up etc.

# A proxy class would implement
#   - A UI integration component
#     - define operations strings and opcodes to be called back with.
#     - A class that would implement the callback. Typically, the callback
#       would show a GUI component if required, get necessary input from the
#       user and invoke the op on the agent 
#   - Actual implementation of methods to talk to the appliance (typically
#     an agent in the vm)

class ApplianceProxy:
    def getProxyIntegration(self):
        # example :
        # ops =  { "Check for updates" : "CHECK_FOR_UPDATE",
        #          "Backup Now" : "BACKUP_NOW"
        #        }
        # return ops
        return None

    # Callback 
    def executeOp(self, context, opcode):
        raise Exception("Appliance operation not implemented ", opcode)


