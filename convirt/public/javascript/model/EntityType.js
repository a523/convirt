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

function entitytypeUI(){

    var entitytype_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("Create / Edit Enity Type")+'<br/></div>'
    });

    var entitytype_new_button=new Ext.Button({
        id: 'entitytype_new',
        text: _('New'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :_('New Entity Type'),
                    width :430,
                    height:320,
                    modal : true,
                    resizable : false
                });
                w.add(entitytypeDetailsPanel(enttype_grid,'NEW',null,w));
                w.show();            
            }
        }
    }) ;

    //     var enttype_remove_button=new Ext.Button({
    //                id: 'Opsgroup_remove',
    //                text: 'Remove',
    //                icon:'icons/delete.png',
    //                cls:'x-btn-text-icon',
    //                listeners: {
    //
    //                   click: function(btn) {
    //                if(!enttype_grid.getSelectionModel().getSelected()){
    //                    Ext.MessageBox.alert("Error","Please select the record from the group list");
    //                    return false;
    //                }
    //                //group_grid.getStore().remove(group_grid.getSelectionModel().getSelected());
    //                var edit_rec=enttype_grid.getSelectionModel().getSelected();
    //                var enttypeid=edit_rec.get('entid');
    //                var enttypename=edit_rec.get('entname');
    //                var url='/model/delete_enttype?enttypeid='+enttypeid;
    //                Ext.MessageBox.confirm("Confirm","About to delete Entity Type: "+enttypename+"?", function (id){
    //                    if(id=='yes'){
    //                        var ajaxReq=ajaxRequest(url,0,"POST",true);
    //                        ajaxReq.request({
    //                            success: function(xhr) {
    //                                var response=Ext.util.JSON.decode(xhr.responseText);
    //                                if(response.success){
    //                                    enttype_grid.getStore().load();
    //                                }else{
    //                                    Ext.MessageBox.alert("Failure",response.msg);
    //                                }
    //                            },
    //                            failure: function(xhr){
    //                                Ext.MessageBox.alert( "Failure " , xhr.statusText);
    //                            }
    //                        });
    //                    }
    //                });
    //            }
    //         }
    //     });

    var enttype_edit_button= new Ext.Button({
        id: 'entitytype_edit',
        text: _('Edit'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!enttype_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the EntityType list"));
                    return false;
                }
                var edit_rec=enttype_grid.getSelectionModel().getSelected();
                //alert(edit_rec);
                var enttypeid=edit_rec.get('entid');

                var url="/model/edit_enttype_details?enttypeid="+enttypeid;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        // alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){

                            var opsgrp=response.edit_enttype_det[0];
                            var w=new Ext.Window({
                                title :_('Edit Entity Type'),
                                width :430,
                                height:320,
                                modal : true,
                                resizable : false
                            });
                            w.add(entitytypeDetailsPanel(enttype_grid,'EDIT',opsgrp,w));
                            w.show();
                        }else{
                            Ext.MessageBox.alert(_("Failure"),response.msg);
                        }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert(_("Failure") , xhr.statusText);
                    }
                });
            }
        }
    });

    var entitytype_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var entitytype_columnModel = new Ext.grid.ColumnModel([
        {
            header: _("Entity Id"),
            width: 10,
            dataIndex: 'entid',
            sortable:false,
            hidden:true
        },
        {
            header: _("Name"),
            width: 200,
            dataIndex: 'entname',
            sortable:true
        },
        {
            header: _("Display Name"),
            width: 295,
            sortable: true,
            dataIndex: 'dispname'
        }
    ]);

    var entitytype_store =new Ext.data.JsonStore({
        url: "/model/get_enttype",
        root: 'rows',
        fields: [ 'entid','entname', 'dispname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    entitytype_store.load();

    var enttype_grid=new Ext.grid.GridPanel({
        store: entitytype_store,
        stripeRows: true,
        colModel:entitytype_columnModel,
        frame:false,
        selModel:entitytype_selmodel,
        height:360,
        width:'100%',
        enableHdMenu:false,
        id:'enttype_grid',
        layout:'fit',
        loadMask:true,
        //            bbar: new Ext.PagingToolbar({
        //            store: opsgrp_store,
        //            displayInfo:true,
        //            displayMessage:"Displaying userInfo {0} - {1} of {2}"
        //            }),

        tbar:[
            _('Search (By Name):'),
            new Ext.form.TextField({
                fieldLabel: _('Search'),
                name: 'search',
                id: 'search',
                allowBlank:true,
                enableKeyEvents:true,
                listeners: {
                    keyup: function(field) {
                        enttype_grid.getStore().filter('entname', field.getValue(), false, false);
                    }
                }

            }),
            {xtype: 'tbfill'},
            entitytype_new_button,'-',enttype_edit_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                enttype_edit_button.fireEvent('click',enttype_edit_button);
            }
        }
    });

    var entitytypepanel=new Ext.Panel({
        id:"entitytypepanel",
        layout:"form",
        title:_('Entity Type'),
        width:535,
        height:450,
        frame:false,
        cls: 'whitebackground',
        labelWidth:130,
        border:0,
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [entitytype_label,enttype_grid]
    });

    return entitytypepanel;
}


function entitytypeDetailsPanel(grid,mode,ent,w){
    
    var opsgrp_label1=new Ext.form.Label({
        html:'<div style="" class="backgroundcolor" width="250">'+_("Entity Type Information")+'</font><br/></div><br>'
    });

    var ent_id=new Ext.form.TextField({
        fieldLabel:_('Entity Id'),
        name: 'entityid',
        width: 150,
        id: 'entityid',
        allowBlank:false,
        disabled: true

    });
    var  ent_name=new Ext.form.TextField({
        fieldLabel:_('Name'),
        name: 'entityname',
        width: 180,
        id: 'entityname',
        allowBlank:false,
        enableKeyEvents:true

    });
    var disp_name=new Ext.form.TextField({
        fieldLabel: _('Display Name'),
        name: 'dispname',
        width: 180,
        id: 'dispname',
        allowBlank:false

    });
    var createdby=new Ext.form.TextField({
        fieldLabel:_('Created By'),
        name: 'createdby',
        width: 150,
        id: 'createdby',
        allowBlank:false,
        disabled:true

    });
    var createddate=new Ext.form.TextField({
        fieldLabel: _('Created Date'),
        name: 'createddate',
        width: 150,
        id: 'createddate',
        allowBlank:false,
        disabled:true

    });
    var modifiedby=new Ext.form.TextField({
        fieldLabel:_('Modified By'),
        name: 'modifiedby',
        width: 150,
        id: 'modifiedby',
        allowBlank:false,
        disabled:true

    });
    var modifieddate=new Ext.form.TextField({
        fieldLabel: _('Modified Date'),
        name: 'modifieddate',
        width: 150,
        id: 'modifieddate',
        allowBlank:false,
        disabled:true

    });

    var enttype_cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('Cancel'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                w.close();
            }
        }
    });
    
    var enttype_save_button=new Ext.Button({
        id: 'save',
        text: _('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                // enttype_grid.enable();
                var errmsg='';

                if(ent_name.getValue()=='') {
                    errmsg+=_('Enter Name')+'<br/>';
                }
                if(disp_name.getValue()=='') {
                    errmsg+=_('Enter Display Name')+'<br/>';
                }

                if(errmsg != '') {
                    Ext.MessageBox.alert(_('Validation'), errmsg);
                    return false;
                }

                if(enttype_rightpanel.getForm().isValid()) {
                    if(mode=='NEW'){
                        var url="/model/save_enttype_details?enttypename="+ent_name.getValue()+"&dispname="+disp_name.getValue();
                    }
                    else if(mode=='EDIT') {

                        url="/model/updatesave_enttype_details?enttypeid="+ent_id.getValue()+"&enttypename="+ent_name.getValue()+"&dispname="+disp_name.getValue();
                    }
                    var ajaxReq=ajaxRequest(url,0,"POST",true);

                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var groups_det=response.opsgroup_det[0];
                                if('F'==groups_det){
                                    Ext.MessageBox.alert(_("Failure"),format(_("EntityType {0} is already existing"),ent_name.getValue()));
                                    return false;
                                }
                                Ext.MessageBox.alert(_("Success"),_("Successfully saved the values"));
                                w.close();
                                grid.getStore().load();

                            }else{
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert(_("Failure ") , xhr.statusText);
                        }
                    });
                }
                else{
                    Ext.MessageBox.alert(_('Errors'), _('Some of the required information is missing.'));
                }
            }
        }
    });

    var tabPanel = new Ext.TabPanel({
        defaults: {
            autoScroll:true
        },
        margins: '2 2 2 0',
        minTabWidth:155,
        tabWidth:150,
        activeTab:0,
        pinned:true,
        dynamic:true,
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },enttype_save_button,'-',enttype_cancel_button]
    });
    var enttype_rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        layout:"form",
        title:_('Entity Type'),
        width:300,
        height:230,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[opsgrp_label1,ent_name,disp_name]
    });

    var enttype_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('Audit'),
        width:300,
        height:230,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });

    if(mode=="EDIT"){
        ent_id.setValue(ent.enttypeid);
        ent_name.setValue(ent.entname);
        ent_name.disabled=true;
        disp_name.setValue(ent.entdisp);
        createdby.setValue(ent.createdby);
        modifiedby.setValue(ent.modifiedby);
        createddate.setValue(ent.createddate);
        modifieddate.setValue(ent.modifieddate);
        tabPanel.add(enttype_rightpanel);
        tabPanel.add(enttype_auditpanel);
        tabPanel.setActiveTab(enttype_auditpanel);
        tabPanel.setActiveTab(enttype_rightpanel);
    }
    else{
        tabPanel.add(enttype_rightpanel);
        tabPanel.setActiveTab(enttype_rightpanel);
    }

    var new_enttype_panel=new Ext.Panel({
        id:"userpanel",
        layout:"form",
        minWidth:410,
        minHeight:520,
        width:410,
        height:520,
        frame:true,
        split:true,
        dynamic:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });

    return  new_enttype_panel;

}
