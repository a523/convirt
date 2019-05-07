
function SPSelectionDialog(node,jsonData,action,vm,sp,objData){
//    var lbl=new Ext.form.Label({
//        html:'<div style="" class="boldlabelheading">'+_("Select Destination Server Pool")+'</div><br>'
//    });

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
        //items:[node_tree],
        autoScroll:true,
        bbar:[
            {xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('OK'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) { 
                        submitSPSelection(node_tree,node,panel,action,vm,sp,objData);
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

    //panel.add(lbl);
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
    appendChildrenSP(nodes,dataNode);
    dataNode.expand();    
    sp_node_tree = node_tree;

    return panel;
}

function appendChildrenSP(nodes,prntNode){
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
        prntNode.appendChild(node);
    }

}


function submitSPSelection(node_tree,node,panel,action,vm,sp,objData){
    var dest_node=node_tree.getSelectionModel().getSelectedNode();
       
        if(dest_node.attributes.nodetype!='SERVER_POOL')
        {
          Ext.MessageBox.alert(_('Warning'),_('Please select a Server Pool'));
            return;
        }

        closeWindow();
        transferNode(node,sp,dest_node,true)
     
}

