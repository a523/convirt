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
var nw_win_popup;
function handleEvents(node,action,item){

    if(node.attributes.nodetype=="DOMAIN"){
        if(action=='hibernate'){
            getNodeProperties(node,node.parentNode,action);
            return;
        }else if(action=='migrate'){
            getTargetNodes(node,node.parentNode,action);
            return;
        }else if(action=='edit_vm_config_file'){
            getVMConfigFile(node,action);
            return;
        }else if(action=='remove_vm_config'){
            removeVMConfigFile(node,action);
            return;
        }else if(action=='set_boot_device'){
            getBootDevice(node,action);
            return;
        }else if(action=='change_vm_settings'){
            changeVmSettings(node,action);
            return;
        }else if(action=='delete'){
            removeVM(node,action);
            return;
        }else if(action=='view_console'){
            select_view(node.parentNode,node);
//            getVNCInfo(node.parentNode,node);
            return;
        } else if(action=='annotate'){
            annotateEntity(node,action);
            return;
        }

        vm_action(node,item);
        return;
    }
    switch (action) {
        case 'add_server_pool':
            addServerPool(node);
            break;
        case 'remove_server_pool':
            removeServerPool(node);
            break;
        case 'add_node':
            showWindow(_("Select Platform"),315,120,select_platform(node));
            break;
        case 'connect_all':
            connectAll(node,null,true);
            break;
        case 'group_provision_settings':
            showWindow(_("Provisioning Settings")+" :- "+node.text,510,375,GroupProvisionSettingsDialog(node));
            break;
        case 'provision_vm':
            Provision(node,null,"provision_vm");
            break;
        case 'edit_node':
            getNodeProperties(null,node,'edit_node');
            break;
       
        case 'ssh_node':
            getSshTerminal(node);
            break;
        case 'migrate_server':
            getTargetSP(node.childNodes,node,node.parentNode,action);
            break;
        case 'connect_node':
            connectNode(node,"","")
            //node.fireEvent('click',node);
            break;
        case 'restore_hibernated':
            getNodeProperties(null,node,'restore');
            break;
        case 'import_vm_config':
            getNodeProperties(null,node,'import');
            break;
        case 'remove_node':
            removeNode(node);
            break;
        case 'start_all':
            server_action(node,item);
            break;
        case 'shutdown_all':
            server_action(node,item);
            break;
        case 'kill_all':
            server_action(node,item);
            break;
        case 'migrate_all':
            getTargetNodes('all',node,action);
            break;
        case 'create_network':
            getTargetNodes(null,node,action);
            break;
        case 'add_image_group':
            addImageGroup(node);
            break;
        case 'remove_image_group':
            removeImageGroup(node);
            break;
        case 'rename_image_group':
            renameImageGroup(node);
            break;
        case 'clone_image':
            cloneImage(node);
            break;
        case 'remove_image':
            removeImage(node);
            break;
        case 'rename_image':
            renameImage(node);
            break;
        case 'edit_image_script':
            editImageScript(node,action);
            break;
        case 'edit_image_desc':
            editImageDesc(node,action);
            break;
        case 'provision_image':
            getTargetNodes(null,node,action);
            break;
        case 'import_appliance':           
//            showApplianceList(node,action);
               showWindow(_("Create Template")+":- "+node.text,400,300 ,templateform(node));
            break;
        case 'storage_pool':
            showWindow(_("Storage")+":- "+node.text,444,495,StorageDefList(node),null,true);
            break;
       case 'edit_image_settings':
            editImageSettings(node,action);
            break;
       case 'manage_virtual_networks':
            nw_win_popup = showWindow(_("Manage Virtual Network")+":- "+node.text,466,450,VirtualNetwork(node),null,true);
           break;
        case 'annotate':
           annotateEntity(node,action);
           break;
    }
}

function confirmAction(node,url,id,action,parentClick){
    if(id=='yes'){
        var ajaxReq=ajaxRequest(url,0,"GET",true); 
        ajaxReq.request({
            success: function(xhr) {                
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){                    
                    if(parentClick){
                        node.parentNode.fireEvent('click',node.parentNode);
                        }                    
                    show_task_popup(response.msg);  
                }
                if(action=="start_view_console"){
                    (function(){
                        select_view(node.parentNode,node);
                    }).defer(response.wait_time*1000)
                }

//                node.parentNode.fireEvent('click',node.parentNode);
//                task_panel_do();
                
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure"), xhr.statusText);
            }
        });
    }
}

