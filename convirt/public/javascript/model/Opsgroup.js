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

function opsgroupUI(){

    var opsgrp_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("Groups set of operations into Operations Group")+'<br/></div>'
    });


    var opsgrp_new_button=new Ext.Button({
        id: 'opsgrp_new',
        text: _('New'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :_('New Operation Group'),
                    width :480,
                    height:380,
                    modal : true,
                    resizable : false
                });
                w.add(opgrpsDetailsPanel(opsgrp_grid,'NEW',null,w));
                w.show();
            }
        }
    }) ;

    var opsgrp_remove_button=new Ext.Button({
        id: 'Opsgroup_remove',
        text: _('Remove'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {

            click: function(btn) {
                if(!opsgrp_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the group list"));
                    return false;
                }

                var edit_rec=opsgrp_grid.getSelectionModel().getSelected();
                var opsgroupid=edit_rec.get('opsgroupid');
                var opsgroupname=edit_rec.get('opsgrpname');
                var url='/model/delete_opsgroup?opsgroupid='+opsgroupid;
                Ext.MessageBox.confirm(_("Confirm"),_("About to delete OpsGroup:")+opsgroupname+"?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    opsgrp_grid.getStore().load();
                                }else{
                                    Ext.MessageBox.alert(_("Failure"),response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                            }
                        });
                    }
                });
            }
        }
    });

    var opsgrp_edit_button= new Ext.Button({
        id: 'opsgrp_edit',
        text: _('Edit'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',

        listeners: {
            click: function(btn) {
                if(!opsgrp_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the group list"));
                    return false;
                }
                var edit_rec=opsgrp_grid.getSelectionModel().getSelected();
                //alert(edit_rec);
                var opsgroupid=edit_rec.get('opsgroupid');
                var opid=edit_rec.get('opid');
                //alert(opsgroupid);

                var url="/model/edit_opsgroup_details?opsgroupid="+opsgroupid;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        // alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){

                            var opsgrp=response.edit_opsgroup_det[0];
                            var w=new Ext.Window({
                                title :_('Edit OperationGroup'),
                                width :480,
                                height:380,
                                modal : true,
                                resizable : false
                            });
                            w.add(opgrpsDetailsPanel(opsgrp_grid,'EDIT',opsgrp,w));
                            w.show();
                        }else{
                            Ext.MessageBox.alert(_("Failure"),response.msg);
                        }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                    }
                });
            }
        }
    });

    var opsgroup_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var opsgrp_columnModel = new Ext.grid.ColumnModel([
        {
            header: _("Ops GroupId"),
            width: 150,
            dataIndex: 'opsgroupid',
            sortable:false,
            hidden:true
        },
        {
            header: _("Ops Group"),
            width: 140,
            sortable:false,
            dataIndex: 'opsgrpname'
        },
        {
            header: _("Op Name"),
            width: 130,
            sortable: true,
            dataIndex: 'opname'
        },
        {
            header: _("Op Id"),
            width: 100,
            sortable: false,
            dataIndex: 'opid',
            hidden:true
        },
        {
            header: _("Ops description"),
            width:145,
            sortable: false,
            dataIndex: 'desc'
        },
        {
            header: _("Entity Type"),
            width: 80,
            sortable: true,
            dataIndex: 'entitytype'
        },
        {
            header: _("Search Name"),
            width: 150,
            dataIndex: 'searchName',
            sortable:false,
            hidden:true
        }
        ]);

    var opsgrp_store =new Ext.data.JsonStore({
        url: "/model/get_opsgroups",
        root: 'rows',
        fields: [ 'opsgroupid','opsgrpname', 'opname', 'opid', 'desc','entitytype','searchName'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error2",store_response.msg);
            }

        }
    });

    opsgrp_store.load();

    var opsgrp_grid=new Ext.grid.GridPanel({
        store: opsgrp_store,
        stripeRows: true,
        colModel:opsgrp_columnModel,
        frame:false,
        selModel:opsgroup_selmodel,
        height:360,
        width:'100%',
        enableHdMenu:false,
        id:'opsgrp_grid',
        layout:'fit',
        loadMask:true,
        //            bbar: new Ext.PagingToolbar({
        //            store: opsgrp_store,
        //            displayInfo:true,
        //            displayMessage:"Displaying userInfo {0} - {1} of {2}"
        //            }),

        tbar:[
            _('Search (By Name): '),new Ext.form.TextField({
            fieldLabel: _('Search'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    opsgrp_grid.getStore().filter('searchName', field.getValue(), false, false);
                }
            }

        }),{ 
            xtype: 'tbfill'
        },opsgrp_new_button,'-',opsgrp_edit_button,'-',opsgrp_remove_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                opsgrp_edit_button.fireEvent('click',opsgrp_edit_button);
            }
        // alert(opsgroupid);
        }

    });

    var opsgrouppanel=new Ext.Panel({
        id:"opsgrouppanel",
        layout:"form",
        title:_('Operations Group'),
        width:535,
        height:450,
        cls: 'whitebackground',
        frame:false,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [opsgrp_label,opsgrp_grid]
    });


    return opsgrouppanel;

}


