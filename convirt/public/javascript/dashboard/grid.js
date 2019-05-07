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
////Associative arrays for the mapping between summary table headers and response XML attributes.
//for server pool
var srvrpool_hdr_attr=new Array();
srvrpool_hdr_attr[_('Server Pools')]='NODE_NAME';
srvrpool_hdr_attr[_('Servers')]='NODE_NAME';
srvrpool_hdr_attr[_('Server CPU(s)')]='SERVER_CPUs';
srvrpool_hdr_attr[_('Server Mem')]='SERVER_MEM';
srvrpool_hdr_attr[_('Version')]='VER';
srvrpool_hdr_attr[_('VM CPU(%)')]='VM_TOTAL_CPU_PERCENT';
srvrpool_hdr_attr[_('VM Mem(%)')]='VM_TOTAL_MEM_PERCENT';
srvrpool_hdr_attr[_('Status')]='NODE_STATUS';
srvrpool_hdr_attr[_('Storage(GB)')]='VM_SHARED_STORAGE*POOL_STORAGE_TOTAL';
srvrpool_hdr_attr[_('Network')]='VM_TOTAL_NETS*VM_TOTAL_NETRX_k*VM_TOTAL_NETTX_k';
srvrpool_hdr_attr[_('I/O')]='VM_TOTAL_VBDS*VM_TOTAL_VBD_OO*VM_TOTAL_VBD_RD*VM_TOTAL_VBD_WR';
srvrpool_hdr_attr[_('VM Summary')]='TOTAL_VMs*RUNNING_VMs*PAUSED_VMs*CRASHED_VMs';
srvrpool_hdr_attr[_('status')]='NODE_STATUS';
srvrpool_hdr_attr[_('NodeID')]='NODE_ID';
//for managed node
var srvr_hdr_attr=new Array();
srvr_hdr_attr[_('Id')]='PID';
srvr_hdr_attr[_('Virtual Machines')]='NAME';
srvr_hdr_attr[_('State')]='STATE';
srvr_hdr_attr[_('CPU(%)')]='CPU_PERCENT';
srvr_hdr_attr[_('Mem(%)')]='MEM_PERCENT';
srvr_hdr_attr[_('Storage(GB)')]='VM_LOCAL_STORAGE*VM_SHARED_STORAGE*POOL_STORAGE_TOTAL';
srvr_hdr_attr[_('Network')]='NETS*NETRX_k*NETTX_k';
srvr_hdr_attr[_('I/O')]='VBDS*VBD_OO*VBD_RD*VBD_WR';
srvr_hdr_attr[_('NodeID')]='NODE_ID';

var srvr_pool_colModel = new Ext.grid.ColumnModel([
    {header: _("NodeID"), dataIndex: 'node_id', hidden:true},
    {header: _("Name"), width: 220, sortable: true, dataIndex: 'name'},
    {header: _("VM Summary"), width: 120, sortable: true, dataIndex: 'vm summary',tooltip:'Total/Running/Paused/Crashed'},
    {header: _("VM CPU(%)"), width: 120, sortable: true, dataIndex: 'vm cpu(%)',renderer:showBar},
    {header: _("VM Mem(%)"), width: 120, sortable: true, dataIndex: 'vm mem(%)',renderer:showBar},
//    {header: _("Storage(GB)"), width: 120, sortable: true, dataIndex: 'storage(gb)',tooltip:'Pool Used/Pool Total'},
    {header: _("Network"), width: 120, sortable: true, dataIndex: 'network',tooltip:'Total/Rx/Tx'},
    {header: _("I/O"), width: 120, sortable: true, dataIndex: 'i/o',tooltip:'Total/OO/RD/WR'}
//    {header: _("Server CPU(s)"), width: 100, sortable: true, dataIndex: 'server cpu(s)'},
//    {header: _("Server Mem"), width: 100, sortable: true, dataIndex: 'server mem'},
//    {header: _("Version"), width: 120, sortable: true, dataIndex: 'version'}
    //,{header: _("NodeID"), dataIndex: 'node_id', hidden:true}
]);

var srvr_colModel = new Ext.grid.ColumnModel([
    {header: _("Id"), width: 35, sortable: true, dataIndex: 'id'},
    {header: _("Name"), width: 140, sortable: true, dataIndex: 'name'},
    {header: _("State"), width: 120, sortable: true, dataIndex: 'state',renderer:function(value,params,record){
            return value;
        }
    },
    {header: _("CPU(%)"), width: 120, sortable: true, dataIndex: 'cpu(%)',renderer:showBar},
    {header: _("Mem(%)"), width: 120, sortable: true, dataIndex: 'mem(%)',renderer:showBar},
    {header: _("Storage(GB)"), width: 100, sortable: true, dataIndex: 'storage(gb)',
        renderer:formatValue,tooltip:'Local/Pool Used/Pool Total'},
    {header: _("Network"), width: 100, sortable: true, dataIndex: 'network',tooltip:'Total/Rx/Tx'},
    {header: _("I/O"), width: 100, sortable: true, dataIndex: 'i/o',tooltip:'Total/OO/RD/WR'}
    ,{header: _("NodeID"), dataIndex: 'node_id',hidden:true}
]);

var srvr_pool_info_colModel = new Ext.grid.ColumnModel([
    {header: _("Status"), width: 40, sortable: true, dataIndex: 'status',renderer:showStatus},
    {header: _("Servers"), width: 140, sortable: true, dataIndex: 'name'},
    {header: _("Server CPU(s)"), width: 120, sortable: true, dataIndex: 'server cpu(s)'},
    {header: _("Server Mem"), width: 100, sortable: true, dataIndex: 'server mem'},
    {header: _("Storage(GB)"), width: 120, sortable: true, dataIndex: 'storage(gb)',
        renderer:formatValue,tooltip:'Pool Used/Pool Total'},
    {header: _("Version"), width: 120, sortable: true, dataIndex: 'version'}
    ,{header: _("NodeID"), dataIndex: 'node_id',hidden:true}
 ]);

 var data_center_info_colModel = new Ext.grid.ColumnModel([
    {header: _("Server Pools"), width: 140, sortable: true, dataIndex: 'name'},
    {header: _("Server CPU(s)"), width: 120, sortable: true, dataIndex: 'server cpu(s)'},
    {header: _("Server Mem"), width: 100, sortable: true, dataIndex: 'server mem'},
    {header: _("Storage(GB)"), width: 120, sortable: true, dataIndex: 'storage(gb)',
        renderer:formatValue,tooltip:'Pool Used/Pool Total'}
    ,{header: _("NodeID"), dataIndex: 'node_id',hidden:true}
 ]);