function vm_action(vm,btn){
    var url="/node/vm_action";
    var action=btn.id;
    if (action=="start_view_console"){
        action="start";
    }
    url+="?dom_id="+vm.attributes.id+"&node_id="+vm.parentNode.attributes.id+"&action="+action;

    if(btn.id=='start' || btn.id=='start_view_console')
        confirmAction(vm,url,'yes',btn.id);
    else
        Ext.MessageBox.confirm(_("Confirm"),format(_("{0} {1} on {2}? "),btn.tooltip,vm.text,vm.parentNode.text), function (id){
            confirmAction(vm,url,id,btn.id);
        });
}

function server_action(node,btn){
    var url="/node/server_action";
    url+="?node_id="+node.attributes.id+"&action="+btn.id;
   
    Ext.MessageBox.confirm(_("Confirm"), format(_("{0} in {1} on {2}? "),btn.tooltip,node.text,node.parentNode.text), function(id){
        if(id=='yes'){
            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var action_response=Ext.util.JSON.decode(xhr.responseText);
                    if(action_response.success){
                      show_task_popup(action_response.msg);
                    }else{
                        Ext.MessageBox.alert(_("Error"),action_response.msg);
                    }
                    task_panel_do();
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("Failure") + xhr.statusText);
                }
            });
        }
    });
}

function getTargetSP(vm,node,sp,action,objData){
    var url="/node/get_migrate_target_sps?node_id="+node.attributes.id+"&sp_id="+sp.attributes.id;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(eval(res.success)){
                show_dialog_SP(node,res,action,vm,sp,objData);
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
            }
        },
        failure: function(xhr){
            //alert('Fail');
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
            }
        }
    });
}


function removeNode(node){
    var url="/node/remove_node";
    url+="?node_id="+node.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                url+="&force=True"
                var msg="";
                msg+=format(_("Remove {0} from {1}? "), node.text,node.parentNode.text);
                if(response.vms>0){
                    msg+=_("All VMs under this server will be removed. ");
                    msg+="<br>"+_("Related VBDs/Volumes will not be deleted.");
                }                
                Ext.MessageBox.confirm(_("Confirm"),msg, function(id){
                            confirmAction(node,url,id,null,false);
                });
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });    
}

function getNodeProperties(vm,node,action){
    var url="/node/get_node_properties";
    url+="?node_id="+node.attributes.id;

    var ajaxReq=ajaxRequest(url,0,"GET");
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
            if(action=='edit_node')
                show_platform(node,response.node);
            else
                show_dialog(node,response.node,action,vm);

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function importVMConfig(node,directory,filenames){
    //alert(directory+"--"+filenames);
    var url="/node/import_vm_config?node_id="+node.attributes.id+"&directory="+directory+"&filenames="+filenames;
    var ajaxReq=ajaxRequest(url,0,"GET");    
    closeWindow();
    ajaxReq.request({
        success: function(xhr) {
            var import_response=Ext.util.JSON.decode(xhr.responseText);
            if(import_response.success)
                show_task_popup(import_response.msg);
            else
                Ext.MessageBox.alert(_("Error"),import_response.msg);
//            node.fireEvent('click',node);
        },
        failure: function(xhr){
            try{
                var import_response=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), import_response.msg);
            }catch(e){
                Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
            }
        }
    });
}

