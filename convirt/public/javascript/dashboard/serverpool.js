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

function server_pool_summary_page(mainpanel,node_id,node){
    //node_id='d9a3bd4a-062a-5017-22af-94222763e8b9';
    if(mainpanel.items)
        mainpanel.removeAll(true);

    var label0_1=new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("Daily")+'<br/></div>'
    });
    var label1_1=new Ext.form.Label({
        //html:getChartHdrMsg(node.text,"Hourly","CPU")
        html:'<div class="toolbar_hdg">'+_("Top 5 Servers")+'</div>'
    });

    var period_combo=getPeriodCombo();
    var fdate="",tdate="",selperiod=convirt.constants.HRS12;
    period_combo.on('select',function(field,rec,index){
        if(field.getValue() ==convirt.constants.CUSTOM){
            var cust=new CustomPeriodUI(_("Select Period for Metric Utilization"),fdate,tdate,selperiod);
            var cust_window = cust.getWindow();
            var custom_btn= new Ext.Button({
                text: _('OK'),
                listeners: {
                    click: function(btn) {
                        if(cust.validate()){
                            cust_window.hide();
                            fdate=cust.fromTime();
                            tdate=cust.toTime();
                            redrawChart(convirt.constants.SERVER_POOL,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'sp_chart'+node_id,true,panel1_1,convirt.constants.TOP5SERVERS);

                            //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
            redrawChart(convirt.constants.SERVER_POOL,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'sp_chart'+node_id,true,panel1_1,convirt.constants.TOP5SERVERS);
            //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
        }
    });

    var type_combo=getMetricCombo();
    type_combo.on('select',function(field,rec,index){
        redrawChart(convirt.constants.SERVER_POOL,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'sp_chart'+node_id,true,panel1_1,convirt.constants.TOP5SERVERS);
        //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
    });

//    var srvr_pool_info_grid=server_pool_info_grid(node_id);
//    var srvr_pool_sec_info_grid=server_pool_sec_info_grid(node_id);
    var srvr_pool_vm_grid=server_pool_vm_grid(node_id);
//    var srvr_pool_storage_grid=server_pool_storage_grid(node_id,node);
//    var srvr_pool_nw_grid=server_pool_nw_grid(node_id,node);

    //var sp_provisionsetg_grid=serverpool_provisionsetg_grid(node_id,node);

    var panel1 = new Ext.Panel({
        height:250,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:10px;padding-right:5px;'
    });
    var panel1_0 = new Ext.Panel({
        height:240,
        width:'30%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
    var panel1_1 = new Ext.Panel({
        height:240,
        width:'69%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle:'padding-left:15px;'
        ,tbar:[getTop5Info(),label1_1,{xtype:'tbfill'},period_combo,'-',type_combo]
    });  
//    var panel2 = new Ext.Panel({
//        height:250,
//        width:'100%',
//        layout: 'fit',
//        bodyStyle:'padding-left:15px;padding-right:30px;padding-bottom:12px;padding-top:10px;',
//        border:false,
//        bodyBorder:false
//    });
//    var summary_grid=drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);
   var panel3 = new Ext.Panel({
        width:'100%',
        height:185,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var panel4 = new Ext.Panel({
        width:'100%',
        height: 185,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });
    var dummy_panel2 = new Ext.Panel({
        width:20,
        border:false,
        bodyBorder:false
    });
    var dummy_panel3 = new Ext.Panel({
        width:'1%',
        border:false,
        html:'&nbsp;',
        bodyBorder:false
    });
    var dummy_panel4 = new Ext.Panel({
        width:'1%',
        border:false,
        html:'&nbsp;',
        bodyBorder:false
    });
//    var dummy_panel5 = new Ext.Panel({
//        width:10,
//        border:false,
//        bodyBorder:false
//    });
    var top_cpu_grid=topN_spvms(node_id, node, "CPU");
    var top_mem_grid=topN_spvms(node_id, node, "Memory");


     var cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 175,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:5px;',
        layout:'fit'
    });

    
    
//    var storage_panel=new Ext.Panel({
//        width:'48%',
//        height: 220,
//        border:false,
//        bodyBorder:false,
//        bodyStyle:'padding-left:15px;padding-right:3px;padding-top:10px;',
//        layout:'fit'
//    });
//    var nw_panel=new Ext.Panel({
//        width:'48%',
//        height: 220,
//        border:false,
//        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
//        layout:'fit'
//    });

    //panel1_1.add(get_sp_cpu_chart());
    redrawChart(convirt.constants.SERVER_POOL,convirt.constants.CPU,node_id,node.text,
                    convirt.constants.HRS12,fdate,tdate,'sp_chart'+node_id,true,panel1_1,convirt.constants.TOP5SERVERS);

    panel1_0.add(srvr_pool_vm_grid);
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel1.add(panel1_1);
    //panel1_1.add(label1_1);

//    panel1.add(dummy_panel2);
//    panel1.add(chpanel2);

//    panel2.add(summary_grid);

//    panel3.add(srvr_pool_info_grid);
//    panel3.add(dummy_panel3);
//    panel3.add(srvr_pool_sec_info_grid);

    //storage_panel.add(label3);
   var server_cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 175,
        border:false,
        bodyBorder:false,
        layout:'fit'
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;'
    });
    var server_mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
        layout:'fit'
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:5px;'
    });

    var top_servercpu_grid=topN_spservers(node_id, node, "CPU");
    var top_servermem_grid=topN_spservers(node_id, node, "Memory");
    server_cpu_panel.add(top_servercpu_grid);
    //nw_panel.add(label4);
    server_mem_panel.add(top_servermem_grid);

    cpu_panel.add(top_cpu_grid);
    //nw_panel.add(label4);
    mem_panel.add(top_mem_grid);

    panel3.add(server_cpu_panel);
    panel3.add(dummy_panel3);
    panel3.add(cpu_panel);

    panel4.add(server_mem_panel);
    panel4.add(dummy_panel4);
    panel4.add(mem_panel);

//    storage_panel.add(srvr_pool_storage_grid);
//    //nw_panel.add(label4);
//    nw_panel.add(srvr_pool_nw_grid);
//
//    panel5.add(storage_panel);
//    panel5.add(dummy_panel5);
//    panel5.add(nw_panel);
    //panel4.add(label2);



    var topPanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[panel1,panel3,panel4]
    });

    var label_provstg=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Provision Settings")+'</div>',
        id:'label_task'
    });
    var provision_setting_panel = new Ext.Panel({
        width:'50%',
        autoHeight: true,
        bodyBorder:false,
        layout:'column'
//        ,items:[label_provstg,sp_provisionsetg_grid]
    });