function drawsummaryGrid(nodelist,type,nodeid,listviews,prntPanel){

	var dataObj=new Array(),fields=new Array();
    var lbl_msg='';
    var columnModel,map=new Array();
    if(type==convirt.constants.DATA_CENTER){
        columnModel=srvr_pool_colModel;
        columnModel.setColumnHeader(1,_('Server Pools'));
        lbl_msg=_('Server Pool Information');
        map=srvrpool_hdr_attr;
    }else if(type==convirt.constants.SERVER_POOL){
        columnModel=srvr_pool_colModel;
        columnModel.setColumnHeader(1,_('Servers'));
        map=srvrpool_hdr_attr;
        lbl_msg=_('Server Information');
    }else if(type==convirt.constants.MANAGED_NODE){
        columnModel=srvr_colModel;
        map=srvr_hdr_attr;
        lbl_msg=_('Virtual Machine Information');
    }
	//var children=node.childNodes;
    var obj=load_data_store(nodelist,columnModel,map);
    dataObj=obj[0];
    fields=obj[1];

	var store = new Ext.data.SimpleStore({
        fields:fields,
        sortInfo:{
            dir:'ASC',
            field:'name'
        }
        ,listeners:{
            load:function(obj,recs,opts){
                insert_dummyrecs(obj);
            }
        }
    });
    store.loadData(dataObj);
    var tb_lbl=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+lbl_msg+'</div>'
    });

    var srvr_list_btn=new Ext.Button({
        tooltip:'Server List',
        tooltipType : "title",
        icon:'icons/server_list.png',
        cls:'x-btn-icon',
        hidden:(type!=convirt.constants.DATA_CENTER),
        listeners: {
            click: function(btn) {
                prntPanel.getEl().mask("Loading ...");
                var g=showServerList(nodeid,type,prntPanel);
                prntPanel.remove(grid.getId());
                prntPanel.add(g);
                prntPanel.doLayout();
            }
        }
    });

    var vm_list_btn=new Ext.Button({
        tooltip:'VM List',
        tooltipType : "title",
        icon:'icons/vm_list.png',
        cls:'x-btn-icon',
        hidden:(type==convirt.constants.MANAGED_NODE),
        listeners: {
            click: function(btn) {   
                prntPanel.getEl().mask("Loading ...");
                var g=showVMList(nodeid,type,prntPanel);
                prntPanel.remove(grid.getId());
                prntPanel.add(g);
                prntPanel.doLayout();
            }
        }
    });

    var items=new Array();
    items.push(tb_lbl);
//    items.push({xtype:'tbfill'});
//    if(listviews===true){
//        if(type==convirt.constants.DATA_CENTER){
//            items.push('|');
//            items.push(srvr_list_btn);
//        }
//        if(type!=convirt.constants.MANAGED_NODE){
//            items.push('|');
//            items.push(vm_list_btn);
//        }
//    }
    items.push({xtype:'tbfill'});
    items.push(_('Search: '));
    items.push(new Ext.form.TextField({
        //fieldLabel: _('Search'),
        name: 'search',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));
    var toolbar = new Ext.Toolbar({
        items: items
    });
	var grid = new Ext.grid.GridPanel({
        store: store,
        //title:'Performance Details',
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        //id:'summary_grid',
        width:'80%',
        autoExpandColumn:1,
        autoExpandMax:300,
//        autoHeight:true,
        maxHeight:120,
        height:150,
        tbar:toolbar
        ,listeners:{
            rowcontextmenu: function(grid,rowIndex,e){
                e.preventDefault();
                handleGridEvent(grid,rowIndex,e,'contextmenu');
            }
            ,rowdblclick: function(grid,rowIndex,e) {
                handleGridEvent(grid,rowIndex,e,'click');
            }
        }
    });

	return grid;
}

function drawinfoGrid(nodelist,type){

	var dataObj=new Array(),fields=new Array();

    var columnModel,map=new Array();
    if(type==convirt.constants.DATA_CENTER){
        columnModel=data_center_info_colModel;
        map=srvrpool_hdr_attr;
    }else if(type==convirt.constants.SERVER_POOL){
        columnModel=srvr_pool_info_colModel;
        map=srvrpool_hdr_attr;
    }

	//var children=node.childNodes;
    var obj=load_data_store(nodelist,columnModel,map);
    dataObj=obj[0];
    fields=obj[1];

	var store = new Ext.data.SimpleStore({
        fields:fields,
        sortInfo:{
            dir:'ASC',
            field:'name'
        }
    });
    store.loadData(dataObj);

	var grid = new Ext.grid.GridPanel({        
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:true,
        width:'100%',
        id:'information_grid',
        //autoExpandColumn:1,
        height:600,
        tbar:[_('Search: '),new Ext.form.TextField({
            fieldLabel: _('Search'),
            name: 'search',
            id: 'search_info',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    grid.getStore().filter('name', field.getValue(), false, false);
                }
            }
        })]
        ,listeners:{
            rowcontextmenu: function(grid,rowIndex,e){
                e.preventDefault();
                handleGridEvent(grid,rowIndex,e,'contextmenu')
            }
            ,rowdblclick: function(grid,rowIndex,e) {
                handleGridEvent(grid,rowIndex,e,'click')
            }
        }
    });

	return grid;
}

function load_data_store(nodelist,colModel,map){
    var len=colModel.getColumnCount();
    var obj=new Array(),dataobj=new Array(),fields=new Array();
    var count=0;
    for(var i=0;i<nodelist.length;i++){
        if(nodelist[i].DISPLAY!=0){
            dataobj[count]=new Array();
            for(var j=0;j<len;j++){
                var attrs=map[colModel.getColumnHeader(j)].split('*');
                var data="";
                for(var k=0;k<attrs.length;k++){                    
                    var n=eval("nodelist[i]."+attrs[k]);//alert(n);
                    data+=((k==0)?"":"/")+((n!=null)?n:"?");                    
                }
                dataobj[count][j]=data;                
            }
            count++;
        }
    }
    for(var j=0;j<len;j++){
        fields[j]={name: colModel.getDataIndex(j)};
    }
    obj[0]=dataobj;
    obj[1]=fields;
    return obj;
}

function roundNumber(value, meta, rec){
    var result;
    if (value=="" ||value ==0 || value==null){
            result=0;
     }else{
            result=Math.round(value*100)/100;
     }
     result=result.toFixed (2);
     return "<div align=right>"+result+"</div>";
}

function progressbar(value, meta, rec){
    var result;
     if (value=="" ||value ==0 || value==null){
            result=0;
     }else{
            result=Math.round(value*100)/100;
     }
     result=result.toFixed (2);
     var width=60;
     var inwidth=width*(result/100);
     var progessbar="<div style='border-style: solid;\n\
     border-color: gray;border-width: 1px; width:"+width+"px; height:14px;'>\n\
     <img src='images/blue_bar.jpg' width="+inwidth+"px height=14px/></div>\n\
     <div style='text-align:center;position:relative;margin-bottom:-15px;top:-15px;\n\
     width:"+width+"px;'/>"+result+"</div>";
     return progessbar;
}

