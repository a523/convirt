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
var nw_new_win_popup;
var virtual_nw_def_form;
function VirtualNetworkDefinition(node,mode,response,parentPanel,network_scope,windowid){
    //We are checking whether the node passed is server or servergroup.
    if(node.attributes.nodetype == 'DATA_CENTER'){
        //When menu is invoked at data center level
        //Consider the node is a data center
        //node and group would be null
        sSiteId = "site_id=" + node.attributes.id;
        op_level = "&op_level=DC";
        sGroupId = "";
        sNodeId = "";
    }
    else if(node.attributes.nodetype == 'SERVER_POOL'){
        //When menu is invoked at server pool level
        //Consider the node is a servergroup
        //node would be null
        sSiteId = "site_id=" + node.parentNode.attributes.id;
        op_level = "&op_level=SP";
        sGroupId = "&group_id=" + node.attributes.id;
        sNodeId = "";
    }
    else{
        //When menu is invoked at server level
        //Consider the node is a server
        sSiteId = "site_id=" + node.parentNode.parentNode.attributes.id;
        op_level = "&op_level=S";
        sGroupId = "&group_id=" + node.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.attributes.id;
    }

    var network_name=new Ext.form.TextField({
        fieldLabel: _('Name'),
        name: 'network_name',
        id: 'network_name',
        width: 200,
        allowBlank:false
    });
    var network_description=new Ext.form.TextField({
        fieldLabel: _('Description'),
        name: 'network_description',
        width: 200,
        id: 'network_description'
    });
    var dhcprange=new Ext.form.TextField({
        fieldLabel: _('DHCP Range'),
        name: 'dhcpname',
        id: 'dhcpname',
        width: 200,
        allowBlank:false
    });
    var bridgename=new Ext.form.TextField({
        fieldLabel: _('Bridge Name'),
        name: 'bridgename',
        width: 200,
        id: 'bridgename'
    });


    var lb2=new Ext.form.Label({
        text:_("Specify Virtual Network Details.")
    });

    var lb3=new Ext.form.Label({
        html:'<table><tr><td width="100"></td><td width="275"><i>Tip: Create isolated N/W or forward to a physical N/W using NAT.</i></td></tr></table>'

    });
    var lb4=new Ext.form.Label({
        html:'<table><tr><td width="100"></td><td width="275"><i>Tip: A bridge is created to for every virtual network defined.</i></td></tr></table>'
    });

    var hostonly_radio=new Ext.form.Radio({
        boxLabel:_('Host only(Isolated)'),
        checked: true,
        name:"nw_type",
        value:'host_only',
        width:130,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    nat_forward.hide();
                    nat_forward.getEl().up('.x-form-item').setDisplayed(false);
                }
            }
        }
    });

    var nat_radio=new Ext.form.Radio({
        boxLabel:_('NAT Forwarded'),
        name:"nw_type",
        value:'nat_forwarded',
        width:130,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    if(virtual_nw_det_fldset.findById('nat_forward')){
                        nat_forward.show();
                        nat_forward.getEl().up('.x-form-item').setDisplayed(true);
                    }else{
                        virtual_nw_det_fldset.insert(6,{
                            width: 420,
                            layout:'form',
                            items:[nat_forward]
                        });
                        virtual_nw_def_form.doLayout();
                        //nat_forward.getEl().up('.x-form-item').setDisplayed(true);
                    }
                }
            }
        }
    });
    var nw_type=new Ext.form.RadioGroup({
        frame: true,
        title:_('RadioGroups'),
        fieldLabel: _('Isolated or NAT'),
        labelWidth: 80,
        width: 300,
        bodyStyle: 'padding:0 10px 0;',
        name:'radio',
        columns:1,
        vertical:true,
        items: [hostonly_radio,nat_radio]

    });

   var address_space_store = new Ext.data.JsonStore({
        url: '/network/get_nw_address_space_map',
        root: 'nw_address_space',
        fields: [ 'name', 'value'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    address_space_store.load();
    var address_space=new Ext.form.ComboBox({
        store:address_space_store,
        fieldLabel: _('Address space'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: false,
        typeAhead: true,
//        forceSelection: true,
        selectOnFocus:true,
        editable:true,
        enableKeyEvents:true,
        name:'address_space',
        id:'address_space',
        mode:'local',
        listeners:{
            	blur : function(combo) {
                    var value1="";
                    value1=address_space.getRawValue();
//                    alert(value1);
                    addressspace_ajax(value1,dhcprange);
                },
                 select:function(combo,record,index){
                    var value2="";
                    value2=record.get('value');
                    addressspace_ajax(value2,dhcprange);
            }
        }

    });
    var nat_forward_store= new Ext.data.JsonStore({
        url: '/network/get_nw_nat_fwding_map?node_id='+node.attributes.id,
        root: 'nw_nat',
        fields: [ 'name', 'value'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if(mode=="EDIT")
                  nat_forward.setValue(network.nw_nat_info_interface);
            }
        }
    });
    nat_forward_store.load();
    var nat_forward=new Ext.form.ComboBox({
        store:nat_forward_store,
        fieldLabel: _('NAT Forwarding'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'forward',
        id:'nat_forward',
        mode:'local'
    });
    var virt_save_button=new Ext.Button({
            name: 'ok',
            id: 'ok',
             text:_("Save"),
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            listeners: {
                    click: function(btn) {
                        //server pool level
                        if(sGroupId != "" && sNodeId == "") {
                            //If the network is defined at data center level
                            if(network_scope == 'DC') {
                                Ext.MessageBox.alert("Info", "Data Center level network can not be edited here");
                                return
                            }
                        } //server level
                        else if(sGroupId != "" && sNodeId != "") {
                            //If the network is defined at server pool level
                            if(network_scope == 'SP' || network_scope == 'DC') {
                                Ext.MessageBox.alert("Info", "Data Center and Server Pool level network can not be edited here");
                                return
                            }
                        }

                        if(!network_name.getValue()){
                             Ext.MessageBox.alert( _("Error") ,_("Network Name is required"));
                             return;
                        }
                        if(!network_description.getValue()){
                             Ext.MessageBox.alert( _("Error") ,_("Network Description is required"));
                             return;
                        }
                         if(!address_space.getRawValue()){
                             Ext.MessageBox.alert( _("Error") ,_("Address space is required"));
                             return;
                        }
                        if(!dhcprange.getRawValue()){
                             Ext.MessageBox.alert( _("Error") ,_("DHCP address range is required "));
                             return;
                        }

                        if(nat_radio.getValue()){
                             if(!nat_forward.getValue()){
                                 Ext.MessageBox.alert( _("Error") ,_("NAT Forwarding is required"));
                                 return;
                            }
                        }
//                        alert(address_space.getRawValue()+"---"+dhcprange.getRawValue());
                        if(mode=="NEW"){
                                var params="";
                                var url="";
                                params= sSiteId + op_level_main + sGroupId + sNodeId + "&nw_name="+network_name.getValue()+"&nw_desc="+network_description.getValue()+
                                    "&bridge="+bridgename.getValue()+"&nw_address_space="+address_space.getRawValue()+
                                    "&nw_dhcp_range="+dhcprange.getRawValue()+"&nat_radio="+nat_radio.getValue()+"&nw_nat_fwding="+nat_forward.getValue(); 
                                url="/network/add_nw_defn?"+params;
                    //                            alert(network_name.getValue());
                        }else{
                            var id=response.network.nw_id;
                            params= params="nw_id="+id+"&nw_name="+network_name.getValue()+"&nw_desc="+network_description.getValue();
                            url="/network/edit_nw_defn?"+params;
                        }

                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {//alert(xhr.responseText);
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    //                                           closeVirtualNetworkDefinition();
                                    //                                           parentPanel.remove('virtual_nw_def_form');
                                    closeThisWindow(nw_new_win_popup);
                                    reloadVirtualNetworkDefList();

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
     var virt_cancel_button=new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('Cancel'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                       click: function(btn) {
                        closeThisWindow(nw_new_win_popup);
                        reloadVirtualNetworkDefList();
                }
                }
            });
    if(mode=='NEW'){
        //nat_forward.hide();


   }
   var  virtual_nw_det_fldset=new Ext.form.FieldSet({
        title: _('Specify Virtual Network Details'),
        collapsible: false,
        autoHeight:true,
        width:400,
        labelSeparator: ' ',
        labelWidth:100,
        layout:'column',
        items: [
            {
                width: 420,
                layout:'form',
                items:[network_name]
            },{
                width: 420,
                layout:'form',
                items:[network_description]
            },{
                width: 420,
                layout:'form',
                items:[nw_type]
            },{
                width: 420,
                layout:'form',
                items:[lb3]
            },{
                width: 420,
                layout:'form',
                items:[address_space]
            },{
                width: 420,
                layout:'form',
                items:[dhcprange]
            }
//            ,{
//                width: 420,
//                layout:'form',
//                items:[nat_forward]
//            }
            ,{
                width: 420,
                layout:'form',
                items:[bridgename]
            },
            {
                width: 400,
                layout:'form',
                items:[lb4]
            }
        ]
    });

    //Start - From existing definitions
    var new_def_radio=new Ext.form.Radio({
        boxLabel: _('Define new network'),
        id:'new_def',
        name:'radio',
        //icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    existing_nw_def_form.setVisible(false);
                    virtual_nw_def_form.setVisible(true);
                    nw_def_form.getBottomToolbar().show();
                }
            }
        }
    });

    var from_dc_radio=new Ext.form.Radio({
        checked:true,
        boxLabel: _('Select from existing network'),
        id:'from_dc',
        name:'radio',
        //icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    existing_nw_def_form.setVisible(true);
                    virtual_nw_def_form.setVisible(false);
                    nw_def_form.getBottomToolbar().hide();
                }
            }
        }
    });

    var dc_radio_group= new  Ext.form.RadioGroup({
        columns: 1,
        //vertical: false,
        id:'dcradiogroup',
        items: [new_def_radio,from_dc_radio]
    });

    dc_radio_panel=new Ext.Panel({
        id:"dc_radio_panel_id",
        width:'100%',
        height:65,
        frame:true,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[dc_radio_group]
    });

    var dc_nw_columnModel = new Ext.grid.ColumnModel([

        {header: _("Name"), width: 90, sortable: false, dataIndex: 'name'},
        {header: _("Details"), width: 200, sortable: false, dataIndex: 'definition'},
        {header: _("Description"), width: 105, sortable: false, dataIndex: 'description'},
        {header: _("Status"), hidden: true, sortable: false, dataIndex: 'status'},
        {header: _("Scope"), hidden: true, sortable: false, dataIndex: 'scope'}
    ]);

     var network_list_dc_store = new Ext.data.JsonStore({
        url: '/network/get_nw_dc_defns?' + sSiteId + op_level + sGroupId + sNodeId,
        root: 'rows',
        fields: [ 'name', 'definition', 'description','status','type','id', 'status', 'scope'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    network_list_dc_store.load();

    var  virtual_nw_dc_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:false
    });

    var virt_associate_button=new Ext.Button({
        name: 'btnNwAssociate',
        id: 'btnNwAssociate',
        text:"Associate",
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                //var nwId = virtual_nw_dc_grid.getSelectionModel().getSelected().get('id');
                var def_ids = "";
                var sm = virtual_nw_dc_grid.getSelectionModel();
                var rows = sm.getSelections();
                for(i=0; i<rows.length; i++) {
                    if(i == rows.length-1) {
                        def_ids += rows[i].get('id');
                    } else {
                        def_ids += rows[i].get('id') + ',';
                    }
                }
                associate_nw_defns("NETWORK",def_ids);
            }
        }
    });

     var virt_associate_cancel_button=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('Close'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(windowid);
                reloadVirtualNetworkDefList();
            }
        }
    });

    virtual_nw_dc_grid = new Ext.grid.GridPanel({
        store: network_list_dc_store,
        colModel:dc_nw_columnModel,
        stripeRows: true,
        frame:false,
        selModel:virtual_nw_dc_selmodel,
        width:'100%',
        height:270,
        autoScroll:true,
        enableHdMenu:false
    });

    existing_nw_def_form = new Ext.Panel({
        frame:true,
        id:'existing_nw_def_form',
        width:'100%',
        items:[virtual_nw_dc_grid],
        tbar:[{xtype: 'tbfill'},virt_associate_button,'-',virt_associate_cancel_button]
    });
    //End - From existing definitions

    virtual_nw_def_form = new Ext.Panel({
        frame:true,
        id:'virtual_nw_def_form',
        width:'100%',
        items:[virtual_nw_det_fldset]
    });

    nw_def_form = new Ext.FormPanel({
        frame:true,
        width:'100%',
        height:420,
        items:[dc_radio_panel,existing_nw_def_form,virtual_nw_def_form],
        bbar:[{xtype: 'tbfill'},virt_save_button,'-',virt_cancel_button]
    });

    //nat_forward.getEl().up('.x-form-item').setDisplayed(true);
    if(mode=="NEW"){
        bridgename.setValue(response.bridge.bridge);

        if(node.attributes.nodetype == 'SERVER_POOL'){
            dc_radio_panel.setVisible(true);
            existing_nw_def_form.setVisible(true);
            virtual_nw_def_form.setVisible(false);
        } else {
            dc_radio_panel.setVisible(false);
            existing_nw_def_form.setVisible(false);
            virtual_nw_def_form.setVisible(true);
            nw_def_form.height = 350;
        }

    }else{
        var network=response.network;
        network_name.enable();
        network_description.enable();

        //server pool level
        if(sGroupId != "" && sNodeId == "") {
            if(network_scope == "DC") {
                network_name.disable();
                network_description.disable();
            }
        }
        //server level
        else if(sGroupId != "" && sNodeId != "") {
            if(network_scope == "DC" || network_scope == "SP") {
                network_name.disable();
                network_description.disable();
            }
        }
        network_name.setValue(network.name);
        network_description.setValue(network.description);
        address_space.setValue(network.nw_ipv4_info_ip_network);
        dhcprange.setValue(network.dhcp_range_value);
        bridgename.setValue(network.nw_bridge_info_name);

        nw_type.disable();
        address_space.disable();
        nat_forward.disable();
        dhcprange.disable();
        bridgename.disable();
        lb3.disable();
        lb4.disable();

        if(network.nw_nat_forward){
            nat_radio.setValue(true);
            hostonly_radio.setValue(false);
//            nat_forward.setValue(network.nw_nat_info_interface);
        }

        //show normal edit window
        dc_radio_panel.setVisible(false);
        existing_nw_def_form.setVisible(false);
        virtual_nw_def_form.setVisible(true);
    }

    return nw_def_form;
}

function addressspace_ajax(value,dhcprange){
    var url="/network/nw_address_changed?ip_value="+value;
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                dhcprange.setValue(response.range.range);
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
