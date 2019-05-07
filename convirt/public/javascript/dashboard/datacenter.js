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

function data_center_summary_page(mainpanel,node_id,node){
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
                            redrawChart(convirt.constants.DATA_CENTER,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'dc_chart'+node_id,true,panel1_1,convirt.constants.TOP5SERVERS);

                            //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false,convirt.constants.TOP5SERVERS);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
            redrawChart(convirt.constants.DATA_CENTER,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'dc_chart'+node_id,true,panel1_1,convirt.constants.TOP5SERVERS);
            //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false,convirt.constants.TOP5SERVERS);
        }
    });

    var type_combo=getMetricCombo();
    type_combo.on('select',function(field,rec,index){
        redrawChart(convirt.constants.DATA_CENTER,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'dc_chart'+node_id,true,panel1_1,convirt.constants.TOP5SERVERS);
        //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false,convirt.constants.TOP5SERVERS);
    });

    var dt_cntr_vm_grid=data_center_vm_grid(node_id);

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

    var panel3 = new Ext.Panel({
        width:'100%',
        height: 185,
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

    var cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 170,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:5px;padding-top:10px;',
        layout:'fit'
    });
    var mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 170,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:5px;padding-top:10px;',
        layout:'fit'
    });
     var srvr_cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 170,
        border:false,
        bodyBorder:false,
        layout:'fit'
        //bodyStyle:'padding-right:5px;padding-top:10px;'
    });
    var srvr_mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 170,
        border:false,
        bodyBorder:false,
        layout:'fit'
        //bodyStyle:'padding-right:5px;padding-top:10px;'
    });

    var top_cpu_vms_grid=topN_dcvms(node_id, node, "CPU");
    var top_mem_vms_grid=topN_dcvms(node_id, node, "Memory");
    var top_cpu_srvr_grid=topN_dcservers(node_id, node, "CPU");
    var top_mem_srvr_grid=topN_dcservers(node_id, node, "Memory");
    //var error_console_grid=err_console_grid();

    redrawChart(convirt.constants.DATA_CENTER,convirt.constants.CPU,node_id,node.text,
                convirt.constants.HRS12,fdate,tdate,'dc_chart'+node_id,true,panel1_1,convirt.constants.TOP5SERVERS);

    panel1_0.add(dt_cntr_vm_grid);
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel1.add(panel1_1);

    srvr_cpu_panel.add(top_cpu_srvr_grid);
    srvr_mem_panel.add(top_cpu_vms_grid);
    //err_panel.add(error_console_grid);
    
    panel3.add(srvr_cpu_panel);
    panel3.add(dummy_panel3);
    panel3.add(srvr_mem_panel);

    cpu_panel.add(top_mem_srvr_grid);
    mem_panel.add(top_mem_vms_grid);

    panel4.add(cpu_panel);
    panel4.add(dummy_panel4);
    panel4.add(mem_panel);

    //panel5.add(err_panel);
    
    var topPanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[panel1,panel3,panel4]
    });

//    var bottomPanel = new Ext.Panel({
//        //layout  : 'fit',
//        collapsible:true,
////        title:"Shared Information",
//        height:'50%',
//        width:'100%',
//        border:false,
//        bodyBorder:false,
//        items:[]
//    });

    var data_center_homepanel=new Ext.Panel({
        width:"100%",
        height:"100%"
        ,items:[topPanel]
        ,bodyStyle:'padding-left:10px;padding-right:5px;'
    });
    //data_center_homepanel.add(topPanel);
    //data_center_homepanel.add(bottomPanel);
    mainpanel.add(data_center_homepanel);
    data_center_homepanel.doLayout();
    mainpanel.doLayout();
    centerPanel.setActiveTab(mainpanel);
}

