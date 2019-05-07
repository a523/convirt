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

function ajaxRequest(url,timeout,method,unmask){

    var ajaxReq = new Ext.data.Connection({
        url:url,
        disableCaching:false,
        timeout:timeout,
        method:method,
        listeners: {
            'beforerequest': {
                fn: function(con, opt){
//                    if(!unmask)
//                        Ext.get('centerPanel').mask(_('Loading...'));
                },
                scope: this
            },
            'requestcomplete': {
                fn: function(con, res, opt){
                    if(!unmask)
                        Ext.get('centerPanel').unmask();
                },
                scope: this
            },
            'requestexception': {
                fn: function(con, res, opt){
                    if(!unmask)
                        Ext.get('centerPanel').unmask();
                },
                scope: this
            }
        }
    });

    return ajaxReq;
}
