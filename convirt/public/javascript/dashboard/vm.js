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

function vm_summary_page(mainpanel,node_id,node){
    if(mainpanel.items)
        mainpanel.removeAll(true);

    var label0_1=new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("Daily")+'<br/></div>'
    });
    var label1_1=new Ext.form.Label({
        html:getChartHdrMsg(node.text,"Hourly","CPU")
    });
     var label1_2=new Ext.form.Label({
        html:getChartHdrMsg(node.text,"Hourly","Memory")
    });

    var avg_fdate="",avg_tdate="";
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
                            redrawChart(convirt.constants.DOMAIN,convirt.constants.CPU,node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);
                        }
                    }
                }
            });
            avg_window.addButton(btn);
            avg_window.show();

        }
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
                            redrawChart(convirt.constants.DOMAIN,convirt.constants.CPU,node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);

                            label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),'CPU'),false);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
            redrawChart(convirt.constants.DOMAIN,convirt.constants.CPU,node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);
            label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),'CPU'),false);
        }
    });

//    var type_combo=getMetricCombo();
//    type_combo.on('select',function(field,rec,index){
//        redrawChart(convirt.constants.DOMAIN,type_combo.getValue(),node_id,node.text,
//                            period_combo.getValue(),fdate,tdate,'vm_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);
//        label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
//    });

    var avg_fdate1="",avg_tdate1="";
    var avg_button1=new Ext.Button({
        icon: '/icons/date.png', // icons can also be specified inline
        cls: 'x-btn-icon',
        tooltip: {
            text:'<b>Show Average</b><br/>'
        },
        handler:function(){
            var avg1=new CustomPeriodUI(_("Show Average"),fdate1,tdate1,selperiod1);
            var avg_window1 = avg1.getWindow();
            var btn= new Ext.Button({
                text: _('OK'),
                listeners: {
                    click: function(btn) {
                        if(avg1.validate()){
                            avg_window1.hide();
                            avg_fdate1=avg1.fromTime();
                            avg_tdate1=avg1.toTime();
                            var label=formatDate(new Date(avg_fdate1))+" - "+formatDate(new Date(avg_tdate1));
                            var btnEl = avg_button1.getEl().child(avg_button1.buttonSelector);
                            var tgt = Ext.QuickTips.getQuickTip().targets[btnEl.id];
                            tgt.text = '<b>Show Average</b><br/>'+label;
                            redrawChart(convirt.constants.DOMAIN,convirt.constants.MEM,node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'vm_memory_chart'+node_id,true,panel1_11,null,avg_fdate1,avg_tdate1);
                        }
                    }
                }
            });
            avg_window1.addButton(btn);
            avg_window1.show();

        }
    });

    var period_combo1=getPeriodCombo();    
    var fdate1="",tdate1="",selperiod1=convirt.constants.HRS12;
    period_combo1.on('select',function(field,rec,index){
        if(field.getValue() ==convirt.constants.CUSTOM){
            var cust1=new CustomPeriodUI(_("Select Period for Metric Utilization"),fdate1,tdate1,selperiod1);
            var cust_window1 = cust1.getWindow();
            var custom_btn1= new Ext.Button({
                text: _('OK'),
                listeners: {
                    click: function(btn) {
                        if(cust1.validate()){
                            cust_window1.hide();
                            fdate1=cust1.fromTime();
                            tdate1=cust1.toTime();
                            redrawChart(convirt.constants.DOMAIN,convirt.constants.MEM,node_id,node.text,
                                period_combo1.getValue(),fdate1,tdate1,'vm_memory_chart'+node_id,true,panel1_11,null,avg_fdate,avg_tdate);

                            label1_2.setText(getChartHdrMsg(node.text,period_combo1.getRawValue(),'Memory'),false);
                        }
                    }
                }
            });
            cust_window1.addButton(custom_btn1);
            cust_window1.show();
        }else{
            selperiod1=period_combo1.getValue();
            fdate1="",tdate1="";
            redrawChart(convirt.constants.DOMAIN,convirt.constants.MEM,node_id,node.text,
                            period_combo1.getValue(),fdate1,tdate1,'vm_memory_chart'+node_id,true,panel1_11,null,avg_fdate,avg_tdate);
            label1_2.setText(getChartHdrMsg(node.text,period_combo1.getRawValue(),'Memory'),false);
        }
    });

	
    var vm_grid=vm_info_grid(node_id);