//    var bottomPanel = new Ext.Panel({
//        //layout  : 'fit',
//        collapsible:true,
//        title:"Shared Information",
//        height:'50%',
//        width:'100%',
//        border:false,
//        cls:'headercolor',
//        bodyBorder:false,
//        items:[panel5]
//    });

    var server_pool_homepanel=new Ext.Panel({
        width:"100%",
        height:"100%"
        ,items:[topPanel]
        ,bodyStyle:'padding-left:10px;padding-right:5px;'
    });
    //server_pool_homepanel.add(topPanel);
    //server_pool_homepanel.add(bottomPanel);
    mainpanel.add(server_pool_homepanel);
    server_pool_homepanel.doLayout();
    mainpanel.doLayout();
	centerPanel.setActiveTab(mainpanel);
}

function server_pool_info_grid(node_id){
    var server_pool_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=SERVER_POOL_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_pool_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var server_pool_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader padded',
        width: 450,
        //height: 200,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
         autoExpandColumn:1,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 100, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 300, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:server_pool_info_store
    });

    return server_pool_info_grid
}

function server_pool_sec_info_grid(node_id){
    var server_pool_sec_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=SERVER_POOL_SEC_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_pool_sec_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var server_pool_sec_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader padded',
        width: 450,
        //height: 200,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 100, sortable: false, css:'font-weight:bold;',dataIndex: 'name'},
            {header: "", width: 300, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:server_pool_sec_info_store
    });

    return server_pool_sec_info_grid
}