function addServerPool(node){
    Ext.MessageBox.prompt(_("Add Server Pool"),_("Enter Server Pool Name"),function(btn, text){
        if (btn == 'ok'){
            if(text.length==0){
                Ext.MessageBox.alert(_("Error"),_("Please enter valid Group Name."));
                return;
            }
            var url="/node/add_group?group_name="+text+"&site_id="+node.attributes.id;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        Ext.MessageBox.alert(_("Success"),response.msg);
                        node.fireEvent('click',node);
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

function removeServerPool(node){
    var msg=format(_("All servers in the server pool, {0} will be removed. Continue?"),node.text);
    Ext.MessageBox.confirm(_("Confirm"),msg,function(id){
        if (id == 'yes'){
            var url="/node/remove_group?group_id="+node.attributes.id;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        Ext.MessageBox.alert(_("Success"),response.msg);
                        node.parentNode.fireEvent('click',node.parentNode);
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

function restoreVM(node,directory,filenames){
    //alert(directory+"--"+filenames);
    var url="/node/restore_vm?node_id="+node.attributes.id+"&directory="+directory+"&filenames="+filenames;

    var ajaxReq=ajaxRequest(url,0,"GET");
    ajaxReq.request({
        success: function(xhr) {
            var import_response=Ext.util.JSON.decode(xhr.responseText);
            if(import_response.success)
                Ext.MessageBox.alert(_("Success"),import_response.msg);
            else
                Ext.MessageBox.alert(_("Error"),import_response.msg);
//            node.fireEvent('click',node);
//            task_panel_do();
        },
        failure: function(xhr){
            try{
                var import_response=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), import_response.msg);
            }catch(e){
                Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
            }
        }
    });
   closeWindow();
}

function snapshotVM(node,directory,filenames){
    
    var url="/node/save_vm?dom_id="+node.attributes.id+"&node_id="+node.parentNode.attributes.id+"&directory="+directory+"&filenames="+filenames;
    closeWindow();
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    closeWindow();
    ajaxReq.request({
        success: function(xhr) {
            var import_response=Ext.util.JSON.decode(xhr.responseText);
            if(import_response.success)
                  show_task_popup(import_response.msg);  
//                Ext.MessageBox.alert(_("Success"),import_response.msg);
            else
                Ext.MessageBox.alert(_("Error"),import_response.msg);
//            node.fireEvent('click',node);
//            task_panel_do();
        },
        failure: function(xhr){
            try{
                var import_response=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), import_response.msg);
            }catch(e){
                Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
            }
        }
    });
}

function getTargetNodes(vm,node,action){
    var url="/node/get_migrate_target_nodes?node_id="+node.attributes.id;
    if(action=='provision_image' || action == 'create_network'){
        url="/template/get_image_target_nodes?image_id="+node.attributes.nodeid;
    }
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(eval(res.success)){
                show_dialog(node,res,action,vm)
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
            }
        },
        failure: function(xhr){
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
            }
        }
    });
}

function migrateVM(vm,node,dest_node,live,force){
    var url="",msg="";
    //alert('url='+vm);
    if(vm=='all'){
        url="/node/migrate_vm?dom_name=None&dom_id=None&source_node_id="+node.attributes.id+
        "&dest_node_id="+dest_node.attributes.id+"&live="+live+"&force="+force+"&all=true";
        msg=format(_("Migrate all VMs from {0} to {1}?"),node.text,dest_node.text);
    }else{
        url="/node/migrate_vm?dom_name="+vm.attributes.text+"&dom_id="+vm.attributes.id+"&source_node_id="+node.attributes.id+
        "&dest_node_id="+dest_node.attributes.id+"&live="+live+"&force="+force+"&all=false"; 
        msg=format(_("Migrate {0} from {1} to {2}?"),vm.text,node.text,dest_node.text);
    }   
    //alert(url);
    var args=Ext.util.JSON.encode({
        "force":force,
        "live":live
    });
    args.dest_node=dest_node;
    args.vm=vm;
    args.node=node;
    args.src_node=node;
    
//    closeWindow();
   
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    if(force!='true'){
            Ext.MessageBox.confirm(_("Confirm"), msg , function(id){
                if(id=='yes'){
                    runMigration(ajaxReq,force,node,dest_node,vm,node,live);
                }
            });
    }else{
        runMigration(ajaxReq,force,node,dest_node,vm,node,live);
    }
}

function runMigration(ajaxReq,force,src_node,dest_node,vm,node,live){
    //var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(res.success){
                if(force!='true' && res.rows){
                    showWindow(_("Migration Check Results"),515,325,MigrationChecksDialog(vm,node,dest_node,live,res.rows));
                }else{
//                    src_node.fireEvent('click',src_node);
//                    dest_node.fireEvent('click',dest_node);
                    show_task_popup(res.msg);
//                    task_panel_do();
                }
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
//                task_panel_do();
            }
        },
        failure: function(xhr){
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
            }
        }
    });
}

