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

function server_summary_page(mainpanel,node_id,node){
    //node_id='d9a3bd4a-062a-5017-22af-94222763e8b9';
    if(mainpanel.items)
        mainpanel.removeAll(true);

//    var label0_1=new Ext.form.Label({
//        html:'<div class="toolbar_hdg" >'+_("Daily")+'<br/></div>'
//    });
    var label2=new Ext.form.Label({
        html:getChartHdrMsg(node.text,"Hourly","CPU")
    });

    var avg_fdate="",avg_tdate="",selperiod=convirt.constants.HRS12;
    var avg_button=new Ext.Button({
        icon: '/icons/date.png', // icons can also be specified inline
        cls: 'x-btn-icon',
        tooltip: {
            text:'<b>Show Average</b><br/>'
        },
        handler:function(){
            var avg=new CustomPeriodUI(_("Show Average"),fdate,tdate,selperiod);
            var avg_window = avg.getWindow();
            var btn= new Ext.Button({
                id:'avg_button',
                text: _('OK'),
                listeners: {
                    click: function(btn) {
                        if(avg.validate()){
                            avg_window.hide();
                            avg_fdate=avg.fromTime();
                            avg_tdate=avg.toTime();
                            var label=formatDate(new Date(avg_fdate))+" - "+formatDate(new Date(avg_tdate));
                            var btnEl = avg_button.getEl().child(avg_button.buttonSelector);
                            var tgt = Ext.QuickTips.getQuickTip().targets[btnEl.id];
                            tgt.text = '<b>Show Average</b><br/>'+label;
                            redrawChart(convirt.constants.MANAGED_NODE,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);
                        }
                    }
                }
            });
            avg_window.addButton(btn);
            avg_window.show();

        }
    });

    var period_combo=getPeriodCombo();
    var fdate="",tdate="";
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
                            redrawChart(convirt.constants.MANAGED_NODE,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);

                            label2.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
            redrawChart(convirt.constants.MANAGED_NODE,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);
            label2.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
        }
    });

    var type_combo=getMetricCombo();
    type_combo.on('select',function(field,rec,index){
        redrawChart(convirt.constants.MANAGED_NODE,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);
        label2.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
    });

//    var srvr_info_grid=server_info_grid(node_id);
//    var srvr_sec_info_grid=server_sec_info_grid(node_id);
    var srvr_vm_grid=server_vm_grid(node_id);
//    var srvr_storage_grid=server_storage_grid(node_id,node);
//    var srvr_nw_grid=server_nw_grid(node_id,node);
    var top_cpu_grid=topNvms(node_id, node, "CPU");
    var top_mem_grid=topNvms(node_id, node, "Memory");

    var panel1 = new Ext.Panel({
        height:280,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:5px;padding-right:5px;'
    });
    var panel1_0 = new Ext.Panel({
        height:275,
        width:'30%',
        border:false,
        bodyBorder:false
        //,bodyStyle:'padding-right:15px;'
        ,layout:'fit'
    });
    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("CPU Usage")+'<br/></div>'
    });
    var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("Memory Usage")+'<br/></div>'
    });
    var panel1_1 = new Ext.Panel({
        height:230,
        width:'49.5%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_1]
    });
    var panel1_2 = new Ext.Panel({
        height:230,
        width:'49.5%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle :'padding-left:15px;padding-right:15px;'
        ,tbar:[label1_2]
    });
//    var panel1_5 = new Ext.Panel({
//        height:'100%',
//        width:'60%',
//        border:false,
//        bodyBorder:false
//        //,bodyStyle:'padding-left:15px;padding-right:30px;padding-bottom:12px;padding-top:10px;'
//        ,layout:'fit'
//    });
    var panel2 = new Ext.Panel({
        height:275,
        width:'69%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle:'padding-left:15px;padding-right:30px;padding-bottom:12px;padding-top:10px;'
        ,tbar:[' ',label2,{xtype:'tbfill'},avg_button,'-',period_combo,'-',type_combo]
    });  
    //var summary_grid=drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    var panel3 = new Ext.Panel({
        height:'100%',
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column'
        , bodyStyle:'padding-top:10px;padding-right:5px;'
    });

    var panel4 = new Ext.Panel({
        height:'100%',
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column'
        , bodyStyle:'padding-top:10px;padding-right:5px;'
    });

    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });
    
    var dummy_panel3 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;',
        bodyBorder:false
    });
    var dummy_panel4 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;',
        bodyBorder:false
    });