function server_pool_vm_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=SERVER_POOL_VM_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type','list'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vm_info_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Summary")+'</div>',
        id:'label_task'
    });

    var server_pool_vm_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 210,
        enableHdMenu:false,
         autoExpandColumn:1,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 130, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 120, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return server_pool_vm_grid
}

function server_pool_storage_grid(node_id,node){

    var server_pool_storage_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Name"),
        width: 90,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("Type"),
        width: 60,
        sortable:true,
        dataIndex: 'type'
    },
    {
        header: _("Size(GB)"),
        width: 80,
        dataIndex: 'size',
        sortable:true,
        align: 'right'
    },
    {
        header: _("Allocation(%)"),
        width: 120,
        dataIndex: 'usage',
        sortable:true,
        renderer:showBar
    },
    {
        header: _("Description"),
        width: 150,
        dataIndex: 'description',
        sortable:true
    }]);

    var server_pool_storage_store = new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=STORAGE_INFO",
        root: 'info',
        fields: ['name','type','size','description','usage'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_pool_storage_store.load({
        params:{
            node_id:node_id
        }
    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Storage Resources")+'</div>',
        id:'label_strge'
    });
    var settings_btn=new Ext.Button({
        tooltip:'Manage Storage Pool',
        tooltipType : "title",
        icon:'icons/settings.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                showWindow(_("Storage Pool")+":- "+node.text,444,495,StorageDefList(node));

            }
        }
    });
	var server_pool_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_pool_storage_store,
        colModel:server_pool_storage_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:3,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'server_pool_storage_summary_grid',
        //cls:'padded',
//        viewConfig: {
//            getRowClass: function(record, index) {
//                return 'row-border';
//            }
//        },
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_strge]
    });

	return server_pool_storage_grid;

}

function server_pool_nw_grid(node_id,node){

    var server_pool_nw_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Name"),
        width: 90,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("Type"),
        width: 80,
        sortable:true,
        dataIndex: 'type'
    },
    {
        header: _("Server"),
        width: 100,
        sortable:true,
        dataIndex: 'server'
    },
    {
        header: _("Details"),
        width: 80,
        sortable:true,
        dataIndex: 'definition'
    },
    {
        header: _("Description"),
        width: 150,
        sortable:true,
        dataIndex: 'description'
    }]);

    var server_pool_nw_store = new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=VIRT_NW_INFO",
        root: 'info',
        fields: ['name','definition','type','description','server'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_pool_nw_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_nw=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Virtual Networks")+'</div>',
        id:'label_nw'
    });
    var settings_btn=new Ext.Button({
        tooltip:'Manage Virtual Network',
        tooltipType : "title",
        icon:'icons/settings.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
           showWindow(_("Manage Virtual Network")+":- "+node.text,466,450,VirtualNetwork(node));
            }
        }
    });
	var server_pool_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_pool_nw_store,
        colModel:server_pool_nw_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:4,
        autoExpandMax:300,
        autoExpandMin:150,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'server_pool_nw_summary_grid',
        //cls:'padded',
