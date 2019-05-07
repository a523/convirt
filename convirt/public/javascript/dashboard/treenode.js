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

function appendNode(node,prntNode){

    var name="NODE_NAME",type="NODE_TYPE",nodetype="",nodename="",nodeid="";
    var attrs=node.attributes;
    if(!attrs.getNamedItem(name)){
        name="NAME",type="NAME";
        nodetype="DOMAIN";
        if(!attrs.getNamedItem(name)){
            name="name",type="name"
            nodetype="IMAGE";
        }
    }
    nodetype=(nodetype=="")?attrs.getNamedItem("NODE_TYPE").nodeValue:nodetype;
    nodename=attrs.getNamedItem(name).nodeValue;
    nodeid=nodename;
    var grpLbl=(attrs.getNamedItem(type).nodeValue=="MANAGED_NODE")?prntNode.text:nodename;
    var url="";
    if(prntNode.attributes.nodetype=="IMAGE_STORE"){
        url="/template//get_images?group_id="+attrs.getNamedItem("id").nodeValue;
        nodetype="IMAGE_GROUP";
        nodeid=attrs.getNamedItem("id").nodeValue;
    }else if(prntNode.attributes.nodetype=="IMAGE_GROUP"){
        url="/template/get_image_info?image_id="+attrs.getNamedItem("id").nodeValue;
        nodetype="IMAGE";
        nodeid=attrs.getNamedItem("id").nodeValue;
    }else{
        url="/dashboard/dashboardservice?type="+attrs.getNamedItem(type).nodeValue+"&nodeLabel="+nodename+"&groupLabel="+grpLbl;
    }

    var state="",icon=nodetype+"_icon";
    if(prntNode.attributes.nodetype=="MANAGED_NODE"){
        state=node.attributes.getNamedItem('STATE').nodeValue;
        if(state=='0')
            state='Running';
        if(state=='Running' || state=='Blocked' || state=='')
            icon='runningvm_icon';
        else if(state=='Paused')
            icon='pausedvm_icon';
        else
            icon='stoppedvm_icon';
    }
    var id=attrs.getNamedItem("NODE_ID").nodeValue;
    var n = new Ext.tree.TreeNode({
        text:nodename,
        draggable: (nodetype!="IMAGE_GROUP" && nodetype!="SERVER_POOL"),
        allowDrop : (nodetype!="DOMAIN" && nodetype!="IMAGE"),
        leaf:false,
        url:url,
        nodetype:nodetype,
        //later to be changed to the id
        nodeid:nodeid,
        id:id,
        iconCls: icon,
        contextMenu: getContextMenu(nodetype,node),
        state:state
    });

    if(nodename!="Domain-0")
        prntNode.appendChild(n);
    return prntNode;
}

function createNode(node,prntNode){

    var name="NODE_NAME",type="NODE_TYPE",nodetype="",nodename="",nodeid="";
    var attrs=node.attributes;
    if(!attrs.getNamedItem(name)){
        name="NAME",type="NAME";
        nodetype="DOMAIN";
        if(!attrs.getNamedItem(name)){
            name="name",type="name"
            nodetype="IMAGE";
        }
    }
    nodetype=(nodetype=="")?attrs.getNamedItem("NODE_TYPE").nodeValue:nodetype;
    nodename=attrs.getNamedItem(name).nodeValue;
    nodeid=nodename+"_"+prntNode.text;
    var grpLbl=(attrs.getNamedItem(type).nodeValue=="MANAGED_NODE")?prntNode.text:nodename;

    var n = new Ext.tree.TreeNode({
        text:nodename,
        draggable: false,
        leaf:false,
        url:"/dashboard/dashboardservice?type="+attrs.getNamedItem(type).nodeValue+"&nodeLabel="+attrs.getNamedItem(name).nodeValue+"&groupLabel="+grpLbl,
        nodetype:nodetype,
        nodeid:nodeid,
        iconCls: nodetype+"_icon"
    });

    if (node.childNodes.length>0)
    {
        var y=node.childNodes;
        for (var j=0;j<y.length;j++)
        {
            if(y[j].nodeType==1)
                createNode(y[j],n);
        }
    }
    return node;
}