function showServerStatus(value){
    if (value==true){
        return "<img width='13px' title='Connected' height='13px' src='../icons/small_connect.png'/>";
    }else{
        return "<img width='13px' title='Not Connected' height='13px' src='../icons/small_disconnect.png'/>";
    }
}

function showBar(value, meta, rec){
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
    if(value==undefined)
        return "?" ;
    else
        return '<span id="' + id + '"></span>';
}

function getVMState(value, meta, rec){
    //alert(value);
    var state="Unknown";
    if(value===convirt.constants.RUNNING){
        state='Running';
    }else if(value===convirt.constants.BLOCKED){
        state='Blocked';
    }else if(value===convirt.constants.PAUSED){
        state='Paused';
    }else if(value===convirt.constants.SHUTDOWN){
        state='Shutdown';
    }else if(value===convirt.constants.CRASHED){
        state='Crashed';
    }else if(value===convirt.constants.NOT_STARTED){
        state='Not Started';
    }else if(value===convirt.constants.UNKNOWN){
        state='Unknown';
    }else{
        state='Unknown';
    }
    return state;
}

function formatValue(value, meta, rec){
    if(value!=undefined){
        if(value.indexOf('/')>-1){
            var values=value.split('/');
            value="";
            for (var i=0;i<values.length;i++){
                var tmp=values[i];
                if(tmp.indexOf('.')>-1){
                    tmp=tmp.split('.')[0]+"."+Ext.util.Format.substr(tmp.split('.')[1],0,2);
                }
                value+=(i==0?"":"/")+tmp;
            }
        }else{
            value=Ext.util.Format.substr(value,0,4);
        }
        return value
    }else
        return '';
}

function showStatus(value, meta, rec){
    var icon="/icons/small_disconnect.png";
    if(value=='Connected'){
        icon="/icons/small_connect_blue.png"
    }
    return '<img height="20px" src="' + icon + '"/>';
}

function handleGridEvent(grid,rowIndex,e,evt){
    //get the node corresponding to the selected row object and fire the event on that node
    var rec=grid.getStore().getAt(rowIndex);
    grid.getSelectionModel().clearSelections();
    grid.getSelectionModel().selectRow(rowIndex,false);
    //node id should be unique, now using name as id.
    var node=leftnav_treePanel.getNodeById(rec.get('node_id'));
    if(node)
        node.fireEvent(evt,node,e);
}

