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

function getChartHdrMsg(node,period,type){
    return '<div class="toolbar_hdg" >'+format(_("{0} Utilization"),type)+'<div>';
}
function showChart(node_type,metric,node_id,node_name,period,frmdate,todate,chartid,chart_type){
    chartid="popup"+chartid;
    
    var period_combo=getPeriodCombo('Period',100,period,50,"combo_ct");
    var fdate=frmdate,tdate=todate,selperiod=period;
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
//                            redrawChart(node_type,metric,node_id,node_name,
//                                period_combo.getValue(),fdate,tdate,chartid,false,chart_panel);
                            go_btn.fireEvent('click',go_btn);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
//            redrawChart(node_type,metric,node_id,node_name,
//                                period_combo.getValue(),fdate,tdate,chartid,false,chart_panel);
        }
    });

    var metric_combo1=getMetricCombo('Metric',80,metric,60,"combo_ct");
    var metric_combo2=getMetricCombo('Metric',80,metric,60,"combo_ct");
    metric_combo2.setDisabled(true);
    
    var enttype_store1 = new Ext.data.JsonStore({
        url: '/model/get_enttype_for_chart',
        root: 'rows',
        fields: ['entid', 'entname','dispname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_( "Error"),store_response.msg);
            }
            ,load:function(store,recs,options){
                for(var i=0;i<recs.length;i++){
                    if(recs[i].get("entname")===node_type){
                        enttype_combo1.setValue(recs[i].get("entid"));
                        enttype_combo1.fireEvent('select',enttype_combo1,recs[i],0);
                        enttype_combo1.selectedIndex=i;
                    }
                }
            }
        }
    });
    var enttype_combo1=new Ext.form.ComboBox({
        triggerAction:'all',
        store: enttype_store1,
        emptyText :_("Select"),
        fieldLabel:'Type',
        displayField:'dispname',
        valueField:'entid',
        width: 100,
        labelStyle: 'width:50px;',
        ctCls:"combo_ct",
        forceSelection: true,
        mode:'local',
        listeners:{
            select:function(combo){
                ent1_store.load({
                    params:{enttype_id:combo.getValue()}
                });
            }
        }
    });
    enttype_store1.load();
    var ent1_store = new Ext.data.JsonStore({
        url: '/model/get_entities',
        root: 'rows',
        fields: ['entid', 'entname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_( "Error"),store_response.msg);
            }
            ,load:function(store,recs,options){
                var rec=enttype_combo1.getStore().getAt(enttype_combo1.selectedIndex);
                if(node_type==rec.get('entname')){
                    ent1_combo.setValue(node_id);
                }else{
                    ent1_combo.reset();
                }
            }
        }
    });
    var ent1_combo=new Ext.form.ComboBox({
        triggerAction:'all',
        store: ent1_store,
        emptyText :_("Select"),
        fieldLabel:'Name',
        displayField:'entname',
        valueField:'entid',
        width: 100,
        labelStyle: 'width:50px;',
        ctCls:"combo_ct",
        minListWidth:150,
        forceSelection: true,
        mode:'local',
        listeners:{
            select:function(combo){
                if(combo.getValue()==ent2_combo.getValue()){
                    //ent2_combo.reset();
                }
            }
        }
    });

    var enttype_store2 = new Ext.data.JsonStore({
        url: '/model/get_enttype_for_chart',
        root: 'rows',
        fields: ['entid', 'entname','dispname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_( "Error"),store_response.msg);
            }
        }
    });
    var enttype_combo2=new Ext.form.ComboBox({
        triggerAction:'all',
        store: enttype_store2,
        emptyText :_("Select"),
        fieldLabel:'Type',
        displayField:'dispname',
        valueField:'entid',
        width: 100,
        labelStyle: 'width:50px;',
        ctCls:"combo_ct",
        forceSelection: true,
        disabled:true,
        mode:'local',
        listeners:{
            select:function(combo){
                ent2_store.load({
                    params:{enttype_id:combo.getValue()}
                });
            }
        }
    });
    enttype_store2.load();
    var ent2_store = new Ext.data.JsonStore({
        url: '/model/get_entities',
        root: 'rows',
        fields: ['entid', 'entname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_( "Error"),store_response.msg);
            }
            ,load:function(store,recs,options){
                ent2_combo.reset();
            }
        }
    });
    var ent2_combo=new Ext.form.ComboBox({
        triggerAction:'all',
        store: ent2_store,
        emptyText :_("Select"),
        fieldLabel:'Name',
        displayField:'entname',
        listWidth:150,
        valueField:'entid',
        width: 100,
        labelStyle: 'width:50px;',
        ctCls:"combo_ct",
        forceSelection: true,
        disabled:true,
        mode:'local',
        listeners:{
            select:function(combo){
                if(combo.getValue()==ent1_combo.getValue()){
                    //ent1_combo.reset();
                }
            }
        }
    });

    var go_btn= new Ext.Button({
        text: _('GO'),
        width:60,
        bodyStyle:'padding-left:20px;',
        listeners: {
            click: function(btn) {
                chart_type=null;
                
                var st=enttype_combo1.getStore();
                var rec=st.getAt(enttype_combo1.selectedIndex);
                node_type=rec.get('entname');
                node_id=ent1_combo.getValue()

                if(compare.getValue()){
                    if(ent2_combo.getValue()=='' || ent1_combo.getValue()==''){
                        Ext.MessageBox.alert(_("Warning."),_('Select Entities for Comparison.'));
                        return false;
                    }
                    if(ent1_combo.getValue()==ent2_combo.getValue()){
                        Ext.MessageBox.alert(_("Warning."),_('Please select different Entities.'));
                        return false;
                    }
                    chart_type=convirt.constants.COMPARISONCHART;
                    node_id+="*"+ent2_combo.getValue();
                    
                    st=enttype_combo2.getStore();
                    rec=st.getAt(enttype_combo2.selectedIndex);
                    node_type+="*"+rec.get('entname');
                }else{
                    if(ent1_combo.getValue()==''){
                        Ext.MessageBox.alert(_("Warning."),_('Please select an Entity.'));
                        return false;
                    }
                }
//                alert(node_type+"--\n"+metric_combo.getValue()+"--"+node_id+"--"+node_name+"--"+
//                    period_combo.getValue()+"--\n"+fdate+"--"+tdate+"--"+chartid+"--"+false+"--\n"+chart_panel+"--"+chart_type);
                redrawChart(node_type,metric_combo1.getValue(),node_id,node_name,
                    period_combo.getValue(),fdate,tdate,chartid,false,chart_panel,chart_type);
                return true;
            }
        }
    }); 
    var compare=new Ext.form.Checkbox({
        fieldLabel: _('Compare'),
        listeners: {
            check: function(box) {
                if(compare.getValue()){
                    enttype_combo2.setDisabled(false);
                    ent2_combo.setDisabled(false);
                    //metric_combo2.setDisabled(false);
                }else{
                    enttype_combo2.setDisabled(true);
                    ent2_combo.setDisabled(true);
                    metric_combo2.setDisabled(true);
                }
            }
        }
    });

    var compare_lbl=new Ext.form.Label({
        html:"<b>"+_("Compare &nbsp;&nbsp;")+"</b>"
        ,width:75
    });


    var pnl1=new Ext.Panel({
        collapsible: false,
        anchor:'100% 8%',
        border:false,
        bodyStyle:'padding-bottom:0px;',
        labelSeparator:' ',
        layout:'column',
        items: [
//            {
//                width:"75%",
//                border:false,
//                labelAlign:'right',
//                layout:'form',
//                //labelWidth:30,
//                labelSeparator:' ',
//                items:[msg_lbl]
//            },
            {
                width:"25%",
                border:false,
                layout:'form',
                items:[enttype_combo1]
            }
            ,{
                width:"25%",
                border:false,
                layout:'form',
                items:[ent1_combo]
            }
            ,{
                width:"25%",
                border:false,
                layout:'form',
                items:[metric_combo1]
            }
            ,{
                width:"25%",
                border:false,
                layout:'form',
                items:[period_combo]
            }
        ]
    });

    var dummy_panel1 = new Ext.Panel({
        width:50,
        border:false,
        bodyBorder:false,
        items:[go_btn]
    });
    var dummy_panel0 = new Ext.Panel({
        width:100,
        border:false,
        bodyBorder:false,
        layout:'column',
        items:[compare_lbl,compare]
        //bodySttyle:'padding-left:15px;'
    });
    var pnl2=new Ext.Panel({
        collapsible: false,
        anchor:'100% 8%',
        border:false,
        bodyStyle:'padding-bottom:0px;',
        labelSeparator:' ',
        layout:'column',
        items: [
            {
                width:"25%",
                border:false,
                layout:'form',
                items:[enttype_combo2]
            }
            ,{
                width:"25%",
                border:false,
                layout:'form',
                items:[ent2_combo]
            }
            ,{
                width:"25%",
                border:false,
                layout:'form',
                items:[metric_combo2]
            }
            ,{
                width:"25%",
                border:false,
                layout:'column',
                items:[dummy_panel0,dummy_panel1]
            }
        ]
    });


    var chart_panel = new Ext.FormPanel({
        border:0,
        width:400,
        height:400,
        labelSeparator: ' ',
        labelAlign: 'right',
        bodyStyle:'padding:5px;',
        items:[pnl1,pnl2]
    });
    redrawChart(node_type,metric,node_id,node_name,period,frmdate,todate,chartid,false,chart_panel,chart_type);

    var window = new Ext.Window({
        //title:'Server Memory Usage',
        width: 650,
        height:400,
        modal:false,
        minWidth: 650,
        minHeight: 400,
        layout: 'fit',
        plain:true,
        //bodyStyle:'padding:5px;',
        items:[chart_panel]
    });

    window.show();
}

