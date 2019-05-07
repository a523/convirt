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

function KVMUI(node,prntNode,mode,mgd_node){
    var hostname=new Ext.form.TextField({
        fieldLabel: _('Host Name'),
        name: 'host_name',
        id: 'host_name',
        width: 150,
        allowBlank:false
    });
    var username=new Ext.form.TextField({
        fieldLabel: _('Username'),
        name: 'user_name',
        id: 'user_name',
        value:'root',
        width: 150,
        allowBlank:false
    });
    var password=new Ext.form.TextField({
        fieldLabel: _('Password'),
        name: 'pwd',
        id: 'pwd',
        width: 150,
        inputType : 'password'
    });
    var ssh_port=new Ext.form.TextField({
        fieldLabel: _('SSH Port'),
        name: 'sshport',
        id: 'sshport',
        allowBlank:false,
        width: 150,
        value:22
    });
    var use_keys=new Ext.form.Checkbox({
        fieldLabel: _('Use SSH Keys'),
        name: 'usekeys',
        id: 'usekeys',
        width: 150
//        listeners:{
//            check:function(field,checked){
//                password.setDisabled(checked);
//            }
//        }
    });

    var fldset=new Ext.form.FieldSet({
        title: _('Advanced'),
        collapsible: true,
        autoHeight:true,
        width: 300,
        collapsed: false,
        items :[ ssh_port,use_keys ]
    });

    var simple = new Ext.FormPanel({
        labelWidth:120,
        frame:true,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        labelAlign:"right" ,
        width:315,
        height:220,
        labelSeparator: ' ',
        items:[hostname,username,password,fldset]
    });
    var url='/node/add_node?group_id='+prntNode.attributes.id;
    use_keys.setValue(true); // Check ssh by default
    if(mode=='edit'){
        url='/node/edit_node?node_id='+node.attributes.id;
        hostname.setValue(mgd_node.hostname);
        hostname.setDisabled(true);
        username.setValue(mgd_node.username);
        ssh_port.setValue(mgd_node.ssh_port);
        use_keys.setValue(mgd_node.use_keys=='True');
//        password.setDisabled(mgd_node.use_keys=='True');
    }
    simple.addButton(_("OK"),function(){
        if (simple.getForm().isValid()) {
            simple.getForm().submit({
                url:url,
                params: {
                    platform:'kvm',
                    hostname:hostname.getValue(),
                    username:username.getValue(),
                    password:password.getValue(),
                    ssh_port:ssh_port.getValue(),
                    use_keys:use_keys.getValue() 
                },
                success: function(form,action) {
                    Ext.Msg.alert(_("Success"),action.result.msg );
                    closeWindow();
                    prntNode.fireEvent('click',prntNode);
                },
                failure: function(form, action) {
                    Ext.Msg.alert(_("Failure"),action.result.msg );
                },

                waitMsg:_('Adding...')
            });
        }else{
            Ext.MessageBox.alert(_('Errors'), _('Some of the required information is missing.'));
        }
    });
    simple.addButton(_("Cancel"),function(){
        closeWindow();
    });

    return simple;
}