//    var info_panel=new Ext.Panel({
//        width:'48%',
//        height: 140,
//        border:false,
//        bodyBorder:false,
//        bodyStyle:'padding-left:15px;padding-right:3px;padding-top:10px;',
//        layout:'fit'
//    });
//    var sec_info_panel=new Ext.Panel({
//        width:'48%',
//        height: 140,
//        border:false,
//        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
//        layout:'fit'
//    });

    var cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 230,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:15px;padding-right:3px;padding-top:2px;',
        layout:'fit'
    });
    var mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 230,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:15px;padding-right:3px;',
        layout:'fit'
    });

    //panel1_1.add(get_cpu_chart());
    redrawChart(convirt.constants.MANAGED_NODE,convirt.constants.CPU,node_id,node.text,
                        convirt.constants.HRS12,fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);
    panel1_0.add(srvr_vm_grid);
    //panel1_5.add(panel2)
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel1.add(panel2);
//    panel1.add(panel1_0);
//    panel1.add(dummy_panel1);
//
    panel1_1.add(server_usage_chart(node_id, node, "CPU"));
    panel1_2.add(server_usage_chart(node_id, node, "Memory"));
//    panel1.add(panel1_1);
//    panel1.add(dummy_panel2);
//    panel1.add(panel1_2);
    //panel1_1.add(label1_1);

//    panel1.add(dummy_panel2);
//    panel1.add(chpanel2);

    //panel2.add(summary_grid);

//    info_panel.add(srvr_info_grid);
//    sec_info_panel.add(srvr_sec_info_grid);

//    panel3.add(info_panel);
//    panel3.add(dummy_panel3);
//    panel3.add(sec_info_panel);

    //storage_panel.add(label3);
    cpu_panel.add(top_cpu_grid);
    //nw_panel.add(label4);
    mem_panel.add(top_mem_grid);

    panel3.add( panel1_1);
    panel3.add(dummy_panel3);
    panel3.add(cpu_panel);
    panel4.add(panel1_2);
    panel4.add(dummy_panel4);
    panel4.add(mem_panel);
    
    //panel4.add(label2);


    var topPanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Information for {0}"),node.text),
        height:'100%',
        width:'100%',
        border:false,
        cls:'headercolor',
        layout:'column',
        bodyBorder:false,
//        ,bodyStyle:'padding-left:10px;padding-right:5px;padding-top:5px;',
        items:[panel1,panel3,panel4]
    });

//    var bottomPanel = new Ext.Panel({
//        //layout  : 'fit',
////        collapsible:true,
////        title:"Top VMs",
//        height:'35%',
//        width:'100%',
//        border:false,
//        cls:'headercolor',
//        bodyBorder:false,
//        bodyStyle:'padding-top:15px;',
//        items:[]
//    });

    var server_homepanel=new Ext.Panel({
         height:'50%',
         width:'100%',
         border:false,
         bodyBorder:false
        ,collapsible:false
        ,items:[topPanel]
        ,bodyStyle:'padding-left:10px;padding-right:5px;padding-top:5px;'
    });
    //server_homepanel.add(topPanel);
    //server_homepanel.add(bottomPanel);
    mainpanel.add(server_homepanel);
    server_homepanel.doLayout();
    mainpanel.doLayout();
    centerPanel.setActiveTab(mainpanel);
}