function removeChildNodes(node){
    var children=node.childNodes;
    for(var i=children.length-1;i>=0;i--){
        node.removeChild(children[i]);
    }
}
function removeNodes(node,rm_nodes){
    for(var i=rm_nodes.length-1;i>=0;i--){
        node.removeChild(rm_nodes[i]); 
    }
}

function addChildNodes(x,t){
    for(var i=0;i<x.length;i++){
        if(x[i].nodeType==1)
            appendNode(x[i],t);
    }
    t.expand();
}

function update_expanded_node(node){

        var ajaxReq = ajaxRequest(node.attributes.url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(!response.success){
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                    return;
                }
                var r_children=response.nodes;
                var n_children=node.childNodes;
                var new_nodes=get_new_nodes(r_children,node);
                var del_nodes=get_del_nodes(r_children,n_children);
                //alert(node.attributes.text+"==new=="+new_nodes+"del=="+del_nodes);
                if(new_nodes.length!=0)
                    appendChildNodes(new_nodes,node);
                if(del_nodes.length!=0)
                    removeNodes(node,del_nodes);
                node.expand();
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                node.getUI().getIconEl().className=iconClass;
            }
        });

}

function appendChildNodes(childnodes,prntNode){

    for(var i=0;i<childnodes.length;i++){
        var childnode=childnodes[i];        
        var url="/dashboard/dashboardservice?node_id="+childnode.NODE_ID+"&type="+childnode.NODE_TYPE;
        var iconCls= childnode.NODE_TYPE+"_icon";
        var nodeid=childnode.NODE_NAME;
        var draggable=false,allowDrop=false;
//        if(childnode.NODE_TYPE===convirt.constants.DATA_CENTER){
//            url="/dashboard/dashboardservice?type=DATA_CENTER&nodeLabel=None&groupLabel=None";
//        }else
        if(childnode.NODE_TYPE===convirt.constants.IMAGE_STORE){
            url="/template/get_image_groups?store_id="+childnode.NODE_ID;
            nodeid=childnode.NODE_ID;
        }else if(childnode.NODE_TYPE===convirt.constants.SERVER_POOL){
            allowDrop=true;
//            url="/dashboard/dashboardservice?type=SERVER_POOL&nodeLabel="+childnode.NODE_NAME+"&groupLabel=None";
        }else if(childnode.NODE_TYPE===convirt.constants.MANAGED_NODE){
            allowDrop=true;
            //url="/dashboard/dashboardservice?type=MANAGED_NODE&nodeLabel="+childnode.NODE_NAME+"&groupLabel="+prntNode.attributes.nodeid;
            iconCls= childnode.NODE_PLATFORM+"_icon";
            draggable=true;
        }else if(childnode.NODE_TYPE===convirt.constants.DOMAIN){
            draggable=true;
            var state=""+childnode.STATE;

            //alert(state+"-----"+childnode.NODE_NAME+"---"+childnode.NODE_ID);
            var icon_state=""+childnode.ICONSTATE;
            iconCls=getIconCls(icon_state,childnode.DOMAIN_TYPE);
        }else if(childnode.NODE_TYPE===convirt.constants.IMAGE_GROUP){
            allowDrop=true;
            url="/template/get_images?group_id="+childnode.NODE_ID;
            nodeid=childnode.NODE_ID;
        }else if(childnode.NODE_TYPE===convirt.constants.IMAGE){
            draggable=true;
            url="/template/get_image_info?node_id="+childnode.NODE_ID+"&level="+childnode.NODE_TYPE;
            nodeid=childnode.NODE_ID;
        }

        var node=new Ext.tree.TreeNode({
            text: childnode.NODE_NAME,
            id: childnode.NODE_ID,
            nodeid: nodeid,
            iconCls: iconCls,
            draggable: draggable,
            leaf: false,
            allowDrop: allowDrop,
            url: url,
            nodetype: childnode.NODE_TYPE
            ,state:state
            ,clickable:childnode.DOMAIN_TYPE
        });
//        alert(childnode.NODE_NAME+"==="+childnode.NODE_CHILDREN);
        if(childnode.NODE_CHILDREN){
            var dummy_node=new Ext.tree.TreeNode({
                id: "dummy_node",
                nodeid: "dummy_node"
            });
            node.appendChild(dummy_node);
        }
        if(childnode.NODE_NAME!='Domain-0'){
            var cur_node = leftnav_treePanel.getNodeById(node.attributes.id);
            if (cur_node != null &&
                cur_node.parentNode.attributes.id != prntNode.attributes.id){
                var pNode = cur_node.parentNode;
                pNode.removeChild(cur_node);
            }
            prntNode.appendChild(node);
        }
    }
}