function drawChart(node_type,metric,node_id,node_name,period,frmdate,todate,
                    chartid,clickable,data_info,chart_type){
    var data_series=[],data=[];
    //var cpu_data=[],mem_data=[];
    var label='',avg=0.0;
    
    var time_format="%H:%M";
    
    data_series=[{data:data}];
    var prvdate=new Date();
    prvdate.setHours(prvdate.getHours()-1);
    var min=prvdate.getTime(),max=(new Date()).getTime(),minTick='hour',ymax=100,labelx="",labely="";
    //alert((new Date()).getTimezoneOffset());alert(new Date());
    var offsetmillis=((new Date()).getTimezoneOffset())*60*1000*(-1);

    if(data_info!=null){
        time_format=data_info.time_format;
        label=data_info.label;//alert((new Date(data_info.min))+"+++"+(new Date(data_info.max)))
        label=formatDate(new Date(data_info.min))+" - "+formatDate(new Date(data_info.max));
        
//        if(!data_info.show_avg){
//            var tgts=Ext.QuickTips.getQuickTip().targets;
//            for (var key in tgts) {
//                if (tgts.hasOwnProperty(key)) {
//                    if(tgts[key]!=null && (node_type==convirt.constants.MANAGED_NODE
//                    || node_type==convirt.constants.DOMAIN)){
//                        tgts[key].text='<b>Show Average</b><br/>'+label;
//                    }
//                }
//            }
//        }
        
        min=data_info.min+offsetmillis;
        max=data_info.max+offsetmillis;

        avg=data_info.avg;
        ymax=data_info.ymax;
        minTick=data_info.minTick;
        labelx=data_info.xlabel;
        labely=data_info.ylabel;
        //data_series=[ { data: data, label: label,color:1}];
        var series=data_info.series;
        var serie=new Array();
        
        for(var i=0;i<series.length;i++){
            var rows=series[i].data;
            data=new Array();
            for(var j=0;j<rows.length;j++){
                //alert(rows[j].metric+"---"+rows[j].millis);
                data.push([rows[j].millis+offsetmillis,rows[j].metric]);
            }
            data_series=[];
            serie.push({data:data,label:series[i].label,color:i});

        }
        //alert(serie.length);
        if(serie.length>0)
            data_series=serie;
    }


    var avg_color=(avg!=0.0)?"#FF0000":"#FFFFFF";
    var ch1={
        xtype: 'flot',
        id:chartid,
        anchor:'100% 85%',
//        threshold: {
//            above: 2,
//            color: "#FFFFFF"
//        },
        grid: {
            backgroundColor: { colors: ["#000", "#999"] }
            ,markings: [ { yaxis: { from: avg, to: avg },color:avg_color } ]
        },//,timeformat: "%d:%H:%M:%s"
        xaxis: { mode: 'time',timeformat: time_format,min:min,max:max,minTickSize: minTick },
        yaxis: { min: 0,max: ymax,ticks:4  },
        legend: { position: 'ne',
            labelFormatter: function(label, series) {
                // series is the series object for the label
                return '<span style="font-size:11px;">' + label + '</span>';
            }
        },
        series: data_series
        ,listeners:{
            render:function(me){
                if(clickable){
                    me.on('plotclick',function(p,evt,pos,item){
                        showChart(node_type,metric,node_id,node_name,period,frmdate,todate,chartid,chart_type);
                    });
                }
            }
        }
    };
    var ylabel=new Ext.form.Label({
        width:"100%",
        html:'<span style="width:100%;font-style:bold;font-size:10px;">'
                    +labely+'</span>'
    });
    var xlabel=new Ext.form.Label({
        width:"100%",
        html:'<span style="padding-left:80%;width:100%;font-style:bold;font-size:10px;align:right;">'
                    +labelx+'</span>'
    });
    ht=180
    if (node_type===convirt.constants.MANAGED_NODE){
       ht = 210
    }
    var chpanel=new Ext.Panel({
        width:'100%',
        height: ht,
        border:false,
        bodyBorder:false,
        layout:'fit'
    });

    if(clickable){
        //chpanel.add(label1_1);
        chpanel.add(ch1);
        return [[ylabel,chpanel,xlabel],label];
    }else{
        return [[ch1],label];
    }
}

