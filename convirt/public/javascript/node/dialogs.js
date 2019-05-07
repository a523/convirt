/*
*   ConVirt   -  Copyright (c) 2008 Convirture Corp.
*   ======

* ConVirt is a Virtualization management tool with a graphical user
* interface that allows for performing the standard set of VM operations
* (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
* also attempts to simplify various aspects of VM lifecycle management.


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Jd <jd_jedi@users.sourceforge.net>
*/

function show_dialog(node,responseData,action,vm){
    if(action=='import')
        showWindow(_("Select Virtual Machine configuration file(s)"),515,425,FileDialog(node,responseData,action));
    else if(action=='restore')
        showWindow(_("Hibernate"),515,425,FileDialog(node,responseData,action));
    else if(action=='hibernate')
        showWindow(_("Hibernate"),515,425,FileDialog(node,responseData,action,vm));
    else if(action=='migrate' || action=='migrate_all' || action=='provision_image' || action=='create_network')
        showWindow(_("Select a Target Node"),315,325,NodeSelectionDialog(vm,node,responseData,action));
}


function show_dialog_SP(node,responseData,action,vm,sp,objData){
    if(objData == undefined || objData == null || objData == "") {
        objData = null;
    }

        showWindow(_("Select a Target Server Pool"),315,325,SPSelectionDialog(node,responseData,action,vm,sp,objData));
}