function get_new_nodes(children,parentNode){
    var node_array=new Array();
    var n=0;
    for(var k=0;k<children.length;k++){
        var node=leftnav_treePanel.getNodeById(children[k].NODE_ID);
        if(!node || (node!=null && !parentNode.contains(node))){
            node_array[n]=children[k];
            n++;
        }else{
            if(node.attributes.nodetype==convirt.constants.DOMAIN){
                node.setText(children[k].NAME);
                node.attributes.state=children[k].STATE;
                var icon_state=""+children[k].ICONSTATE;
                var iconCls=getIconCls(icon_state,children[k].DOMAIN_TYPE);

                node.getUI().getIconEl().className="x-tree-node-icon "+iconCls;
            }
            if(node.attributes.nodetype==convirt.constants.MANAGED_NODE){
                var iconCls= children[k].NODE_PLATFORM+"_icon";
                node.getUI().getIconEl().className="x-tree-node-icon "+iconCls;
            }
        }
    }
    return node_array;
}

function get_del_nodes(r_children,n_children){
    var node_array=new Array();
    var n=0;
    for(var k=0;k<n_children.length;k++){
        var count=0;
        for(var j=0;j<r_children.length;j++){
            if(n_children[k].attributes.id==r_children[j].NODE_ID){
                count++;
            }
        }
       if(count==0){
            node_array[n]=n_children[k];
            n++;
        }
    }
    return node_array;
}

function getIconCls(state,domain_type){
    var iconCls='';
    if (domain_type==convirt.constants.OUTSIDE_DOMAIN){
        if(state===convirt.constants.RUNNING || state===convirt.constants.UNKNOWN){
            iconCls='down_runningvm_icon';
        }else if(state===convirt.constants.PAUSED){
            iconCls='down_pausedvm_icon';
        }else{//SHUTDOWN ,CRASHED ,NOT_STARTED
            iconCls='down_stoppedvm_icon';
        }
        return iconCls;
    }else{
        if(state===convirt.constants.RUNNING || state===convirt.constants.UNKNOWN){
            iconCls='runningvm_icon';
        }else if(state===convirt.constants.PAUSED){
            iconCls='pausedvm_icon';
        }else if(state===convirt.constants.DOWN_RUNNING|| state===convirt.constants.DOWN_UNKNOWN){
            iconCls='down_runningvm_icon';
        }else if(state===convirt.constants.DOWN_PAUSED){
            iconCls='down_pausedvm_icon';
        }else if(state===convirt.constants.DOWN_SHUTDOWN||state===convirt.constants.DOWN_NOT_STARTED){
            iconCls='down_stoppedvm_icon';
        }else{//SHUTDOWN ,CRASHED ,NOT_STARTED
            iconCls='stoppedvm_icon';
        }
        return iconCls;
     }
}

