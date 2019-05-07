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

function InfoGrid(node){
    var json_record = Ext.data.Record.create([
        {name: 'id'},
        {name: 'label'},
        {name: 'value'},
        {name: 'type'},
        {name: 'extra'}
    ]);

    var json_reader = new Ext.data.JsonReader({
        totalProperty: "results",
        root: "rows",
        successProperty:'success',
        id: "id"
    },json_record);

    var url="";
    if(node.attributes.nodetype===convirt.constants.DOMAIN){
        url='/node/get_node_info?node_id='+node.attributes.id+'&level='+convirt.constants.DOMAIN;
    }else if(node.attributes.nodetype===convirt.constants.MANAGED_NODE){
        url='/node/get_node_info?node_id='+node.attributes.id+'&level='+convirt.constants.MANAGED_NODE;
    }
    var store = new Ext.data.GroupingStore({
        url: url,
        reader:json_reader,
        remoteSort :true,
        remoteGroup:true, 
        groupField:'type',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    store.load();
    var columnModel = new Ext.grid.ColumnModel([
        {header: "", width: 100,  dataIndex: 'label',sortable: false},
        {header: "", width: 200, dataIndex: 'value',sortable: false},
        {header: "", hidden: true, width: 200, sortable: false, dataIndex: 'type'},
        {header: "", width: 100, dataIndex: 'extra',sortable: false}
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
        hidden:(node.attributes.nodetype=="DOMAIN"),
        listeners: {
            click: function(btn) {
                reloadInformation(node.attributes.id,node.attributes.nodetype,grid);
            }
        }
    });

    var grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        enableHdMenu:false,
        enableColumnMove:false,
        frame:false,
        border:false,
        width:'100%',
        autoExpandColumn:1,        
        height:600,
        selModel:selmodel,
        view: new Ext.grid.GroupingView({
            forceFit:true,
            groupTextTpl: '{group}'
        })
        ,tbar:[refresh_btn]
    });

    return grid;

}

function reloadInformation(node_id, node_type,grid){
    Ext.MessageBox.show({
        title:_('Please wait...'),
        msg: _('Refreshing Information, ')+ _('Please wait...'),
        width:300,
        wait:true,
        waitConfig: {interval:200}
    });
    var url="/node/refresh_node_info?node_id="+node_id+"&level="+node_type;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            Ext.MessageBox.hide();
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(!res.success)
                Ext.MessageBox.alert(_("Error"),res.msg);
            else
                grid.getStore().load()
        },
        failure: function(xhr) {
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
