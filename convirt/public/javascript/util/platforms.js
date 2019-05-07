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

function select_platform(prntNode){

    var store = new Ext.data.JsonStore({
        url: '/get_platforms?',
        root: 'rows',
        fields: ['name', 'value'],
        //id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    store.load();
    var platform = new Ext.form.ComboBox({
        fieldLabel: _('Select Platform'),
        allowBlank:false,
        store: store,
        emptyText :"Select Platform",
        mode: 'local',
        displayField:'name',
        valueField:'value',
        width: 140,
        triggerAction :'all',
        forceSelection: true,
        name:'plat_form'        
    });

    var simple = new Ext.FormPanel({
        labelWidth:120,
        frame:true,
        border:0,
        labelAlign:"right" ,
        width:300,
        height:100,
        labelSeparator: ' ',
        items:[platform]
    });

    simple.addButton(_("OK"),function(){
        if (simple.getForm().isValid()) {
            closeWindow();
            if(platform.getValue()=='xen')
                showWindow(_("Add Server"),330,335,XenUI(null,prntNode,'add'));
            else if(platform.getValue()=='kvm')
                showWindow(_("Add Server"),330,240,KVMUI(null,prntNode,'add'));
            
        }else{
            Ext.MessageBox.alert(_('Error'), _('Please select a Platform.'));
        }
    });
    simple.addButton(_("Cancel"),function(){
        closeWindow();
    });

    return simple;
}

function show_platform(node,nodeinfo){
    var platform=nodeinfo.platform;
    if(platform=='xen')
        showWindow(_("Edit Server")+node.text,315,340,XenUI(node,node.parentNode,'edit',nodeinfo));
    else if(platform=='kvm')
        showWindow(_("Edit Server")+node.text,315,240,KVMUI(node,node.parentNode,'edit',nodeinfo));
}