function data_center_config_page(mainpanel,node_id,node){

    if(mainpanel.items)
        mainpanel.removeAll(true);

    var dt_cntr_storage_grid=data_center_storage_grid(node_id,node);
    var dt_cntr_nw_grid=data_center_nw_grid(node_id,node);
    var dt_cntr_info_grid=data_center_info_grid(node_id);
    var panel1 = new Ext.Panel({
        height:250,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:5px;padding-right:5px;'
    });
    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("Host Operating System")+'<br/></div>'
    });
    var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("Guest Operating System")+'<br/></div>'
    });
     var panel1_1 = new Ext.Panel({
        height:245,
        width:'35%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle:'padding-left:15px;'
        ,tbar:[label1_1]
    });
    var panel1_2 = new Ext.Panel({
        height:245,
        width:'35%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle:'padding-left:15px;'
        ,tbar:[label1_2]
    });
    var dummy_panel1 = new Ext.Panel({
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
    var panel1_0 = new Ext.Panel({
        height:245,
        width:'29%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
     var panel4 = new Ext.Panel({
         width:'100%',
        height: 300,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var dummy_panel4 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });

    var storage_panel=new Ext.Panel({
        width:'49.5%',
        height: 220,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var nw_panel=new Ext.Panel({
        width:'49.5%',
        height: 220,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
	
    panel1_0.add(dt_cntr_info_grid);   
    panel1_1.add(os_dist_chart(node_id, node,convirt.constants.MANAGED_NODE));
    panel1_2.add(os_dist_chart(node_id, node,convirt.constants.DOMAIN));
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel1.add(panel1_1);
    panel1.add(dummy_panel2);
    panel1.add(panel1_2);


    storage_panel.add(dt_cntr_storage_grid);
    nw_panel.add(dt_cntr_nw_grid);

   
    panel4.add(storage_panel);
    panel4.add(dummy_panel4);
    panel4.add(nw_panel);
    var data_center_configpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        //cls:'headercolor',
        bodyBorder:false,
        items:[panel1,panel4]
        ,bodyStyle:'padding-left:10px;padding-right:5px;padding-top:5px;'
    });
//     var bottomPanel1 = new Ext.Panel({
//        //layout  : 'fit',
//        collapsible:true,
////        title:"Shared Information",
//        height:'50%',
//        width:'100%',
//        border:false,
////        cls:'headercolor',
//        bodyBorder:false,
//        items:[panel4]
//    });
//
//     var data_center_configpanel=new Ext.Panel({
//        width:"100%",
//        height:"100%"
//        ,items:[topPanel1,bottomPanel1]
//        ,bodyStyle:'padding:5px;'
//    });
    mainpanel.add(data_center_configpanel);
    data_center_configpanel.doLayout();
    mainpanel.doLayout();

}

function UIMakeUP(value, meta, rec){
    if(rec.get('type')==='bar'){
        var val=Ext.util.Format.substr(value,0,4);
        var id = Ext.id();
        (function(){
            new Ext.ProgressBar({
                renderTo: id,
                value: val/100,
                text:val,
                width:100,
                height:16
            });
        }).defer(25)
        return '<span id="' + id + '"></span>';
    }else if(rec.get('type')==='storage'){
        var val=Ext.util.Format.substr(value,0,4);
        var id = Ext.id();
        (function(){
            new Ext.ProgressBar({
                renderTo: id,
                value: val/100,
                text:val,
                width:75,
                height:16
            });
        }).defer(25)
        return '<span id="' + id + '"></span>';
    }else if(rec.get('type')==='vmsummary'){
        var summary=value;
        if(value.indexOf('/')>-1){
            var values=value.split('/');
            var tot=values[0];
            var run=values[1];
            var paus=values[2];
            var down=values[3];

            summary=tot;
            if(run!=0 || paus!=0 || down!=0){
                var str_down="";
                if(values[4]=="node_down"){
                    str_down="_down";
                }
                summary+=" [ ";
                var flag=false;
                if(run!=0){
                    flag=true;
                    summary+=" "+run+" "+
                        "<img width='13px' title='"+run+"Running' height='13px' src='../icons/small_started_state"+str_down+".png'/>";
                }
                if(paus!=0){                    
                    summary+=((flag)?" , ":"")+paus+" "+
                        "<img width='13px' title='"+paus+"Paused' height='13px' src='../icons/small_pause"+str_down+".png'/>";
                    flag=true;
                }
                if(down!=0){
                    summary+=((flag)?" , ":"")+down+" "+
                        "<img width='13px' title='"+down+"Down' height='13px' src='../icons/small_shutdown"+str_down+".png'/>";
                }

                summary+="]";
            }
            
        }
        return summary;
    }
    else if(rec.get('type') == 'Notifications'){
        
        var notificationValue = showNotifications(value,meta,rec);
        return notificationValue;
    }
     else if(rec.get('type') == 'Systemtasks'){

        var sysTasks = showSysTasks(value,meta,rec);
        return sysTasks;
    }
    else{
        return value;
    }
}


function data_center_info_grid(node_id){
    var data_center_info_store =new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=DATA_CENTER_INFO",
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
    data_center_info_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Summary")+'</div>',
        id:'label_task'
    });

    var data_center_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //title:_("Summary"),
        //autoHeight:true,
        border:true,
        //cls:'hideheader padded headercolor1',
        cls:'hideheader ',
        //width: 450,
        width: '100%',
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
             {header: "", width: 120, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
             {header: "", width: 100, sortable: true,dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:data_center_info_store
        ,tbar:[label_strge]
    });

    return data_center_info_grid
}

function data_center_sec_info_grid(node_id){
    var data_center_sec_info_store =new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=DATA_CENTER_SEC_INFO",
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
    data_center_sec_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var data_center_sec_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:false,
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
        store:data_center_sec_info_store
    });

    return data_center_sec_info_grid
}

function data_center_vm_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=DATA_CENTER_VM_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type','list','entType'],
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
    
    var data_center_vm_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        autoExpandColumn:1,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 225,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        loadMask:true,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 130, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 100, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return data_center_vm_grid
}

