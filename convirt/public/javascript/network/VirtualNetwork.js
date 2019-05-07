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

var virtual_def;
var virtual_nw_grid;
var selNode;
var sSiteId, sGroupId, sNodeId, op_level, op_level_main;
var server_grid;
var create_network_panel;
var hideServerCol, hideDisplayScopeCol;

function VirtualNetwork(node){
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
        hideServerCol = false;
        hideDisplayScopeCol = true;
    }
    else if(node.attributes.nodetype == 'SERVER_POOL'){
        //When menu is invoked at server pool level
        //Consider the node is a group (server pool)
        //node would be null
        sSiteId = "site_id=" + node.parentNode.attributes.id;
        op_level = "&op_level=SP";
        sGroupId = "&group_id=" + node.attributes.id;
        sNodeId = "";
        hideServerCol = false;
        hideDisplayScopeCol = true;
    }
    else{
        //When menu is invoked at server level
        sSiteId = "site_id=" + node.parentNode.parentNode.attributes.id;
        op_level = "&op_level=S";
        sGroupId = "&group_id=" + node.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.attributes.id;
        hideServerCol = true;
        hideDisplayScopeCol = true;
    }

    op_level_main = op_level;

    var columnModel = new Ext.grid.ColumnModel([

        {header: _("Name"), width: 80, sortable: false, dataIndex: 'name'},
        {header: _("Details"), width: 100, sortable: false, dataIndex: 'definition'},
        {header: _("Description"), width: 120, sortable: false, dataIndex: 'description'},
        {header: _("Status"), width: 100, hidden: true, sortable: false, renderer: showDefStatusLink, dataIndex: 'status'},
        {header: _("Scope"), width: 80, hidden: true, sortable: false, dataIndex: 'scope'},
        {header: _("Scope"), width: 80, hidden: hideServerCol, sortable: false, dataIndex: 'server'},
        {header: _("Scope"), width: 40, hidden: hideDisplayScopeCol, sortable: false, dataIndex: 'displayscope'},
        {header: _("Associated"), width: 80,hidden: true, sortable: false, dataIndex: 'associated'}
    ]);
     var network_list_store = new Ext.data.JsonStore({
        url: '/network/get_nw_defns?' + sSiteId + op_level + sGroupId + sNodeId,
        root: 'rows',
        fields: [ 'name', 'definition', 'description','status','type','id', 'status', 'scope', 'associated', 'server', 'displayscope'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    network_list_store.load();
    var  virtual_nw_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var virtual_new_button=new Ext.Button({
        name: 'add_network',
        id: 'add_network',
        text:_("New"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(node.attributes.nodetype == 'DATA_CENTER' || node.attributes.nodetype == 'SERVER_POOL') {
                    handleEvents(node,'create_network',null);
                } else {
                    var url="/network/get_new_private_bridge_name?" + sSiteId + op_level + sGroupId + sNodeId;
                    OpenNewNetworkDialog(node, null, null, null, null, url);
                }
            }
        }

    });

    var virtual_remove_button=new Ext.Button({
        name: 'remove_network',
        id: 'remove_network',
        text:_("Remove"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon' ,
        listeners: {
            click: function(btn) {
                if(virtual_nw_grid.getSelectionModel().getCount()>0){
                    var net_rec=virtual_nw_grid.getSelectionModel().getSelected();
                    if(sGroupId != "" && sNodeId != "") {
                        //If the network is defined at data center or server pool level
                        if(net_rec.get('scope') == 'SP' || net_rec.get('scope') == 'DC') {
                            Ext.MessageBox.alert("Info", "Data Center and Server Pool level network can not be removed");
                            return
                        }
                    }
                    var message_text = "Do you wish to remove network " + net_rec.get('name') + "?";
                    if(node.attributes.nodetype == 'SERVER_POOL' &&  net_rec.get('scope') == 'DC') {
                        message_text = "Do you wish to disassociate network " + net_rec.get('name') + "?";
                    }
                    Ext.MessageBox.confirm(_("Confirm"),message_text,function(id){
                        if(id=='yes'){

                            var def_id=net_rec.get('id');
                            var url="/network/remove_nw_defn?" + sSiteId + op_level + sGroupId + sNodeId + "&def_id=" + def_id;
                            var ajaxReq=ajaxRequest(url,0,"POST",true);
                            ajaxReq.request({
                                success: function(xhr) {//alert(xhr.responseText);
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                          reloadVirtualNetworkDefList();
                                          virtual_nw_dc_grid.getStore().load();
                                          Ext.MessageBox.alert("Success",response.msg);
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
                }else{
                    Ext.MessageBox.alert(_("Failure"),_("Select a network to delete"));
                }

            }
        }

    });
    var  virtual_edit_button= new Ext.Button({
        name: 'edit_network',
        id: 'edit_network',
        text:_("Edit"),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(virtual_nw_grid.getSelectionModel().getCount()>0){
                    var edit_rec=virtual_nw_grid.getSelectionModel().getSelected();
                    var network_scope = edit_rec.get('scope');
                    var nw_id=edit_rec.get('id');
                    var url="/network/get_edit_network_details?nw_id="+nw_id;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                        success: function(xhr) {//alert(xhr.responseText);
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                              windowid=Ext.id();
                              nw_new_win_popup = showWindow(_("Edit Definition"),438,450,VirtualNetworkDefinition(node,'EDIT',response,panel,network_scope,windowid),null);
                            }else{
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });
                }else{
                    Ext.MessageBox.alert(_("Failure"),_("Select a network to edit"));
                }

            }
        }

    });
    virtual_nw_grid = new Ext.grid.GridPanel({
        store: network_list_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        selModel:virtual_nw_selmodel,
        width:'100%',
        //autoExpandColumn:2,
        height:330,
        autoScroll:true,
        enableHdMenu:false,
        autoExpandColumn:2,
        tbar:[{
                xtype: 'tbfill'
            },
            virtual_new_button,
            '-',
            virtual_edit_button,
            '-',
            virtual_remove_button,

            new Ext.Button({
                name: 'btnRefreshNetwork',
                id: 'btnRefreshNetwork',
                text:"Refresh",
                icon:'icons/refresh.png',
                cls:'x-btn-text-icon',
                hidden: false,
                listeners: {
                    click: function(btn) {
                        //alert("Refreshing network");
                        reloadVirtualNetworkDefList();
                    }
                }
            })

        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                virtual_edit_button.fireEvent('click',virtual_edit_button);
            }
         }
    });

    var lbl=new Ext.form.Label({
        html:'<div style="" class="labelheading">'+_("Virtual Networks allow VMs on the same managed server to communicate with each other")+'</div>'
//          html:'<font style: size="2"><i>'+
//              _("Virtual Networks allow VMs on the same managed server to communicate with each other")+
//              '</i></font><br/></div>'
    });

    var panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:450,
        height:420,
        //frame:true,
        cls: 'whitebackground',
        items:[lbl,virtual_nw_grid]
        ,bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('Close'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeThisWindow(nw_win_popup);}
                    }
            })
        ]
    });
    create_network_panel = panel;
    return panel;

}
function closeVirtualNetworkDefinition(){
     virtual_def.close();
}
function reloadVirtualNetworkDefList(){
    virtual_nw_grid.enable();
    virtual_nw_grid.getStore().load();
}