function connectAll(srvrpool,statusList,start){
    if(statusList==null && start){
        statusList=new Array();
        var ch=srvrpool.childNodes;
        for(var i=0;i<ch.length;i++){
            statusList[i]=new Array();
            statusList[i][0]=ch[i].attributes.nodeid;
            statusList[i][1]=false;
            statusList[i][2]='';
            statusList[i][3]=ch[i];
        }
    }
    //alert(statusList);

    var node;
    for(var i=0;i<statusList.length;i++){
        if(!statusList[i][1]){
            break;
        }
    }
    if(i<statusList.length){
        node=statusList[i][3];
        var url="/node/connect_node?node_id="+node.attributes.id;
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var res=Ext.util.JSON.decode(xhr.responseText);
                if(res.success){
                    //Ext.MessageBox.alert("---",res.msg);
                    statusList[i][1]=true;
                    statusList[i][2]=_('Success');
                    connectAll(srvrpool,statusList,false);
                }else{
                    //Ext.MessageBox.alert("Error",res.error);
                    if(res.error!=_('Not Authenticated')){
                        statusList[i][1]=true;
                        statusList[i][2]=""+node.text+":- "+res.msg;
                        connectAll(srvrpool,statusList,false);
                        return
                    }
                    var form=credentialsForm();
                    form.addButton(_("OK"),function(){
                        if (form.getForm().isValid()) {
                            var uname=form.find('name','user_name')[0].getValue();
                            var pwd=form.find('name','pwd')[0].getValue();
                            closeWindow();
                            form.getForm().submit({
                                url:url,
                                params: {
                                    username:uname,
                                    password:pwd
                                },
                                success: function(form,action) {
                                    statusList[i][1]=true;
                                    statusList[i][2]=_('Success');
                                    connectAll(srvrpool,statusList,false);
                                },
                                failure: function(form, action) {
                                    if(action.result.error!=_('Not Authenticated')){
                                        statusList[i][1]=true;
                                        statusList[i][2]=""+node.text+":- "+action.result.msg;
                                    }
                                    connectAll(srvrpool,statusList,false);
                                }
                            });
                        }else{
                            Ext.MessageBox.alert(_('Errors'), _('Some of the required information is missing.'));
                        }
                    });
                    form.addButton(_("Cancel"),function(){
                        closeWindow();
                        statusList[i][1]=true;
                        statusList[i][2]=node.text+":"+_('Server not Authenticated');
                        connectAll(srvrpool,statusList,false);
                    });
                    showWindow(_("Credentials for ")+node.text,280,150,form);
                }
            },
            failure: function(xhr){
                try{
                    var res=Ext.util.JSON.decode(xhr.responseText);
                    Ext.MessageBox.alert(_("Error"), res.msg);
                }catch(e){
                    Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
                }
            }
        });
    }else if(i==statusList.length){
        srvrpool.fireEvent('click',srvrpool);
        var msg='';
        for(var i=0;i<statusList.length;i++){
            if(statusList[i][2]!=_('Success')){
                msg+=statusList[i][2]+"<br/>";
            }
        }
        if(msg!=''){
            Ext.MessageBox.alert(_("Status"),msg);
        }
    }
}