function server_config_page(mainpanel,node_id,node){

    if(mainpanel.items)
        mainpanel.removeAll(true);

    var panel1 = new Ext.Panel({
        width:'100%',
        height: '30%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
    var panel2 = new Ext.Panel({
        width:'100%',
        height: '100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
    var panel3 = new Ext.Panel({
        width:'100%',
        height: '100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
    var panel4 = new Ext.Panel({
        width:'100%',
        height: '100%',
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
    var dummy_panel2 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
    var dummy_panel3 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
    var dummy_panel4 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
    var panel1_1=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel1_2=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel2_1=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel2_2=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel3_1=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel3_2=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel4_1=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel4_2=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });

    var srvr_interface_grid= server_interface_grid(node_id,node);
    var srvr_dvce_grid=server_dvce_grid(node_id,node);

    var srvr_storage_grid=server_storage_grid(node_id, node);
    var srvr_nw_grid=server_nw_grid(node_id, node);

    panel1_1.add(server_config_grid(node_id, node, "Platform"));
    panel1_2.add(server_config_grid(node_id, node, "Memory"));

    panel2_1.add(server_config_grid(node_id, node, "OS"));
    panel2_2.add(server_config_grid(node_id, node, "CPU"));

    panel3_1.add(srvr_interface_grid);
    panel3_2.add(srvr_dvce_grid);

    panel4_1.add(srvr_storage_grid);
    panel4_2.add(srvr_nw_grid);

    panel1.add(panel1_1);
    panel1.add(dummy_panel1);
    panel1.add(panel1_2)

    panel2.add(panel2_1);
    panel2.add(dummy_panel2);
    panel2.add(panel2_2)

    panel3.add(panel3_1);
    panel3.add(dummy_panel3);
    panel3.add(panel3_2);   

    panel4.add(panel4_1);
    panel4.add(dummy_panel4);
    panel4.add(panel4_2);

    var configpanel = new Ext.Panel({
        height:"100%",
        width:"100%",
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:5px;',
        items:[panel1,panel2,panel3,panel4]
    });
    mainpanel.add(configpanel);
    configpanel.doLayout();
    mainpanel.doLayout();

}

function server_vminfo_page(mainpanel,node_id,node){

     if(mainpanel.items)
        mainpanel.removeAll(true);

    var panel2 = new Ext.Panel({
        height:300,
        width:'100%',
        layout: 'fit',
        bodyStyle:'padding-bottom:1px;padding-top:1px;',
        border:false,
        bodyBorder:false
    });
    var summary_grid=showVMList(node_id,convirt.constants.MANAGED_NODE,panel2);
    //drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    panel2.add(summary_grid);

    var vminformpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
//        cls:'headercolor',
//        cls:'westPanel',
        bodyBorder:false,
        bodyStyle:'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;background-color: #F1F1F1;',
        resizable:true,
        items:[panel2]
    });

    mainpanel.add(vminformpanel);
    vminformpanel.doLayout();
    mainpanel.doLayout();
}

function server_info_grid(node_id){
    var server_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=SERVER_INFO",
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
    server_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var server_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader',
        width:'100%',
        //height: 200,
        enableHdMenu:false,
        enableColumnMove:false,
         autoExpandColumn:1,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 100, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 200, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:server_info_store
    });

    return server_info_grid
}

function server_sec_info_grid(node_id){
    var server_sec_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=SERVER_SEC_INFO",
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
    server_sec_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var server_sec_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader padded',
        width:'100%',
        //height: 200,
        enableHdMenu:false,
        enableColumnMove:false,
         autoExpandColumn:1,
        //plugins:[action],
        autoScroll:true,
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
        store:server_sec_info_store
    });

    return server_sec_info_grid
}

function server_vm_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=VM_INFO",
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

    var server_vm_grid = new Ext.grid.GridPanel({
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
            {header: "", width: 140, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 100, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return server_vm_grid
}

function server_dvce_grid(node_id,node){

    var server_dvce_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Device"),
        width: 150,
        dataIndex: 'file_system',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("Mounted On"),
        width: 150,
        sortable:true,
        dataIndex: 'mounted_on'
    },
    {
        header: _("Size"),
        width: 100,
        dataIndex: 'size',
        sortable:true
    }]);

    var server_dvce_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=DISK_INFO",
        root: 'info',
        fields: ['file_system','mounted_on','size'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_dvce_store.load({
        params:{
            node_id:node_id
        }
    });
    
   var label_dvce=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("Mounted Devices")+'</div>'
   });
	var server_dvce_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_dvce_store,
        colModel:server_dvce_columnModel,
        stripeRows: true,
        frame:false,
        //title:_("Mounted Devices"),
        autoExpandColumn:1,
        autoExpandMax:300,
//        border:false,
        enableHdMenu:false,
        //cls:'headercolor1',
        autoScroll:true,
        //cls:'padded',
//        viewConfig: {
//            getRowClass: function(record, index) {
//                return 'row-border';
//            }
//        },
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_dvce]
    });

	return server_dvce_grid;

}