function data_center_storage_grid(node_id,node){

    var data_center_storage_columnModel = new Ext.grid.ColumnModel([
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
    },
    {
        header: _("Server Pools"),
        width: 150,
        dataIndex: 'serverpools',
        sortable:true
    }]);

    var data_center_storage_store = new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=STORAGE_INFO",
        root: 'info',
        fields: ['name','type','size','description','serverpools','usage'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    data_center_storage_store.load({
        params:{
            node_id:node_id
        }
    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Storage Resources")+'</div>'
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
    var data_center_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: data_center_storage_store,
        colModel:data_center_storage_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:1,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:false,
        autoScroll:true,
        id:'data_center_storage_summary_grid',
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

	return data_center_storage_grid;

}

function data_center_nw_grid(node_id,node){

    var data_center_nw_columnModel = new Ext.grid.ColumnModel([
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
        width: 100,
        sortable:true,
        dataIndex: 'definition'
    },
    {
        header: _("Description"),
        width: 150,
        sortable:true,
        dataIndex: 'description'
    }]);

    var data_center_nw_store = new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=VIRT_NW_INFO",
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
    data_center_nw_store.load({
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
	var data_center_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: data_center_nw_store,
        colModel:data_center_nw_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:4,
        autoExpandMin:150,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'data_center_nw_summary_grid',
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

	return data_center_nw_grid;

}

function topN_dcvms(node_id,node,metric){
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
            width: 100,
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
        //autoExpandMax:300,
        autoExpandMin:80,
        //border:false,
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
function topN_dcservers(node_id,node,metric){
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
            width: 100,

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
        html:'<div class="toolbar_hdg">'+format(_("Top 5 Servers by {0} Usage"),metric)+'</div>'
    });

	var top_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: top_store,
        colModel:top_cm,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        //autoExpandMax:300,
        autoExpandMin:80,
        //border:false,
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

Ext.override(Ext.grid.GridPanel, {
     rowcontextmenu :function(grid,rowIndex,e) {
        e.preventDefault();
        handle_rowclick(grid,rowIndex,"contextmenu",e);
    },
    rowdblclick:function(grid,rowIndex,e){
        handle_rowclick(grid,rowIndex,"click",e);
    }
});

function os_dist_chart(node_id,node,metric){
    var srvr_distribution_store = new Ext.data.Store({
        url:"/dashboard/os_distribution_chart?node_id="+node_id+"&metric="+metric+"&node_type="+node.attributes.nodetype,
        reader: new Ext.data.JsonReader({
        root: 'info',
            fields: ['label', 'value']
        })
    });

    var srvr_distribution_pie = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value,percent,textValue, pie, series, options) {
                //alert(label+"==value=="+value+"===percent==="+percent+"==textValue==="+textValue+"pie==="+pie);
                if(value==0){
                    return "";
                }
                return textValue+"%("+value+")";
            },  
            labelStyle: 'font-size:10px; '

        },
        height:'100%',
        width:'100%',
        legend: {
            show: true,
            position: "se",
            margin: [0,0],
            backgroundOpacity: 0
            ,labelFormatter: function(label, series) {                
                return '<div style="font-size:10px;">' + label + '</div>';
            }
        },
        series: []
    });

    srvr_distribution_store.on('load',
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
        srvr_distribution_pie
    );

    srvr_distribution_store.load();

    return srvr_distribution_pie;
}

function data_center_vminfo_page(mainpanel,node_id,node){

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
    
    var server_grid=showServerList(node_id,convirt.constants.DATA_CENTER,panel2);

    panel2.add(server_grid);

    var vm_grid=showVMList(node_id,convirt.constants.DATA_CENTER,panel3);
    panel3.add(vm_grid);
    var vminformpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        //cls:'headercolor1',
//        cls:'headercolor',
        bodyStyle:'padding-left:15px;padding-right:10px;padding-bottom:12px;padding-top:10px;',
        bodyBorder:false,
        resizable:true,
        items:[panel2,panel3]
    });

    mainpanel.add(vminformpanel);
    vminformpanel.doLayout();
    mainpanel.doLayout();
}