function redrawChart(node_type,metric,node_id,node_name,period,frmdate,todate,
                    chartid,clickable,prntPanel,chart_type,avg_fdate,avg_tdate){
    
    if(period===convirt.constants.CUSTOM){        
        if(frmdate == null || todate==null ||
            frmdate == "" || todate==""){
            Ext.MessageBox.alert(_("Warning"),_("From and To should be selected for the Custom Period."))
            return;
        }
    }else if(period===convirt.constants.DTD){
        todate=(new Date()).getTime();        
    }
    
    var url="/dashboard/get_chart_data?metric="+metric+"&node_id="+node_id+
        "&node_type="+node_type+""+"&period="+period+"&frmdate="+frmdate+"&todate="+todate;
    var offsetmillis=parseInt((new Date()).getTimezoneOffset())*60*1000*(-1);
    url+="&offset="+offsetmillis;
    if(chart_type!=null){
        url+="&chart_type="+chart_type;
    }
    if(avg_fdate!=null && avg_fdate!=""){
        url+="&avg_fdate="+avg_fdate+"&avg_tdate="+avg_tdate;
    }//alert(url);
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            //alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            var cmps=drawChart(node_type,metric,node_id,node_name,period,
                                frmdate,todate,chartid,clickable,response.info,chart_type);
            
            if(clickable){
                if(prntPanel.items){
                    prntPanel.removeAll();
                }
                for (var x=0;x<cmps[0].length;x++){
                    prntPanel.add(cmps[0][x]);
                }
                prntPanel.doLayout();
            }else{
                prntPanel.remove(chartid);
                for (var x=0;x<cmps[0].length;x++){
                    prntPanel.add(cmps[0][x]);
                }
                prntPanel.doLayout();
            }
            var tlbar=prntPanel.getTopToolbar();

            if(tlbar !=null && cmps.length==2){
                var txtitem=tlbar.items.itemAt(2);

//                for (var key in txtitem) {
//                  if (txtitem.hasOwnProperty(key)) {
//                    alert(key + " -> " + txtitem[key]);
//                  }
//                }
                if(txtitem!=null){
                    if (txtitem.hasOwnProperty("destroy")) {
                        txtitem.destroy();
                    }
                }
                var label=cmps[1];//alert(label);
                var period_item=new Ext.Toolbar.TextItem({
                    id:"period_label",
                    //html:'<div class="toolbar_hdg">'+label+'</div>'
                    text:"   ("+label+")"
                });
                tlbar.insertButton(2,period_item);
            }
            

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

