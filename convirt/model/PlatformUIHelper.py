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

# helper for integrating UI.
# This may need to be moved to some better place.
class PlatformUIHelper:
    def __init__(self, ui_context, platform_config):
        self.ui_context = ui_context    # handle to commonly required elements
        self.platform_config =  platform_config

        # get stuff from the context
        # TODO : Minimize context elements... (use callback scheme)
        self.manager = self.ui_context["manager"]
        self.client_config = self.ui_context["client_config"]
        self.left_nav = self.ui_context["left_nav"]


    # Interface to add a new server or edit an existing server.
    # mode : add/edit
    # group_name : name of the server pool in which to create/edit server
    # existing_node : None in add mode, in edit mode, server to be edited
    # parentwin : parent window to which it would be modal.

    # Semantics : the dialog is supposed to handle validation and adding/editing
    #             the server
    #
    # NOTE : See PlatformUIUtils.py
    def show_add_server_dialog(self, mode, group_name, platform,
                               existing_node=None,
                               parentwin=None):
        raise Exception("show_add_node_dialog Not implemted for %s", platform)

    # get the VM settings dialog.
    # This is a multipurpose dialog used for
    # -- EDIT_IMAGE, EDIT_VM_CONFIG, EDIT_VM_INFO, PROVISION_VM
    # -- ctx contains
    #    -- managed_node, image_store, vm
    def get_vm_settings_dialog(self, mode, ctx, mainwin):
        raise Exception("get_vm_settings_dialog Not implemted.")


    # return a class that can handle displaying vm infor in a tree view.
    # If none provided, default would be used.
    # The handler is expected to implement display_vm_info(treeview, vm)
    # Typically derived from VMInfoHelper class and augment platform
    # specific information.
    def get_vm_info_helper(self):
        return None