//        viewConfig: {
//            getRowClass: function(record, index) {
//                return 'row-border';
//            }
//        },
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_nw]
    });

	return server_pool_nw_grid;

}
function serverpool_provisionsetg_grid(node_id,node){
    var serverpool_provisionsetg_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Id"),
        width: 50,
        hidden: true,
        dataIndex: 'id'
    },
    {
        header: _("Variable"),
        width: 150,
        dataIndex: 'variable'
    },
    {
        header: _("Value"),
        width: 100,
        dataIndex: 'value'
    }]);

    var provisionsetg_store = new Ext.data.JsonStore({
        url: '/node/get_group_vars?group_id='+node_id,
        root: 'rows',
        fields: ['id', 'variable', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });
   provisionsetg_store.load();
   var serverpool_provisionsetg_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: provisionsetg_store,
        colModel: serverpool_provisionsetg_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        enableHdMenu:false,
        autoScroll:true,
        id:'serverpool_provisionsetg_grid',
        width:'100%',
        height:220
     });

	return serverpool_provisionsetg_grid;
  

}
function topN_spvms(node_id,node,metric){
    var top_cm = new Ext.grid.ColumnModel([
        {
            header: _("VMid"),
            width: 110,
            dataIndex: 'vmid',
            hidden:true,
            sortable:true
        },
        {
            header: _("Name"),
            width: 150,
            dataIndex: 'vm',
            //css:'font-weight:bold;',
            sortable:true
        },
        {
            header: format(_("Host {0}(%)"),metric),
            width: 180,
            sortable:true,
            dataIndex: 'usage',
            renderer:showBar
        }
    ]);

    var top_store = new Ext.data.JsonStore({
        url: "/dashboard/topNvms?node_id="+node_id+"&metric="+metric+"&node_type="+node.attributes.nodetype,
        root: 'info',
        fields: ['vmid','vm','usage','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    top_store.load();

    var label=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+format(_("Top 5 Virtual Machines by {0} Usage"),metric)+'</div>',
        id:'label_task'
    });

	var top_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: top_store,
        colModel:top_cm,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        autoExpandMin:80,
//        border:true,
        enableHdMenu:false,
        autoScroll:true,
        width:'100%',
        //autoExpandColumn:1,
        height:170
        ,tbar:[label]
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick:function(grid,rowIndex,e){
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });

	return top_grid;
}
function topN_spservers(node_id,node,metric){
    var top_cm = new Ext.grid.ColumnModel([
        {
            header: _("Serverid"),
            width: 110,
            dataIndex: 'serverid',
            hidden:true,
            sortable:true
        },
        {
            header: _("Name"),
            width: 150,
            dataIndex: 'server',
            //css:'font-weight:bold;',
            sortable:true
        },
        {
            header: format(_("{0} Usage(%)"),metric),
            width: 180,
            sortable:true,
            dataIndex: 'usage',
            renderer:showBar
        }
    ]);

    var top_store = new Ext.data.JsonStore({
        url: "/dashboard/topNservers?node_id="+node_id+"&metric="+metric+"&node_type="+node.attributes.nodetype,
        root: 'info',
        fields: ['serverid','server','usage','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    top_store.load();

    var label=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+format(_("Top 5 Servers by {0} Usage"),metric)+'</div>',
        id:'label_task'
    });

	var top_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: top_store,
        colModel:top_cm,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        autoExpandMin:80,
//        border:true,
        enableHdMenu:false,
        autoScroll:true,
        width:'100%',
        //autoExpandColumn:1,
        height:170
        ,tbar:[label]
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick:function(grid,rowIndex,e){
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });

	return top_grid;
}
function server_pool_config_page(configPanel,node_id,node){
   if(configPanel.items)
        configPanel.removeAll(true);
   var panel1 = new Ext.Panel({
        width:'100%',
        height:250,
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:5px;padding-right:5px;'
    });
    var panel5 = new Ext.Panel({
        width:'100%',
        height: 300,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
     var dummy_panel1 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
    var dummy_panel3 = new Ext.Panel({
        width:'0.5%',
        border:false,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });
    var dummy_panel2 = new Ext.Panel({
        width:'0.5%',
        border:false,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });
    var storage_panel=new Ext.Panel({
        width:'49.5%',
        height: 220,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var nw_panel=new Ext.Panel({
        width:'49.5%',
        height: 220,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("Host Operating System")+'<br/></div>'
    });
    var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("Guest Operating System")+'<br/></div>'
    });
    var panel1_1 = new Ext.Panel({
        height:245,
        width:'29%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
    var panel1_2 = new Ext.Panel({
        height:245,
        width:'35%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        ,tbar:[label1_1]
        ,layout:'fit'
    });

    var panel1_3 = new Ext.Panel({
        height:245,
        width:'35%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        ,tbar:[label1_2]
        ,layout:'fit'
    });

    
    panel1_2.add(os_dist_chart(node_id, node, convirt.constants.MANAGED_NODE));
    panel1_3.add(os_dist_chart(node_id, node, convirt.constants.DOMAIN));
    var srvr_pool_summarygrid=srvr_pool_summary_grid(node_id,node);
    panel1_1.add(srvr_pool_summarygrid);
    panel1.add(panel1_1);
    panel1.add(dummy_panel2);
    panel1.add(panel1_2);
    panel1.add(dummy_panel3);
    panel1.add(panel1_3);

    var srvr_pool_storage_grid=server_pool_storage_grid(node_id,node);
    var srvr_pool_nw_grid=server_pool_nw_grid(node_id,node);
    
    storage_panel.add(srvr_pool_storage_grid);
    //nw_panel.add(label4);
    nw_panel.add(srvr_pool_nw_grid);

    panel5.add(storage_panel);
    panel5.add(dummy_panel1);
    panel5.add(nw_panel);
    var bottomPanel = new Ext.Panel({
      //layout  : 'fit',
//        collapsible:true,
        height:'50%',
        width:'100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:5px;padding-top:5px;',
        items:[panel1,panel5]
    });
    configPanel.add(bottomPanel);
	bottomPanel.doLayout();
    configPanel.doLayout();
}

function srvr_pool_summary_grid(node_id,node){
      var summary_store =new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=SUMMARY",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    summary_store.load({
        params:{
            node_id:node_id
        }
    });
    

    var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Summary")+'</div>',
        id:'label_task'
    });

    var sp_summary_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Summary"),
        cls:'hideheader',
        width: '100%',
        height: 250,
         autoExpandColumn:1,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 120, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 100, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:summary_store
        ,tbar:[label_summary]
    });

    return sp_summary_grid;
}

