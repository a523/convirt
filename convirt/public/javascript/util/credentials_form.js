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

function credentialsform(node){
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

    form.addButton(_("OK"),function(){
        if (form.getForm().isValid()) {
            var uname=username.getValue();
            var pwd=password.getValue();
            closeWindow();
            connectNode(node,uname,pwd);
            
        }else{
            Ext.MessageBox.alert(_('Errors'), _('Some of the required information is missing.'));
        }
    });
    form.addButton(_("Cancel"),function(){
        Ext.MessageBox.alert(_('Error:'), format(_("{0}:Server not Authenticated"),node.text));
        form.destroy();
        closeWindow();
    });

    return form;
}

function connectNode(node,username,password){
    var url="/node/connect_node?node_id="+node.attributes.id+"&username="+username+"&password="+password;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    var iconClass=node.getUI().getIconEl().className;
    node.getUI().getIconEl().className="x-tree-node-icon loading_icon";
    ajaxReq.request({
        success: function(xhr) {
            node.getUI().getIconEl().className=iconClass;
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(res.success){
                node.fireEvent('click',node);
            }else{
                if(res.error=='Not Authenticated'){
                    showWindow(_("Credentials for ")+node.text,280,150,credentialsform(node));
                    return;
                }else{
                    Ext.MessageBox.alert(_("Error"),res.msg);
                }
            }
        },
        failure: function(xhr){
            node.getUI().getIconEl().className=iconClass;
            Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
        }
    });
}
