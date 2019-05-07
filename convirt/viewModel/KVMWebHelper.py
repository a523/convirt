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
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# author : Jd <jd_jedi@users.sourceforge.net>
#
# KVMWebHelper.py
#
#   This module contains code to return KVM platform information for Web
#

from convirt.viewModel.helpers.WebVMInfoHelper import WebVMInfoHelper

class KVMWebHelper:
    def __init__(self, platform_config):
        self.platform_config =  platform_config

    def get_vm_info_helper(self):
        return WebVMInfoHelper()