//    var vm_gridext=vm_info_gridext(node_id);
//    var vm_strge_grid=vm_storage_grid(node_id);
//    var vm_ntw_grid=vm_nw_grid(node_id);

    var panel1 = new Ext.Panel({
        height:500,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column'
//        bodyStyle:'padding-top:5px;padding-left:5px;'
    });
    var panel2 = new Ext.Panel({
        height:250,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:7px;padding-left:5px;'
    });

    var label_summ=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Summary")+'</div>',
        id:'label_task'
    });
    var panel1_0 = new Ext.Panel({
        height:500,
        width:'30%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
    var panel1_1 = new Ext.Panel({
        height:240,
       // width:'69%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        ,tbar:[' ',label1_1,{xtype:'tbfill'},avg_button,'-',period_combo,'-']
    });  
    var label2_0=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("Availability")+'<br/></div>'
    });
    var panel2_0 = new Ext.Panel({
        height:'100%',
        width:'30%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        ,layout:'fit'

    });
    var panel2_1 = new Ext.Panel({
        height:500,
        width:'69%',
        border:false,
        bodyBorder:false
        //,layout:'fit'
    });
     var panel1_11 = new Ext.Panel({
        height:250,
        //width:'35%',
        border:true,
        cls: 'whitebackground',
        bodyStyle:'padding-top:10px;',
        bodyBorder:true
        ,tbar:[' ',label1_2,{xtype:'tbfill'},avg_button1,'-',period_combo1,'-']
    });


    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;',
        bodyBorder:false
    });
    var dummy_panel2 = new Ext.Panel({
        height:10,
        border:true,
        html:'&nbsp;',
        bodyBorder:false
    });
    
    panel1_0.add(vm_grid);
    //panel1_1.add(chart_panel);

    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel2_1.add(panel1_1);
//    panel1_11.add(vm_life_cycle)dummy_panel2
    panel2_1.add(dummy_panel2)
    panel2_1.add(panel1_11)
    panel1.add(panel2_1)
  //panel1.add(panel1_1);

//    panel1.add(vm_avail_pie);
    redrawChart(convirt.constants.DOMAIN,convirt.constants.CPU,node_id,node.text,
                    convirt.constants.HRS12,fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);

    redrawChart(convirt.constants.DOMAIN,convirt.constants.MEM,node_id,node.text,
                    convirt.constants.HRS12,fdate1,tdate1,'vm_memory_chart'+node_id,true,panel1_11,null,avg_fdate1,avg_tdate1);
//    storage_panel.add(vm_strge_grid);
//    nw_panel.add(vm_ntw_grid);
//
//    panel4.add(storage_panel);
//    panel4.add(dummy_panel4);
//    panel4.add(nw_panel);
    var topPanel = new Ext.Panel({
        //title:format(_("Information for {0}"),node.text),
        collapsible:false,
        height:'100%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false
        ,bodyStyle:'padding-right:5px;',
        items:[panel1]
    });

//    var bottomPanel = new Ext.Panel({
//        title:"Shared Information",
//        collapsible:true,
//        height:'50%',
//        width:'100%',
//        border:false,
//        cls:'headercolor',
//        bodyBorder:false,
//        items:[panel4]
//    });

    var vm_homepanel = new Ext.Panel({
        height:'100%',
        items:[topPanel]
        ,bodyStyle:'padding-left:10px;padding-right:5px;padding-top:10px;'
    });

    mainpanel.add(vm_homepanel);
    vm_homepanel.doLayout();
    mainpanel.doLayout();
    centerPanel.setActiveTab(mainpanel);

}

function vm_info_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=VM_INFO",
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
    vm_info_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Summary")+'</div>',
        id:'label_task'
    });

    var vm_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: false,
        //autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 230,
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
            {header: "", width: 130, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 120, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return vm_grid;
}