CustomPeriodUI=function(title,fdate,tdate,period){
    var frm_lbl=new Ext.form.Label({
        html:_('From')+"&nbsp;"
    });
    var date1="",date2="";
    if(fdate != null && fdate != ""){
        date1=new Date(fdate);
        date2=new Date(tdate);
    }else if (period != null && period != ""){
        date2=new Date();
        date1=getPeriodStartDate(period);
    }
    var time1=((date1.getHours()<10)?"0":"")+date1.getHours()+":"+
        ((date1.getMinutes()<10)?"0":"")+date1.getMinutes();
    var time2=((date2.getHours()<10)?"0":"")+date2.getHours()+":"+
        ((date2.getMinutes()<10)?"0":"")+date2.getMinutes();
    //alert(time1+"--"+time2);
    var frmdate=new Ext.form.DateField({
        width:100,
        value:date1,
        fieldLabel: _('From')
        ,listeners:{
            select:function(field,val){
                todate.setMinValue(val);
                if(todate.getValue()!='' && todate.getValue()<val){
                    todate.setValue('');
                }
            }
        }
    });
    var frmtime=new Ext.form.TimeField({
        width:70,
        format:'H:i',
        value:time1,
        anchor:'30%'
    });

    var to_lbl=new Ext.form.Label({
        html:_('To')+"&nbsp;"
    });
    var todate=new Ext.form.DateField({
        width:100,
        value:date2,
        fieldLabel: _('To')
    });

    var totime=new Ext.form.TimeField({
        width:70,
        format:'H:i',
        value:time2
    });

    var custom_fldset=new Ext.form.FieldSet({
        collapsible: false,
        anchor:'100%',
        //labelWidth:30,
        labelAlign:'right',
        labelSeparator:' ',
        layout:'table',
        layoutConfig: {columns:3},
        items: [frm_lbl,frmdate,frmtime,to_lbl,todate,totime]
    });

    var cncl_btn=new Ext.Button({
        text: _('Cancel'),
        listeners: {
            click: function(btn) {
                window.hide();
            }
        }
    });
    if(title == null){
        title=_("Select Custom Period");
    }
    var window = new Ext.Window({
        title:title,
        width: 250,
        height:150,
        minWidth: 250,
        minHeight: 150,
        resizable:false,
        layout: 'fit',
        plain:true,
        modal:true,
        closable:false,
        bodyStyle:'padding:5px;',
        buttonAlign:'center',
        items: custom_fldset
        ,buttons:[cncl_btn]
    });
    this.getWindow=function(){
        return window;
    };
    this.fromDate=function(){
        return frmdate.getValue();
    };
    this.toDate=function(){
        return todate.getValue();
    };
    this.xyz=function(){
        return frmtime.getValue();
    };
    this.fromTime=function(){        
        return frmdate.getValue().getTime()+
                this.convertToMillis(frmtime.getValue());
    };
    this.toTime=function(){
        return todate.getValue().getTime()+
                this.convertToMillis(totime.getValue());
    };
    this.fromValue=function(){
        return frmdate.getValue();
    };
    this.toValue=function(){
        return todate.getValue();
    };
    this.validate=function(){        
        if(!frmtime.validate()){
            Ext.MessageBox.alert(_("Warning."),_('Please correct the From Time.'));
            return false;
        }
        if(!totime.validate()){
            Ext.MessageBox.alert(_("Warning."),_('Please correct the To Time.'));
            return false;
        }
        if(this.fromValue()==''||this.fromValue()==null){
            Ext.MessageBox.alert(_("Warning."),_('From Date can not be empty.'));
            return false;
        }
        if(this.toValue()==''||this.toValue()==null){
            Ext.MessageBox.alert(_("Warning."),_('To Date can not be empty.'));
            return false;
        }
        if(this.fromTime()==this.toTime()){
            Ext.MessageBox.alert(_("Warning."),_('From and To can not be same.'));
            return false;
        }
        if(this.fromTime()>this.toTime()){
            Ext.MessageBox.alert(_("Warning."),_('From can not be greater than To.'));
            return false;
        }
        if((this.toTime()-this.fromTime())<(1*60*60*1000)){
            Ext.MessageBox.alert(_("Warning."),_('Difference between From and To can not be less than 1 Hour.'));
            return false;
        }
        return true;
    };
    this.convertToMillis=function(time){ 
        var ts=time.split(":");
        ts[0]=ts[0].toString();
        //workaround for parseInt(08 or 09) returning 0
        if(ts[0].substr(0,1)==='0'){
            ts[0]=ts[0].substr(1,2)
        }
        if(ts[1].substr(0,1)==='0'){
            ts[1]=ts[1].substr(1,2)
        } 
        var hr=parseInt(ts[0]);
        var min=parseInt(ts[1]);
        var millis=hr*60*60*1000+min*60*1000;
        return millis;
    };
}

