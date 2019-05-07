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

function ApplianceList(image_group){

    var rec = Ext.data.Record.create([
       {name: 'name', type: 'string'},
       {name: 'id', type: 'string'},
       {name: 'value', type: 'string'}
    ]);
    var r=new rec({
        name: _('Any'),
        id: '0',
        value: 'Any'
    });

    var prvdr_store = new Ext.data.JsonStore({
        url: '/appliance/get_appliance_providers',
        root: 'rows',
        fields: ['name', 'value'],
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,load:function(store,recs,opts){
                store.insert(0,[r])
            }
        }
    });
    prvdr_store.load();
   
    var prvdrs=new Ext.form.ComboBox({
        fieldLabel: _('Provider'),
        triggerAction:'all',
        store: prvdr_store,
        emptyText :_("Provider"),
        displayField:'name',
        valueField:'value',
        width: 100,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'prvdr',
        id:'prvdr',
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                var prvdr=record.get('value');
                filterApplianceGrid(grid)
            }
        }
    });

    var pkg_store = new Ext.data.JsonStore({
        url: '/appliance/get_appliance_packages',
        root: 'rows',
        fields: ['name', 'value'],
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,load:function(store,recs,opts){
                store.insert(0,[r])
            }
        }
    });
    pkg_store.load();
    var pkgs=new Ext.form.ComboBox({
        fieldLabel: _('Package'),
        triggerAction:'all',
        store: pkg_store,
        emptyText :_("Package"),
        displayField:'name',
        valueField:'value',
        width: 100,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'pkg',
        id:'pkg',
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                var pkg=record.get('value');
                filterApplianceGrid(grid)
            }
        }
    });

    var arch_store = new Ext.data.JsonStore({
        url: '/appliance/get_appliance_archs',
        root: 'rows',
        fields: ['name', 'value'],
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,load:function(store,recs,opts){
                store.insert(0,[r])
            }
        }
    });
    arch_store.load();
    var archs=new Ext.form.ComboBox({
        fieldLabel: _('Arch'),
        triggerAction:'all',
        store: arch_store,
        emptyText :_("Architecture"),
        displayField:'name',
        valueField:'value',
        width: 100,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'arch',
        id:'arch',
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                var arch=record.get('value');
                filterApplianceGrid(grid)
            }
        }
    });

    var pae=new Ext.form.Checkbox({
        name: 'pae',
        id: 'pae',
        boxLabel:_('PAE'),
        checked:false,
        listeners:{
            check:function(box,checked){
                var check=(checked)?"Y":"";
                filterApplianceGrid(grid)
            }
        }
    });

    var title=new Ext.form.TextField({
        fieldLabel: _('Search'),
        name: 'title',
        id: 'title',
        allowBlank:true,
        enableKeyEvents:true,
        emptyText:_('Name'),
        width:250,
        listeners: {
            keyup: function(field) {
                filterApplianceGrid(grid);
            }
        }
    });

    var store = new Ext.data.JsonStore({
        url: "/appliance/get_appliance_list",
        root: 'rows',
        fields: ['PACKAGE','TITLE','SHORT_DESC','DESC','SIZE_MB','PAE','PROVIDER','PROVIDER_LOGO','ARCH','UPDATED','APPLIANCE_ENTRY'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    store.load();
    store.sort('TITLE','ASC');
    var columnModel = new Ext.grid.ColumnModel([
        {header: "",width: 25,sortable: true, dataIndex: 'PROVIDER_LOGO',renderer:function(value,params,record){
                    return '<img height="16px" src="'+value+'"/>';
            }
        },
        {header: _("Provider"), width: 150, sortable: true, dataIndex: 'PROVIDER'},
        {header: _("Name"), width: 150, sortable: true, dataIndex: 'TITLE',renderer:function (value, params, record){
            var desc=record.get("SHORT_DESC");
            if(desc==""){
                desc=record.get("DESC")
            }
            params.attr = 'title="'+desc+'"';
            return value;
        }},
        {header: _("Package"), width: 90, sortable: true, dataIndex: 'PACKAGE'},
        {header: _("Arch"), width: 60, sortable: true, dataIndex: 'ARCH'},
        {header: _("PAE"), width: 35, sortable: true, dataIndex: 'PAE'},
        {header: _("Size"), width: 80, sortable: true, dataIndex: 'SIZE_MB'},
        {header: _("Updated"), width: 130, sortable: true, dataIndex: 'UPDATED'},
        {header: _("Description"), hidden:true, width: 200, sortable: true, dataIndex: 'DESC'},
        {header: _("Short Desc"), hidden:true, width: 200, sortable: true, dataIndex: 'SHORT_DESC'}
    ]);

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var refresh_btn=new Ext.Button({
        name: 'refresh',
        id: 'refresh',
        //tooltip:'Refresh',
        //tooltipType : "title",
        icon:'icons/refresh.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                reloadApplianceList(grid);
            }
        }
    });
    var grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        border:true,
        width:'100%',
        autoExpandColumn:1,
        height:365,
        selModel:selmodel,
        enableHdMenu:false
        ,tbar:[refresh_btn,_('Search'),'-',prvdrs,'-',title,'-',pkgs,'-',archs,'-',pae]
        ,listeners: {
            rowdblclick:function(grid, rowIndex, e){
                import_button.fireEvent('click',import_button);
            }
        }
    });

    var import_button= new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('Import'),
        icon:'icons/appliance_import.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(grid.getSelectionModel().getSelections().length==0){
                    Ext.MessageBox.alert(_("Warning"),_("Please select an appliance from the list."));
                    return;
                }
                closeWindow();
                var rec=grid.getSelectionModel().getSelected();
                //alert(grid.getSelectionModel().getSelected().get('APPLIANCE_ENTRY'));
                showApplianceDialog(image_group,rec.get('APPLIANCE_ENTRY'));
            }
        }
    });

    var cancel_button=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('Cancel'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {closeWindow();}
        }
    });

    var panel = new Ext.Panel({
        layout:'form',
        bodyStyle:'padding:1px 0px 0px 0px',
        labelWidth:60,
        labelSeparator:' ',
        width:700,
        height:400,
        items:[grid],
        bbar:[{xtype: 'tbfill'},
//            new Ext.Button({
//                name: 'manual',
//                id: 'manual',
//                text:'Specify Manually',
//                icon:'icons/appliance_edit.png',
//                cls:'x-btn-text-icon',
//                listeners: {
//                    click: function(btn) {
//                        closeWindow();
//                        showApplianceDialog(image_group,null,null);
//                    }
//                }
//            }),
//            '-',
            import_button,
            '-',
            cancel_button
        ]
    });

    return panel;
}