function server_pool_vminfo_page(mainpanel,node_id,node){

    if(mainpanel.items)
        mainpanel.removeAll(true);
    var p2_expand=1;
    var p3_expand=1;
    var panel2 = new Ext.Panel({
        height:250,
        width:'100%',
        layout: 'fit',
        bodyStyle:'padding-bottom:12px;padding-top:10px;',
        border:false,
        bodyBorder:false,
        title:_('Server Information'),
        collapsible:true,
        //cls:'headercolor1',
        listeners:({
            collapse:function(p2){
                p2_expand=0;
                panel3.setHeight(520);
                p3_expand=1;
            },
            expand:function(p2){
               if (p3_expand==1){
                   p2.setHeight(250);
                   panel3.setHeight(250);
                   p2.doLayout();
                   panel3.doLayout();
               }
            }

        })
    });
     var panel3 = new Ext.Panel({
        height:250,
        width:'100%',
        title:_('Virtual Machines Information'),
        layout: 'fit',
        bodyStyle:'padding-bottom:12px;padding-top:10px;',
        border:false,
        bodyBorder:false,
        collapsible:true,
        //cls:'headercolor1',
        listeners:({
            collapse:function(p3){
                 p3_expand=0;
                 panel2.setHeight(520);
                 p2_expand=1;

            },
             expand:function(p3){
                 if (p2_expand==1){
                   p3.setHeight(250);
                   panel2.setHeight(250);
                   panel2.doLayout();
                   p3.doLayout();
               }
             }
        })
    });
    var summary_grid=showServerList(node_id,convirt.constants.SERVER_POOL,panel2);
    //drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    panel2.add(summary_grid);

    var vm_grid=showVMList(node_id,convirt.constants.SERVER_POOL,panel3);
    panel3.add(vm_grid);
    var vminformpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
//        cls:'headercolor',
        bodyStyle:'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
        bodyBorder:false,
        resizable:true,
        items:[panel2,panel3]
    });

    mainpanel.add(vminformpanel);
    vminformpanel.doLayout();
    mainpanel.doLayout();
}