function vm_storage_grid(node_id){

    var vm_storage_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Type"),
        width:50,
        dataIndex: 'type',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("Location"),
        width: 150,
        sortable:true,
        dataIndex: 'filename'
    },
    {
        header: _("Size"),
        width: 50,
        sortable:true,
        dataIndex: 'size'
    },
    {
        header: _("Device"),
        width: 50,
        dataIndex: 'device'
    },
    {
        header: _("Mode"),
        width: 35,
        dataIndex: 'mode'
    },
    {
        header: _("Shared"),
        width: 45,
        dataIndex: 'shared'
    }]);

    var vm_storage_store = new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=STORAGE_INFO",
        root: 'info',
        fields: ['type','filename','device','mode','shared','size'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vm_storage_store.load({
        params:{
            node_id:node_id
        }
    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Storage Information")+'</div>'
    });
	var vm_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vm_storage_store,
        colModel:vm_storage_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        autoExpandMin:150,
        border:true,
        enableHdMenu:false,
        autoScroll:true,
        id:'vm_storage_summary_grid',
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_strge]
    });

	return vm_storage_grid;

}

function vm_nw_grid(node_id){

    var vm_nw_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Name"),
        width: 150,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("Details"),
        width: 110,
        sortable:true,
        dataIndex: 'description'
    },
    {
        header: _("MAC"),
        width: 170,
        dataIndex: 'mac'
    } ]);


    var vm_nw_store = new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=NW_INFO",
        root: 'info',
        fields: ['name','description','mac'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vm_nw_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_nw=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Network Information")+'</div>'
    });
	var vm_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vm_nw_store,
        colModel:vm_nw_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        border:true,
        enableHdMenu:false,
        autoScroll:true,
        id:'vm_nw_summary_grid',
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_nw]
    });

	return vm_nw_grid;

}

function vm_availability_chart(node_id,node){
    var vm_avail_store = new Ext.data.Store({
        url: "/dashboard/vm_availability?node_id="+node_id,
        reader: new Ext.data.JsonReader({
            root: 'info',
            fields: ['label', 'value']
        })
    });

    var vm_avail_pie = new Ext.ux.PieFlot({
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
            position: "ne",
            margin: [0,0],
            backgroundOpacity: 0
        },
        series: []
    });

    vm_avail_store.on('load',
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
        vm_avail_pie
    );

    vm_avail_store.load();

    return vm_avail_pie;
}

//function vm_storage_chart(node_id,node){
//    var vm_storage_store = new Ext.data.Store({
//        url: "/dashboard/vm_storage?node_id="+node_id,
//        reader: new Ext.data.JsonReader({
//            root: 'info',
//            fields: ['label', 'value']
//        })
//    });
//
//    var vm_storage_pie = new Ext.ux.PieFlot({
//        pies: {
//            show: true,
//            autoScale: true,
//            fillOpacity: 1,
//            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
//                if(value == 0)
//                {
//                    return '';
//                }
//                return textValue + '% ('+value+"GB)";
//            },
//            labelStyle: 'font-size:11px; '
//
//        },
//        width:'100%',
//        height:'100%',
//        legend: {
//            show: true,
//            position: "ne",
//            margin: [0,0],
//            backgroundOpacity: 0
//        },
//        series: []
//    });
//
//    vm_storage_store.on('load',
//        function(store, records, options) {
//            try{
//                var series = this.createSeries(store, 'label', 'value');
//                this.plot(series);
//                this.baseRanges = this.getRanges();
//            }catch(e)
//            {
//                Ext.MessageBox.alert(_("Error"),e);
//            }
//
//        },
//        vm_storage_pie
//    );
//
//    vm_storage_store.load();
//
//    return vm_storage_pie;
//}

function vm_info_gridext(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=VM_INFO_EXT",
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
    vm_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var vm_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader padded',
        width: '100%',
        height: 210,
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
            {header: "", width: 110, sortable: false, css:'font-weight:bold;',dataIndex: 'name'},
            {header: "", width: 160, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
//        ,tbar:[label_strge]
    });

    return vm_grid;
}