function getMetricCombo(label,width,val,lblwdth,ctCls){
    var lbl='';
    var wdth=100,lblwidth=100;;
    var value=convirt.constants.CPU;
    if(label!=null)
        lbl=label;
    if(width!=null)
        wdth=width;
    if(val!=null)
        value=val
    if(lblwdth!=null)
        lblwidth=lblwdth;
    var combo=new Ext.form.ComboBox({
        //anchor:'90%',
        width:wdth,
        minListWidth: 50,
        fieldLabel:lbl,
        allowBlank:false,
        triggerAction:'all',
        ctCls:ctCls,
        labelStyle: 'width:'+lblwidth+'px;',
        store:[[convirt.constants.CPU,_('CPU')],[convirt.constants.MEM,_('Memory')]],
        forceSelection: true,
        mode:'local',
        value:value
    });
    return combo;
}

function getPeriodCombo(label,width,val,lblwdth,ctCls){
    var lbl=_("");
    var wdth=120,lblwidth=100;
    var value=convirt.constants.HRS12;
    if(label!=null)
        lbl=label;
    if(width!=null)
        wdth=width;
    if(val!=null)
        value=val
    if(lblwdth!=null)
        lblwidth=lblwdth;
    var combo=new Ext.form.ComboBox({
        //anchor:'90%',
        width:wdth,
        minListWidth: 90,
        fieldLabel:lbl,
        allowBlank:false,
        triggerAction:'all',
        ctCls:ctCls,
        labelStyle: 'width:'+lblwidth+'px;',
        store:[[convirt.constants.HRS12,_('Last 12 Hours')],
                [convirt.constants.DTD,_('Today')],
                [convirt.constants.HRS24,_('Last 24 Hours')],
                [convirt.constants.DAYS7,_('Last 7 Days')],
                [convirt.constants.DAYS30,_('Last 30 Days')],
                [convirt.constants.WTD,_('Week To Date')],
                [convirt.constants.MTD,_('Month To Date')],
                [convirt.constants.CUSTOM,_('Custom')]],
        forceSelection: true,
        mode:'local',
        value:value
    });

    return combo;
}