function showVMList(node_id,type,prntPanel){
    var s_hidden=(type===convirt.constants.MANAGED_NODE);
    var vms_colModel = new Ext.grid.ColumnModel([
        {header: _("Id"), width: 22, sortable: true, hidden: true, dataIndex: 'id'},
        {header: _("Name"), width: 160, sortable: true, dataIndex: 'name'},
        {header: _("Server"), width: 100, sortable: true, dataIndex: 'server',hidden:s_hidden},
        {header: _("State"), width: 80, sortable: true, dataIndex: 'state',renderer:getVMState},
        {header: _("CPU(%)"), width: 70, sortable: true, dataIndex: 'cpu',renderer:progressbar},
        {header: _("Mem(%)"), width: 70, sortable: true, dataIndex: 'mem',renderer:progressbar},
        {header: _("Storage(GB)"), width: 100, sortable: true, dataIndex: 'storage',renderer:formatValue,tooltip:'Local/Pool Used'},
        {header: _("Network"), width: 80, sortable: true, hidden: true, dataIndex: 'network',tooltip:'Total/Rx/Tx'},
        {header: _("I/O"), width: 80, sortable: true, hidden: true, dataIndex: 'io',tooltip:'Total/OO/RD/WR'},
        {header: _("Guest OS"), width: 125, sortable: true, dataIndex: 'os'},
        {header: _("Template"), width: 130, sortable: true, dataIndex: 'template'},
        {header: _("Template Version"), width: 100, sortable: true, dataIndex: 'template_version'},
        {header: _("Comments"), width: 150, sortable: true, dataIndex: 'template_updates'},
        {header: _("NodeID"), dataIndex: 'node_id',hidden:true}
    ]);


    var items=new Array();   
    
    var vm_query_store = new Ext.data.JsonStore({
        url:"/dashboard/get_canned_custom_list?node_level="+type+"&lists_level="+convirt.constants.VMS,
        root: 'info',
        successProperty:'success',
        fields:['value'],
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }        
    });
    vm_query_store.load();  

     var tb_lbl=new Ext.form.Label({
        html:getHdrMsg("The table shows top 50 Virtual Machines by current CPU Utilization(%)")
    });


    var vmquery_combo=new Ext.form.ComboBox({
        id: 'vm_id',
        fieldLabel: _('Query name'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("Select Type"),
        store: vm_query_store,
        width:220,
        displayField:'value',
        valueField:'value',
        editable:false,
        typeAhead: true,
        minListWidth:50,
        mode:'local',
        tpl: '<tpl for="."><div class="x-combo-list-item">{value}</div><tpl if="xindex == 4"><hr /></tpl></tpl>',
        forceSelection: true,
        selectOnFocus:true,
        listeners:{
            select:function(combo,record,index){
                if (combo.getValue()==convirt.constants.TOP50BYCPUVM){
                    tb_lbl.setText(getHdrMsg("The table shows top 50 Virtual Machines by current CPU Utilization(%)."),false);
                }
                else if(combo.getValue()==convirt.constants.TOP50BYMEMVM){

                    tb_lbl.setText(getHdrMsg("The table shows top 50 Virtual Machines by current Memory Utilization(%)."),false);
                }
                else if(combo.getValue()==convirt.constants.DOWNVM){

                    tb_lbl.setText(getHdrMsg("The table shows top 50 Down Virtual Machines"),false);

                }
                else if(combo.getValue()==convirt.constants.RUNNINGVM){

                    tb_lbl.setText(getHdrMsg("The table shows top 50 Running Virtual Machines"),false);

                }
                else{
                    
                    var url="/dashboard/get_custom_search?name="+combo.getValue()+"&lists_level="+convirt.constants.VMS;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){                                    
                                    var info=response.info;                                   
                                    tb_lbl.setText(getHdrMsg("List of Top "+info.max_count+" Virtual Machines with condition : "+combo.getValue()),false);
                                }else{
//                                    Ext.MessageBox.alert(_("Failure"),response.msg);
                                }
                            },
                            failure: function(xhr){
//                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                            }
                        });  
                }              
               
                vms_list_store.load({
                    params:{
                        canned:combo.getValue()
                    }
                });
            }
        }
        
    });


    var custom_btn=new Ext.Button({
        tooltip:'Custom Search',
        tooltipType : "title",
        icon:'icons/add_search.png',
        id: 'add',
        height:120,
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                CustomSearchDefList(type,node_id,convirt.constants.VMS,vm_query_store);
//                showWindow(_("Custom Search")+":- ",530,450,CustomSearchDefList(type,node_id,convirt.constants.VMS,vm_query_store),null,false,false);
            }
        }
    });   

   

    items.push(tb_lbl);
    items.push({xtype:'tbfill'});
    items.push(_('Search: '));
    items.push(new Ext.form.TextField({
        //fieldLabel: _('Search'),
        name: 'search',
        //id: 'search_summary',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));

    items.push(vmquery_combo);
    items.push(custom_btn);
    
    var toolbar = new Ext.Toolbar({
        items: items
    });


    var vms_list_store = new Ext.data.JsonStore({
        url:"/dashboard/dashboard_vm_info?node_id="+node_id+"&type="+type,
        root: 'info',
        successProperty:'success',
        fields:['id','name','server','state','cpu','mem','storage','network','template','os','io','node_id','template_version','template_updates'],
        listeners:{
            beforeload:function(obj,recs,opts){
                if(prntPanel.getEl()){
                    prntPanel.getEl().mask();
                }  
            },
            load:function(obj,recs,opts){
               //insert_dummyrecs(obj);
               prntPanel.getEl().unmask();
            },
            loadexception:function(obj,opts,res,e){
                prntPanel.getEl().unmask();
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vms_list_store.load();

    var grid = new Ext.grid.GridPanel({
//        title:'Performance Details',
        store: vms_list_store,
        colModel:vms_colModel,
        stripeRows: true,
        frame:false,
        //id:'summary_grid',
        width:820,
        autoExpandColumn:1,
//        autoHeight:true,
        autoExpandMax:300,
        autoExpandMin:150,
        height:150,
        maxHeight:100,
        enableHdMenu:true,
        tbar:toolbar
       ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick :function(grid,rowIndex,e) {
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });

//    var window = new Ext.Window({
//        //title:'VM Information',
//        width: 820,
//        height:250,
//        modal:true,
//        layout: 'fit',
//        plain:true,
//        items:[grid]
//    });
//    window.show();

    return grid;
}

function showServerList(node_id,type,prntPanel){
    var sp_hidden=(type===convirt.constants.SERVER_POOL);
    var srvrs_colModel = new Ext.grid.ColumnModel([
        {header: _("NodeID"), dataIndex: 'node_id', hidden:true},
        {header: _(""), width: 25, sortable: false, dataIndex: 'status',renderer:showServerStatus},
        {header: _("Name"), width: 160, sortable: true, dataIndex: 'name'},
        {header: _("Server Pool"), width: 100, sortable: true, dataIndex: 'serverpool',hidden:sp_hidden},
        {header: _("Virtual Machine Summary"), width:150, sortable: true, dataIndex: 'vmsummary',tooltip:'Total/Running/Paused/Crashed'},
        {header: _("Host CPU(%)"), width: 80, sortable: true, dataIndex: 'cpu',renderer:progressbar},
        {header: _("Host Memory(%)"), width: 100, sortable: true, dataIndex: 'mem',renderer:progressbar},
        {header: _("Storage(%)"), width: 70, sortable: true, dataIndex: 'storage',renderer:progressbar,tooltip:'Pool Used/Pool Total'},
        {header: _("Network"), width: 80, sortable: true, hidden: true, dataIndex: 'network',tooltip:'Total/Rx/Tx'},
        {header: _("I/O"), width: 80, sortable: true, hidden: true, dataIndex: 'io',tooltip:'Total/OO/RD/WR'},
        {header: _("Host OS"), width: 125, sortable: true, dataIndex: 'os'},
        {header: _("Platform"), width: 120, sortable: true, dataIndex: 'platform'} 
    ]);
 
    var items=new Array();
    var query_store = new Ext.data.JsonStore({
        url:"/dashboard/get_canned_custom_list?node_level="+type+"&lists_level="+convirt.constants.SERVERS,
        root: 'info',
        successProperty:'success',
        fields:['value'],
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    query_store.load();

     var tb_lbl=new Ext.form.Label({
        html:getHdrMsg("The table shows top 50 Servers by current CPU Utilization(%)")
    });

    var server_query_combo=new Ext.form.ComboBox({
        id: 'server_id',
        fieldLabel: _('Query name'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("Select Type"),
        store: query_store,
        width:220,
        displayField:'value',
        editable:false,
        valueField:'value',
        typeAhead: true,
        minListWidth:50,
        mode:'local',
        tpl: '<tpl for="."><div class="x-combo-list-item">{value}</div><tpl if="xindex == 3"><hr /></tpl></tpl>',
        forceSelection: true,
        selectOnFocus:true,
        listeners:{
            select:function(combo,record,index){
               
                if (combo.getValue()==convirt.constants.TOP50BYCPU){                     
                    tb_lbl.setText(getHdrMsg("The table shows top 50 Servers by current CPU Utilization(%)"),false);
                }
                else if(combo.getValue()==convirt.constants.TOP50BYMEM){

                    tb_lbl.setText(getHdrMsg("The table shows top 50 Servers by current Memory Utilization(%)"),false);
                }
                else if(combo.getValue()==convirt.constants.DOWNSERVERS){

                    tb_lbl.setText(getHdrMsg("The table shows top 50 Down Servers"),false);
                    
                }
                else if(combo.getValue()==convirt.constants.STANDBYSERVERS){

                    tb_lbl.setText(getHdrMsg("The table shows top 50 Standby Servers"),false);
                    
                }
                else{
                    var url="/dashboard/get_custom_search?name="+combo.getValue()+"&lists_level="+convirt.constants.SERVERS;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    var info=response.info;
                                    tb_lbl.setText(getHdrMsg("List of Top "+info.max_count+" Servers with condition : "+combo.getValue()),false);
                                }else{
//                                    Ext.MessageBox.alert(_("Failure"),response.msg);
                                }
                            },
                            failure: function(xhr){
//                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                            }
                        });
                }                             
                srvrs_store.load({
                    params:{
                        canned:combo.getValue()
                    }
                });
            }
        }

    });

    var custom_btn=new Ext.Button({
        tooltip:'Custom Search',
        tooltipType : "title",
        icon:'icons/add_search.png',
        id: 'add',
        height:120,
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                CustomSearchDefList(type,node_id,convirt.constants.SERVERS,query_store);
//                showWindow(_("Custom Search")+":- ",530,450,CustomSearchDefList(type,node_id,convirt.constants.SERVERS,query_store),null,false,false);
            }
         }
    });

    items.push(tb_lbl);
    items.push({xtype:'tbfill'});
    items.push(_('Search: '));
    items.push(new Ext.form.TextField({
        //fieldLabel: _('Search'),
        name: 'search',
        //id: 'search_summary',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));

    items.push(server_query_combo);
    items.push(custom_btn);
    var toolbar = new Ext.Toolbar({
        items: items
    });        

    var srvrs_store = new Ext.data.JsonStore({
        url:"/dashboard/dashboard_server_info?node_id="+node_id+"&type="+type,
        root: 'info',
        successProperty:'success',
        fields:['node_id','name','status','serverpool','vmsummary','cpu','mem','os','platform','storage','network','io'],
        listeners:{
            beforeload:function(obj,recs,opts){
                if(prntPanel.getEl()){
                    prntPanel.getEl().mask();
                }
            },
            load:function(obj,recs,opts){
//                   insert_dummyrecs(obj);
               prntPanel.getEl().unmask();
            },
            loadexception:function(obj,opts,res,e){
                prntPanel.getEl().unmask();
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
       
    });
    
    srvrs_store.load();

    var grid = new Ext.grid.GridPanel({
//        title:'Performance Details',
        store: srvrs_store,
        colModel:srvrs_colModel,
        stripeRows: true,
        frame:false,
        //id:'summary_grid',
        width:820,
        autoExpandColumn:2,
        autoExpandMax:300,
        autoExpandMin:150,
//        autoHeight:true,
        maxHeight:120,
        height:150,
        enableHdMenu:true,
        tbar:toolbar
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick :function(grid,rowIndex,e) {
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });

//    var window = new Ext.Window({
//        //title:'VM Information',
//        width: 820,
//        height:250,
//        modal:true,
//        layout: 'fit',
//        plain:true,
//        items:[grid]
//    });
//    window.show();
    return grid;
    
      }

function showServerPoolList(node_id,type,prntPanel){
    var srvrpools_colModel = new Ext.grid.ColumnModel([
        {header: _("NodeID"), dataIndex: 'node_id', hidden:true},
        {header: _("Server Pool"), width: 160, sortable: true, dataIndex: 'name'},
        //{header: _("ServerPool"), width: 100, sortable: true, dataIndex: 'serverpool'},
        {header: _("VM Summary"), width: 90, sortable: true, dataIndex: 'vmsummary',tooltip:'Total/Running/Paused/Crashed'},
        {header: _("VM CPU(%)"), width: 120, sortable: true, dataIndex: 'cpu',renderer:showBar},
        {header: _("VM Mem(%)"), width: 120, sortable: true, dataIndex: 'mem',renderer:showBar},
        {header: _("Storage(GB)"), width: 100, sortable: true, dataIndex: 'storage',tooltip:'Pool Used/Pool Total'},
        {header: _("Network"), width: 80, sortable: true, dataIndex: 'network',tooltip:'Total/Rx/Tx'},
        {header: _("I/O"), width: 80, sortable: true, dataIndex: 'io',tooltip:'Total/OO/RD/WR'}
    ]);

    var srvrpools_store = new Ext.data.JsonStore({
        url:"/dashboard/dashboard_serverpool_info?node_id="+node_id+"&type="+type,
        root: 'info',
        successProperty:'success',
        fields:['node_id','name','vmsummary','cpu','mem','storage','network','io'],
        listeners:{
//           load:function(obj,recs,opts){
//                insert_dummyrecs(obj);
//                prntPanel.getEl().unmask();
//            },
            loadexception:function(obj,opts,res,e){
                prntPanel.getEl().unmask();
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
        ,sortInfo:{
            dir:'ASC',
            field:'name'
        }
    });
    srvrpools_store.load();

    var tb_lbl=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Server Pool Information")+'</div>'
    });    

    var items=new Array();
    items.push(tb_lbl);
//    items.push({xtype:'tbfill'});
    //items=items.concat(toolbarListBtns(node_id,type,prntPanel,convirt.constants.SERVER_POOL));
    items.push({xtype:'tbfill'});
    items.push(_('Search: '));
    items.push(new Ext.form.TextField({
        //fieldLabel: _('Search'),
        name: 'search',
        //id: 'search_summary',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));
    var toolbar = new Ext.Toolbar({
        items: items
    });

    var grid = new Ext.grid.GridPanel({
//        title:'Performance Details',
        store: srvrpools_store,
        colModel:srvrpools_colModel,
        stripeRows: true,
        frame:false,
        //id:'summary_grid',
        width:820,
        autoExpandColumn:1,
        autoExpandMax:300,
        autoExpandMin:150,
        height:150,
//        autoHeight:true,
        maxHeight:120,
        enableHdMenu:false,
        tbar:toolbar
    });

//    var window = new Ext.Window({
//        //title:'VM Information',
//        width: 820,
//        height:250,
//        modal:true,
//        layout: 'fit',
//        plain:true,
//        items:[grid]
//    });
//    window.show();
    return grid;

}

function toolbarListBtns(node_id,type,prntPanel,grid_type){

    var srvrpool_list_btn=new Ext.Button({
        tooltip:'Server Pool List',
        tooltipType : "title",
        icon:'icons/server_pool_list.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                prntPanel.getEl().mask("Loading ...");
                var g=showServerPoolList(node_id,type,prntPanel);
                prntPanel.removeAll();
                prntPanel.add(g);
                prntPanel.doLayout();
            }
        }
    });

    var srvr_list_btn=new Ext.Button({
        tooltip:'Server List',
        tooltipType : "title",
        icon:'icons/server_list.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                prntPanel.getEl().mask("Loading ...");
                var g=showServerList(node_id,type,prntPanel);
                prntPanel.removeAll();
                prntPanel.add(g);
                prntPanel.doLayout();
            }
        }
    });

    var vm_list_btn=new Ext.Button({
        tooltip:'VM List',
        tooltipType : "title",
        icon:'icons/vm_list.png',
        cls:'x-btn-icon',
        hidden:(type==convirt.constants.MANAGED_NODE),
        listeners: {
            click: function(btn) {
                prntPanel.getEl().mask("Loading ...");
                var g=showVMList(node_id,type,prntPanel);
                prntPanel.removeAll();
                prntPanel.add(g);
                prntPanel.doLayout();
            }
        }
    });

    var items=new Array();
    if(grid_type==convirt.constants.SERVER_POOL){
        if(type==convirt.constants.DATA_CENTER){
            items.push('|');
            items.push(srvr_list_btn);
            items.push('|');
            items.push(vm_list_btn);
        }
        if(type==convirt.constants.SERVER_POOL){
            items.push('|');
            items.push(vm_list_btn);
        }
    }else if(grid_type==convirt.constants.MANAGED_NODE){
        if(type==convirt.constants.DATA_CENTER){
            items.push('|');
            items.push(srvrpool_list_btn);
            items.push('|');
            items.push(vm_list_btn);
        }
        if(type==convirt.constants.SERVER_POOL){
            items.push('|');
            items.push(vm_list_btn);
        }
    }else if(grid_type==convirt.constants.DOMAIN){
        if(type==convirt.constants.DATA_CENTER){
            items.push('|');
            items.push([srvrpool_list_btn]);
            items.push('|');
            items.push(srvr_list_btn);
        }
        if(type==convirt.constants.SERVER_POOL){
            items.push('|');
            items.push(srvr_list_btn);
//            items.push('|');
        }
    }

    return items;
} 

function insert_dummyrecs(obj){
    var rec = Ext.data.Record.create([
           {name: 'node_id', type: 'string'},
           {name: 'name', type: 'string'},
           {name: 'value', type: 'string'}

    ]);
    var no_rows=obj.getCount();
    var min_rowsize=3;
    if (no_rows<min_rowsize){
        for(var i=0;i<min_rowsize-no_rows;i++){
              var r=new rec({
                node_id: ''
//                name: '',
//                value: ''
            });
            obj.add(r);
        }
    }
}

function handle_rowclick(grid,rowIndex,evt,e){
    var rec=grid.getStore().getAt(rowIndex);
    grid.getSelectionModel().clearSelections();
    grid.getSelectionModel().selectRow(rowIndex,false);
    var node_ids=new Array();
    var node_id=rec.get("node_id");
    if (node_id == undefined) 
    {
        var node_id=rec.get("vm_id");
    }
    if(evt=="click"){
        var node=leftnav_treePanel.getNodeById(node_id);
        if (node==null){
            node_ids[0]=node_id;
            rowclick_ajax(evt,node_id,node_ids,e)
        }else{
            leftnav_treePanel.expandPath(node.getPath());
            node.fireEvent(evt,node,e);
        }
    }else if(evt=="contextmenu"){
        set_row_context_menu(node_id,e);
    }
 }
function rowclick_ajax(evt,node_id,node_ids,e){
     var url="/node/get_parent_id?node_id="+node_id;
     var ajaxReq = ajaxRequest(url,0,"GET",true);
     ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
//            alert(xhr.responseText);
            if(!res.success)
                Ext.MessageBox.alert(_("Error"),res.msg);
            else{                 
                var node=leftnav_treePanel.getNodeById(res.node_details.node_id);
                node_ids[node_ids.length]=res.node_details.node_id;
                if (node==null){
                    rowclick_ajax(evt,res.node_details.node_id,node_ids,e);
                }else{
                        set_nodes(node_ids,node_ids.length-1,evt,e);
                }
            }
        },
        failure: function(xhr) {
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
     });
}

function set_nodes(node_ids,length,evt,e){
        var node=leftnav_treePanel.getNodeById(node_ids[length]);
 
        var iconClass=node.getUI().getIconEl().className;
        node.getUI().getIconEl().className="x-tree-node-icon loading_icon";
        var ajaxReq = ajaxRequest(node.attributes.url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                node.getUI().getIconEl().className=iconClass;
//                alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(!response.success){
                    if(node.attributes.nodetype==convirt.constants.MANAGED_NODE &&
                         response.msg==_('Server not authenticated.')){
                         showWindow(_("Credentials for ")+node.text,280,150,credentialsform(node));
                         return;
                    }
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                    return;
                }
                if(length>0){
                    removeChildNodes(node);
                    appendChildNodes(response.nodes,node);
                    node.expand();
                    set_nodes(node_ids,length-1,evt,e);
                }else{
                    node.fireEvent(evt,node,e);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                node.getUI().getIconEl().className=iconClass;
            }
        });
}
function set_row_context_menu(node_id,e){
        var nodes=new Array(3);
        for(var i=0; i<nodes.length; i++)
            nodes[i]=new Array()
        
        var node_base=["entity","parent","g_parent"]
        var node_data=["node_id","node_text","node_type","state"]
        var url="/node/entity_context?node_id="+node_id;
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                     var node_details=response.node_details
                     for(var o=0;o<node_base.length;o++){
                         for(var d=0;d<node_data.length;d++){
//                             alert(eval("node_details."+node_base[o]+"."+node_data[d]));
                             if(eval("node_details."+node_base[o]+"."+node_data[d])!=null)
                                nodes[o][d]=eval("node_details."+node_base[o]+"."+node_data[d]);
                         }
                     }
                     set_contextmenu(nodes,e);
                }else{
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                }
            },
            failure: function(xhr) {
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        });
}
function set_contextmenu(nodes,e){
        var c=new Ext.menu.Menu({
            items: [],
            listeners: {
                itemclick: function(item) {
                    //To avoid separator
                    if(item.id.substring(0,8)=='ext-comp')
                        return
                    var node = item.parentMenu.contextNode;
                    if (!node)
                        return;
                    handleEvents(node,item.id,item);
                }
            }
        });
        
        var node_id=nodes[0][0];
        var node_type=nodes[0][2];
        var url="/get_context_menu_items?node_id="+node_id+"&node_type="+node_type;
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    if(response.rows!=null){
                        var menu=createMenu(response.rows);
                        c=menu;
                    }
                }else{
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                }
                var tmp_node=new Ext.tree.TreeNode({});
                for(var s=nodes.length-1;s>=0;s--){
                    var node=new Ext.tree.TreeNode({
                       text:nodes[s][1],
                       nodetype:nodes[s][2],
                       nodeid:nodes[s][0],
                       id:nodes[s][0],
                       state:nodes[s][3]
                    });
                   tmp_node=tmp_node.appendChild(node);
                }
                c.contextNode = node;
                c.showAt(e.getXY());
            },
            failure: function(xhr) {
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                c.showAt(e.getXY());
            }
        });
}

