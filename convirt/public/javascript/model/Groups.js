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

function groupUI(){
    
    var group_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("Create/Edit Groups,")+_("Add Users to Groups")+'<br/></div>'
    });    

    var group_new_button=new Ext.Button({
        id: 'group_new',
        text: _('New'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :_('New Group'),
                    width :370,
                    height:400,
                    modal : true,
                    resizable : false
                });
                w.add(groupDetailsPanel(group_grid,'NEW',null,w));
                w.show();
            }
        }
    });

    var group_remove_button=new Ext.Button({
        id: 'group_remove',
        text: _('Remove'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!group_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the group list"));
                    return false;
                }
                //group_grid.getStore().remove(group_grid.getSelectionModel().getSelected());
                var edit_rec=group_grid.getSelectionModel().getSelected();
                var groupid=edit_rec.get('groupid');
                var groupname=edit_rec.get('groupname');
                var url='/model/delete_group?groupid='+groupid;
                Ext.MessageBox.confirm(_("Confirm"),_("About to delete group:")+groupname+"?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    group_grid.getStore().load();
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
    var group_edit_button= new Ext.Button({
        id: 'group_edit',
        text: _('Edit'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',

        listeners: {
            click: function(btn) {
                if(!group_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the group list"));
                    return false;
                }
                var edit_rec=group_grid.getSelectionModel().getSelected();
                var groupid=edit_rec.get('groupid');

                var url="/model/edit_group_details?groupid="+groupid;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {

                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){

                            var groups_det=response.edit_group_det[0];                      
                            var w=new Ext.Window({
                                title :_('Edit Group'),
                                width :370,
                                height:400,
                                modal : true,
                                resizable : false
                            });
                            w.add(groupDetailsPanel(group_grid,'EDIT',groups_det,w));
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

    var group_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var group_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Group Id"),
        width: 0,
        dataIndex: 'groupid',
        menuDisabled: true,
        hidden:true
    },
    {
        header: _("Name"),
        width: 150,
        dataIndex: 'groupname',
        sortable:true
    },
    {
        header: _("Description"),
        width: 225,
        sortable: true,
        dataIndex: 'desc'
    }
    ]);

    var group_store =new Ext.data.JsonStore({
        url: "/model/get_groupsdetails",
        root: 'rows',
        fields: ['groupid','groupname','desc'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });

    group_store.load();

    var group_grid=new Ext.grid.GridPanel({
        store: group_store,
        stripeRows: true,
        colModel:group_columnModel,
        frame:false,
        selModel:group_selmodel,
        height:355,
        //width:515,
        width:'100%',
		autoExpandColumn:2,
        enableHdMenu:false,
        id:'group_grid',
        loadMask:true,
//        bbar: new Ext.PagingToolbar({
//            store: group_store,
//            displayInfo:true,
//            displayMessage:"Displaying groupInfo {0} - {1} of {2}"
//        }),
       tbar:[
            _('Search (By Name):'),new Ext.form.TextField({
            fieldLabel: _('Search'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    group_grid.getStore().filter('groupname', field.getValue(), false, false);
                }
            }

        }),{ xtype: 'tbfill'},group_new_button,'-',group_edit_button,'-',group_remove_button], 
        listeners:{
             rowdblclick:function(grid, rowIndex, e){
                group_edit_button.fireEvent('click',group_edit_button);
            }
        }
    });

    var grouppanel=new Ext.Panel({
        id:"grouppanel",
        title:_('Groups'),
        layout:"form",
        width:535,
        height:450,
        frame:false,
        labelWidth:30,
        border:0,
        cls: 'whitebackground',
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [group_label,group_grid ]
    });

    return grouppanel;
}

function groupDetailsPanel(grid,mode,group,w){
    
    var empty_label=new Ext.form.Label({
        html:'<div style="" align="center" width="250"><br></div>'
    });
    
    var group_id=new Ext.form.TextField({
        fieldLabel: _('Group Id'),
        name: 'groupid',
        width: 150,
        id: 'groupid',
        allowBlank:false,
        disabled: true

    });
    var group_name=new Ext.form.TextField({
        fieldLabel: _('Name'),
        name: 'groupname',
        sortable:true,
        width: 150,
        id: 'group_name',
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

    var grp_desc=new Ext.form.TextField({
        fieldLabel: _('Description'),
        name: 'description',
        width: 200,
        id: 'desc',
        allowBlank:false

    });


    var url="";
    if(mode=='NEW'){
         url="/model/get_users_map";
    }
    else if(mode=='EDIT'){
          url="/model/get_users_map?groupid="+group.groupid;
    }

    var users_fromstore = new Ext.data.JsonStore({
        url: url,
        root: 'user_det',
        fields: ['userid','username'],
        successProperty:'success',
        sortInfo: {
            field: 'username',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });
    users_fromstore.load();

    var users_tostore = new Ext.data.JsonStore({
        url: '/model/get_tousers_map',
        root: 'touser_det',
        fields: ['userid','username'],
        successProperty:'success',
        sortInfo: {
            field: 'username',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });

    var group_cancel_button= new Ext.Button({
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

    var group_save_button=new Ext.Button({
        id: 'save',
        text: _('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(group_rightpanel.getForm().isValid()) {
                    var url="";
                    if(mode=='NEW'){
                        url="/model/save_group_details?groupid="+group_id.getValue()+"&groupname="+group_name.getValue()+"&userids="+useritemselector.getValue()+"&desc="+grp_desc.getValue();
                    }else if(mode=='EDIT'){
                        
                        url="/model/updatesave_group_details?groupid="+group.groupid+"&groupname="+group_name.getValue()+"&userids="+useritemselector.getValue()+"&desc="+grp_desc.getValue();
                    }

                    var ajaxReq=ajaxRequest(url,0,"POST",true);

                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var groups_det=response.group_det[0];
                                if('F'==groups_det){
                                    Ext.MessageBox.alert(_("Failure"),format(_("Group {0} is already existing"),group_name.getValue()));
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
        minTabWidth: 115,
        tabWidth:135,
        activeTab:0,
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },group_save_button,'-',group_cancel_button]

    });
    var useritemselector=new Ext.ux.ItemSelector({
        name:"itemselector",
        dataFields:["userid", "username"],
        toStore:users_tostore,
        msWidth:120,
        msHeight:190,
        valueField:"userid",
        displayField:"username",
        imagePath:"icons/",
        drawUpIcon:false,
        drawDownIcon:false,
        drawLeftIcon:true,
        drawRightIcon:true,
        drawTopIcon:false,
        drawBotIcon:false,
        toLegend:_("Selected Users"),
        fromLegend:_("Available Users"),
        fromStore:users_fromstore,
        toTBar:[{
            text:_("Clear"),
            handler:function(){
                useritemselector.reset();
            }
        }]
    });

    var group_rightpanel=new Ext.FormPanel({
        id:"grouprightpanel",
        layout:"form",
        title:_('Group'),
        width:310,
        height:300,
        frame:true,
        labelWidth:60,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[group_name, grp_desc ,empty_label,useritemselector]
    });

    var group_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('Audit'),
        width:300,
        height:300,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });

    if(mode=='EDIT'){
        var  groupid=group.groupid;
        group_name.setValue(group.groupname);
        if (group_name.getValue()=='adminGroup'){
            group_name.disabled=true;
        }        
        grp_desc.setValue(group.desc);
        
        users_fromstore.load();
        users_tostore.load({
            params:{
                groupid:groupid
            }
        });
       
        tabPanel.add(group_rightpanel);
        tabPanel.add( group_auditpanel);
        tabPanel.setActiveTab(group_auditpanel);
        tabPanel.setActiveTab(group_rightpanel);
        createdby.setValue(group.createdby);
        modifiedby.setValue(group.modifiedby);
        createddate.setValue(group.createddate);
        modifieddate.setValue(group.modifieddate);

    }
    else{

        tabPanel.add(group_rightpanel);
        tabPanel.setActiveTab(group_rightpanel);
    }
    var new_group_panel=new Ext.Panel({
        id:"new_group_panel",
        layout:"form",
        width:350,
        height:400,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });


    return   new_group_panel;
}

