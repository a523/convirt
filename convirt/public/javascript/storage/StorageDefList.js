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

var storage_def,storage_grid,storage_panel;
var selNode;
var sSiteId, sGroupId, sNodeId,op_level;
var server_grid;
var windowid;
var edit_seperator;
var strg_load_counter=0;
var strg_timeout;
var curr_strg_count=0;
var initial_strg_count=0;
var is_timer=false; 
var strg_name_adding="";
var adding_storage=false;
var removing_storage=false;

var hideServerPoolsCol;
function StorageDefList(node){
    selNode = node;

    //We are checking whether the node passed is server or servergroup.
    if(node.attributes.nodetype == 'DATA_CENTER'){
        //When menu is invoked at data center level
        //Consider the node is a data center
        //node and group would be null
        sSiteId = "site_id=" + node.attributes.id;
        op_level = "&op_level=DC";
        sGroupId = "";
        sNodeId = "";
        new_button_text = "New";
        remove_button_text = "Remove";
        hideEditButton = false;
        hideServerPoolsCol = true;
        edit_seperator = "-";
        headingmsg = "This represents shared storage resources available to all servers in a Server Pool to which the storage is attached.";
    }
    else if(node.attributes.nodetype == 'SERVER_POOL'){
        //When menu is invoked at server pool level
        //Consider the node is a group (server pool)
        //node would be null
        sSiteId = "site_id=" + node.parentNode.attributes.id;
        op_level = "&op_level=SP";
        sGroupId = "&group_id=" + node.attributes.id;
        sNodeId = "";
        new_button_text = "Attach";
        remove_button_text = "Detach";
        hideEditButton = true;
        hideServerPoolsCol = true;
        edit_seperator = "";
        headingmsg = "This represents shared storage resources available to all servers with in a Server Pool.";
    }
    else{
        //When menu is invoked at server level
        //Consider the node is a server
        sSiteId = "site_id=" + node.parentNode.parentNode.attributes.id;
        op_level = "&op_level=S";
        sGroupId = "&group_id=" + node.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.attributes.id;
        new_button_text = "New";
        remove_button_text = "Remove";
        hideEditButton = false;
        hideServerPoolsCol = true;
        edit_seperator = "-";
        headingmsg = "This represents shared storage resources available to a server.";
    }

    var columnModel = new Ext.grid.ColumnModel([
        {header: _("Id"), width: 40, hidden: true, dataIndex: 'id'},
        {header: _("Name"), width: 80, sortable: false, dataIndex: 'name'},
        {header: _("Type"), width: 40, sortable: false, dataIndex: 'type'},
        {header: _("Size(GB)"), width: 60, sortable: false, dataIndex: 'size'},
        {header: _("Definition"), width: 225, hidden: true, sortable: false, dataIndex: 'definition'},
        {header: _("Server Pools"), width: 150, hidden: hideServerPoolsCol, sortable: true, dataIndex: 'serverpools'},
        {header: _("Description"), width: 232, sortable: false, dataIndex: 'description'},
        {header: _("Status"), width: 100, hidden: true, sortable: false, renderer: showStorageDefStatusLink, dataIndex: 'status'},//100
        {header: _("Scope"), width: 40, hidden: true, sortable: false, dataIndex: 'scope'},
        {header: _("Associated"), width: 100, hidden: true, sortable: false, dataIndex: 'associated'}
        ]);

    var store = new Ext.data.JsonStore({
        url: '/storage/get_storage_def_list?' + sSiteId + op_level + sGroupId,
        root: 'rows',
        fields: ['id', 'name', 'type','size', 'definition', 'description','stats','connection_props','status', 'scope', 'associated', 'serverpools'],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){
                //alert("Loading...");
                strg_load_counter++
                if(strg_load_counter>10) {
                    clearTimeout(strg_timeout);
                    is_timer = false;
                    return;
                }
                curr_strg_count = my_store.getCount();
                if(is_timer == true) {
                    if(initial_strg_count != curr_strg_count) {
                        //alert("Breaking...");
                        if(adding_storage==true){
                            for(i=0;i<=curr_strg_count;i++) {
                                rec = my_store.getAt(i);
                                if(selNode.attributes.nodetype == 'SERVER_POOL') {
                                    if(strg_name_adding == rec.get('name') || strg_name_adding == "") {
                                        //alert("Breaking for add...");
                                        clearTimeout(strg_timeout);
                                        is_timer = false;
                                        adding_storage = false;
                                        break;
                                    }
                                } else if(parseFloat(rec.get('size')) > 0) {
                                    //alert("Breaking for add...");
                                    clearTimeout(strg_timeout);
                                    is_timer = false;
                                    adding_storage = false;
                                    setTimeout("reloadStorageDefList()", 5000);
                                    break;
                                }
                            }
                        } else {
                            //alert("Breaking for remove...");
                            clearTimeout(strg_timeout);
                            is_timer = false;
                            removing_storage = false;
                        }
                    } else {
                        strg_timeout = setTimeout("reloadStorageDefList()", 1000);
                    }
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    store.load();

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var storage_new_button=new Ext.Button({
        name: 'add_storage',
        id: 'add_storage',
        text:_(new_button_text),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adding_storage=true;
                removing_storage=false;
                storage_grid.getSelectionModel().clearSelections();
//                storage_details=StorageDefinition(node.attributes.id,"NEW",null);
                windowid=Ext.id();
                storage_scope=null;
                showWindow(_("Storage Details"),435,500,StorageDefinition(node,"NEW",null,storage_scope,null,null,null,null,windowid),windowid);
//                storage_panel.add(storage_details);
                hidefields("NEW");

            }
        }
    });
    var storage_remove_button=new Ext.Button({
        name: 'remove_storage',
        id: 'remove_storage',
        text:_(remove_button_text),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adding_storage=false;
                removing_storage=true;
                if(checkSelectedStorage(storage_grid)){
                    if(storage_grid.getSelectionModel().getCount()>0){
                        var rec=storage_grid.getSelectionModel().getSelected();
                        var message_text = "If you remove storage " + rec.get('name') + ", it would unmount the storage. Do you wish to remove it?";
                        var storage_id=storage_grid.getSelectionModel().getSelected().get('id');
                        CheckAndRemoveStorage(storage_id,node,storage_grid,message_text);
                        /*
                        Ext.MessageBox.confirm(_("Confirm"),message_text,function(id){
                            if(id=='yes'){
                                var storage_id=storage_grid.getSelectionModel().getSelected().get('id');
                                //removeStorage(storage_id,node,storage_grid);
                                CheckAndRemoveStorage(storage_id,node,storage_grid);
                            }
                        });
                        */
                    }
                }
            }
        }
    });
    var storage_rename_button=new Ext.Button({
        name: 'rename_storage',
        id: 'rename_storage',
        text:_("Rename"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedStorage(storage_grid)){
                    var storage_id=storage_grid.getSelectionModel().getSelected().get('id');
                    renameStorage(storage_id,node,storage_grid);
                }
            }
        }
    });
    var storage_edit_button=new Ext.Button({
        name: 'edit_storage',
        id: 'edit_storage',
        text:_("Edit"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        hidden: hideEditButton,
        listeners: {
            click: function(btn) {
                adding_storage=false;
                removing_storage=false;
                if(checkSelectedStorage(storage_grid)){
                    var rec=storage_grid.getSelectionModel().getSelected();
                    var storage_scope = rec.get('scope');
//                      storage_details=StorageDefinition(node.attributes.id,"EDIT",rec);
                    windowid=Ext.id();
                    showWindow(_("Storage Details"),435,500,StorageDefinition(node,"EDIT",rec,storage_scope,null,null,null,null,windowid),windowid);
//                      storage_panel.add(storage_details);
                    showStorageFields(rec.get('type'));
                    hidefields("EDIT");
                   
                }
            }
        }
    });
    var storage_test_button=new Ext.Button({
        name: 'test_storage',
        id: 'test_storage',
        text:_("Test"),
        icon:'icons/storage_test.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adding_storage=false;
                removing_storage=false;
                if(checkSelectedStorage(storage_grid)){
                    var rec=storage_grid.getSelectionModel().getSelected();
//                      storage_details=StorageDefinition(node.attributes.id,"TEST",rec);
                     windowid=Ext.id();
                     storage_scope=null;
                     showWindow(_("Storage Details"),435,500,StorageDefinition(node,"TEST",rec,storage_scope,null,null,null,null,windowid),windowid);

//                      storage_panel.add(storage_details);
                    showStorageFields(rec.get('type'));
                    hidefields("TEST");                   
                }
            }
        }
    })

    var storage_details;
    storage_grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:415,
        height:365,
        enableHdMenu:false,
        tbar:[{xtype: 'tbfill'},
            storage_new_button,            
            '-',
            //We are hiding the rename button as per requirement 
			//since edit functionality is doing rename also.
            //storage_rename_button,
            //'-',
            storage_edit_button,
            edit_seperator,
            storage_test_button,
            '-',
            storage_remove_button,

            new Ext.Button({
                name: 'btnRefreshStorage',
                id: 'btnRefreshStorage',
                text:"Refresh",
                icon:'icons/refresh.png',
                cls:'x-btn-text-icon',
                hidden: false,
                listeners: {
                    click: function(btn) {
                        adding_storage=false;
                        removing_storage=false;
                        //alert("Refreshing storage");
                        reloadStorageDefList();
                    }
                }
            })
        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                storage_edit_button.fireEvent('click',storage_edit_button);
            }
         }
    });

    var lbl=new Ext.form.Label({
         html:'<div style="" class="labelheading">'+headingmsg+'</div>'
    });

	storage_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:430,
        height:468,