function CustomSearchDefList(type,node_id,lists_level,query_store){
    
    
    var custom_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Id"),
        width: 50,
        dataIndex: 'id',
        hidden:true
    },
    {
        header: _("Name"),
        width: 100,
        dataIndex: 'name',
        sortable:true
       
    },
    {
        header: _("Condition"),
        width: 160,
        dataIndex: 'desc',
        sortable:true

    },    
    {
        header: _("Created By"),
        width: 90,
        dataIndex: 'user_name',
        sortable:true
    },
    {
        header: _("Level"),
        width: 160,
        dataIndex: 'level',
        sortable:true,
        hidden:true

    },
    {
        header: _("Creadted Time"),
        width: 160,
        dataIndex: 'created_date',
        sortable:true,
        renderer:format_date
        
    },
    {
        header: _("Modified Time"),
        width: 160,
        dataIndex: 'modified_date',
        sortable:true,       
        renderer:format_date,
        hidden:true
    },
     {
        header: _("Max Count"),
        width: 160,
        dataIndex: 'max_count',
        sortable:true,       
        hidden:true
    }  
    
    ]);

    var search_store =new Ext.data.JsonStore({
        url: "/dashboard/get_custom_search_list?node_level="+type+"&lists_level="+lists_level,
        root: 'info',
        fields: ['id','name','user_name','created_date','modified_date','desc','condition','level','max_count'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    search_store.load();

    var cancel_button= new Ext.Button({   
        id: 'ok',
        text: _('Close'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                win.close();
                query_store.load();
            }
        }
    });   


    var new_button=new Ext.Button({
        id: 'new',
        text: _('New'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :'New User',
                    width :370,
                    height:440,
                    modal : true,
                    resizable : false
                });
                SearchDefList(node_id,type,"NEW",custom_grid,null,lists_level);
                //showWindow(_("New Custom Search")+":- ",550,370,SearchDefList(node_id,type,"NEW",custom_grid,null,lists_level),null,false,false);
            }
        }
    });
    

    var remove_button=new Ext.Button({
        id: 'user_remove',
        text: _('Remove'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!custom_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the ist"));
                    return false;
                }
                var edit_rec=custom_grid.getSelectionModel().getSelected();
                var name=edit_rec.get('name');               
                var url='/dashboard/delete_custom_search?name='+name;//alert(url);
                Ext.MessageBox.confirm(_("Confirm"),_("About to delete definition:")+name+"?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    custom_grid.getStore().load();
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
    

    var edit_button= new Ext.Button({
        id: 'user_edit',
        text: _('Edit'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
             click: function(btn) {
                 if(!custom_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the list"));
                    return false;
                }
                var edit_rec=custom_grid.getSelectionModel().getSelected();                
                SearchDefList(node_id,type,"EDIT",custom_grid,edit_rec,lists_level);
                //showWindow(_("Edit Custom Search")+":- ",550,370,SearchDefList(node_id,type,"EDIT",custom_grid,edit_rec,lists_level),null,false,false);
             }           
        }
    });

    var custom_grid=new Ext.grid.GridPanel({
        store: search_store,
        stripeRows: true,
        colModel:custom_columnModel,
        frame:false,
        autoscroll:true,
        height:415,
        width:'100%',
        loadMask:true,
        enableHdMenu:false,
        id:'task_grid',
         tbar:[
            _('Search (By Name): '),new Ext.form.TextField({
            fieldLabel: _('Search'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    search_store.filter('name', field.getValue(), false, false);
                }
            }
        }),{
            xtype: 'tbfill'
        },new_button,remove_button],
        bbar:[{xtype: 'tbfill'},cancel_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
        }
    });

    var custompanel=new Ext.Panel({
        id:"taskpanel",
        title:'',
        layout:"form",
        width:'100%',
        height:460,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items: [custom_grid]        
    });

//    return custompanel;
     var win=new Ext.Window({
        title:"Search",
        width: 530,
        layout:'fit',
        height: 455,
        modal: true,
        resizable: false,
        closable: false
    });
    win.add(custompanel);
    win.show();

  }  

function SearchDefList(node_id,type,mode,custom_grid,custom_rec,listlevel){

   
    var name_text=new Ext.form.TextField({
        fieldLabel: _('Name'),
        name: 'name',
        id: 'name_text',
        allowBlank:false,
        width:180
    });

    var property_store = new Ext.data.JsonStore({
        url:"/dashboard/get_property_forsearch?node_id="+node_id+"&node_type="+type+"&listlevel="+listlevel,
        root: 'info',
        successProperty:'success',
        fields:['value','text'],
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
        ,sortInfo:{
            dir:'ASC',
            field:'text'
        }
    });

    property_store.load();

    var filter_store = new Ext.data.JsonStore({
        url:"/dashboard/get_filter_forsearch",
        root: 'info',
        successProperty:'success',
        fields:['id','value'],
        listeners:{

            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
       
    });
    
    filter_store.load();
   
    var cancel_button= new Ext.Button({
        id: 'ok',
        text: _('Close'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                win.close();
            }
        }
    });   

    var value="",url="",property_val="";

    var store =new Ext.data.SimpleStore({
        fields: ['property','property_val','filter','value']
    });

    var columnModel = new Ext.grid.ColumnModel([
        {

            header: _("Property"),
            width: 160,
            sortable: false,
            dataIndex: 'property',
            editor: new Ext.form.ComboBox({
                typeAhead: true,
                store:property_store,
                triggerAction: 'all'
                ,mode:'local'
                ,displayField:'text'
                ,valueField:'text'
                ,listeners:{
                    select:function(combo,record,index){
                        property_val = property_store.getAt(combo.selectedIndex).get("value");
                        grid.getSelectionModel().getSelected().set("property_val",property_val);
                        grid.getSelectionModel().getSelected().set("property",combo.getRawValue());                        
                    }
                }
            })
        },
        {
            header: _("Filter"),
            width: 140,
            sortable: false,
            dataIndex: 'filter',
            editor: new Ext.form.ComboBox({
                typeAhead: true,
                store:filter_store,
                triggerAction: 'all'
                ,mode:'local'
                ,displayField:'value'
                ,valueField:'value'
            })
        },
        {
            header: _("Value"),
            width: 50,
            sortable: false,
            dataIndex: 'value',
            editor: new Ext.form.TextField({
                allowBlank: false
            })
        },
        {

            header: _("Property"),
            width: 160,
            sortable: false,
            dataIndex: 'property_val',
            hidden:true
        }

    ]);

    var Max_count=new Ext.form.NumberField({
        fieldLabel: _('Max row count'),
        name: 'vm_count',
        width: 100,
        id: 'vm_count',
        allowBlank:false
    });

    Max_count.setValue(50);
    
    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var condn_rec = Ext.data.Record.create([
           {name: 'property', type: 'string'},
           {name: 'filter', type: 'string'},
           {name: 'value', type: 'string'},
           {name: 'property_val', type: 'string'}
    ]);

    var grid = new Ext.grid.EditorGridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:true,
        selModel:selmodel,
        width:'100%',
        autoExpandColumn:2,
        height:270,
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'add_var',
                id: 'add_var',
                text:_("Add"),
                icon:'icons/add.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        var r=new condn_rec({
                            property: '',                            
                            filter: '',
                            value: '',
                            property_val: ''
                        });

                        grid.stopEditing();
                        store.insert(0, r);
                        grid.startEditing(0, 0);
                        grid.getSelectionModel().selectFirstRow(); 
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'remove_var',
                id: 'remove_var',
                text:_("Remove"),
                icon:'icons/delete.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        grid.getStore().remove(grid.getSelectionModel().getSelected());
                    }
                }
            })
        ]
    });    

    var test_btn=new Ext.Button({
        tooltip:'test select statement',
        tooltipType : "title",
        icon:'icons/information.png',
        id: 'test',
        text:_('Test'),
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var x=""
                if (store.getCount()>0 && name_text.getValue()){
                    var recs=store.getRange(0,store.getCount());
                    var test_value="";
                    for(var i=0;i<recs.length;i++){
                        test_value+=recs[i].get('property_val')+" "+recs[i].get('filter')+" "+recs[i].get('value');
                        if (i != recs.length-1){
                            test_value+=",";
                         }
                        x+=recs[i].get('value');
                    }
                }                
                
//                var invalid_chars=new Array('!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*',';',':','?','/','\'');
//                for(var i=0;i<x.length;i++){
//                    for(var j=0;j<=invalid_chars.length;j++){
//                        if(x.charAt(i) == invalid_chars[j]){
//                            Ext.MessageBox.alert(_("Error"),_("value should not contain special characters.<br>")+
//                            "comma,single quote,'!','@','#',<br>'$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','.',';',':','?','/'");
//                            return false;
//                        }
//                    }
//                }
                url="/dashboard/test_newcustom_search?name="+name_text.getValue()+"&value="+test_value+"&node_id="+node_id+"&type="+type+"&listlevel="+listlevel;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){                            
                            Ext.MessageBox.alert(_("Success"),response.msg);
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

    var save=new Ext.Button({
        tooltip:'save select statement',
        name: 'ok',
        id: 'ok',
        text:_('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var x="",desc = "",value="";
                if (store.getCount()>0  && name_text.getValue() && Max_count.getValue()){
                    if(Max_count.getValue()>200){
                        Ext.MessageBox.alert(_("Message"),"The maximum row count should be less than 200.");
                        return false;
                    }                    
                    var recs=store.getRange(0,store.getCount());
                    for(var i=0;i<recs.length;i++){
                        if(recs[i].get('property') && recs[i].get('filter') && recs[i].get('value')){
                            desc+=recs[i].get('property')+" "+recs[i].get('filter')+" "+recs[i].get('value');
                            value+=recs[i].get('property_val')+" "+recs[i].get('filter')+" "+recs[i].get('value');                   
                            if (i != recs.length-1){
                                value+=",";
                                desc+=",";
                            }
                            x+=recs[i].get('value');
                        }
                    }
                    
//                    var invalid_chars=new Array('!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*',';',':','?','/','\'');

                        if (mode == "NEW"){
//
//                                for(var i=0;i<x.length;i++){
//                                    for(var j=0;j<=invalid_chars.length;j++){
//                                        if(x.charAt(i) == invalid_chars[j]){
//                                            Ext.MessageBox.alert(_("Error"),_("value should not contain special characters.<br>")+
//                                            "comma,single quote,'!','@','#',<br>'$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','.',';',':','?','/'");
//                                            return false;
//                                        }
//                                    }
//                            }
                            url="/dashboard/save_custom_search?name="+name_text.getValue()+"&desc="+desc+"&condition="+value+
                                "&node_id="+node_id+"&level="+type+"&lists_level="+listlevel+"&max_count="+Max_count.getValue();
                            var ajaxReq=ajaxRequest(url,0,"POST",true);
                            ajaxReq.request({
                                success: function(xhr) {
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                        Ext.MessageBox.alert(_("Success"),_("Successfully saved the values"));
                                        custom_grid.getStore().load();
                                        win.close();

                                    }else{
                                        Ext.MessageBox.alert(_("Failure"),response.msg);
                                    }
                                },
                                failure: function(xhr){
                                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                                }
                            });
                        }                
                        else if(mode=="EDIT"){                             
//                            for(var i=0;i<x.length;i++){
//                                    for(var j=0;j<=invalid_chars.length;j++){
//                                        if(x.charAt(i) == invalid_chars[j]){
//                                            Ext.MessageBox.alert(_("Error"),_("value should not contain special characters.<br>")+
//                                            "comma,single quote,'!','@','#',<br>'$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','.',';',':','?','/'");
//                                            return false;
//                                        }
//                                    }
//                            }
                            url="/dashboard/edit_save_custom_search?name="+name_text.getValue()+"&desc="+desc+"&condition="
                                +value+"&max_count="+Max_count.getValue();
                            var ajaxReq=ajaxRequest(url,0,"POST",true);
                            ajaxReq.request({
                                success: function(xhr) {
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                        Ext.MessageBox.alert(_("Success"),_("Successfully saved the values."));
                                        custom_grid.getStore().load();
                                        win.close();

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
                else{
                    if(store.getCount()==0){
                        Ext.MessageBox.alert(_('Errors'), _('Specify atleast one condition.'));
                    }
                    else if(! name_text.getValue()){

                        Ext.MessageBox.alert(_('Errors'), _('Name of new custom search is missing.'));
                    } else if(! Max_count.getValue()){

                        Ext.MessageBox.alert(_('Errors'), _('The maximun row count for custom search is missing.'));
                    }


                }
            }
        }
    });       
    
   
    var panel7 = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        layout:"form",
        frame:true,
        width:'100%',
        items:[name_text,Max_count],
        bbar:[{xtype: 'tbfill'},test_btn,save,cancel_button]
    });

    
    var name="";
    var title = "Add Search";
    if (mode=="EDIT"){
        name=custom_rec.get("name");
        title = "Edit Search : "+name;
        var count=custom_rec.get("max_count");

        name_text.setValue(name);
        name_text.disabled=true;
        Max_count.setValue(count);

        var description=custom_rec.get("desc");
        var descriptions = description.split(',');
        var condition=custom_rec.get("condition");
        var conditions = condition.split(',');
        var length=descriptions.length;
        for (var i=0;i<length;i++){
            if(conditions[i]!="" && conditions[i]!=" "){
                var condn = conditions[i].split(" ");
                var descn = descriptions[i].split(condn[1]);

//                alert(condn.length);
                if(condn.length > 3){
                    var value_field=""
                    for (var c=2;c<condn.length;c++){
                         value_field+=condn[c]
                         if (c != condn.length-1){
                             value_field+=" "
                         }

                    }
                }else{
                    value_field=condn[2]
                }
                
                var new_entry=new condn_rec({
                    property_val:condn[0],
                    filter:condn[1],
                    value:value_field,
                    property:descn[0]
                });

                grid.getStore().insert(0,new_entry);
            }
        }
    }

    panel7.add(grid);    
//    return panel7;
    var win=new Ext.Window({
        title:title,
        width: 550,
        layout:'fit',
        height: 370,
        modal: true,
        resizable: false,
        closable: false
    });
    win.add(panel7);
    win.show();
       
}


