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
var provision_node_tree;
function NodeSelectionDialog(vm,node,jsonData,action){    

    var lbl=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("Only connected servers will be shown here.")+'</div><br>'
    });
    var node_tree=new Ext.tree.TreePanel({
        rootVisible      : true,
        useArrows        : true,
        collapsible      : false,
        animCollapse     : false,
        border           : false,
        id               : "tree_nodelist",
        autoScroll       : true,
        animate          : false,
        enableDD         : false,
        containerScroll  : true,
        layout           : 'fit'
    });

    var panel = new Ext.Panel({
        layout:'form',
        bodyStyle:'padding:0px 0px 0px 3px',
        labelWidth:60,
        labelSeparator:' ',
        cls: 'whitebackground',
        width:300,
        height:300,
        autoScroll:true,
        bbar:[
            new Ext.form.Checkbox({
                name: 'live',
                id: 'live',
                boxLabel:_('Live Migration'),
                checked:true,
                hidden:(action=='provision_image' || action=='create_network')
            }),
            {xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('OK'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        submitNodeSelection(node_tree,node,vm,panel,action);
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
    panel.add(lbl);
    panel.add(node_tree);
    
    var dataNode = new Ext.tree.TreeNode({
        text: _("Data Center"),
        draggable: false,
        iconCls: "small_pool",
        id: "data_center",
        leaf:false,
        expandable:true,
        expanded:true,
        nodetype:"DATA_CENTER"
    });
    node_tree.setRootNode(dataNode);

    new Ext.tree.TreeSorter(node_tree,{
        folderSort:true,
        dir:'ASC'
    });

    var nodes=jsonData.nodes;
    appendChildren(nodes,dataNode);
    dataNode.expand();
    
    provision_node_tree = node_tree;

    return panel;
}

function appendChildren(nodes,prntNode){
    for(var i=0;i<nodes.length;i++){
        var iconcls=nodes[i].type+"_icon";
        if(nodes[i].platform!=null){
            iconcls=nodes[i].platform+"_icon";
        }
        var node = new Ext.tree.TreeNode({
            text: nodes[i].name,
            id:nodes[i].id,
            draggable: false,
            iconCls: iconcls,
            leaf:false,
            nodetype:nodes[i].type,
            nodeid:nodes[i].name
        });
        appendChildren(nodes[i].children,node);
        prntNode.appendChild(node);
    }
}

function submitNodeSelection(node_tree,node,vm,panel,action){
    var dest_node=node_tree.getSelectionModel().getSelectedNode();

    if(action=='provision_image'){
        closeWindow();
        var n=leftnav_treePanel.getNodeById(dest_node.attributes.id);
        dest_node=(n!=null?n:dest_node);
        Provision(dest_node,node,action);
    }else if(action=='create_network'){
        if(dest_node.attributes.nodetype!='MANAGED_NODE'){
            Ext.MessageBox.alert(_('Warning'),_('Please select a Managed Node.'));
            return;
        }
        closeWindow();
        //When menu is invoked at server level
        site_id = dest_node.parentNode.parentNode.attributes.id;
        strOpLevel = "S";
        group_id = dest_node.parentNode.attributes.id;
        node_id = dest_node.attributes.id;

        OpenNewNetworkDialog(dest_node, site_id, group_id, node_id, strOpLevel);
    }else{
        if(dest_node.attributes.nodetype!='MANAGED_NODE'){
            Ext.MessageBox.alert(_('Warning'),_('Please select a Managed Node.'));
            return;
        }
        closeWindow();
        migrateVM(vm,node,dest_node,panel.getBottomToolbar().items.get('live'). getValue(),'false');
    }
}