function formatDate(date){
    if(date == null || date== ""){
        return "";
    }
    return date.getFullYear()+"/"+
         ((date.getMonth()<9)?"0":"")+(date.getMonth()+1)+"/"+
         ((date.getDate()<9)?"0":"")+(date.getDate())+" "+
         ((date.getHours()<9)?"0":"")+(date.getHours())+":"+
         ((date.getMinutes()<9)?"0":"")+(date.getMinutes());
}


function getTop5Info(){
    var info_button=new Ext.Button({
        icon: '/icons/information.png',
        cls: 'x-btn-icon',
        tooltip: {
            text:'Top 5 Servers are calculated based on the last hour data.'+
                ' Historical data is shown for these servers.'
        }
    });
    return info_button;
}
 
function getPeriodStartDate(period,enddate){
    var startdate=new Date();
    if(enddate != null && enddate != ""){
        startdate=enddate;
    }
    //alert(period);
    if(period===convirt.constants.HRS12){
        startdate.setHours(startdate.getHours()-12);
    }else if(period===convirt.constants.HRS24){
        startdate.setHours(startdate.getHours()-24);
    }else if(period===convirt.constants.DAYS7){
        startdate.setDate(startdate.getDate()-7);
    }else if(period===convirt.constants.DAYS30){
        startdate.setDate(startdate.getDate()-30);
    }else if(period===convirt.constants.DTD){
        startdate.setHours(0);
        startdate.setMinutes(0);
    }else if(period===convirt.constants.WTD){
        startdate.setDate(startdate.getDate()-startdate.getDay());
        startdate.setHours(0);
        startdate.setMinutes(0);
    }else if(period===convirt.constants.MTD){
        startdate.setDate(1);
        startdate.setHours(0);
        startdate.setMinutes(0);
    }
    //alert(enddate+"--"+startdate);
    return startdate;
}
