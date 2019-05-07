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

function operationsUI(){

    var operations_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("Manage low level operations for an Entity Type")+'<br/></div>'
    });

    var operation_new_button=new Ext.Button({
        id: 'operations_new',
        text: _('New'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :_('New Operation'),
                    width :450,
                    height:450,
                    modal : true,
                    resizable : false
                });
                w.add(operationDetailsPanel(operation_grid,'NEW',null,w));
                w.show();
            }
        }
    }) ;

    var operation_remove_button=new Ext.Button({
        id: 'operation_remove',
        text: _('Remove'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {

            click: function(btn) {
                if(!operation_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the user list"));
                    return false;
                }
                var edit_rec=operation_grid.getSelectionModel().getSelected();
                var opid=edit_rec.get('opid');
                var opname=edit_rec.get('opname');

                var url='/model/delete_operation?opid='+opid;

                Ext.MessageBox.confirm(_("Confirm"),_("About to delete operation:")+opname+"?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    operation_grid.getStore().load();
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
    var operation_edit_button= new Ext.Button({
        id: 'operation_edit',
        text: _('Edit'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',

        listeners: {
            click: function(btn) {

                if(!operation_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the user list"));
                    return false;
                }
                var edit_rec=operation_grid.getSelectionModel().getSelected();
                var opid=edit_rec.get('opid');
                var ent=edit_rec.get('enttype');
                var url="/model/edit_op_det?opid="+opid+"&enttype="+ent;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var users_det=response.edit_op_det[0];
                            var w=new Ext.Window({
                                title :_('Edit Operation'),
                                width :450,
                                height:450,
                                modal : true,
                                resizable : false
                            });
                            w.add(operationDetailsPanel(operation_grid,'EDIT',users_det,w));
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

    var operation_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var operation_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Name"),
        width: 150,
        sortable:true,
        dataIndex: 'opname'
    },
    {
        header: _("Description"),
        width: 180,
        sortable: true,
        dataIndex: 'description'
    },
    {
        header: _("Display"),
        width: 55,
        sortable: false,
        dataIndex: 'cd'
    },
    {
        header: _("Entity Type"),
        width:110,
        sortable: true,
        dataIndex: 'enttype'
    },
    {
        header: _("Op Id"),
        width: 0,
        dataIndex: 'opid',
        menuDisabled: true,
        hidden:true
    }
    ]);

    var operation_store =new Ext.data.JsonStore({
        url: "/model/get_operations",
        root: 'rows',
        fields: ['opname','description', 'cd','enttype', 'opid'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });

    operation_store.load();

    var operation_grid=new Ext.grid.GridPanel({
        store: operation_store,
        stripeRows: true,
        colModel:operation_columnModel,
        frame:false,
        selModel:operation_selmodel,
        height:360,
        width:'100%',
        enableHdMenu:false,
        id:'op_grid',
        layout:'fit',
        loadMask:true,

        //            bbar: new Ext.PagingToolbar({
        //            store: operation_store,
        //            displayInfo:true,
        //            displayMessage:"Displaying userInfo {0} - {1} of {2}"
        //            }),

        tbar:[
            _('Search (By Name):'),new Ext.form.TextField({
            fieldLabel: _('Search'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    operation_grid.getStore().filter('opname', field.getValue(), false, false);
                }
            }

        }),{ 
            xtype: 'tbfill'
        },operation_new_button,'-',operation_edit_button,'-',operation_remove_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                operation_edit_button.fireEvent('click',operation_edit_button);
            }
        }

    });

    var oppanel=new Ext.Panel({
        id:"oppanel",
        title:_('Operations'),
        layout:"form",
        width:535,
        height:450,
        cls: 'whitebackground',
        frame:false,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [operations_label,operation_grid]
    });

    return oppanel;
}
function operationDetailsPanel(grid,mode,operation,w){
    
    var op_id=new Ext.form.TextField({
        fieldLabel: _('OP Id'),
        name: 'opid',
        width: 150,
        id: 'opid',
        allowBlank:false
    });

    var op_name=new Ext.form.TextField({
        fieldLabel: _('Name'),
        name: 'opname',
        width: 150,
        id: 'opname',
        allowBlank:false
    });
    var desc=new Ext.form.TextField({
        fieldLabel: _('Description'),
        name: 'desc',
        width: 150,
        id: 'desc',
        allowBlank:false
    });
    var context_display=new Ext.form.Checkbox({
        fieldLabel: _('Context Display'),
        name: 'contextdisplay',
        value: 'true',
        width: 150,
        id: 'contextdisplay',
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
    var disp_name=new Ext.form.TextField({
        fieldLabel: _('Display Name'),
        name: 'dispname',
        width: 150,
        id: 'dispname',
        allowBlank:false
    });
    var icon=new Ext.form.TextField({
        fieldLabel: _('Icon'),
        name: 'icon',
        width: 150,
        id: 'icon',
        allowBlank:false
    });

    var url="";
    if(mode=='NEW'){
        url="/model/get_entitytype_map";
    }
    else if(mode=='EDIT'){
        url="/model/get_entitytype_map?opid="+operation.opid;
    }

    var entity_fromstore = new Ext.data.JsonStore({
        url: url,
        root: 'entitytype_det',
        fields: ['entid','entname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    entity_fromstore.load();

    var entity_tostore = new Ext.data.JsonStore({
        url: '/model/get_toentitytype_map',
        root: 'toentitytype_det',
        fields: ['entid','entname'],
        successProperty:'success',
        sortInfo: {
            field: 'entname',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    var operation_cancel_button= new Ext.Button({
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

    var operation_save_button=new Ext.Button({
        id: 'save',
        text: _('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',

        listeners: {
            click: function(btn) {
                if(operation_rightpanel.getForm().isValid()) {
                    var url="";
                    if(mode=='NEW'){
                        url="/model/save_oper_det?opname="+op_name.getValue()+"&descr="+desc.getValue()+"&context_disp="+context_display.getValue()+"&entityid="+itemselector.getValue()+"&dispname="+disp_name.getValue()+"&icon="+icon.getValue();
                    }else if(mode=='EDIT'){
                        url="/model/updatesave_op_det?opid="+operation.opid+"&opname="+op_name.getValue()+"&desc="+desc.getValue()+"&entid="+itemselector.getValue()+"&context_disp="+context_display.getValue()+"&dispname="+disp_name.getValue()+"&icon="+icon.getValue();
                    }

                    var ajaxReq=ajaxRequest(url,0,"POST",true);

                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var users_det=response.operation_det[0];
                                if('F'==users_det){
                                    Ext.MessageBox.alert(_("Failure"),format(_("Operation {0} is already existing"),op_name.getValue()));
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

    var itemselector=new Ext.ux.ItemSelector({
        name:"itemselector",
        dataFields:["entid","entname"],
        toStore:entity_tostore,
        msWidth:120,
        msHeight:180,
        allowBlank:false,
        valueField:"entid",
        displayField:"entname",
        imagePath:"icons/",
        drawUpIcon:false,
        drawDownIcon:false,
        drawLeftIcon:true,
        drawRightIcon:true,
        drawTopIcon:false,
        drawBotIcon:false,
        toLegend:_("Selected"),
        fromLegend:_("Available"),
        fromStore:entity_fromstore,
        toTBar:[{
            text:_("Clear"),
            handler:function(){
                itemselector.reset();
            }
        }]
    });
    var tabPanel=new Ext.TabPanel({
        defaults: {
            autoScroll:true
        },
        margins: '2 2 2 0',
        minTabWidth: 115,
        tabWidth:135,
        activeTab:0,
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },operation_save_button,'-',operation_cancel_button]

    });

        
    var operation_rightpanel=new Ext.FormPanel({
        id:'rightpanel',
        title:_('Operations'),
        layout:"form",
        width:440,
        height:350,
        frame:true,
        labelWidth:100,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[op_name,desc,disp_name,icon,context_display,itemselector]
    });

    var operation_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('Audit'),
        width:440,
        height:350,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });


    tabPanel.add(operation_rightpanel);
    tabPanel.setActiveTab(operation_rightpanel);
    if(mode=='EDIT'){

        var opid=operation.opid;
        op_id.setValue(operation.opid);
        op_name.setValue(operation.opname);
        op_name.disabled=true;
        desc.setValue(operation.desc);
        context_display.setValue(operation.contextdisplay);
        disp_name.setValue(operation.dispname);
        icon.setValue(operation.icon);
        entity_fromstore.load();
        entity_tostore.load({
            params:{
                opid:opid
            }
        });
        tabPanel.add(operation_rightpanel);
        tabPanel.add(operation_auditpanel);
        tabPanel.setActiveTab(operation_auditpanel);

        tabPanel.setActiveTab(operation_rightpanel);
        createdby.setValue(operation.createdby);
        modifiedby.setValue(operation.modifiedby)
        createddate.setValue(operation.createddate)
        modifieddate.setValue(operation.modifieddate)
    }

    var new_operation_panel=new Ext.Panel({
        id:"new_operation_panel",
        layout:"form",
        width:440,
        height:440,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });
    return new_operation_panel;
}