function filterApplianceGrid(grid){

    var value="";
    var grid_tool=grid.getTopToolbar();
    var prvdr=((value=grid_tool.items.get('prvdr').getValue())=='Any')?"":value;
    var pkg=((value=grid_tool.items.get('pkg').getValue())=='Any')?"":value;
    var arch=((value=grid_tool.items.get('arch').getValue())=='Any')?"":value;
    var pae=(grid_tool.items.get('pae').getValue())?"Y":"";
    var title=grid_tool.items.get('title').getValue();
    //alert(prvdr+"--"+title+"--"+pkg+"--"+arch+"--"+pae+"--");

    grid.getStore().filterBy(function(rec,id){
        if(prvdr!="" && rec.get('PROVIDER').indexOf(prvdr)<0)
            return false;
        if(title!="" && rec.get('TITLE').indexOf(title)<0)
            return false;
        if(pkg!="" && rec.get('PACKAGE').indexOf(pkg)<0)
            return false;
        if(arch!="" && rec.get('ARCH')!=arch)
            return false;
        if(pae!="" && rec.get('PAE').indexOf(pae)<0)
            return false;

        return true;
    });
}

function showApplianceDialog(image_group,appliance){
    showWindow(_("Appliance Catalog"),595,230,ImportApplianceDialog(image_group,appliance));
}

function reloadApplianceList(grid){
    Ext.MessageBox.show({
        title:_('Please wait...'),
        msg: _('Reloading Appliance List') + _('Please wait...'),
        width:300,
        wait:true,
        waitConfig: {interval:200}
    });
    var ajaxReq = ajaxRequest("refresh_appliances_catalog",0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            Ext.MessageBox.hide();
            grid.getStore().load()
        },
        failure: function(xhr) {
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
