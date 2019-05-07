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

function MigrationChecksDialog(vm,node,dest_node,live,rows){
    var columnModel = new Ext.grid.ColumnModel([
        {header: _("Type"), width: 40, sortable: false, dataIndex: 'type',renderer:function(value,params,record){
                if(value=='error'){
                    return '<img src="icons/cancel.png" />';
                }else if(value=='warning'){
                    return '<img src="icons/warning.png" />';
                }
        }},
        {header: _("Category"), width: 75, sortable: true, dataIndex: 'category'},
        {header: _("Message"), width: 150, sortable: true, dataIndex: 'message'}
    ]);

    var store = new Ext.data.SimpleStore({
        fields:[{name: 'type'},
                {name: 'category'},
                {name:'message'}]
    });
    store.loadData(getData(rows));
    var grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        border:true,
        width:495,
        autoExpandColumn:2,
        height:240
    });

    var lbl=new Ext.form.Label({
        text:_("Results of prerequsite checks done for Migration.")
    });
    var panel = new Ext.Panel({
        layout:'form',
        bodyStyle:'padding:15px 0px 0px 0px',
        labelWidth:60,
        labelSeparator:' ',
        width:500,
        height:300,
        autoScroll:true,
        enableColumnHide:false,
        items:[lbl,grid],
        bbar:[
            {xtype: 'tbfill'},
            new Ext.Button({
                name: 'continue',
                id: 'continue',
                text:_('Continue'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();
                        migrateVM(vm,node,dest_node,live,'true');
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('Cancel'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow();}
                }
            })
        ]
    });

    return panel;
}

function getData(rows){
    var data=new Array();
    for(var i=0;i<rows.length;i++){
        data[i]=new Array();
        data[i][0]=rows[i].type;
        data[i][1]=rows[i].category;
        data[i][2]=rows[i].message;
    }
    return data;
}