function server_interface_grid(node_id,node){

    var server_interface_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Name"),
        width: 110,
        dataIndex: 'interface_name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("IP Address"),
        width: 300,
        sortable:true,
        dataIndex: 'ip_address'
    }]);

    var server_interface_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=INTERFACE_INFO",
        root: 'info',
        fields: ['interface_name','ip_address'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_interface_store.load({
        params:{
            node_id:node_id
        }
    });
   var label_interface=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("Available Interfaces")+'</div>'
   });
    
	var server_interface_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_interface_store,
        colModel:server_interface_columnModel,
        stripeRows: true,
        //title:_("Available Interfaces"),
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:350,
        //cls:'headercolor1',
        //border:false,
        enableHdMenu:false,
        autoScroll:true,
        //cls:'padded',
//        viewConfig: {
//            getRowClass: function(record, index) {
//                return 'row-border';
//            }
//        },
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_interface]
    });

	return server_interface_grid;

}

function server_config_grid(node_id,node,config){    

    var server_config_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type="+config+"_INFO",
        root: 'info',
        fields: ['label','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_config_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_config=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+format(_("{0} Information"),config)+'</div>'
   });
    
    var srvr_config_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        //title:format(_("{0} Information"),config),
        border:true,
        //cls:'hideheader padded headercolor1',
        cls:'hideheader',
        width:'100%',
//        autoHeight:true,
        height:150,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'label'},
            {header: "", width: 280, sortable: false, dataIndex: 'value',renderer:UIMakeUP,css: 'white-space: normal !important;'}
        ],
        store:server_config_store
        ,tbar:[label_config]
    });

    return srvr_config_grid
}

function server_usage_chart(node_id,node,metric){
    var srvr_usage_store = new Ext.data.Store({
        url: "/dashboard/server_usage?node_id="+node_id+"&metric="+metric,
        reader: new Ext.data.JsonReader({
            root: 'info',
            fields: ['label', 'value']
        })
    });

    var srvr_usage_pie = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
                if(value == 0)
                {
                    return '';
                }
                return textValue + '% ';
            },
            labelStyle: 'font-size:11px; '

        },
        width:'100%',
        height:'100%',
        legend: {
            show: true,
            position: "se",
            margin: [0,0],
            backgroundOpacity: 0
        },
        series: []
    });

    srvr_usage_store.on('load',
        function(store, records, options) {
            try{
                var series = this.createSeries(store, 'label', 'value');
                this.plot(series);
                this.baseRanges = this.getRanges();
            }catch(e)
            {
//                Ext.MessageBox.alert(_("Error"),e);
            }

        },
        srvr_usage_pie
    );

    srvr_usage_store.load();

    return srvr_usage_pie;
}

function topNvms(node_id,node,metric){
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
            width: 350,
            dataIndex: 'vm',
            //css:'font-weight:bold;',
            sortable:true
        },
        {
            header: format(_("Host {0}(%)"),metric),
            width: 230,
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
        //border:false,
        enableHdMenu:false,
        autoScroll:true,
        width:'100%',
        //autoExpandColumn:1,
        height:300
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

function server_storage_grid(node_id,node){

    var server_storage_columnModel = new Ext.grid.ColumnModel([
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
        header: _("Size (GB)"),
        width: 100,
        dataIndex: 'size',
        sortable:true,
        align: 'right'
    },
    {
        header: _("Description"),
        width: 150,
        dataIndex: 'description',
        sortable:true
    }]);

    var server_storage_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=STORAGE_INFO",
        root: 'info',
        fields: ['name','type','size','description'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_storage_store.load({
        params:{
            node_id:node_id
        }
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
    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Storage Resources")+'</div>'
    });

    var server_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_storage_store,
        colModel:server_storage_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:3,
        autoExpandMax:300,
//        border:false,
        enableHdMenu:true,
        autoScroll:true,
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

	return server_storage_grid;

}

function server_nw_grid(node_id,node){

    var server_nw_columnModel = new Ext.grid.ColumnModel([
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
        header: _("Details"),
        width: 100,
        sortable:true,
        dataIndex: 'definition'
    },
    {
        header: _("Description"),
        width: 80,
        sortable:true,
        dataIndex: 'description'
    },
    {
        header: _("Scope"),
        width: 110,
        sortable:true,
        dataIndex: 'displayscope',
        hidden:true
    }]);

    var server_nw_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=VIRT_NW_INFO",
        root: 'info',
        fields: ['name','definition','type','description','displayscope'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_nw_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_nw=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Virtual Networks")+'</div>'
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
	var server_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_nw_store,
        colModel:server_nw_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:3,
        autoExpandMax:300,
        //border:false,
        enableHdMenu:true,
        autoScroll:true,
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

	return server_nw_grid;

}