function opgrpsDetailsPanel(grid,mode,opsgrp,w){
    
    var opsgrp_label1=new Ext.form.Label({
        html:'<div style="" class="backgroundcolor" width="250">'+_("OperationsGroup Information")+'<br/></div><br>'
    });


    var opsgrp_label2=new Ext.form.Label({
        html:'<div style="" class="backgroundcolor" width="250">'+_("Select Operations")+'<br/></div><br>'
    });

    var opsgrp_id=new Ext.form.TextField({
        fieldLabel: _('Ops Group Id'),
        name: 'opsgroupid',
        width: 150,
        id: 'opsgroupid',
        allowBlank:false,
        disabled: true

    });
    var  opsgrp_name=new Ext.form.TextField({
        fieldLabel: _('Name'),
        name: 'opsgroupname',
        width: 150,
        id: 'username',
        allowBlank:false,
        enableKeyEvents:true

    });
    var opsgrp_desc=new Ext.form.TextField({
        fieldLabel: _('Description'),
        name: 'description',
        width: 200,
        id: 'pass',
        allowBlank:false

    });
    var createdby=new Ext.form.TextField({
        fieldLabel: _('Created By'),
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
        fieldLabel: _('Modified By'),
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
    
    var url="";
    if(mode=='NEW'){
        url="/model/get_operations_map";
    }
    else if(mode=='EDIT'){
        url="/model/get_operations_map?opsgrpid="+opsgrp.opsgroupid;
    }
    var operations_fromstore = new Ext.data.JsonStore({
        url: url,
        root: 'operation_det',
        fields: ['operationid','operationname'],
        successProperty:'success',
        sortInfo: {
            field: 'operationname',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });
    operations_fromstore.load();

    var operations_tostore = new Ext.data.JsonStore({
        url: '/model/get_tooperations_map',
        root: 'tooperations_det',
        fields: ['operationid','operationname'],
        successProperty:'success',
        sortInfo: {
            field: 'operationname',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });

    var opsgrp_cancel_button= new Ext.Button({
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

    var opsgrp_save_button=new Ext.Button({
        id: 'save',
        text: _('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                if(opsgrp_rightpanel.getForm().isValid()) {
                    var url="",flag=false,errmsg="";
                    if(opsgrpitemselector.toStore.getCount()==0){
                        errmsg+="<br>"+_("Please select at least one Operation");
                        flag=true;
                    }
                    if(flag){
                        Ext.MessageBox.alert(_("Warning"),errmsg);
                        return ;
                    }
                    if(mode=='NEW'){
                        url="/model/save_opsgroup_details?opsgroupname="+opsgrp_name.getValue()+"&opsgroupdesc="+opsgrp_desc.getValue()+"&operation="+opsgrpitemselector.getValue();
                    }
                    else if(mode=='EDIT') {
                        var record=null;
                        var  opids="";
                        var rec_count=opsgrpitemselector.toStore.getCount();

                        for (var i=0; i<rec_count; i++) {
                            record = opsgrpitemselector.toStore.getAt(i);
                            var  opid=record.get('operationid');
                            opids+=opid+",";
                        }

                        url="/model/updatesave_opsgroup_details?opsgroupid="+opsgrp_id.getValue()+"&opsgroupname="+opsgrp_name.getValue()+"&opsgroupdesc="+opsgrp_desc.getValue()+"&operation="+opids;
                    }
                    var ajaxReq=ajaxRequest(url,0,"POST",true);

                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var groups_det=response.opsgroup_det[0];
                                if('F'==groups_det){
                                    Ext.MessageBox.alert(_("Failure"),format(_("Ops Group {0} is already existing"),opsgrp_name.getValue()));
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
                            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });

                }
                else{
                    Ext.MessageBox.alert(_('Errors'), _('Some of the required information is missing.'));

                }
            }
        }
    });

    var tabPanel=new Ext.TabPanel({
        defaults: {
            autoScroll:true
        },
        margins: '2 2 2 0',
        minTabWidth:155,
        tabWidth:150,
        activeTab:0,
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },opsgrp_save_button,'-',opsgrp_cancel_button]

    });
    var opsgrpitemselector=new Ext.ux.ItemSelector({

        name:"itemselector",
        dataFields:["operationid", "operationname"],
        toStore:operations_tostore,
        msWidth:200,
        msHeight:235,
        valueField:"operationid",
        displayField:"operationname",
        imagePath:"icons/",
        drawUpIcon:false,
        drawDownIcon:false,
        drawLeftIcon:true,
        drawRightIcon:true,
        drawTopIcon:false,
        drawBotIcon:false,
        toLegend:_("Selected"),
        fromLegend:_("Available"),
        fromStore:operations_fromstore,
        toTBar:[{
            text:_("Clear"),
            handler:function(){
                opsgrpitemselector.reset();
            }
        }]

    });

    var opsgrp_rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        layout:"form",
        title:_('Ops Group'),
        width:300,
        height:280,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[opsgrp_label1,opsgrp_name,opsgrp_desc]
    });


    var opsgrp_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('Audit'),
        width:300,
        height:280,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });


    var groupassign_details_panel=new Ext.Panel({
        id:"opsgroupassignpanel",
        title:_('Operations'),
        width:300,
        height:280,
        layout:"form",
        frame:true,
        labelWidth:5,
        border:false,
        bodyBorder:false,
        items: [opsgrp_label2,opsgrpitemselector]
    });


    if(mode=='EDIT'){

        var opsgroupid=opsgrp.opsgroupid;
        opsgrp_id.setValue(opsgrp.opsgroupid);
        opsgrp_name.setValue(opsgrp.opsgroupname);
        opsgrp_name.disabled=true;
        opsgrp_desc.setValue(opsgrp.opsgroupdesc);        
        //alert(opsgrp_name);
        
        operations_fromstore.load();

        operations_tostore.load({
            params:{
                opsgroupid:opsgroupid

            }
        });
        tabPanel.add(opsgrp_rightpanel);
        tabPanel.add(groupassign_details_panel);
        tabPanel.add(opsgrp_auditpanel);
        tabPanel.setActiveTab(opsgrp_auditpanel);
        tabPanel.setActiveTab(groupassign_details_panel);
        tabPanel.setActiveTab(opsgrp_rightpanel);

        createdby.setValue(opsgrp.createdby);
        modifiedby.setValue(opsgrp.modifiedby)
        createddate.setValue(opsgrp.createddate)
        modifieddate.setValue(opsgrp.modifieddate)
    }

    tabPanel.add(opsgrp_rightpanel);
    tabPanel.add(groupassign_details_panel);
    tabPanel.setActiveTab(groupassign_details_panel);
    tabPanel.setActiveTab(opsgrp_rightpanel);

    var new_opsgrp_panel=new Ext.Panel({
        id:"userpanel",
        layout:"form",
        width:460,
        height:520,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });

    return   new_opsgrp_panel;

}