//        hidemode:"offset",
        frame:true,
        items:[lbl,storage_grid]
        ,bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('Close'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {adding_storage=false; removing_storage=false; closeWindow();}
                }
            })
        ]
    });

    return storage_panel;
}

function checkSelectedStorage(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("Warning"),_("Please select a storage."));
        return false;
    }
    return true;
}

function closeStorageDefinition(){
    storage_def.close();
}

function renameStorage(storage_id,node,grid){

    Ext.MessageBox.prompt(_("Rename Shared Storage"),_("Enter new Shared Storage Name"),function(btn, text){
        if (btn == 'ok'){
            if(text.length==0){
                Ext.MessageBox.alert(_("Error"),_("Please enter valid Name."));
                return;
            }
            var url="/storage/rename_storage_def?" + sSiteId + sGroupId + "&storage_id="+storage_id+"&new_name="+text; 
            var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
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
    });


}

function CheckAndRemoveStorage(storage_id,node,grid,message_text){
    var url="/storage/is_storage_allocated?storage_id="+storage_id; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if(response.msg == "IN_USE") {
                    Ext.MessageBox.confirm(_("Confirm"),"One of more Virtual Machines seems to be using the storage. Are you sure you want to continue ?",function(id){
                        if(id=='yes'){
                            removeStorage(storage_id,node,grid);
                        }
                    });
                } else {
                    Ext.MessageBox.confirm(_("Confirm"),message_text,function(id){
                        if(id=='yes'){
                            removeStorage(storage_id,node,grid);
                        }
                    });
                }
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function removeStorage(storage_id,node,grid){
    var url="/storage/remove_storage_def?" + sSiteId + op_level + sGroupId + "&storage_id="+storage_id; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                grid.getStore().load();
                DelayReloadStorageDefList();
                var msg="Task Submitted."
                show_task_popup(msg);
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function reloadStorageDefList(){
    storage_grid.getStore().load();
}

//Start - Changes from Showing definition status
function showStorageDetailsLink(data,cellmd,record,row,col,store) {
    if(data != "") {
        var server_id = record.get("id");
        var storage_sync_details = record.get("details");
        var returnVal = '<a href="#" onClick="showStorageSyncDetails()">Details</a>';
        return returnVal;
    }
    else {
        return data;
    }
}

function showStorageSyncDetails() {
    var rec = server_grid.getSelectionModel().getSelected();
    var storage_sync_details = rec.get('details');

    if (storage_sync_details == null) {
        storage_sync_details = "No details found";
    }
    txt_details.setValue(storage_sync_details);
    win_detail_status.show(this);
}

var txt_details=new Ext.form.TextArea({
    readOnly:true
});

var win_detail_status = new Ext.Window({
    title: 'Sync Details',
    layout:'fit',
    width:300,
    height:300,
    closeAction:'hide',
    plain: true,
    items:[txt_details],
    bbar:[{xtype: 'tbfill'},
        new Ext.Button({
            text:"OK",
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            listeners: {
                click: function(btn) {
                    win_detail_status.hide();
                }
            }
        })
    ]
});

function showStorageDefStatusLink(data,cellmd,record,row,col,store) {
    var returnVal = "";
    if(data != "") {
        var def_id = record.get("id");
        var sStatus = record.get("status");
        var associated = record.get("associated");

        var fn = "showServerStorageDefList('" + def_id + "','" + sStatus + "')";
        returnVal = '<a href="#" onClick=' + fn + '>' + data + '</a>';
        //if(selNode.attributes.nodetype == 'DATA_CENTER' || selNode.attributes.nodetype == 'SERVER_POOL'){
        if(selNode.attributes.nodetype == 'SERVER_POOL'){
            if (associated == false) {
                returnVal = ""; //If difinition is not associated with any server then show status as blank
            }
        }
    }
    return returnVal;
}

function showServerStorageDefList(id, sStatus) {
    var win, storageId;
    //get selected definition id
    if(checkSelectedStorage(storage_grid)){
        storageId = storage_grid.getSelectionModel().getSelected().get('id');
        sel_def_name = storage_grid.getSelectionModel().getSelected().get('name');
    }

    var lbl_desc=new Ext.form.Label({
        html:"<div><font size='2'><i>This represents the list of servers linked with the selected storage along with the status.</i></font></div><br/>"
    });

    var label_level = "";
    if(selNode.attributes.nodetype == 'DATA_CENTER'){
        label_level = "Site";
    } else {
        label_level = "Server Pool";
    }

    var lbl_server=new Ext.form.Label({
        html:"<div><font size='2'><i><b>" + label_level + "</b> - " + selNode.attributes.text + ". <br /><b>Storage</b> - " +  sel_def_name + "</i></font></div>"
    });

    var serverDefListColumnModel = new Ext.grid.ColumnModel([
        {header: "Id", hidden: true, dataIndex: 'id'},
        {header: "Server", width: 150, sortable: false, dataIndex: 'name'},
        {header: "Status", width: 105, sortable: false, dataIndex: 'status'},
        {header: "Details", width: 100, sortable: false, renderer: showStorageDetailsLink, dataIndex: 'details_link'},
        {header: "Details", hidden: true, dataIndex: 'details'}
    ]);

    var serverDefListStore = new Ext.data.JsonStore({
        url: '/storage/get_server_storage_def_list?' + sSiteId + sGroupId + '&def_id=' + storageId + '&defType=STORAGE',
        root: 'rows',
        fields: ['id', 'name', 'status', 'details'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });
    serverDefListStore.load();

    var serverDefListSelModel = new Ext.grid.RowSelectionModel({
            singleSelect: false
    });
    
    server_grid = new Ext.grid.GridPanel({
        store: serverDefListStore,
        colModel:serverDefListColumnModel,
        stripeRows: true,
        frame:true,
        autoScroll:true,
        selModel:serverDefListSelModel,
        width:372,
        //autoExpandColumn:2,
        height:157,
        enableHdMenu:false
    });
    
    // create the window on the first click and reuse on subsequent clicks
    win = new Ext.Window({
        title: 'Status',
        layout:'fit',
        width:400,
        height:300,
        closeAction:'hide',
        plain: true,
        items: new Ext.Panel({
            id: "serverDefPanel",
            bodyStyle:'padding:10px 0px 0px 0px',
            //width:500,
            //height:300,
            hidemode:"offset",
            frame:true,
            items:[lbl_desc, lbl_server, server_grid]
        }),
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'btnSvrDefListClose',
                id: 'btnSvrDefListClose',
                text:"Close",
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        win.hide();
                    }
                }
            })
        ]
    });
    win.show(this);
}

function associate_defns(def_type, def_ids){
    if(def_ids == ""){
        Ext.MessageBox.alert("Warning","Please select storage");
        return;
    }

    var url="/storage/associate_defns?" + sSiteId + op_level + sGroupId + "&def_type=" + def_type + "&def_ids=" + def_ids; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                DelayReloadStorageDefList();
//                Ext.MessageBox.alert("Success", "Task submitted.");
                show_task_popup("Task Submitted.");
                closeWindow(windowid);
                storage_grid.enable();
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}

function DelayReloadStorageDefList()
{
    is_timer = true;
    strg_load_counter=0;
    initial_strg_count = storage_grid.getStore().getCount();
    if(selNode.attributes.nodetype == 'SERVER_POOL'){
        strg_name_adding = storage_dc_grid.getSelectionModel().getSelected().get('name');
        //alert("strg_name_adding= " + strg_name_adding )
    }
    //check the record count in the grid and if you get record count by +1 and the name of the newly added record then break the following loop. This is called on load event of store.

    strg_timeout = setTimeout("reloadStorageDefList()", 1000); 
}

function DelayReload()
{
    //Call function after every second
    setTimeout("reloadStorageDefList()", 1000); 
    is_timer = true;
}
//End - Changes from Showing definition status