function vm_config_page(configPanel,node_id,node){
    if(configPanel.items)
        configPanel.removeAll(true);
    var vm_strge_grid=vm_storage_grid(node_id);
    var vm_ntw_grid=vm_nw_grid(node_id);

    var panel1 = new Ext.Panel({
        width:'100%',
        height: '100%',
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

    var template_info=get_templateinfo(node_id);
    var general_info=get_generalinfo(node_id);
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

    panel1_1.add(general_info);
    panel1_2.add(template_info);
    panel1.add(panel1_1);
    panel1.add(dummy_panel1);
    panel1.add(panel1_2);

    var bootparam_info=get_bootparaminfo(node_id);
    var advanced_info=get_advancedinfo(node_id);

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
    panel2_1.add(bootparam_info);
    panel2_2.add(advanced_info);
    panel2.add(panel2_1);
    panel2.add(dummy_panel2);
    panel2.add(panel2_2);

    var usb_info=get_usbdeviceinfo(node_id);
    var display_info=get_displayinfo(node_id)
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
    panel3_1.add(display_info);
    panel3_2.add(usb_info);

    panel3.add(panel3_1);
    panel3.add(dummy_panel3);
    panel3.add(panel3_2);
    

    var storage_panel=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var nw_panel=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });

    storage_panel.add(vm_strge_grid);
    nw_panel.add(vm_ntw_grid);
    
    panel4.add(storage_panel);
    panel4.add(dummy_panel4);
    panel4.add(nw_panel);

    var bottomPanel = new Ext.Panel({
//        collapsible:true,
        height:'100%',
        width:'100%',
        border:false,
//        cls:'headercolor',
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:5px;',
        items:[panel1,panel3,panel2,panel4]
    });
    
    configPanel.add(bottomPanel);
    bottomPanel.doLayout();
    configPanel.doLayout();
}

function get_generalinfo(node_id){

    var vm_general_store =new Ext.data.JsonStore({
//        url: "vm_general_info",
        url: "/dashboard/vm_info?type=GENERAL_INFO",
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
    vm_general_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("General")+'</div>', 
        id:'label_general'
    });

    var general_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        //title:_("General"),
        cls:'hideheader  ',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        width: '100%',
        height: 150,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold;color:#414141;',dataIndex: 'name'},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_general_store
        ,tbar:[label_general]
    });

    return general_grid;

}
function get_templateinfo(node_id){
    var vm_template_store =new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=TEMPLATE_INFO",
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
    vm_template_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_template=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("Template")+'</div>',
       id:'label_template'
   });

    var template_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Template"),
        cls:'hideheader ',
        width: '100%',
        height: 150,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_template_store
        ,tbar:[label_template]
    });

    return template_grid;
}
function get_bootparaminfo(node_id){

    var vm_bootparam_store =new Ext.data.JsonStore({
//        url: "vm_bootparam_info",
        url: "/dashboard/vm_info?type=BOOT_PARAM",
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
    vm_bootparam_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_bp=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("Boot Parameters")+'</div>',
       id:'label_bp'
   });

    var bootparams_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Boot Parameters"),
        cls:'hideheader',
        width: '100%',
        height: 260,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_bootparam_store
        ,tbar:[label_bp]
    });

    return bootparams_grid;

}
function get_displayinfo(node_id){

    var vm_display_store =new Ext.data.JsonStore({
//        url: "vm_bootparam_info",
        url: "/dashboard/vm_info?type=DISPLAY",
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
    vm_display_store.load({
        params:{
            node_id:node_id
        }
    });
   var label_display=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("Display Configuration")+'</div>',
       id:'label_general'
   });

    var display_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Display Configuration"),
        cls:'hideheader',
        width: '100%',
        height: 130,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_display_store
        ,tbar:[label_display]
    });

    return display_grid;

}
function get_usbdeviceinfo(node_id){

    var vm_usbdevice_store =new Ext.data.JsonStore({
//        url: "vm_bootparam_info",
        url: "/dashboard/vm_info?type=USB_DEVICE",
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
    vm_usbdevice_store.load({
        params:{
            node_id:node_id
        }
    });
   
    var label_usb=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("USB Configuration")+'</div>',
       id:'label_usb'
    });

    var display_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("USB Configuration"),
        cls:'hideheader ',
        width: '100%',
        height: 130,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_usbdevice_store
        ,tbar:[label_usb]
    });

    return display_grid;

}
function get_advancedinfo(node_id){
       var adv_store =new Ext.data.JsonStore({
//        url: "vm_bootparam_info",
        url: "/dashboard/vm_info?type=ADVANCED",
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
    adv_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_adv=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("Advanced")+'</div>',
       id:'label_adv'
   });

    var adv_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Advanced"),
        cls:'hideheader',
        width: '100%',
        height: 260,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:adv_store
        ,tbar:[label_adv]
    });

    return adv_grid;

}
