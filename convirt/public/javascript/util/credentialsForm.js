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

function credentialsForm(){
    var username=new Ext.form.TextField({
        fieldLabel: _('Username'),
        name: 'user_name',
        allowBlank:false,
        width: 150,
        value:'root'
    });
    var password=new Ext.form.TextField({
        fieldLabel: _('Password'),
        name: 'pwd',
        allowBlank:false,
        width: 150,
        inputType : 'password'
    });
    var form = new Ext.FormPanel({
        labelWidth:90,
        frame:true,
        border:0,
        labelAlign:"left" ,
        width:280,
        height:120,
        labelSeparator: ' ',
        items:[username,password]
    });

    return form;
}