function getVMConfigFile(vm,action){
    var url="/node/get_vm_config_file?dom_id="+vm.attributes.id+
        "&node_id="+vm.parentNode.attributes.id; 
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
//            var content=xhr.responseText.substring(xhr.responseText.indexOf('data="')+6,xhr.responseText.lastIndexOf('"/>'));
//            content=formatHTML(content);
            showWindow(_("Edit Config File:-")+vm.text,525,500,FileViewEditDialog(response.content,"",'edit','text',vm,action));
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function removeVMConfigFile(vm,action){
    var url="/node/remove_vm_config_file?dom_id="+vm.attributes.id+
        "&node_id="+vm.parentNode.attributes.id;

    Ext.MessageBox.confirm(_("Confirm"), format(_("Remove {0} from list under {1}?"),vm.text,vm.parentNode.text), function(id){
            confirmAction(vm,url,id,null,true);
    });
}

function removeVM(vm,action){
    var url="/node/get_node_status";
    url+="?dom_id="+vm.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var url="/node/remove_vm?dom_id="+vm.attributes.id+
                    "&node_id="+vm.parentNode.attributes.id;
                //alert(response.node_up);
                if(response.node_up === false){
                    url+="&force=True";
                }
                var msg="Delete "+ vm.text+" on "+vm.parentNode.text+"?";
                if(response.node_up === false){
                    msg+="<br>"+_("WARNING: Related VBDs/Volumes will not be deleted "+
                                    "because the server is down.");
                }else{
                    msg+="<br>"+_("WARNING: Related VBDs/Volumes would also be deleted.");
                }
                //showScheduleWindow(vm,msg,url,"delete","");
                Ext.MessageBox.confirm(_("Confirm"), msg, function(id){
                        confirmAction(vm,url,id,action,false);
                });
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function getBootDevice(vm,action){
    var url="/node/get_boot_device?dom_id="+vm.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                showWindow(_("Set Boot Device:-")+vm.text,315,120,BootImageSelection(vm,response.boot));
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
function changeVmSettings(node,action){
   
        var node_id=node.parentNode.attributes.id; 
        var group_id=node.parentNode.parentNode.attributes.id; 
        var dom_id=node.attributes.text;
        var vm_id = node.attributes.id;

        var url="/node/get_vm_config?domId="+node.attributes.text+"&nodeId="+node_id;
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                      showWindow(_("Virtual Machine Config Settings for ")+dom_id,640,480,VMConfigSettings(action,node_id,group_id,null,node.attributes.state,response.vm_config,dom_id,node.parentNode,vm_id));
                  }else{
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        });

}
function editImageSettings(node,action){

        var url="/node/get_initial_vmconfig?image_id="+node.attributes.nodeid+"&mode="+action;
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    var vm_config=response.vm_config;
                    showWindow(_("Template Settings"),640,440,VMConfigSettings(action,null,null,node,null,vm_config,null,null));
                    }
                    else
                        Ext.MessageBox.alert(_("Failure"),response.msg);
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                }
            });
}
function processDrop(e){
    var node=e.dropNode;
    var dest_node=e.target;
    var src_node=e.dropNode.parentNode;
    //alert(node+"--"+dest_node+"--"+src_node+"--"+e.data+"--"+e.point);
    if(dest_node.attributes.nodetype!=src_node.attributes.nodetype){
        Ext.Msg.alert(_("Error"),_("Invalid Drop Location."));
        return ;
    }

    if(node.attributes.nodetype=="DOMAIN"){
        migrateVM(node,src_node,dest_node,true,false);
        return;
    }

    Ext.Msg.confirm(_("Confirm"),format(_("Do you want to move {0} from {1} to {2}?"),node.text,src_node.text,dest_node.text),function(id){
        if(id=='yes'){
            if(node.attributes.nodetype=="IMAGE"){ 
                transferImage(node,src_node,dest_node);
            }else if(node.attributes.nodetype=="MANAGED_NODE"){
                transferNode(node,src_node,dest_node,false);
            }
        }
    });
}

