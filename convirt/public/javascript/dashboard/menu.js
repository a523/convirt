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

function getMenu(){
    var menu = new Ext.menu.Menu({
        id: 'mainMenu',
        items: [
        {
            text: 'I like Ext'
        },
        {
            text: 'Ext for jQuery'
        },
        {
            text: 'I donated!'
        }
        ]
    });

    return menu;
}

function getContextMenu(nodetype,node){//DATA_CENTER,SERVER_POOL,MANAGED_NODE,VM,IMAGE_STORE,IMAGE_GROUP,IMAGE

    var items=new Array();
    if(nodetype=="DATA_CENTER"){
        items.push({id: 'add_server_pool',text: 'Add Server Pool',icon:'/icons/add.png'});
    }else if(nodetype=="IMAGE_STORE"){
        items.push({id: 'add_image_group',text: 'Add Image Group',icon:'/icons/add.png'});
    }else if(nodetype=="SERVER_POOL"){
        items.push({id: 'add_node',text: 'Add Server',icon:'/icons/add.png'});
        items.push({id: 'connect_all',text: 'Connect All',icon:'/icons/small_connect.png'});
        items.push('-');
        items.push({id: 'provision_vm',text: 'Provision VM',icon:'/icons/provision_vm.png'});
        items.push({id: 'group_provision_settings',text: 'Provisioning Settings',icon:'/icons/settings.png'});
        items.push('-');
        items.push({id: 'storage_pool',text: 'Storage Pool',icon:'/icons/storage_pool.png'});
        items.push('-');
        items.push({id: 'remove_server_pool',text: 'Remove',icon:'/icons/delete.png'});
    }else if(nodetype=="MANAGED_NODE"){
        items.push({id: 'edit_node',text: 'Edit',icon:'/icons/file_edit.png'});
        items.push({id: 'connect_node',text: 'Connect',icon:'/icons/small_connect.png'});
        items.push("-");
        items.push({id: 'provision_vm',text: 'Provision VM',icon:'/icons/provision_vm.png'});
        items.push({id: 'restore_hibernated',text: 'Restore VM',icon:'/icons/small_restore.png'});
        items.push({id: 'import_vm_config',text: 'Import VM Config File',icon:'/icons/folder.png'});
        items.push("-");
        items.push({id: 'start_all',text: 'Start All VMs',icon:'/icons/small_start.png',tooltip:'Start All VMs'});
        items.push({id: 'shutdown_all',text: 'Shutdown All VMs',icon:'/icons/small_shutdown.png',tooltip:'Shutdown All VMs'});
        items.push({id: 'kill_all',text: 'Kill All VMs',icon:'/icons/small_kill.png',tooltip:'Kill All VMs'});
        items.push({id: 'migrate_all',text: 'Migrate All VMs',icon:'/icons/small_migrate_vm.png',tooltip:'Migrate All VMs'});
        items.push("-");
        items.push({id: 'manage_virtual_networks',text: 'Manage Virtual Networks',icon:'/icons/manage_virtual_networks.png',tooltip:'Migrate All VMs'});
        items.push("-");
        items.push({id: 'remove_node',text: 'Remove',icon:'/icons/delete.png'});
    }else if(nodetype=="DOMAIN"){
        var state=node.attributes.getNamedItem('STATE').nodeValue.replace(/-/g,'');
        if(state=='0')
            state='r';
        state=(state==''||state=='b')?'r':state;

        var pauseid="pause",pausetext="Pause",pausetip="Pause VM";
        if(state=='p')
            pauseid="unpause",pausetext="Resume",pausetip="Resume VM";

        items.push({id: 'change_vm_settings',text: 'Change VM Settings',icon:'/icons/file_edit.png',tooltip:'Change VM Settings'});
        items.push({id: 'edit_vm_config_file',text: 'Edit VM Config File',icon:'/icons/file_edit.png',tooltip:'Edit VM Config File'});
        items.push("-");
        items.push({id: 'migrate',text: 'Migrate',icon:'/icons/small_migrate_vm.png',disabled:(state!='r'&&state!='p'),tooltip:'Migrate VM'});
        items.push({id: 'start',text: 'Start',icon:'/icons/small_start.png',disabled:(state=='r'||state=='p'),tooltip:'Start VM'});
        items.push({id: pauseid,text: pausetext,icon:'/icons/small_pause.png',disabled:!(state=='r'||state=='p'),tooltip:pausetip});
        items.push({id: 'reboot',text: 'Reboot',icon:'/icons/small_reboot.png',disabled:(state!='r'&&state!='p'),tooltip:'Reboot VM'});
        items.push({id: 'shutdown',text: 'Shutdown',icon:'/icons/small_shutdown.png',disabled:(state!='r'&&state!='p'),tooltip:'Shutdown VM'});
        items.push({id: 'kill',text: 'Kill',icon:'/icons/small_kill.png',disabled:(state!='r'&&state!='p'),tooltip:'Kill VM'});
        items.push({id: 'hibernate',text: 'Hibernate',icon:'/icons/small_snapshot.png',disabled:(state!='r'&&state!='p'),tooltip:'Hibernate VM'});
        items.push({id: 'set_boot_device',text: 'Set Boot Device',icon:'/icons/file_edit.png',tooltip:'Set Boot Device'});
        items.push("-");
        items.push({id: 'remove_vm_config_file',text: 'Remove VM Config File',icon:'/icons/delete.png',tooltip:'Remove VM Config File'});
        items.push({id: 'delete',text: 'Delete',icon:'/icons/delete.png',disabled:(state=='r'||state=='p'),tooltip:'Delete VM'});
    }else if(nodetype=="IMAGE_GROUP"){
        items.push({id: 'import_appliance',text: 'Import Appliance',icon:'/icons/add_appliance.png'});
        items.push("-");
        items.push({id: 'rename_image_group',text: 'Rename',icon:'/icons/rename.png'});
        items.push({id: 'remove_image_group',text: 'Remove',icon:'/icons/delete.png'});
    }else if(nodetype=="IMAGE"){
        items.push({id: 'provision_image',text: 'Provision',icon:'/icons/provision_vm.png'});
        items.push("-");
        items.push({id: 'edit_image_settings',text: 'Edit Settings',icon:'/icons/file_edit.png'});
        items.push({id: 'edit_image_script',text: 'Edit Script',icon:'/icons/file_edit.png'});
        items.push({id: 'edit_image_desc',text: 'Edit Description',icon:'/icons/file_edit.png'});
        items.push("-");
        items.push({id: 'clone_image',text: 'Create Like',icon:'/icons/clone.png'});
        items.push({id: 'rename_image',text: 'Rename',icon:'/icons/rename.png'});
        items.push({id: 'remove_image',text: 'Remove',icon:'/icons/delete.png'});
    }

    var contextmenu=new Ext.menu.Menu({
        items: items,
        ignoreParentClicks :true,
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
    return contextmenu;
}

function getApplianceMenu(rows){
    var items=new Array();
    for(var i=0;i<rows.length;i++){
        if(rows[i].name=="--")
            items.push("-");
        else
            items.push({id: rows[i].value,text: rows[i].name});
    }
    var sub_menu=new Ext.menu.Menu({
        items: items,
        listeners: {
            itemclick: function(item) {
                //To avoid separator
                if(item.id.substring(0,8)=='ext-comp')
                    return
                var node = item.parentMenu.parentMenu.contextNode;
                if (!node)
                    return;
                handleApplianceEvents(node,item.id,item);
            }
        }
    });
    var appliance_menu = new Ext.menu.Item({
        text: _('Appliance'),
        icon:'/icons/appliance.png',
        menu: sub_menu
    });

    return appliance_menu;
}

//function showVMMenu(node,c,e){
//    if(c.items.findIndex("text","Appliance")<0){
//        var dom_id=node.attributes.nodeid;
//        var node_id=node.parentNode.attributes.nodeid;
//        var group_id=node.parentNode.parentNode.attributes.nodeid;
//        var url="/appliance/get_appliance_menu_items?dom_id="+dom_id+"&node_id="+node_id+"&group_id="+group_id;
//        var ajaxReq = ajaxRequest(url,0,"GET",true);
//        ajaxReq.request({
//            success: function(xhr) {//alert(xhr.responseText);
//                var response=Ext.util.JSON.decode(xhr.responseText);
//                if(response.success){
//                    if(response.rows!=null && response.rows.length>0){
//                        var sub_menu=getApplianceMenu(response.rows);
//                        c.add(sub_menu);
//                    }
//                }else{
//                    Ext.MessageBox.alert("Failure",response.msg);
//                }
//                c.contextNode = node;
//                c.showAt(e.getXY());
//            },
//            failure: function(xhr) {
//                Ext.MessageBox.alert( "Failure " , xhr.statusText);
//                c.contextNode = node;
//                c.showAt(e.getXY());
//            }
//        });
//    }else{
//        c.contextNode = node;
//        c.showAt(e.getXY());
//    }
//}

function showContextMenu(node,e){
    //node.select();
    var cur_node=leftnav_treePanel.getSelectionModel().getSelectedNode();
    if(cur_node!=null && node.attributes.id!=cur_node.attributes.id){
        node.fireEvent('click',node);
    }
    
    var c=new Ext.menu.Menu({
        items: [],
        minWidth: 275,
        listeners: {
            itemclick: function(item) {
                //To avoid separator
                if(item.id.substring(0,8)=='ext-comp')
                    return
                var node = item.parentMenu.contextNode;
                if (!node)
                    return;
                //alert(node+"-----"+item.id+"------"+item);
                handleEvents(node,item.id,item);
            }
        }
    });

//    if(node.attributes.nodetype=="DOMAIN"){
//        showVMMenu(node,c,e);
//    }else{
        var node_id=node.attributes.id;
        var url="/get_context_menu_items?node_id="+node_id+"&node_type="+node.attributes.nodetype;
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    if(response.rows!=null){
                        var menu=createMenu(response.rows);
                        c=menu;
                        if(node.attributes.nodetype=="DOMAIN"){
                            var dom_id=node.attributes.nodeid;
                            var node_id=node.parentNode.attributes.id;
                            var url="/appliance/get_appliance_menu_items?dom_id="+dom_id+"&node_id="+node_id;
                            var ajaxReq = ajaxRequest(url,0,"GET",true);
                            ajaxReq.request({
                                success: function(xhr) {//alert(xhr.responseText);
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                        if(response.rows!=null && response.rows.length>0){
                                            var sub_menu=getApplianceMenu(response.rows);
                                            c.add(sub_menu);
                                        }
                                    }else{
                                        Ext.MessageBox.alert(_("Failure"),response.msg);
                                    }
                                    c.contextNode = node;
                                    c.showAt(e.getXY());
                                },
                                failure: function(xhr) {
                                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                                    c.contextNode = node;
                                    c.showAt(e.getXY());
                                }
                            });
                            return;
                        }
                    }
                }else{
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                }
                c.contextNode = node;
                c.showAt(e.getXY());
            },
            failure: function(xhr) {
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                c.contextNode = node;
                c.showAt(e.getXY());
            }
        });
    //}
}

function createMenu(rows){
    var items=new Array();
    for(var i=0;i<rows.length;i++){
        if(rows[i].name=="--")
            items.push("-");
        else 
            items.push({id: rows[i].value,text: rows[i].text,tooltip:rows[i].text,icon:"/icons/"+rows[i].icon});
    }
    var menu=new Ext.menu.Menu({
        items: items,
	minWidth: 275,
        listeners: {
            itemclick: function(item) {
                //To avoid separator
                if(item.id.substring(0,8)=='ext-comp')
                    return
                var node = item.parentMenu.contextNode;
                if (!node)
                    return;
                //alert(node+"-----"+item.id+"------"+item);
                handleEvents(node,item.id,item);
            }
        }
    });
    return menu;
}
