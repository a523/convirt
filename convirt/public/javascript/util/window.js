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

var popup;
function showWindow(title,width,height,component,winid,resizable,closable){
    if(closable==null)
        closable=false;
    if(winid==null){
        popup=new Ext.Window({
            title : title,
            width : width,
            height: height,
            modal : true,
            resizable : resizable
        });
        popup.add(component);
        popup.show();
        return popup;
    }else{
        var win=new Ext.Window({
            title : title,
            width : width,
            height: height,
            id:winid,
            modal : true,
            resizable : resizable,
            closable:closable
        });
        win.add(component);
        win.show();
    }
}

function closeWindow(winid,destroy){
    if(winid==null){
        popup.close();
       
    }else{
        if(destroy===false){
            Ext.getCmp(winid).hide();
        }else{
            Ext.getCmp(winid).close();
        }
    }
}

function closeThisWindow(objWin) {
    objWin.close();
}