function transferNode(node,src_grp,dest_grp,forcefully){
    var url="/node/transfer_node?node_id="+node.attributes.id+
        "&source_group_id="+src_grp.attributes.id+
        "&dest_group_id="+dest_grp.attributes.id+
        "&forcefully="+forcefully;

    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                src_grp.fireEvent('click',src_grp);
                dest_grp.fireEvent('click',dest_grp);
            }else{
                if(response.msg == "VM_RUNNING") {
                    // Prompt for user data:
                    Ext.Msg.confirm('Warning', 'Moving server from this server pool will detach all storage associated with it. This will cause running VMs using such storage to crash. Do you want to continue ?', function(btn){
                        if (btn == 'yes'){
                            // process node transfer here...
                            transferNode(node,src_grp,dest_grp,true);
                        }
                    });
                }else{
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                }
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
 function select_view(node,dom){
     showWindow(_("View Console"),300,200, select_type(node,dom));

 }

 function getSshTerminal(nod){
    getSshWindow(nod)
 }

 function select_type(node,dom){
     var description=new Ext.form.Label({
         html:_('You can select local viewer for connecting to the Virtual Machine.')+
             '<br/><br/>'
     });
     var use_applet=new Ext.form.Radio({
         boxLabel: _('Use VNC Applet'),
         id:'use_applet',
         name:'radio',
         hideLabel:true,
         checked:true,
         listeners:{
             check:function(field,checked){
                 if(checked){
                     command_combo.disable();
                 }
             }
             }
     });


     var use_localcommand=new Ext.form.Radio({
         boxLabel: _('Use Local Viewer:&nbsp;'),
         id:'use_localcommand',
         name:'radio',
         hideLabel:true,
         listeners:{
             check:function(field,checked){
                if(checked){
                     command_combo.enable();
                }
             }
             }
     });

     var command_store = new Ext.data.JsonStore({
         url: '/node/get_command_list',
         root: 'commands',
         fields: ['id','value'],
         sortInfo:{
             field:'value',
             direction:'DESC'
         },
         successProperty:'success',
         listeners:{
             load:function(obj,resc,f){
                 var vm_console_cookie=getCookie(convirt.constants.VM_CONSOLE);
                 if (vm_console_cookie!=null && vm_console_cookie!=""){
                     if (eval(vm_console_cookie)==true){
                         use_applet.setValue(true);
                     }else{
                         use_localcommand.setValue(true);
                         use_applet.setValue(false);
                         var vm_console_lcmd_cookie=getCookie(convirt.constants.VM_CONSOLE_LOCAL_CMD);
                         if (vm_console_lcmd_cookie!=""){
                             command_combo.setValue(vm_console_lcmd_cookie);
                         }
                     }
                 }
             },
             loadexception:function(obj,opts,res,e){
                 var store_response=Ext.util.JSON.decode(res.responseText);
                 Ext.MessageBox.alert(_("Error"),store_response.msg);
             }
         }
     }
     );

     command_store.load()
     var command_combo=new Ext.form.ComboBox({
                 id:"command_combo",
                 width: 100,
                 fieldLabel: _('Command'),
                 allowBlank:false,
                 triggerAction:'all',
                 store:command_store,
                 disabled:true,
                 hideLabel:true,
                 displayField:'id',
                 valueField:'value',
                 forceSelection: true,
                 mode:'local'
       });

      var combo_panel=new Ext.Panel({
         border:false,
         width:"100%",
         id:"combo_panel",
         layout:'column',
         items:[use_localcommand,command_combo]
         });

      var button_ok=new Ext.Button({
         name: 'ok',
         id: 'ok',
         text:_('OK'),
         icon:'icons/accept.png',
         cls:'x-btn-text-icon',
         listeners: {
             click: function(btn) {
                 setCookie(convirt.constants.VM_CONSOLE,use_applet.getValue());
                 if(use_applet.getValue()){
                    getVNCInfo(node,dom);
                 }else{
                     if(command_combo.getValue()==""){
                         Ext.MessageBox.alert( _("Failure") , "Please select a value from list");
                         return;
                     }
                     setCookie(convirt.constants.VM_CONSOLE_LOCAL_CMD,command_combo.getValue());
                     get_command(command_combo.getValue(),node,dom)
                 }
                closeWindow();

             }
         }});

     var button_cancel=new Ext.Button({
         name: 'cancel',
         id: 'cancel',
         text:_('Cancel'),
         icon:'icons/cancel.png',
         cls:'x-btn-text-icon',
         listeners: {
             click: function(btn) {
                 closeWindow();
             }
         }
     });


     var select_panel=new Ext.Panel({
         id:"select_panel",
         width:286,
         layout:"form",
         height:170,
         frame:true,
         labelWidth:60,
         bbar:[
         {
             xtype: 'tbfill'
         },button_ok,button_cancel],
         items:[description,use_applet,combo_panel]
     });

     return select_panel;
 }

 function get_command(command,node,dom){

     var url="/node/get_command?node_id="+node.attributes.id+"&dom_id="+dom.attributes.id+"&cmd="+command;
     var ajaxReq = ajaxRequest(url,0,"GET",true);
     ajaxReq.request({
         success: function(xhr) {
             var response=Ext.util.JSON.decode(xhr.responseText);
             if(response.success){
                 getCMDInfo(dom,response.cmd,response);
             }else{
                 Ext.MessageBox.alert( _("Failure") , response.msg);
             }
         },
         failure: function(xhr){
             Ext.MessageBox.alert( _("Failure") , xhr.statusText);
         }
     });
 }

 function setCookie(c_name,value,expiredays)
 {
     var exdate=new Date();
     exdate.setDate(exdate.getDate()+expiredays);
     document.cookie=c_name+ "=" +escape(value)+
            ((expiredays==null) ? "" : ";expires="+exdate.toUTCString());
 }


 function getCookie(c_name)
 {
     if (document.cookie.length>0)
       {
       c_start=document.cookie.indexOf(c_name + "=");
       if (c_start!=-1)
         {
             c_start=c_start + c_name.length+1;
             c_end=document.cookie.indexOf(";",c_start);
             if (c_end==-1) c_end=document.cookie.length;
             var cookie_value=unescape(document.cookie.substring(c_start,c_end));
             return cookie_value;
         }
       }
     return "";
 }
 function del_cookie(name) {
     document.cookie = name +
     '=; expires=Thu, 01-Jan-70 00:00:01 GMT;';
 }