//Start - Changes from Showing definition status
function showDetailsLink(data,cellmd,record,row,col,store) {
    if(data != "") {
        var server_id = record.get("id");
        var vn_sync_details = record.get("details");
        var returnVal = '<a href="#" onclick="showDetails()">Details</a>';
        return returnVal;
    }
    else {
        return data;
    }
}

function showDetails() {
    var rec = server_grid.getSelectionModel().getSelected();
    var vn_sync_details = rec.get('details');

    if (vn_sync_details == null) {
        vn_sync_details = "No details found";
    }
    txt_details.setValue(vn_sync_details);
    win_detail_status.show(this);
}

function showDefStatusLink(data,cellmd,record,row,col,store) {
    var returnVal = "";
    if(data != "") {
        var def_id = record.get("id");
        var sStatus = record.get("status");
        var associated = record.get("associated");

        var fn = "showServerDefList('" + def_id + "','" + sStatus + "')";
        returnVal = '<a href="#" onClick=' + fn + '>' + data + '</a>';
        if(selNode.attributes.nodetype == 'DATA_CENTER'){
            if (associated == false) {
                returnVal = "";  //If difinition is not associated with any server then show status as blank
            }
        }
    }
    return returnVal;
}

function showServerDefList(id, sStatus) {
    var win, sel_def_id;
    //get selected definition id
    if (checkSelectedNetwork(virtual_nw_grid)) {
        sel_def_id = virtual_nw_grid.getSelectionModel().getSelected().get('id');
        sel_def_name = virtual_nw_grid.getSelectionModel().getSelected().get('name');
    }

    var lbl_desc=new Ext.form.Label({
        html:"<div><font size='2'><i>This represents the list of servers linked with the selected network along with the status.</i></font></div><br/>"
    });

    var lbl_server=new Ext.form.Label({
        html:"<div><font size='2'><i><b>Server Pool</b> - " + selNode.attributes.text + ". <br /><b>Network</b> - " +  sel_def_name + "</i></font></div>"
    });

    var serverDefListColumnModel = new Ext.grid.ColumnModel([
        {header: "Id", hidden: true, dataIndex: 'id'},
        {header: "Server", width: 150, sortable: false, dataIndex: 'name'},
        {header: "Status", width: 105, sortable: false, dataIndex: 'status'},
        {header: "Details", width: 100, sortable: false, renderer: showDetailsLink, dataIndex: 'details_link'},
        {header: "Details", hidden: true, dataIndex: 'details'}
    ]);

    var serverDefListStore = new Ext.data.JsonStore({
        url: '/network/get_server_nw_def_list?' + sSiteId + sGroupId + '&def_id=' + sel_def_id + '&defType=NETWORK',
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
        width:400,
        //autoExpandColumn:2,
        height:140,
        enableHdMenu:false

    });
    
    // create the window on the first click and reuse on subsequent clicks
    win = new Ext.Window({
        //applyTo:'hello-win',
        title: 'Status',
        layout:'fit',
        width:400,
        height:300,
        closeAction:'hide',
        plain: true,
        items: new Ext.Panel({
            id: "serverDefPanel",
            bodyStyle:'padding:10px 0px 0px 0px',
            //width:350,
            //height:250,
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

function checkSelectedNetwork(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert("Warning","Please select a network.");
        return false;
    }
    return true;
}

function associate_nw_defns(def_type, def_ids){
    if(def_ids == ""){
        Ext.MessageBox.alert("Warning","Please select network");
        return;
    }

    var url="/network/associate_nw_defns?" + sSiteId + op_level + sGroupId + sNodeId + "&def_type=" + def_type + "&def_ids=" + def_ids; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                virtual_nw_dc_grid.getStore().load();
                closeWindow(windowid);
                reloadVirtualNetworkDefList();
                Ext.MessageBox.alert("Success","Network is associated with the server pool");
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}

//End - Changes from Showing definition status

function OpenNewNetworkDialog(objNode, strSiteId, strGroupId, strNodeId, strOpLevel, url) {
    if (url == null) {
        url="/network/get_new_private_bridge_name?site_id=" + strSiteId + "&op_level=" + strOpLevel + "&group_id=" + strGroupId + "&node_id=" + strNodeId;
    }
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                windowid=Ext.id();
                var win_height = 380;
                if(objNode.attributes.nodetype == 'SERVER_POOL'){
                        win_height = 450;
                } else {
                        win_height = 380;
                }
                nw_new_win_popup = showWindow(_("New Definition"),438,win_height,VirtualNetworkDefinition(objNode,'NEW',response,create_network_panel,null,windowid),null);
                if(objNode.attributes.nodetype == 'SERVER_POOL'){
                    nw_def_form.getBottomToolbar().hide();
                }
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
