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
var vm_storage_disk_id=null;
var storage_id=null;
var storage_name=null;
// vmconfig settings main function
function get_panel(action,disk_mode,change_seting_mode,winId,dsk_val) {
    var node = leftnav_treePanel.getSelectionModel().getSelectedNode();
    var child_nodes = node.childNodes;
    if (child_nodes != null && child_nodes != undefined && child_nodes != "") {
        node = child_nodes[0]; //Take first node
    }

    var panel = StorageDefinition(node,"SELECT",null,null,node.id,action,disk_mode,change_seting_mode,winId,dsk_val);
    storage_def.add(panel);
    storage_def.show();
    hidefields("SELECT");
}

function VMConfigSettings(action,node_id,group_id,image_node,state,vm_config,dom_id,mgd_node, vm_id){
    var change_seting_mode="";
    var servername="",osname="";
    var windowid;
    if(mgd_node != null){
        servername=mgd_node.text;
    }
    if(vm_config != null){
        osname=vm_config.os_name;
    }
//    if(state==1||state==2||state==null){
//        change_seting_mode="EDIT_VM_CONFIG";
//    }else if (state=="b"||state=="r"||state==""){
//        change_seting_mode="EDIT_VM_INFO";
//    }
    
    if(state==convirt.constants.RUNNING || state==convirt.constants.PAUSED){
        change_seting_mode="EDIT_VM_INFO";
    }else{
        change_seting_mode="EDIT_VM_CONFIG";
    }

    if (action == "change_vm_settings") {
        disable_location = false;
    } else {
        disable_location = false;
    }

    var platform="";
    var url="/node/get_platform?"
    if(node_id!=null)
        url+="node_id="+mgd_node.attributes.id+"&type="+convirt.constants.MANAGED_NODE; 
    else if(image_node!=null)
        url+="node_id="+image_node.attributes.nodeid+"&type="+convirt.constants.IMAGE;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                platform=response.platform;
                vm_device_store.load({
                    params:{
                        platform:platform
                    }
                });
                platform_UI_helper(platform,change_seting_mode,true);
            }
            else
                Ext.MessageBox.alert(_("Failure"),response.msg);
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
    count=0;

    // tree panel for left side tree view
    var treePanel= new Ext.tree.TreePanel({
        region:'west',
        width:180,
        rootVisible:false,
        border: false,
        lines : false,
        id:'treePanel',
        cls:'leftnav_treePanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        listeners: {
            click: function(item) {
                count=0;
                var id=item.id;
                process_panel(card_panel,treePanel,id.substr(4,id.length));
            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text	: 'Root Node',
        draggable: false,
        id		: 'rootnode',
        listeners: {
            expand : function(btn) {
                treePanel.getNodeById("node0").select();
            }
        }
    });
    var generalNode = new Ext.tree.TreeNode({
        text: _('General'),
        draggable: false,
        id: "node0",
        icon:'icons/vm-general.png',
        nodeid: "general",
        leaf:false,
        allowDrop : false
       // cls:"labelcolor"
    });

    var disksNode = new Ext.tree.TreeNode({
        text: _('Storage'),
        draggable: false,
        id: "node1",
        nodeid: "disk",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var networkNode = new Ext.tree.TreeNode({
        text: _('Networks'),
        draggable: false,
        id: "node2",
        nodeid: "network",
        icon:'icons/vm-network.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var bootparamsNode = new Ext.tree.TreeNode({
        text: _('Boot Params'),
        draggable: false,
        id: "node3",
        icon:'icons/vm-boot-param.png',
        nodeid: "bootparams",
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });


    var miscellaneousNode = new Ext.tree.TreeNode({
        text: _('Miscellaneous'),
        draggable: false,
        id: "node4",
        nodeid: "disk",
        icon:'icons/vm-misc.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var provisioningNode = new Ext.tree.TreeNode({
        text: _('Template Parameters'),
        draggable: false,
        id: "node5",
        nodeid: "disk",
        icon:'icons/templates-parameters.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var leftnavhdg="";
    var vmmatch = action.match("vm")
    if(vmmatch)
        leftnavhdg="Virtual Machine Settings";
    else
        leftnavhdg=_("Template Settings");
    var treeheading=new Ext.form.Label({
        html:'<br/><center><font size="2"></font></center><br/>'
    });

    var side_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:180,
        height:588,
        id:'side_panel',
        cls:'westPanel',
        items:[treeheading,treePanel]

    });



    var params="node_id="+node_id;
    var label_general=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("General")+'<br/></div>'
    });

    // json store for image combo
    var grp_store = new Ext.data.JsonStore({
        url: '/template/get_target_image_groups?'+params,
        root: 'image_groups',
        fields: ['name', 'id'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if(action=="provision_vm"){
                    image_group.setValue(recs[0].get('id'));
                    image_group.fireEvent('select',image_group,recs[0],0);
                }
            }
        }
    });
    if (action!="edit_image_settings" && action!="change_vm_settings" )
        grp_store.load();
    var image_group=new Ext.form.ComboBox({
        fieldLabel: _('Template Group'),
        allowBlank:false,
        triggerAction:'all',
        store: grp_store,
        emptyText :_("Select Template Group"),
        displayField:'name',
        valueField:'id',
        width: 250,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'image_group',
        id:'image_group',
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                var grpid=record.get('id');
                if (action!="edit_image_settings"){
                    image.getStore().load({
                        params:{
                            image_group_id:grpid
                        }
                    });
                    image.setValue("");
                }
            }
        }
    });

    var img_store = new Ext.data.JsonStore({
        url: '/template/get_target_images?'+params,
        root: 'images',
        fields: ['name', 'id', 'group_id'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if(action=="provision_vm"){
                    image.setValue(recs[0].get('id'));
                    image.fireEvent('select',image,recs[0],0);
                }
            }
        }
    });

    var image=new Ext.form.ComboBox({
        fieldLabel: _('Template Name'),
        allowBlank:false,
        triggerAction:'all',
        store: img_store,
        emptyText :_("Select Template Name"),
        displayField:'name',
        valueField:'id',
        width: 250,
        id:'image',
        forceSelection: true,
        name:'image',
        mode:'local',
        listeners:{

            select:function(obj,rec,index){
                //                alert(obj.getValue());
                //                image_id=obj.getValue();
                image_id=rec.get('id');

                var url="/node/get_initial_vmconfig?image_id="+image_id;
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            vm_config=response.vm_config;
                            vmname.setValue("");
                            memory.setValue(vm_config.memory);
                            vcpu.setValue(vm_config.vcpus);
                            os_flavor.setValue(vm_config.os_flavor);
                            osname=vm_config.os_name;
                            os_flavor.fireEvent('select',os_flavor,null,null);
                            os_version.setValue(vm_config.os_version);
                            vm_config_filename.setValue(vm_config.filename);

                            if(vm_config.bootloader.length>0){
                                boot_chkbox.setValue(true);
                                boot_loader.enable();
                                boot_loader.setValue(vm_config.bootloader);
                                bootparams_panel.getComponent("kernel").disable();
                                bootparams_panel.getComponent("ramdisk").disable()
                            }else{
                                boot_chkbox.setValue(false);
                                boot_loader.setValue("/usr/bin/pygrub");
                                boot_loader.disable();
                            }

                            kernel.setValue(vm_config.kernel);
                            ramdisk.setValue(vm_config.ramdisk);
                            root_device.setValue(vm_config.root);
                            kernel_args.setValue(vm_config.extra);
                            for (var i=0;i<shutdown_event_map.getCount();i++){
                                var rec=shutdown_event_map.getAt(i);
                                if (rec.get("id")==vm_config.on_reboot)
                                    on_reboot.setValue(rec.get("value"));
                                if (rec.get("id")==vm_config.on_crash)
                                    on_crash.setValue(rec.get("value"));
                                if (rec.get("id")==vm_config.on_shutdown)
                                    on_shutdown.setValue(rec.get("value"));
                            }
                        }
                        else
                            Ext.MessageBox.alert(_("Failure"),response.msg);
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                    }
                });

                miscellaneous_store.load({
                    params:{
                        image_id:image_id,
                        group_id:group_id,
                        action:action
                    }
                });

                provisioning_store.load({
                    params:{
                        image_id:image_id
                    }
                });

                disks_store.load({
                    params:{
                        image_id:image_id,
                        mode:action,
                        group_id:group_id,
                        action:action
                    }
                });
                network_store.load({
                    params:{
                        image_id:image_id
                    //                        mode:action
                    }
                });
            }
        }
    });

    var server=new Ext.form.TextField({
        fieldLabel: _('Server'),
        name: 'server_name',
        width: 235,
        id: 'server_name',
        allowBlank:false

    });

    var vm_name_exist_flag = false;
    var vmname=new Ext.form.TextField({
        fieldLabel: _('VM'),
        name: 'vmname',
        width: 235,
        id: 'vmname',
        allowBlank:false,
        enableKeyEvents:true
        ,
        listeners:{
            keyup:function(textbox,e){
                if (action=="change_vm_settings"){
                    var l = vm_config.filename.split("/");
                    var path ='';
                    for(var i=1;i<l.length-1;i++){
                        path += '/'+l[i];
                    }
                    vm_config_filename.setValue(path+"/"+textbox.getValue());
                }else{
                    vm_config_filename.setValue(vm_config.filename+"/"+textbox.getValue());
                }
            },
            blur:function(textbox,e){
                var url="/node/check_vm_name?vm_name="+textbox.getValue()+"&vm_id="+vm_id;
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                        success: function(xhr) {//alert(xhr.responseText);
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                vm_name_exist_flag = false;
                            }else{
                                vm_name_exist_flag = true;
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
     var vm_config_filename=new Ext.form.TriggerField({
            fieldLabel: 'Config File Name',
            name: 'vm_config_filename',
            allowBlank:false,
            id: 'vm_config_filename',
            width:250,
            triggerClass : "x-form-search-trigger"
        });
        vm_config_filename.onTriggerClick = function(){
                var url="";
                if(mgd_node != null){
                    url="node_id="+mgd_node.attributes.id;
                }
                file_browser=new Ext.Window({title:"Select File",width : 515,height: 425,modal : true,resizable : false});
                file_browser.add(FileBrowser("/","",url,true,false,vm_config_filename,file_browser));
                if(!vm_config_filename. disabled)
                    file_browser.show();
        };


    var memory=new Ext.form.TextField({
        fieldLabel: _('Memory (MB)'),
        name: 'memory',
        width: 80,
        id: 'memory',
        allowBlank:false
    });
    var vcpu=new Ext.form.TextField({
        fieldLabel: _('Virtual CPUs'),
        name: 'vcpu',
        width: 80,
        id: 'vcpu',
        allowBlank:false
    });

    var start_vm=new Ext.form.Checkbox({
        fieldLabel: _('Start VM after Provisioning'),
        id: 'start_vm'
    });
    
    var auto_start_vm=new Ext.form.Checkbox({
        fieldLabel: _('Start VM on Server up'),
        id: 'auto_start_vm'
    });
/*
    var os_flavor=new Ext.form.TextField({
        fieldLabel: _('Guest OS Flavor'),
        name: 'os_flavor',
        width: 235,
        id: 'os_flavor',
//        disabled:!(action=="edit_image_settings"||action=="change_vm_settings"),
        allowBlank:false
    });
    var os_name=new Ext.form.TextField({
        fieldLabel: _('Guest OS Name'),
        name: 'os_name',
        width: 235,
        id: 'os_name',
//        disabled:!(action=="edit_image_settings"||action=="change_vm_settings"),
        allowBlank:false
    });
    */   
   var name_rec = Ext.data.Record.create([
        {
            name: 'id',
            type: 'string'
        },
        {
            name: 'name',
            type: 'string'
        }
    ]);
    var os_flavor_store = new Ext.data.SimpleStore({
        fields: ['id', 'name'],
        data : convirt.constants.OS_FLAVORS,
        sortInfo:{
            field:'name',
            direction:'ASC'
        }
    });


    var os_flavor=new Ext.form.ComboBox({
        fieldLabel: _('Guest OS Flavor'),
        name: 'os_flavor',
        id: 'os_flavor',
        allowBlank:false,
        triggerAction:'all',
        store: os_flavor_store,
        emptyText :_("Select OS Flavor"),
        displayField:'name',
        valueField:'id',
        width: 250,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                var flavor=combo.getValue();
                os_names.removeAll();
                os_name.setValue("");
                var tmpname="",j=0;
                var osnames=convirt.constants.OS_NAMES;
                for(var i=0;i<osnames.length;i++){
                    if(osnames[i][2]==flavor){
                        var rec=new name_rec({
                            id: osnames[i][0],
                            name: osnames[i][1]
                        });
                        tmpname=(j==0)?osnames[i][1]:tmpname;
                        os_names.add([rec]);
                        j++;
                    }
                }
                os_names.sort('name','ASC');
                if(osname!=""){
                    os_name.setValue(osname);
                    osname="";
                }else{
                    os_name.setValue(tmpname);
                }
            }
        }
     });      

    var os_names = new Ext.data.SimpleStore({
        fields: ['id', 'name'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        data : []
    });
    var os_name=new Ext.form.ComboBox({
        fieldLabel: _('Guest OS Name'),
        name: 'os_name',
        id: 'os_name',
        allowBlank:false,
        triggerAction:'all',
        store: os_names,
        emptyText :_("Select OS Name"),
        displayField:'name',
        valueField:'id',
        width: 250,
        //forceSelection: true,
        mode:'local'
     }); 

    var os_version=new Ext.form.TextField({
        fieldLabel: _('Guest OS Version'),
        name: 'os_version',
        width: 235,
        id: 'os_version',
//        disabled:!(action=="edit_image_settings"||action=="change_vm_settings"),
        allowBlank:false
    });

//    var update_template=new Ext.form.Checkbox({
//        fieldLabel: _('Update Template'),
//        id:'update_template'
//    })
    var template_version=new Ext.form.TextField({
        fieldLabel: _('Template Version'),
        name: 'version',
        width: 80,
        id: 'template_version',
        allowBlank:false
//        enableKeyEvents:true
        //listeners:{  }
    });

    // General Panel declaration

    var tlabel_general=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("General")+'</div>'
    });
    var general_panel=new Ext.Panel({
        height:370,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        tbar:[tlabel_general]
    });

    var general_details_panel=new Ext.Panel({
        id:"panel0",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:120,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[general_panel]
    });

    //general_panel.add(label_general,general_panel);

    var disk_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("Storage")+'<br/></div>'
    });


    var disks_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Type"),
        width: 60,
        dataIndex: 'type',
        sortable:true
    },

    {
        header: _("Location"),
        width: 190,
        dataIndex: 'filename'
    },

    {
        header: _("VM Device"),
        width: 80,
        dataIndex: 'device'
    },

    {
        header: _("Mode"),
        width: 40,
        dataIndex: 'mode'
    },

    {
        header: _("Option"),
        width: 40,
        dataIndex: 'option',
        hidden:true
    },

    {
        header: _("Disk Create"),
        width: 40,
        dataIndex: 'disk_create',
        hidden:true
    },

    {
        header: _("Size"),
        width: 40,
        dataIndex: 'size',
        hidden:true
    },

    {
        header: _("Disk Type"),
        width: 40,
        dataIndex: 'disk_type',
        hidden:true
    },

    {
        header: _("Template Src"),
        width: 40,
        dataIndex: 'image_src',
        hidden:true
    },

    {
        header: _("Template Src Format"),
        width: 40,
        dataIndex: 'image_src_type',
        hidden:true
    },

    {
        header: _("Template Src Format"),
        width: 40,
        dataIndex: 'image_src_format',
        hidden:true
    },

    {
        header: _("File System"),
        width: 40,
        dataIndex: 'fs_type',
        hidden:true
    },
    {
        header: _("Storage Name"),
        width: 150,
        dataIndex: 'storage_name',
        hidden:false
    },
    {
        header: _("Storage Disk Id"),
        width: 150,
        dataIndex: 'storage_disk_id',
        hidden:true
    },
    {
        header: _("Storage Id"),
        width: 150,
        dataIndex: 'storage_id',
        hidden:true
    },
    {
        header: _("Shared"),
        width: 48,
        dataIndex: 'shared',
        renderer:show_disk_checkbox,
        hidden:true
    }
    ]);


    var disks_store = new Ext.data.JsonStore({
        url: '/node/get_disks',
        root: 'disks',
        fields: ['type','filename','device','mode',{
            name:'shared',
            type: 'boolean'
        },'option','disk_create',
        'size','disk_type','image_src','image_src_type','image_src_format',
        'fs_type','storage_disk_id','storage_id','storage_name','sequence'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });

    var disk_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var network_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var misc_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var prov_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });


    var rem_button= new Ext.Button({
        id: 'remove',
        text: _('Delete'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                disks_grid.getStore().remove(disks_grid.getSelectionModel().getSelected());
            }
        }
    });
    var is_remote=new  Ext.form.Hidden({
        id:"is_remote",
        value:false

    });
    var disk_mode="";
    var disk_new_button=new Ext.Button({
        id: 'new',
        text: _('New'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                        
                btn.toggle(true);
                disk_mode="NEW";
                disk_details_panel.show();
                windowid=Ext.id();
                showWindow(_("Storage Details"),450,400,disk_details_panel,windowid);
                disk_new_button.disable();
                disks_grid.disable();
                disk_ref_fldset.hide();
                disks_grid.getSelectionModel().clearSelections();
                var url="/node/get_disks?image_id="+image_id+"&mode=NEW"+
                "&group_id="+group_id+"&action="+action;
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var new_disk=response.disks[0];
                            disks_options.setValue(new_disk.option);
                            //
                            var recs=disks_options.getStore();
                            var new_rec="";

                            for (var i=0;i<recs.getCount();i++){
                                if(new_disk.option==recs.getAt(i).get('id')){
                                    new_rec=recs.getAt(i);
                                    break;
                                }
                            }

                            //                                    var record=disks_options.getStore().get();
                            disks_options.fireEvent('select',disks_options,new_rec,0);
                            disks_type_value=new_disk.type;
                            disk_size.setValue(new_disk.size);
                            if(action=="change_vm_settings" && disk_mode=="NEW")
                                disk_location.setValue("");
                            else
                                disk_location.setValue(new_disk.filename);

                            device_mode.setValue(new_disk.mode);
                            vm_device.setValue(new_disk.device);
                            //                                    d_shared=new_disk.shared;
                            //                                    d_disk_create=new_disk.disk_create;
                            //                                    d_disk_type=new_disk.disk_type;
                            ref_disk_location.setValue(new_disk.image_src);
                            ref_disk_type.setValue(new_disk.image_src_type);
                            format.setValue(new_disk.image_src_format);
                            if(new_disk.fs_type==null)
                                file_system.setValue("");
                            else
                                file_system.setValue(new_disk.fs_type);

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


    var disk_remove_button= new Ext.Button({
        id: 'remove',
        text: _('Remove'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                if(!disks_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select an item from the list"));
                    return false;
                }
                var disk_rec=disks_grid.getSelectionModel().getSelected()
                device=disk_rec.get('device').replace(":cdrom","");
                disks_grid.getStore().remove(disks_grid.getSelectionModel().getSelected());

                    var create_var = device + "_disk_create";
                    var image_src_var = device + "_image_src";
                    var image_src_type_var = device + "_image_src_type";
                    var image_src_format_var = device + "_image_src_format";
                    var size_var = device + "_disk_size";
                    var disk_fs_type_var = device + "_disk_fs_type";
                    var disk_type_var = device + "_disk_type";
                    var device_attribute=new Array(create_var,image_src_var,image_src_type_var,image_src_format_var,
                        size_var,disk_fs_type_var,disk_type_var);
                   
                    for (var i=provisioning_store.getCount()-1;i>=0;i--){
                        var rec=provisioning_store.getAt(i);
                        for(var j=0;j<device_attribute.length;j++){
                            if(rec.get("attribute")==device_attribute[j]){
                                provisioning_store.remove(rec);
                            }
                        }
                    }


            }
        }
    });

    var device="";
    var edit_button= new Ext.Button({
        id: 'edit',
        text: _('Edit'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                if(!disks_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select an item from the list"));
                    return false;
                }
                disk_mode="";
                windowid=Ext.id();
                showWindow(_("Storage Details"),450,400,disk_details_panel,windowid);
                //var rec=grid.getStore().getAt(rowIndex);
                var rec=disks_grid.getSelectionModel().getSelected();
                var grid_store=rec;
                device=grid_store.get('device').replace(":cdrom","");
                //                alert(rec.get('type'));
                //                rec.set('id',rec.get('option'));
                disks_options.setValue(rec.get('option'));

                var x=0;
                while(x<disks_options_store.getCount()){
                    if(disks_options_store.getAt(x).get('id')==rec.get('option')){
                        rec=disks_options_store.getAt(x);
                        break;
                    }
                    x++;
                }
                disks_type_store.load({
                    params:{
                        type:rec.get('id'),
                        mode:action
                    }
                });
                disks_options.fireEvent('select',disks_options,rec,0);

                disk_location.setValue(grid_store.get('filename'));
                vm_device.setValue(grid_store.get('device'));
                device_mode.setValue(grid_store.get('mode'));
                disk_size.setValue(grid_store.get('size'));
                ref_disk_type.setValue(grid_store.get('image_src_type'));
                ref_disk_location.setValue(grid_store.get('image_src'));
                format.setValue(grid_store.get('image_src_format'));
                disks_type_value=grid_store.get('type');
                if(grid_store.get('fs_type')==null)
                    file_system.setValue("");
                else
                    file_system.setValue(grid_store.get('fs_type'));
                disk_new_button.toggle(false);
                disks_grid.disable();
                disk_details_panel.setVisible(true);
            // disks_grid.getStore().remove(disks_grid.getSelectionModel().getSelected());
            }
        }
    });
    var up_button= new Ext.Button({
        id: 'up',
        text: _('Up'),
        icon:'icons/arrow_up.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                    if(!disks_grid.getSelectionModel().getSelected()){
                        Ext.MessageBox.alert(_("Error"),_("Please select an item from the list"));
                        return false;
                    }
                    var selected_rec=disks_grid.getSelectionModel().getSelected();
                    var selected_idx=disks_grid.getStore().indexOf(selected_rec);
                    if (selected_idx>0){
                        var up_rec=disks_grid.getStore().getAt(selected_idx-1);
                        disks_grid.getStore().remove(selected_rec);
                        disks_grid.getStore().remove(up_rec);

                        disks_grid.getStore().insert(selected_idx-1,selected_rec);
                        disks_grid.getStore().insert(selected_idx,up_rec);
                        disks_grid.getSelectionModel().selectRow(selected_idx-1);
                    }
                }
            }
    });
    var down_button= new Ext.Button({
        id: 'down',
        text: _('Down'),
        icon:'icons/arrow_down.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                    if(!disks_grid.getSelectionModel().getSelected()){
                        Ext.MessageBox.alert(_("Error"),_("Please select an item from the list"));
                        return false;
                    }
                    var selected_rec=disks_grid.getSelectionModel().getSelected();
                    var selected_idx=disks_grid.getStore().indexOf(selected_rec);
                    if (selected_idx<disks_grid.getStore().getCount()-1){
                        var down_rec=disks_grid.getStore().getAt(selected_idx+1);
                        disks_grid.getStore().remove(selected_rec);
                        disks_grid.getStore().remove(down_rec);

                        disks_grid.getStore().insert(selected_idx,down_rec);
                        disks_grid.getStore().insert(selected_idx+1,selected_rec);
                        disks_grid.getSelectionModel().selectRow(selected_idx+1);
                    }

                }
            }
    });

    var disks_type_value="";
    var disks_grid = new Ext.grid.GridPanel({
        store: disks_store,
        stripeRows: true,
        colModel:disks_columnModel,
        frame:false,
        border:false,
        selModel:disk_selmodel,
        //autoExpandColumn:1,
        //autoScroll:true,
        //height:'100%',
        height:315,
        width:'100%',
        forceSelection: true,
        enableHdMenu:false,
        id:'disks_grid',
        tbar:[_("<b>Storage</b>"),{
            xtype: 'tbfill'
        },up_button,down_button,is_remote,disk_new_button,edit_button,disk_remove_button],
        listeners:{
            //            rowclick: function(grid, rowIndex, e) {
            // disk_details_panel.setVisible(true);
            //                disk_mode="";
            //                var rec=grid.getStore().getAt(rowIndex);
            //                var grid_store=rec;
            ////                alert(rec.get('type'));
            ////                rec.set('id',rec.get('option'));
            //                disks_options.setValue(rec.get('option'));
            //
            //                var x=0;
            //                while(x<disks_options_store.getTotalCount()){
            //                    if(disks_options_store.getAt(x).get('id')==rec.get('option')){
            //                        rec=disks_options_store.getAt(x);
            //                        break;
            //                    }
            //                    x++;
            //                }
            //                disks_type_store.load({
            //                      params:{
            //                          type:rec.get('id'),
            //                          mode:action
            //                      }
            //                });
            //                disks_options.fireEvent('select',disks_options,rec,0);
            //
            //                disk_location.setValue(grid_store.get('filename'));
            //                vm_device.setValue(grid_store.get('device'));
            //                device_mode.setValue(grid_store.get('mode'));
            //                disk_size.setValue(grid_store.get('size'));
            //                ref_disk_type.setValue(grid_store.get('image_src_type'));
            //                ref_disk_location.setValue(grid_store.get('image_src'));
            //                format.setValue(grid_store.get('image_src_format'));
            //                disks_type_value=grid_store.get('type');
            //                if(grid_store.get('fs_type')==null)
            //                    file_system.setValue("");
            //                else
            //                    file_system.setValue(grid_store.get('fs_type'));
            //                disk_new_button.toggle(false);
            //        fill_details(rec.get('type'),rec.get('location'),rec.get('vm_device'),rec.get('mode'))
            //           }

            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
        }

    });
    
    var disks_options_store = new Ext.data.JsonStore({
        url: '/node/get_disks_options_map',
        root: 'disks_options',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                disks_options.setValue(recs[0].get('value'));
                disks_options.fireEvent('select',disks_options,recs[0],0);
            }
        }
    });
    disks_options_store.load();


    var disks_options=new Ext.form.ComboBox({
        width:150,
        minListWidth:150,
        fieldLabel:_("Options"),
        allowBlank:false,
        triggerAction:'all',
        id:'disks_options',
        store:disks_options_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        selectOnFocus:true,
        mode:'local',
        listeners:{

            select:function(disk_opt,rec,index){
                try {
                    rec_id_temp = rec.get('id');
                } catch (ex) {
                    return;
                }
                if(rec != undefined || rec != null || rec != "") {
                    disks_type_store.load({
                        params:{
                            type:rec.get('id'),
                            mode:action
                        }
                    })
    
                    if(action=="provision_vm"||action=="provision_image"||action=="edit_image_settings"){
    
                        if(rec.get('id')=='USE_REF_DISK')
                        {
                            disk_ref_fldset.show();
                        }else{
                            disk_ref_fldset.hide();
                        }
                        for(var i=0;i<disk_elements.length;i++){
    
                            disk_details_panel.findById(disk_elements[i]).disable();
                        //Ext.get(disk_elements[i]).up('.x-form-item').setDisplayed(false);
                        }
                        var new_elements=disk_elements_map[rec.get('id')];
                        for(i=0;i<new_elements.length;i++){
                            disk_details_panel.findById(new_elements[i]).enable();
                        //Ext.get(new_elements[i]).up('.x-form-item').setDisplayed(true);
                        }
                    }
                }
            }
        }
    });

    var disk_elements=new Array('disks_type','vm_device','disk_size','disk_location','file_system','ref_disk_type','ref_disk_location','format',
        'device_mode');

    var disk_elements_map=new Array();
    disk_elements_map['CREATE_DISK']=new Array('disks_type','disk_size','file_system','disk_location','vm_device','device_mode');
    disk_elements_map['USE_DEVICE']=new Array('disk_location','file_system','vm_device','device_mode');
    disk_elements_map['USE_ISO']=new Array('disk_location','vm_device','device_mode');
    disk_elements_map['USE_REF_DISK']=new Array('disks_type','disk_location','file_system','ref_disk_location',
        'ref_disk_type','format','vm_device','device_mode');


    var disks_type_store = new Ext.data.JsonStore({
        url: '/node/get_disks_type_map',
        root: 'disks_type',
        fields: ['id','value','disk_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(store,recs,opts){
                //                alert(disks_type_value);"Status "
                if(disks_type_value===""){
                    disks_type.setValue(recs[0].get('id'));
                    disks_type.selectedIndex=0;
                }else{                    
                    //                    alert(disks_type_value);
                    disks_type.setValue(disks_type_value);
                    for(var i=0;i<recs.length;i++){
                        if(recs[i].get('id')===disks_type_value){
                            disks_type.selectedIndex=i;
                            break;
                        }
                    }
                    disks_type_value="";
                }
            }
        }
    }); 
    //    disks_type_store.load();
    var disks_type=new Ext.form.ComboBox({
        width: 150,
        minListWidth: 150,
        fieldLabel:_("Type"),
        allowBlank:false,
        triggerAction:'all',
        store:disks_type_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'disks_type'
    });


    var vm_device_store = new Ext.data.JsonStore({
        url: '/node/get_vmdevice_map',
        root: 'vm_device',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    //vm_device_store.load();
    var vm_device=new Ext.form.ComboBox({
        width:75 ,
        fieldLabel:_("VM Device"),
        allowBlank:false,
        triggerAction:'all',
        store:vm_device_store,
        displayField:'value',
        valueField:'id',
        //forceSelection: true,
        editable: true,
        mode:'local',
        id:'vm_device'
    });

    var disk_size=new Ext.form.TextField({
        fieldLabel: _("Size  (MB)"),
        name: 'disk_size',
        width: 75,
        id: 'disk_size',
        allowBlank:false
    });


    var disk_location=new Ext.form.TriggerField({
        fieldLabel: _("Location"),
        name: 'disk_location',
        allowBlank:false,
        id: 'disk_location',
        width:220,
        disabled:disable_location,
        //        disabled:!is_manual,
        triggerClass : "x-form-search-trigger"
    });
    disk_location.onTriggerClick = function(){
        file_browser=new Ext.Window({
            title:_("Select File"),
            width : 515,
            height: 425,
            modal : true,
            resizable : false
        });
        var url="";
        if(mgd_node != null){
            url="node_id="+mgd_node.attributes.id;
        }
        if(!disk_location.disabled){
            file_browser.add(FileBrowser("/","",url,true,false,disk_location,file_browser));
            file_browser.show();
        }
    //            get_disklocation();
    };

    var disk_fs_store = new Ext.data.JsonStore({
        url: '/node/get_disk_fs_map',
        root: 'disk_fs',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    disk_fs_store.load();

    var file_system=new Ext.form.ComboBox({
        width: 85,
        fieldLabel:_("File System"),
        allowBlank:false,
        triggerAction:'all',
        store:disk_fs_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'file_system'
    });

    var ref_disk_location=new Ext.form.TriggerField({
        fieldLabel: _("Ref Loc"),
        name: 'ref_disk_location',
        width: 280,
        id: 'ref_disk_location',
        allowBlank:false,
        triggerClass : "x-form-search-trigger"
    });
    ref_disk_location.onTriggerClick = function(){
        file_browser=new Ext.Window({
            title:_("Select File"),
            width : 515,
            height: 425,
            modal : true,
            resizable : false
        });
        var url="";
        if(mgd_node != null){
            url="node_id="+mgd_node.attributes.id;
        }
        if(!ref_disk_location.disabled){
            file_browser.add(FileBrowser("/","",url,true,false,ref_disk_location,file_browser));
            file_browser.show();
        }
    //            get_disklocation();
    };

    var ref_disk_type_store = new Ext.data.JsonStore({
        url: '/node/get_ref_disk_type_map',
        root: 'ref_disk_type',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    ref_disk_type_store.load();

    var ref_disk_type=new Ext.form.ComboBox({
        width: 85,
        minListWidth: 85,
        fieldLabel:_("Ref Disk Type"),
        allowBlank:false,
        triggerAction:'all',
        store:ref_disk_type_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'ref_disk_type',
        listeners:{
            select:function(combo,record,index){
                format.getStore().load({
                    params:{
                        format_type:record.get('id')
                    }
                })
            }
            }
    });

    var ref_disk_format_store = new Ext.data.JsonStore({
        url: '/node/get_ref_disk_format_map',
        root: 'ref_disk_img_format',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );

    var format=new Ext.form.ComboBox({
        width: 75,
        minListWidth: 75,
        fieldLabel:_("Ref Format"),
        allowBlank:false,
        triggerAction:'all',
        store:ref_disk_format_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'format'
    });
    var device_mode_store = new Ext.data.JsonStore({
        url: '/node/get_device_mode_map',
        root: 'device_mode',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    device_mode_store.load();
    var device_mode=new Ext.form.ComboBox({
        width:90,
        minListWidth: 90,
        fieldLabel:_("Device Mode"),
        allowBlank:false,
        triggerAction:'all',
        store:device_mode_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'device_mode'
    });


    var storage_button=new Ext.Button({
        id: 'storage_button',
        width:120,
        icon:'/icons/storage_pool.png',
        cls:'x-btn-text-icon',
        listeners:{
            click: function(btn) {
                storage_def=new Ext.Window({
                    title:_("Storage Definition"),
                    width : 435,
                    height: 500,
                    modal : true,
                    resizable : false
                });
                var winId=Ext.id();
                var node = leftnav_treePanel.getSelectionModel().getSelectedNode();
                if(node.attributes.nodetype == "IMAGE") {
                    //node = provision_node_tree.getSelectionModel().getSelectedNode();
                    //provision_node_tree is null here (provision_node_tree is related to NodeSelectionDialog). So take Data_Center node
                    node = leftnav_treePanel.getRootNode().childNodes[0]
                }

                if(node.attributes.nodetype == "SERVER_POOL") {
                    //expand the server pool node
                    //we are expanding node here to get the first child node. If the node is not expanded then we will get "undefined" node.
                    node.expand();
                    var dsk_val = disks_options.getValue();
                    //wait for 3 seconds for the node getting expanded. Then try to get childNodes.
                    setTimeout("get_panel('"+action+"','"+disk_mode+"','"+change_seting_mode+"','" +winId+"','"+dsk_val+"')", 3000);
                    /*
                    var child_nodes = node.childNodes;
                    if (child_nodes != null && child_nodes != undefined && child_nodes != "") {
                        node = child_nodes[0]; //Take first node
                    }
                    */
                }else if(node.attributes.nodetype == "DOMAIN") {
                    node = node.parentNode;
                }

                if(node.attributes.nodetype != "SERVER_POOL") {
                    var panel = StorageDefinition(node,"SELECT",null,null,node.id,action,disk_mode,change_seting_mode,winId, disks_options.getValue());
                    storage_def.add(panel);
                    storage_def.show();
                    hidefields("SELECT");
                }
            }

        }
    });
    
    var disk_det_fldset=new Ext.form.FieldSet({
        title: _('Storage Details'),
        collapsible: false,
        autoHeight:true,            
        width:450,
        labelWidth:90,
        layout:'column',

        items: [{
            width: 400,
            layout:'form',
            border:false,
            items:[disks_options]
        },{
            width: 400,
            layout:'form',
            border:false,
            items:[disks_type]
        },
        {
            width: 350,
            layout:'form',
            border:false,
            items:[disk_location]
        },
        {
            width: 50,
            layout:'form',
            border:false,
            items:[storage_button]
        },
        {
            width: 200,
            layout:'form',
            border:false,
            items:[disk_size]
        },
        {
            width: 200,
            layout:'form',
            border:false,
            items:[file_system]
        }
        ]

    });

    var disk_ref_fldset=new Ext.form.FieldSet({
        title: _('Ref Details'),
        collapsible: false,
        autoHeight:true,
        width:450,
        labelWidth:85,
        layout:'column',
        items: [{
            width: 210,
            layout:'form',
            border:false,
            items:[ref_disk_type]
        },
        {
            width: 200,
            layout:'form',
            border:false,
            items:[format]
        },
        {
            width: 430,
            layout:'form',
            border:false,
            items:[ref_disk_location]
        }
        ]

    });
    var disk_vm_fldset=new Ext.form.FieldSet({
        title: _('VM Device Details'),
        collapsible: false,
        autoHeight:true,
        width:450,
        labelWidth:85,
        layout:'column',
        items: [{
            width: 200,            
            layout:'form',
            border:false,
            items:[vm_device]
        },
        {
            width: 200,           
            layout:'form',
            border:false,
            items:[device_mode]
        }

        ]

    });


    var disk_save_button=new Ext.Button({
        id: 'save',
        text: _('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(disk_location.getValue()){
                    var disk_loc=disk_location.getValue();
                    var  x = disk_loc;
                    var invalid_chars=new Array(' ','!','@','#','%','^','&','(',')','|','?','>','<','[',']','*','"',',','"',';','?','\'');
                    for(var i=0;i<x.length;i++){
                        for(var j=0;j<=invalid_chars.length;j++){
                            if(x.charAt(i) == invalid_chars[j]){
                                Ext.MessageBox.alert(_("Error"),_("Disk Location should not contain special characters.<br>")+
                                "space,comma,single quote,double quotes,'!','@','#',<br>,'%','^','&','(',')','|','?','>','<','[',']','*',';','?','\'");
                                return false;
                            }
                        }
                    }
                }

                disk_new_button.enable();
                disks_grid.enable();
                disk_mode="";
                var shared_val=false;
                //                        shared_val=is_remote.getValue();
                if (is_remote.getValue()=="true")
                    shared_val=true;

                //                        alert(shared_val==false);
                is_remote.setValue(false);

                if(disk_new_button.pressed){
                    //                              alert(disks_type.selectedIndex);
                    device=vm_device.getRawValue().replace(":cdrom","");
                    
                    var r=new disk_rec({
                        option: disks_options.getValue(),
                        type: disks_type.getValue(),
                        filename: disk_location.getValue(),
                        device: vm_device.getRawValue(),
                        mode: device_mode.getValue(),

                        fs_type: file_system.getValue(),
                        size: disk_size.getValue(),
                        image_src: ref_disk_location.getValue(),
                        image_src_type: ref_disk_type.getValue(),
                        image_src_format: format.getValue(),
                        disk_type:disks_type.getStore().getAt(disks_type.selectedIndex).get('disk_type'),
                        shared:shared_val,
                        storage_disk_id: vm_storage_disk_id,
                        storage_id: storage_id,
                        storage_name: storage_name
                    //                                    disk_create: 'yes'
                    });
                    if (!vm_device.getRawValue())
                    {
                        Ext.MessageBox.alert(_("Error"),_("Please select Device under VM Device Details") );

                        disks_grid.disable();
                        return false
                    }if (!disk_location.getValue())
                    {
                        Ext.MessageBox.alert(_("Error"),_("Please enter Disk Location") );
                        disks_grid.disable();
                        return false
                    }
                    if(!device_mode.getValue()){
                        Ext.MessageBox.alert(_("Error"),_("Please select Device Mode under VM Device Details") );
                        return false
                    }
                    //Device validation
                    new_device=vm_device.getRawValue().replace(":cdrom","");
                    if(validate_device(disks_store, new_device)==false) return false;
                    disks_store.insert(disks_store.getCount(), r);
                    disk_new_button.toggle(false);
                    //make vm_storage_disk_id null after it is used in disks_store.
                    vm_storage_disk_id=null;
                    storage_id=null;
                    storage_name=null;
                }else{
                    // edit
                    var edit_rec=disks_grid.getSelectionModel().getSelected();

                    if (!vm_device.getRawValue())
                    {
                        Ext.MessageBox.alert(_("Error"),_("Please select Device under VM Device Details") );
                        return false
                    }
                    if (!disk_location.getValue())
                    {
                        Ext.MessageBox.alert(_("Error"),_("Please enter Disk Location"));
                        return false
                    }

                    if(!device_mode.getValue()){
                        Ext.MessageBox.alert(_("Error"),_("Please select Device Mode under VM Device Details") );
                        return false
                    }
                    if(edit_rec.get("device") != vm_device.getRawValue()) {
                        //Device validation
                        new_device=vm_device.getRawValue().replace(":cdrom","");
                        if(validate_device(disks_store, new_device)==false) return false;
                    }

                    //                            alert(edit_rec.get('type'));
                    edit_rec.set('option',disks_options.getValue());
                    edit_rec.set('type',disks_type.getValue());
                    edit_rec.set('filename',disk_location.getValue());
                    edit_rec.set('device',vm_device.getRawValue());
                    edit_rec.set('mode',device_mode.getValue());

                    edit_rec.set('fs_type',file_system.getValue());
                    edit_rec.set('size',disk_size.getValue());
                    edit_rec.set('image_src',ref_disk_location.getValue());
                    edit_rec.set('image_src_type',ref_disk_type.getValue());
                    edit_rec.set('image_src_format',format.getValue());
                    edit_rec.set('disk_type',disks_type.getStore().getAt(disks_type.selectedIndex).get('disk_type'));
                    edit_rec.set('shared',shared_val);

                //                            Ext.MessageBox.alert( "Status " , "Disk Values Edited");
                    var create_var = device + "_disk_create";
                    var image_src_var = device + "_image_src";
                    var image_src_type_var = device + "_image_src_type";
                    var image_src_format_var = device + "_image_src_format";
                    var size_var = device + "_disk_size";
                    var disk_fs_type_var = device + "_disk_fs_type";
                    var disk_type_var = device + "_disk_type";
                    var device_attribute=new Array(create_var,image_src_var,image_src_type_var,image_src_format_var,
                        size_var,disk_fs_type_var,disk_type_var);

//                    alert(provisioning_store.getCount());
                    for (var i=provisioning_store.getCount()-1;i>=0;i--){ 
                        var rec=provisioning_store.getAt(i);
//                        alert(rec.get("attribute"));

                        for(var j=0;j<device_attribute.length;j++){
                            if(rec.get("attribute")==device_attribute[j]){
                                provisioning_store.remove(rec);
                            }
                        }
                    }
//                    alert(provisioning_store.getCount());
                    device=vm_device.getRawValue().replace(":cdrom","");
//                    alert(device);
                    
                }

                var create_var = device + "_disk_create";
                var image_src_var = device + "_image_src";
                var image_src_type_var = device + "_image_src_type";
                var image_src_format_var = device + "_image_src_format";
                var size_var = device + "_disk_size";
                var disk_fs_type_var = device + "_disk_fs_type";
                var disk_type_var = device + "_disk_type";

                var create_value = null;
                if (disks_options.getValue() == "CREATE_DISK"){
                    create_value = "yes";
                    ref_disk_location.setValue("");
                    ref_disk_type.setValue("");
                    format.setValue("");
                }
                if (disks_options.getValue() == "USE_REF_DISK"){
                    if (disks_type.getValue().replace(" ","") == "phy" &&
                        disks_type.getStore().getAt(disks_type.selectedIndex).get('disk_type') == "")
                        create_value = "";
                    else
                        create_value = "yes";
                }

                if (create_value==null || create_value != "yes"){
                    disk_size.setValue(0);
                    if (disks_options.getValue() != "USE_REF_DISK"){
                        ref_disk_location.setValue("");
                        ref_disk_type.setValue("");
                        format.setValue("");
                    }
                }
                var prov_rec = Ext.data.Record.create([
                    {
                        name: 'attribute',
                        type: 'string'
                    },

                    {
                        name: 'value',
                        type: 'string'
                    }
                ]);
                
                var device_attribute=new Array(create_var,image_src_var,image_src_type_var,image_src_format_var,
                size_var,disk_fs_type_var,disk_type_var);
                var device_value=new Array(create_value,ref_disk_location.getValue(),ref_disk_type.getValue(),
                format.getValue(),disk_size.getValue(),file_system.getValue(),
                disks_type.getStore().getAt(disks_type.selectedIndex).get('disk_type'));

                for(var i=0;i<device_attribute.length;i++){
//                    alert(device_attribute[i]+"---"+device_value[i]);
                    if(device_value[i]!=null && device_value[i]!="" && device_value[i]!=0) {
                        var prov_r=new prov_rec({
                                attribute: device_attribute[i],
                                value: device_value[i]
                            });
                        provisioning_store.insert(0, prov_r);
                    }
                }
                closeWindow(windowid,false);
                disk_details_panel.hide();
            }
        }

    })
    var toptbar=new Ext.Panel({
        border:false,
        tbar:[{
            xtype: 'tbfill'
        },disk_new_button,disk_save_button]
    });
    var disk_rec = Ext.data.Record.create([
    {
        name: 'option',
        type: 'string'
    },

    {
        name: 'type',
        type: 'string'
    },

    {
        name: 'filename',
        type: 'string'
    },

    {
        name: 'device',
        type: 'string'
    },

    {
        name: 'mode',
        type: 'string'
    },

    {
        name: 'disk_create',
        type: 'string'
    },

    {
        name: 'size',
        type: 'string'
    },

    {
        name: 'disk_type',
        type: 'string'
    },

    {
        name: 'image_src',
        type: 'string'
    },

    {
        name: 'image_src_type',
        type: 'string'
    },

    {
        name: 'image_src_format',
        type: 'string'
    },

    {
        name: 'fs_type',
        type: 'string'
    },

    {
        name: 'shared',
        type: 'boolean'
    }
    ]);
    
    var cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('Cancel'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                closeWindow(windowid,false);
                disk_new_button.enable();
                disks_grid.enable();
                disk_details_panel.hide();
                disk_new_button.toggle(false);
            }
        }
    });

    var lbldiskinfo=new Ext.form.Label({
        html:'<div class="backgroundcolor">'+
            _("Please click on Save or Cancel to exit")+'</div>',
        hidden:true
    });
    var bottombar=new Ext.Panel({
        border:false,
        bbar:[{
            xtype: 'tbfill'
        }, lbldiskinfo, disk_save_button,cancel_button,disk_new_button]
    })

    var disk_details_panel=new Ext.Panel({
        height:360,
        layout:"form",
        frame:false,
        //cls: 'paneltopborder',
        width:430,
        border:0,
        bodyBorder:false,
        id:'diskdetailspanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[disk_det_fldset,disk_ref_fldset,disk_vm_fldset],
        bbar:[{
            xtype: 'tbfill'
        }, lbldiskinfo, disk_save_button, cancel_button]
    });
    //    disk_details_panel.setVisible(false);

    // disk panel changes
    var disk_lbl=new Ext.form.Label({
        html:_("&nbsp; Use Up or Down arrow to change the sequence of disks. &nbsp;")
    });
    var seq_des=_("The sequence of disks to be saved  will be in the same order as shown in the table.");

    var tooltip_seq=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(seq_des)+'") />'
    })
    var seq_panel=new Ext.Panel({
        id:"seq_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[disk_lbl,tooltip_seq]
    });
    var notshown=true;
    var disks_panel=new Ext.Panel({
        id:"panel1",
        //        width:100,
        //        height:100,
        //        layout:"form",
        //cls: 'paneltopborder',
        frame:false,
        width:440,
        height:425,
        border:true,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[disks_grid,seq_panel]
        ,
        listeners:{
            show:function(p){
                if(disks_store.getCount()>0 && notshown){
                    disks_store.sort('sequence','ASC');
                    notshown=false;
                }
            }
        }
    });

    var network_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("Networks")+'<br/></div>'
    });
    var network_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Name"),
        width: 100,
        dataIndex: 'name',
        sortable:true
    },

    {
        header: _("Details"),
        width: 150,
        sortable: false,
        dataIndex: 'description'
    },

    {
        header: _("MAC"),
        width: 120,
        sortable: false,
        dataIndex: 'mac'
    },
    {
        header: _("Model"),
        width: 80,
        sortable: false,
        dataIndex: 'model'
    }

    ]);

    var network_store = new Ext.data.JsonStore({
        url: "/network/get_nws",
        root: 'rows',
        fields: [ 'name', 'description', 'mac', 'type','bridge','model'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    

    var network_new_button=new Ext.Button({
        id: 'network_new',
        text: _('New'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                //                        btn.toggle(true);
                //                        available_nws.setValue(available_nws.getStore().getAt(0).get('value'));
                btn.toggle(true);
                network_details_panel.show();
                windowid=Ext.id();
                showWindow(_("Network Details"),450,270,network_details_panel,windowid);
                network_new_button.disable();
                network_grid.disable();
                network_grid.getSelectionModel().clearSelections();
                var url="/network/get_new_nw?image_id="+image_id+"&mode="+action+"&node_id="+node_id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            //                                    alert(response.rows[0]);
                            var new_network=response.rows[0];
                            available_nws.setValue(new_network.description);
                            if(new_network.mac=="Autogenerated"){
                                mac_address.setValue("");
                            }else{
                                mac_address.setValue(new_network.mac);
                            }
                            network_model.setValue("");
                        //                                    alert(new_network.mac);
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
    var network_remove_button=new Ext.Button({
        id: 'network_remove',
        text: _('Remove'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                network_grid.getStore().remove(network_grid.getSelectionModel().getSelected());
                var vif="["
                var net_len=network_store.getCount();
                for(var i=0;i<net_len;i++){
                    var mac= network_store.getAt(i).get("mac");
                    if(mac=="Autogenerated")
                        mac="$AUTOGEN_MAC";
                    var bridge= network_store.getAt(i).get("bridge");
                    if(bridge=="Default")
                        bridge="$DEFAULT_BRIDGE";
                    var model=network_store.getAt(i).get("model");
                    vif+="'mac="+mac+", bridge="+bridge+",model="+model+"'";
                    if(i!=net_len-1)
                        vif+=",";
                }
                //                                    alert(vif);
                vif+="]";
                //                                   vif= eval("("+vif+")");
                //                                   alert(vif);
                var misc_len=miscellaneous_store.getCount();
                for(i=0;i<misc_len;i++){
                    var misc_rec1=miscellaneous_store.getAt(i);
                    if (misc_rec1.get('attribute')=="vif"){
                        misc_rec1.set('value',vif);
                    }
                }
            }
        }
    });
    var network_edit_button= new Ext.Button({
        id: 'edit',
        text: _('Edit'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                if(!network_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select an item from the list"));
                    return false;
                }
                windowid=Ext.id();
                showWindow(_("Network Details"),450,270,network_details_panel,windowid);
                available_nws.setValue(network_grid.getSelectionModel().getSelected().get("description"));
                if(network_grid.getSelectionModel().getSelected().get("mac")=="Autogenerated"){
                    mac_address.setValue("");
                    specify_mac.setValue(false);
                }else{
                    mac_address.setValue(network_grid.getSelectionModel().getSelected().get("mac"));
                    specify_mac.setValue(true);
                }
                network_model.setValue(network_grid.getSelectionModel().getSelected().get("model"));
                network_new_button.toggle(false);
                network_grid.disable();
                network_details_panel.setVisible(true);
            // disks_grid.getStore().remove(disks_grid.getSelectionModel().getSelected());
            }
        }
    });
    var network_grid=new Ext.grid.GridPanel({
        store: network_store,
        stripeRows: true,
        colModel:network_columnModel,
        frame:false,
        border:false,
        //autoScroll:true,
        selModel:network_selmodel,
        //autoExpandColumn:1,
        height:315,
        //height: '100%',
        //        width:418,
        width:"100%",
        enableHdMenu:false,
        id:'network_grid',
        tbar:[_("<b>Networks</b>"),{
            xtype: 'tbfill'
        },network_new_button,network_edit_button,network_remove_button],
        listeners:{
            //            rowclick:function(grid, rowIndex, e){
            //  network_details_panel.setVisible(true);
            //                available_nws.setValue(grid.getSelectionModel().getSelected().get("description"));
            //                if(grid.getSelectionModel().getSelected().get("mac")=="Autogenerated"){
            //                    mac_address.setValue("");
            //                }else
            //                    mac_address.setValue(grid.getSelectionModel().getSelected().get("mac"));
            //                network_new_button.toggle(false);
            rowdblclick:function(grid, rowIndex, e){
                network_edit_button.fireEvent('click',network_edit_button);
            }
        }

    });

    var network_save_button=new Ext.Button({
        id: 'network_save',
        text: _('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                network_new_button.enable();
                network_grid.enable();
                var bridge=available_nws.getValue();
                var mac=mac_address.getValue();
                if(mac=="") {
                    mac="$AUTOGEN_MAC";
                }
                var model=network_model.getValue()
                var url="/network/get_nw_det?bridge="+bridge+"&mac="+mac+"&model="+model;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var network_det=response.nw_det[0];

                            if(network_new_button.pressed){
                                var r=new disk_rec({
                                    name: network_det.name,
                                    description: network_det.description,
                                    mac: network_det.mac,
                                    type: network_det.type,
                                    bridge: network_det.bridge,
                                    model:network_det.model
                                });

                                network_store.insert(0, r);
                                network_new_button.toggle(false);
                            }else{
                                // edit
                                var edit_rec=network_grid.getSelectionModel().getSelected();
                                edit_rec.set('name',network_det.name);
                                edit_rec.set('description', network_det.description);
                                edit_rec.set('mac',network_det.mac);
                                edit_rec.set('type',network_det.type);
                                edit_rec.set('bridge',network_det.bridge);
                                edit_rec.set('model',network_det.model);
                            }
                            specify_mac.setValue(false);
                            network_details_panel.hide();
                            network_new_button.toggle(false);
                            closeWindow(windowid,false);
                            //change in misc panel
                            var vif="["
                            var net_len=network_store.getCount();
                            for(var i=0;i<net_len;i++){
                                var mac= network_store.getAt(i).get("mac");
                                if(mac=="Autogenerated")
                                    mac="$AUTOGEN_MAC";
                                var bridge= network_store.getAt(i).get("bridge");
                                if(bridge=="Default")
                                    bridge="$DEFAULT_BRIDGE";
                                var model= network_store.getAt(i).get("model");
                                if (model==null)
                                    model="";
                                vif+="'mac="+mac+", bridge="+bridge+",model="+model+"'";
                                if(i!=net_len-1)
                                    vif+=",";
                            }

                            vif+="]";

                            var misc_len=miscellaneous_store.getCount();
                            var found=false;
                            for(i=0;i<misc_len;i++){
                                var misc_rec1=miscellaneous_store.getAt(i);
                                if (misc_rec1.get('attribute')=="vif"){
                                    found=true;
                                    misc_rec1.set('value',vif);
                                }
                            }
                            if(found==false){
                                var r=new misc_rec({
                                    attribute: 'vif',
                                    value: vif
                                });
                                miscellaneous_store.insert(0, r);
                                miscellaneous_store.sort('attribute','ASC');
                            }

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

    var network_button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('Cancel'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                specify_mac.setValue(false);
                closeWindow(windowid,false);
                network_new_button.enable();
                network_new_button.toggle(false);
                network_grid.enable();
                network_details_panel.hide();
            }
        }
    });
    var lblnwinfo=new Ext.form.Label({
        html:'<div class="backgroundcolor">'+_("Please click on Save or Cancel to exit")+'</div>',
        hidden:true
    });
    var net_toptbar=new Ext.Panel({
        border:false,
        bbar:[{
            xtype: 'tbfill'
        },lblnwinfo,network_save_button,network_button_cancel]
    });


    var nwlb=new Ext.form.Label({
        //        margins: {left:200},
        html:'<div align="left" width="400" style="margin-left:130px"><i>'+
            _("Specify the network that you wish the VM use. ")+'</i></div><br/>'
    });
    var nwlb3=new Ext.form.Label({
        //        margins: {left:200},
        //        text:"Tip: If not Specified, auto generated mac would be used. "
        html:'<div align="right" width="600"><i>'+
            _("Tip: If not Specified, auto generated mac would be used.")+'</i></div>'
    });

    var available_nws_store = new Ext.data.JsonStore({
        url: "/network/get_available_nws?mode="+action+"&op_level=S&node_id="+node_id,
        root: 'rows',
        fields: ['name', 'value'],
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(store,recs,opts){
                available_nws.selectedIndex=0;

            }
        }
    });
    available_nws_store.load();
    var available_nws=new Ext.form.ComboBox({
        fieldLabel: _('Select Network:'),
        store:available_nws_store,
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width:220,
        minListWidth:220,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'available_nws',
        id:'available_nws',
        mode:'local'
    });

    var specify_mac=new Ext.form.Checkbox({
        fieldLabel:_('Specify MAC address:'),
        width: 200,
        checkboxToggle:false,
        checked:false,
        listeners:{
            check:function(combo,checked){
                if (checked) {
                    mac_address.enable();
                } else {
                    mac_address.setValue("");
                    mac_address.disable();
                }
            }
        }
    });
    var mac_address=new Ext.form.TextField({
        fieldLabel: _('MAC address:'),
        name: 'MAC address',
        width: 220,
        id: 'address',
        hidemode:'offset',
        disabled:true

    });

    var network_det_fldset=new Ext.form.FieldSet({
        title: _('Network Details'),
        collapsible: false,
        // autoHeight:true,
        height:250,
        width:420,
        labelWidth:120
    });


    var nw_model = new Ext.data.JsonStore({
        url: "/network/get_network_models",
        root: 'rows',
        fields: ['name', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(store,recs,opts){
                    nw_model.selectedIndex=0;

            }
        }
     });

     nw_model.load();
     var network_model=new Ext.form.ComboBox({
        fieldLabel: _('Network Model:'),
        store:nw_model,
        triggerAction:'all',
        emptyText :"",
        displayField:'value',
        valueField:'value',
        width:220,
        minListWidth:220,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'model_nws',
        id:'model_nws',
        mode:'local'
    });

    network_det_fldset.add(available_nws);
    network_det_fldset.add(nwlb);
    if(action!="change_vm_settings")
        network_det_fldset.add(specify_mac);
    network_det_fldset.add(mac_address);
    network_det_fldset.add(nwlb3);
    network_det_fldset.add(network_model);

    var network_details_panel=new Ext.Panel({
        height:230,
        layout:"form",
        frame:false,
        //        hidden:true,
        //        autoWidth:true,
        width:430,
        border:false,
        bodyBorder:false,
        //        bodyStyle:'padding:0px 0px 0px 0px',
        items:[network_det_fldset],
        bbar:[{
            xtype: 'tbfill'
        },lblnwinfo,network_save_button,network_button_cancel]
    });

    network_details_panel.add(network_det_fldset);
    var network_panel=new Ext.Panel({
        id:"panel2",
        layout:"form",
        //cls:'paneltopborder', 
        frame:false,
        width:440,
        height:425,
        border:0,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[network_grid]
        ,
        listeners:{
            show:function(p){
                if(network_store.getCount()>0){
                    network_store.sort('name','ASC');
                }
            }
        }
    });

    var boot_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("Boot Params")+'<br/></div>'
    });
    var boot_loader=new Ext.form.TextField({
        id: 'boot_loader',
        hideLabel:true,
        width:250
    //        value:'/usr/bin/pygrub'

    });
    var boot_chkbox= new Ext.form.Checkbox({
        boxLabel: _('Boot Loader'),
        name: 'boot_check',
        id: 'boot_check',
        width:106,
        listeners:{
            check:function(field,checked){
                boot_loader_check(bootparams_panel,boot_loader,checked)
            }
        }
    });
    var boot_check=new Ext.form.CheckboxGroup({
        hideLabel: true,
        id: 'boot_check_group',
        items:[boot_chkbox,boot_loader]
    });

    var kernel=new Ext.form.TriggerField({
        fieldLabel: _('Kernel'),
        name: 'kernel',
        id: 'kernel',
        width:250,

        triggerClass : "x-form-search-trigger"
    });
    kernel.onTriggerClick = function(){
        file_browser=new Ext.Window({
            title:_("Select File"),
            width : 515,
            height: 425,
            modal : true,
            resizable : false
        });
        var url="";
        if(mgd_node != null){
            url="node_id="+mgd_node.attributes.id;
        }
        if(!kernel.disabled){
            file_browser.add(FileBrowser("/","",url,true,false,kernel,file_browser));
            file_browser.show();
        }
    };

    var ramdisk=new Ext.form.TriggerField({
        fieldLabel: _('Ramdisk'),
        name: 'ramstorage',
        // allowBlank:false,
        id: 'ramdisk',
        width:250,

        //        disabled:!is_manual,
        triggerClass : "x-form-search-trigger"
    });
    ramdisk.onTriggerClick = function(){
        file_browser=new Ext.Window({
            title:_("Select File"),
            width : 515,
            height: 425,
            modal : true,
            resizable : false
        });
        var url="";
        if(mgd_node != null){
            url="node_id="+mgd_node.attributes.id;
        }
        if(!ramdisk.disabled){
            file_browser.add(FileBrowser("/","",url,true,false,ramdisk,file_browser));
            file_browser.show();
        }
    };

    var root_device=new Ext.form.TextField({
        fieldLabel: _('Root Device'),
        name: 'root_device',
        width: 250,
        id: 'root_device',
        value:''
    });
    var kernel_args=new Ext.form.TextField({
        fieldLabel: _('Kernel Args'),
        name: 'kernel_args',
        width: 250,
        id: 'kernel_args',
        value:''
    });

    var shutdown_event_map = new Ext.data.JsonStore({
        url: '/node/get_shutdown_event_map',
        fields: ['id','value'],
        root: 'shutdown_event_map',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if (vm_config !=null){
                    //                   on_reboot.selectByValue(vm_config.on_reboot,true);
                    for (var i=0;i<recs.length;i++){
                        if (recs[i].get("id")==vm_config.on_reboot)
                            on_reboot.setValue(recs[i].get("value"));
                        if (recs[i].get("id")==vm_config.on_crash)
                            on_crash.setValue(recs[i].get("value"));
                        if (recs[i].get("id")==vm_config.on_shutdown)
                            on_shutdown.setValue(recs[i].get("value"));
                    }
                }
            }
        }
    });
    shutdown_event_map.load();

    var on_shutdown=new Ext.form.ComboBox({
        fieldLabel: _('On Power off'),
        allowBlank:false,
        width: 250,
        store:shutdown_event_map,
        id:'on_shutdown',
        forceSelection: true,
        triggerAction:'all',
        minListWidth:250,
        displayField:'value',
        valueField:'id',
        mode:'local'


    });
    var on_reboot=new Ext.form.ComboBox({
        fieldLabel: _('On Reboot'),
        allowBlank:false,
        width: 250,
        id:'on_reboot',
        store:shutdown_event_map,
        forceSelection: true,
        triggerAction:'all',
        minListWidth:250,
        displayField:'value',
        valueField:'id',
        mode:'local'


    });

    var on_crash=new Ext.form.ComboBox({
        fieldLabel: _('On Crash'),
        allowBlank:false,
        width: 250,
        id:'on_crash',
        store:shutdown_event_map,
        forceSelection: true,
        triggerAction:'all',
        minListWidth:250,
        displayField:'value',
        valueField:'id',
        mode:'local'

    });

    // Boot Params panel declaration

    var tlabel_bootparams=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("Boot Params")+'</div>'
    });
    var bootparams_panel =new Ext.Panel({
        height:'100%',
        layout:"form",
        frame:false,       
        width:'100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        tbar:[tlabel_bootparams]
    });

    var bootparams_details_panel=new Ext.Panel({
        id:"panel3",
        layout:"form",
        width:100,
        height:100,
        //cls: 'whitebackground paneltopborder',        
        frame:false,
        autoWidth:true,
        border:0,
        bodyStyle:'border-top:1px solid #AEB2BA;',
//         items:[boot_label,boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash]
        items:[bootparams_panel]
    });

    // Miscellaneous Panel declaration

    var misce_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading" >'+_("Miscellaneous")+'<br/></div>'
    });

    var miscellaneous_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Attribute"),
        width:150,
        dataIndex: 'attribute',
        css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },

    {
        header: _("Value"),
        dataIndex: 'value',
        editor: new Ext.form.TextField({
//            allowBlank: false
        }),
        sortable:true
    }
    ]);


    var miscellaneous_store = new Ext.data.JsonStore({
        url: '/node/get_miscellaneous_configs',
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(){
                miscellaneous_panel.doLayout();
            }
        }
    }
    );

    var misc_rec = Ext.data.Record.create([
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    }
    ]);

    var misc_add=new Ext.Button({
        name: 'misc_add',
        id: 'misc_add',
        text:_("New"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new misc_rec({
                    attribute: '',
                    value: ' '
                });

                misc_grid.stopEditing();
                miscellaneous_store.insert(0, r);
                misc_grid.startEditing(0, 0);
            }
        }
    });
    var misc_remove=new Ext.Button({
        name: 'misc_remove',
        id: 'misc_remove',
        text:_("Remove"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                misc_grid.getStore().remove(misc_grid.getSelectionModel().getSelected());
            }
        }
    });

    var misc_grid = new Ext.grid.EditorGridPanel({
        store: miscellaneous_store,
        stripeRows: true,
        colModel:miscellaneous_columnModel,
        frame:false,
        border: false,
        selModel:misc_selmodel,
        autoExpandColumn:1,
        //autoExpandMin:325,
        //autoExpandMax:426,
        autoscroll:true,
        //autoHeight:true,
        height:315,
        //height: '100%',
        width: '100%',
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[_("<b>Miscellaneous</b>"),{
            xtype:'tbfill'
        },misc_add,misc_remove]

    });
    //    alert(misc_grid.)
    var miscellaneous_panel=new Ext.Panel({
        id:"panel4",
        layout:"form",
        //width:100,
        //height:100,
        //cls: 'paneltopborder',
        frame:false,
        autoWidth:true,
        //        autoScroll:true,
        border:true,
        //bodyStyle:'padding:0px 0px 0px 0px',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[misc_grid]
        ,
        listeners:{
            show:function(p){
                if(miscellaneous_store.getCount()>0){
                    miscellaneous_store.sort('attribute','ASC');
                }
            }            
        }
    });

    var provisioning_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("Template Parameters")+'<br/></div>'
    });


    var provisioning_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Attribute"),
        width:150,
        dataIndex: 'attribute',
        css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },

    {
        header: _("Value"),
        dataIndex: 'value',
        editor: new Ext.form.TextField({
//            allowBlank: false
        }),
        sortable:true
    }
    ]);


    var provisioning_store = new Ext.data.JsonStore({
        url: '/node/get_provisioning_configs',
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }

    });

    var prov_rec = Ext.data.Record.create([
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    }
    ]);

    var prov_add=new Ext.Button({
        name: 'prov_add',
        id: 'prov_add',
        text:_("New"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new prov_rec({
                    attribute: '',
                    value: ' '
                });

                provisioning_grid.stopEditing();
                provisioning_store.insert(0, r);
                provisioning_grid.startEditing(0, 0);
            }
        }
    });
    var prov_remove=new Ext.Button({
        name: 'prov_remove',
        id: 'prov_remove',
        text:_("Remove"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                provisioning_grid.getStore().remove(provisioning_grid.getSelectionModel().getSelected());
            }
        }
    });
    var provisioning_grid = new Ext.grid.EditorGridPanel({
        store: provisioning_store,
        stripeRows: true,
        colModel:provisioning_columnModel,
        frame:false,
        border: false,
        selModel:prov_selmodel,
        autoExpandColumn:1,
        //autoExpandMin:325,
        //autoExpandMax:426,
        autoscroll:true,
        height:315,
        width:'100%',
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[_("<b>Template Parameters</b>"),{
            xtype: 'tbfill'
        },prov_add,prov_remove]
    });
    // Provisioning panel declaration


    var provisioning_panel=new Ext.Panel({
        id:"panel5",
        layout:"form",
        width:"100%",
        height:390,
        //cls: 'paneltopborder',
        frame:false,
        autoWidth:true,
        border:0,
        //bodyStyle:'padding:0px 0px 0px 0px',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[provisioning_grid]
        ,
        listeners:{
            show:function(p){
                if(provisioning_store.getCount()>0){
                    provisioning_store.sort('attribute','ASC');
                }
            }
        }
    });




    // change setting panel for in mem and on disk radio buttons
    var inmemory=new Ext.form.Radio({
        boxLabel: _('In Memory'),
        id:'inmemory',
        name:'radio',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    platform_UI_helper(platform,change_seting_mode,false);
                    change_seting_mode="EDIT_VM_INFO";
                    platform_UI_helper(platform,change_seting_mode,true);
                    memory.setValue(vm_config.inmem_memory);
                    vcpu.setValue(vm_config.inmem_vcpus);
                }
                radio_check(bootparams_panel,miscellaneous_panel,disks_panel,checked);
            }
            }
    });

    var indisk=new Ext.form.Radio({
        boxLabel: _('On Disk'),
        id:'ondisk',
        name:'radio',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    platform_UI_helper(platform,change_seting_mode,false);
                    change_seting_mode="EDIT_VM_CONFIG";
                    platform_UI_helper(platform,change_seting_mode,true);
                    memory.setValue(vm_config.memory);
                    vcpu.setValue(vm_config.vcpus);
                }
            }
            }
    });

    var radio_group= new  Ext.form.RadioGroup({
        fieldLabel: _('Change Settings'),
        columns: [100, 100],
        vertical: true,
        id:'radiogroup',
        items: [inmemory,indisk]

    });

    var change_settings=new Ext.Panel({
        id:"change_settings",
        width:435,
        layout:"form",
        height:35,
        frame:false,
        border: false,
        hidden:(action=="edit_image_settings"),
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[radio_group]
    });



    var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('Cancel'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                closeWindow();
                disk_details_panel.destroy();
                network_details_panel.destroy();
            }
        }
    });

    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('OK'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if (vm_name_exist_flag == true){
                    Ext.MessageBox.alert(_("Error"),_("VM <b>"+vmname.getValue()+"</b> already exists."));
                    return false;
                }
                if(action=="provision_vm"||action=="provision_image"||action=="change_vm_settings"){
                       //alert('vmname');
                    if(!vmname.getValue())
                    {
                        Ext.MessageBox.alert(_("Error"),_("Please enter VM name under General tab"));
                        return false;
                    }
                    if(vmname.getValue()){                      
                        //var validate=false;
                        var vm_name=vmname.getValue();
                        var  x = vm_name;
                        var invalid_chars=new Array(' ','!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','"',',','"',';',':','?','/','\'');
                        for(var i=0;i<x.length;i++){
                            for(var j=0;j<=invalid_chars.length;j++){
                                if(x.charAt(i) == invalid_chars[j]){
                                    Ext.MessageBox.alert(_("Error"),_("VM Name should not contain special characters.<br>")+
                                    "space,comma,single quote,double quotes,'!','@','#',<br>'$','%','^','&','(',')','|','?','>','<','[',']','{','}','*',';',':','?','/'");
                                    return false;
                                }
                            }
                        }
                    }
                }
                if(action=="change_vm_settings"){
//                    var vert_split=template_version.getValue().split(".");
                    var vers=vm_config.template_versions;
                    if(vers.length!=0){
                        var version=template_version.getValue();
                        if(!version || isNaN(version) ||
                            (version.indexOf(".")==-1) || version.split(".")[1].length!=1 ||
                            (version<1.0)){
                          Ext.MessageBox.alert(_("Error"),
                                _("Please enter proper Template version under General tab. eg:1.2"));
                          return false;
                        }
                        var flag=false;
                        var ver_list="";
                        for(var i=0;i<vers.length;i++){
                            if(version==vers[i])
                                flag=true;
                            ver_list+=vers[i].toFixed(1);
                            if (i!=vers.length-1)ver_list+=", ";
                        }
                        if (!flag){
                            Ext.MessageBox.alert(_("Error"),_("Enter an available Template version  "+
                                ver_list));
                            return false;
                        }
                    }
                }
                       //alert('vmname');
                if(!os_flavor.getValue())
                {
                    Ext.MessageBox.alert(_("Error"),_("Please enter Guest OS Flavor under General tab"));
                    return false;
                }
                if(!os_name.getRawValue())
                {
                    Ext.MessageBox.alert(_("Error"),_("Please enter Guest OS Name under General tab"));
                    return false;
                }
                if(!os_version.getValue())
                {
                    Ext.MessageBox.alert(_("Error"),_("Please enter Guest OS Version under General tab"));
                    return false;
                }

                var misc_recs=miscellaneous_store.getRange(0,miscellaneous_store.getCount());
                var provision_recs=provisioning_store.getRange(0,provisioning_store.getCount());

                //alert('Mode'+change_seting_mode);
                SubmitVMSettings(mgd_node,action,general_panel,bootparams_panel,
                     node_id,group_id,dom_id,image_id,misc_recs,provision_recs,vm_config,
                     change_seting_mode,vm_id)

                disk_details_panel.destroy();
                network_details_panel.destroy();
                closeWindow();
            }
        }
    });

    var button_prev=new Ext.Button({
        id: 'move-prev',
        //text: _('Prev'),
        disabled: true,
        icon:'icons/2left.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                process_panel(card_panel,treePanel,-1);
            }
        }
    });
    var button_next=new Ext.Button({
        id: 'move-next',
        //text: _('Next'),
        icon:'icons/2right.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                process_panel(card_panel,treePanel,1);
            }
        }
    });


    // card panel for all panels
    var card_panel=new Ext.Panel({
        width:435,
        height:400,
        layout:"card",
        id:"card_panel",
        //        activeItem:0,
        cls: 'whitebackground',
        border:false,
        bbar:[
        {
            xtype: 'tbfill'
        },button_prev,button_next,button_ok,button_cancel],
        items:[general_details_panel,disks_panel,network_panel,bootparams_details_panel,miscellaneous_panel]
    //
    });


    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:448,
        height:600,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[change_settings]
    });



    rootNode.appendChild(generalNode);
    rootNode.appendChild(disksNode);
    rootNode.appendChild(networkNode);
    rootNode.appendChild(bootparamsNode);
    rootNode.appendChild(miscellaneousNode);

    treePanel.setRootNode(rootNode);
   

    if(action=="change_vm_settings" ){

        disks_options.disable();
        disk_size.disable();
        file_system.disable();
        ref_disk_location.disable();
        ref_disk_type.disable();
        format.disable();
        //button_prev.hide();
        //button_next.hide();

    }
    if(action=="edit_image_settings"){
       // button_prev.hide();
        //button_next.hide();
    }

    //    alert("memory="+vm_config.inmem_memory);
    var image_id="";


    if (action=="change_vm_settings") {
        general_panel.add(image);
        general_panel.add(server);
        general_panel.add(vmname);
        general_panel.add(template_version);
        template_version.setValue(vm_config.template_version);
        general_panel.add(vm_config_filename);
        memory.setValue(vm_config.memory);
        vcpu.setValue(vm_config.vcpus);
        os_flavor.setValue(vm_config.os_flavor);
        osname=vm_config.os_name;
        os_flavor.fireEvent('select',os_flavor,null,null);
        os_version.setValue(vm_config.os_version);
        vm_config_filename.setValue(vm_config.filename);



        image.setValue(vm_config.image_name);
        image.setDisabled(true);
        server.setValue(servername);
        server.setDisabled(true);
        vmname.setValue(dom_id);
        vmname.setDisabled(false);
        vm_config_filename.disable();

        boot_loader.setValue(vm_config.bootloader);
        if(vm_config.auto_start_vm!=null){
            auto_start_vm.setValue(vm_config.auto_start_vm);
        }else{
            auto_start_vm.setValue(0);
        }

        kernel.setValue(vm_config.kernel);
        ramdisk.setValue(vm_config.ramdisk);
        root_device.setValue(vm_config.root);
        kernel_args.setValue(vm_config.extra);

        //        right_panel.add(change_settings);

        image_id=vm_config.image_id;

        //        specify_mac.setVisible(false);
        mac_address.enable();


    }else if (action =="provision_vm" ){
        image_group.selectedIndex=0;
        image.selectedIndex=0;

        general_panel.add(image_group);
        general_panel.add(image);
        general_panel.add(server);
        general_panel.add(vmname);
        general_panel.add(vm_config_filename);
        //general_panel.add(start_vm);
        server.setValue(servername);
        server.setDisabled(true);
        change_settings.disable();

        rootNode.appendChild(provisioningNode);
        card_panel.add(provisioning_panel);
    }else if(action=="provision_image"){
        change_settings.disable();
        general_panel.add(image_group);
        general_panel.add(image);
        general_panel.add(server);
        general_panel.add(vmname);
        general_panel.add(vm_config_filename);
        image_group.setValue(image_node.parentNode.text);
        image.setValue(image_node.text);
        image.setDisabled(true);
        server.setValue(servername);
        server.setDisabled(true)
        image_group.setDisabled(true);

        image_id=image_node.attributes.nodeid;

        memory.setValue(vm_config.memory);
        vcpu.setValue(vm_config.vcpus);
        os_flavor.setValue(vm_config.os_flavor);
        osname=vm_config.os_name;
        os_flavor.fireEvent('select',os_flavor,null,null);
        os_version.setValue(vm_config.os_version);
        vm_config_filename.setValue(vm_config.filename);

        boot_loader.setValue(vm_config.bootloader);
        kernel.setValue(vm_config.kernel);
        ramdisk.setValue(vm_config.ramdisk);
        root_device.setValue(vm_config.root);
        kernel_args.setValue(vm_config.extra);

        rootNode.appendChild(provisioningNode);
        card_panel.add(provisioning_panel);

    }else if(action=="edit_image_settings"){
        change_settings.disable();
        general_panel.add(image_group);
        general_panel.add(image);
        general_panel.add(template_version);
        //general_panel.add(vm_config_filename);
        if(image_node.parentNode == null){
            image_group.setValue(vm_config.group);
        }else{
            image_group.setValue(image_node.parentNode.text);
        }
        image.setValue(image_node.text);
        image.setDisabled(true);

        image_group.setDisabled(true);

        image_id=image_node.attributes.nodeid;

        //vm_config_filename.setValue(vm_config.filename);
        memory.setValue(vm_config.memory);
        vcpu.setValue(vm_config.vcpus);
//        template_version.setDisabled(true);
        template_version.setValue(vm_config.version);
        os_flavor.setValue(vm_config.os_flavor);
        osname=vm_config.os_name;
        os_flavor.fireEvent('select',os_flavor,null,null);
        os_version.setValue(vm_config.os_version);
        //        vm_config_filename.setDisabled(true);
        //        (function(){
        //            Ext.get("vm_config_filename").setVisible(false);
        //            Ext.get("vm_config_filename").up('.x-form-item').setDisplayed(false);
        //        }).defer(25)

        boot_loader.setValue(vm_config.bootloader);
        kernel.setValue(vm_config.kernel);
        ramdisk.setValue(vm_config.ramdisk);
        root_device.setValue(vm_config.root);
        kernel_args.setValue(vm_config.extra);
        rootNode.appendChild(provisioningNode);
        card_panel.add(provisioning_panel);
        storage_button.setVisible(false);
    }
    disks_type.selectedIndex=0;
    if (state==convirt.constants.RUNNING || state==convirt.constants.PAUSED){
        //        alert(vm_config.inmem_memory);
        inmemory.setValue(true);
        indisk.setValue(false);
        bootparams_panel.disable();
        miscellaneous_panel.disable();
        //        disks_panel.disable();
        //        alert(vm_config);
        memory.setValue(vm_config.inmem_memory);
        vcpu.setValue(vm_config.inmem_vcpus);
    }else if(state==convirt.constants.SHUTDOWN || state==convirt.constants.CRASHED ||
            state==convirt.constants.NOT_STARTED || state==convirt.constants.UNKNOWN ) {
 
        inmemory.disable();
        indisk.setValue(true);
        change_seting_mode="EDIT_VM_CONFIG";
        change_settings.disable();

    }

    // advance settings

    if(action =="change_vm_settings"||action =="edit_image_settings")
    {
        side_panel.enable();

    }else{
        side_panel.enable();
    //adv_show.disable();
    }

    if (action==='edit_image_settings'){
        provisioning_store.load({
            params:{
                image_id:image_id
            }
        });
    }
    if(action=="change_vm_settings" || action=="provision_image"||action=="edit_image_settings"){
        if(vm_config.bootloader.length>0){
            boot_chkbox.setValue(true);
            bootparams_panel.getComponent("kernel").disable();
            bootparams_panel.getComponent("ramdisk").disable();
        }else{
            boot_chkbox.setValue(false);
            boot_loader.setValue("/usr/bin/pygrub");
            boot_loader.disable();
        }


        miscellaneous_store.load({
            params:{
                image_id:image_id,
                node_id:node_id,
                dom_id:dom_id,
                group_id:group_id,
                action:action
            }
        });

        disks_store.load({
            params:{
                image_id:image_id,
                mode:action,
                node_id:node_id,
                dom_id:dom_id,
                group_id:group_id,
                action:action
            }
        });
        network_store.load({
            params:{
                image_id:image_id,
                //                        mode:action,
                dom_id:dom_id,
                node_id:node_id
            }
        });
    }
    if(action=="provision_image"){
        provisioning_store.load({
            params:{
               image_id:image_id
            }
        });
    }


    var outerpanel=new Ext.FormPanel({
        width:900,
        height:445,
        autoEl: {},
        layout: 'column',
        items:[side_panel,right_panel]

    });



    general_panel.add(memory);
    general_panel.add(vcpu);
    general_panel.add(os_flavor);
    general_panel.add(os_name);
    general_panel.add(os_version);
    
    if (action =="provision_vm" || action =="provision_image"){
        general_panel.add(start_vm);
    }
    if (action!='edit_image_settings'){
        general_panel.add(auto_start_vm);
    }
//    if(action==='edit_image_settings'){
//
//    }
    right_panel.add(card_panel);
    //alert(card_panel.getLayout());
    card_panel.activeItem = 2
    card_panel.activeItem = 0
    return outerpanel;

}

function process_panel(panel,treePanel,value)
{

    count=count+parseInt(value);
    //    alert(count);
    if(count==0){
        panel.getBottomToolbar().items.get('move-prev').disable();
    }else{
        panel.getBottomToolbar().items.get('move-prev').enable();
    }
    if (count==panel.items.length-1){
        panel.getBottomToolbar().items.get('move-next').disable();
    }else{
        panel.getBottomToolbar().items.get('move-next').enable();
    }
    panel.getLayout().setActiveItem("panel"+count);
    treePanel.getNodeById("node"+count).select();

}
function boot_loader_check(bootparams_panel,boot_loader,checked){
    if (checked==true){
        boot_loader.enable();
        bootparams_panel.getComponent("kernel").disable();
        bootparams_panel.getComponent("ramdisk").disable();
    }
    else{
        boot_loader.disable();
        bootparams_panel.getComponent("kernel").enable();
        bootparams_panel.getComponent("ramdisk").enable();
    }
}
function radio_check(bootparams_panel,miscellaneous_panel,disks_panel,checked){
    if (checked==true){
        bootparams_panel.disable();
        miscellaneous_panel.disable();
    //        disks_panel.disable();
    }
    else{
        bootparams_panel.enable();
        miscellaneous_panel.enable();
    //        disks_panel.enable();
    }

}

function show_disk_checkbox (value,params,record){
    var id = Ext.id();
    (function(){
        new Ext.form.Checkbox({
            renderTo: id,
            checked:value,
            width:100,
            height:16,
            disabled:true,
            id:"disk_share_check",
            listeners:{
                check:function(field,checked){
                    if(checked==true){
                        record.set('shared',true);
                    }else{
                        record.set('shared',false);
                    }
                }
            }
        });
    }).defer(5)
    return '<span id="' + id + '"></span>';
}
function SubmitVMSettings(node,action,general_panel,bootparams_panel,
                            node_id,group_id,dom_id,image_id,misc_recs,
                            provision_recs,vm_config,mode,vm_id){
                                
    //    dgrid.getRange(0,dgrid.getCount());
    var filename="";
    //alert(general_panel.getComponent('vm_config_filename'));
    if (general_panel.getComponent('vm_config_filename'))
        filename=general_panel.getComponent('vm_config_filename').getValue();
    var memory=general_panel.getComponent('memory').getValue();
    var vcpus=general_panel.getComponent('vcpu').getValue();
    var disk_grid=Ext.getCmp("disks_grid");
    var disk_store=disk_grid.getStore();
    var colModel=disk_grid.getColumnModel();
    var len=colModel.getColumnCount();

    var network_grid=Ext.getCmp("network_grid");
    var network_store=network_grid.getStore();
    var net_colModel=network_grid.getColumnModel();
    var net_len=net_colModel.getColumnCount();

    var general_object=new Object();
    var boot_params_object=new Object();
    var misc_object=new Object();
    var provision_object=new Object();
    var storage_status_object=new Object();
    var network_object=new Object();


    var os_flavor=general_panel.getComponent('os_flavor').getValue();
    var os_name=general_panel.getComponent('os_name').getRawValue();
    var os_version=general_panel.getComponent('os_version').getValue();

    var disk_name=dom_id;
    var vm_name="";
    var version="";
    
    if(action=="change_vm_settings"){
        vm_name=general_panel.getComponent('vmname').getValue();
        version=general_panel.getComponent('template_version').getValue();
        action=mode;
    }else if(action=="provision_vm"||action=="provision_image"){
        action="PROVISION_VM";
        vm_name=general_panel.getComponent('vmname').getValue();
        disk_name=vm_name;
        var start_checked=general_panel.getComponent('start_vm').getValue();
        if(start_checked == true)
            start_checked='yes';
        else
            start_checked='no';
    }else if(action=="edit_image_settings"){
        action="EDIT_IMAGE";
    }

    var auto_start_vm=0;
    if(action!='EDIT_IMAGE'){
        auto_start_vm=general_panel.getComponent('auto_start_vm').getValue();
        if(auto_start_vm == true)
            auto_start_vm=1;
        else
            auto_start_vm=0;
    }
    //
    var disk_stat="[";
    for(var i=0;i<disk_store.getCount();i++){
        disk_stat+="{";
        for(var j=0;j<len;j++){
            var fld=colModel.getDataIndex(j);
            disk_stat+="'"+fld+"':";
            var val=disk_store.getAt(i).get(fld);

            if(val===""){
                disk_stat+="'"+disk_store.getAt(i).get(fld)+"'";
            }else if (val==null) {
                disk_stat+=null;
            //                alert(val+"---"+(val==null));
            }else if (!(isNaN(val))){
                disk_stat+=disk_store.getAt(i).get(fld);
            }else{
                if(fld=="filename" && action!="EDIT_IMAGE"){
                    val=disk_store.getAt(i).get(fld).replace("$VM_NAME",disk_name);
                    disk_stat+="'"+val+"'";
                }else{
                    var value=disk_store.getAt(i).get(fld);
                    if (fld=="type")
                        value=value.replace(" ","")
                    disk_stat+="'"+value+"'";
                }
            }
            disk_stat+=(j==(len-1))?"":",";
        }
        disk_stat+="}";
        
        if (i!=disk_store.getCount()-1)
            disk_stat+=",";
    }
    disk_stat+="]";
    //    alert(disk_stat);

    var disk_jdata= eval("("+disk_stat+")");

    storage_status_object.disk_stat=disk_jdata;

    var vif="["
    for(i=0;i<network_store.getCount();i++){
        //        for(j=0;j<net_len;j++){
        //            var net_fld=net_colModel.getDataIndex(j);
        vif+="{ mac:'"+network_store.getAt(i).get("mac")+"'";
        vif+=","
        vif+="bridge:'"+network_store.getAt(i).get("bridge")+"'";
        vif+=" }"
        //        }
        if (i!=network_store.getCount()-1)
            vif+=","
    }
    vif+="]"
    //    alert(vif);
    //vif= eval("("+vif+")");
    vif=Ext.util.JSON.decode(vif);

    network_object.network=vif;
    //    alert(network_object.network);




    var boot_loader=bootparams_panel.getComponent('boot_check_group').items.get('boot_loader').getValue();
    var boot_check=bootparams_panel.getComponent('boot_check_group').items.get('boot_check').getValue();
    var kernel=bootparams_panel.getComponent('kernel').getValue();
    var ramdisk=bootparams_panel.getComponent('ramdisk').getValue();
    var extra=bootparams_panel.getComponent('kernel_args').getValue();
    var root=bootparams_panel.getComponent('root_device').getValue();
    var on_reboot=bootparams_panel.getComponent('on_reboot').getValue().toLowerCase();
    var on_crash=bootparams_panel.getComponent('on_crash').getValue().toLowerCase();
    var on_shutdown=bootparams_panel.getComponent('on_shutdown').getValue().toLowerCase();

    //    alert(boot_loader+ "--" +boot_check);

    var params;
    var url;
    var ajaxReq;

    for(var i=0;i<misc_recs.length;i++){
        var attribute=misc_recs[i].get("attribute");
        var misc_value="";

        misc_value=process_value(misc_recs[i].get("value"));
        if(attribute!=""){
            try{
                eval('misc_object.'+attribute+'='+misc_value);
            }catch(ex){
                Ext.MessageBox.alert(_('Errors'), _('Invalid value for Attribute: <b>'+attribute+ '</b> '));
                return;
            }
        }
    }

    for(i=0;i<provision_recs.length;i++){
        attribute=provision_recs[i].get("attribute");
        var prov_value=process_value(provision_recs[i].get("value"));
        if(attribute!=""){
            try{
                eval('provision_object.'+attribute+'='+prov_value);
            }catch(ex){
                Ext.MessageBox.alert(_('Errors'), _('Invalid value for Attribute: <b>'+attribute+ '</b> '));
                return;
            }
        }
    }

    general_object.filename=filename;
    general_object.memory=memory;
    general_object.vcpus=vcpus;
    general_object.start_checked=start_checked;
    general_object.auto_start_vm=auto_start_vm;
//    general_object.update_version=update_version;
    general_object.template_version=version;
    //    vm_config.memory=memory;
    //    vm_config.vcpus=vcpus;

    general_object.os_flavor=os_flavor;
    general_object.os_name=os_name;
    general_object.os_version=os_version;
    //alert(os_flavor+"--"+os_name+"--"+os_version);

    boot_params_object.boot_check=boot_check;
    if(boot_check==true){
        boot_params_object.boot_loader=boot_loader;
    }else{
        boot_params_object.kernel=kernel;
        boot_params_object.ramdisk=ramdisk;
    }

    boot_params_object.extra=extra;
    boot_params_object.root=root;

    boot_params_object.on_reboot=on_reboot;
    boot_params_object.on_crash=on_crash;
    boot_params_object.on_shutdown=on_shutdown;

    //    vm_config.kernel=kernel;
    //    vm_config.ramdisk=ramdisk;
    //    vm_config.on_reboot=on_reboot;
    //    vm_config.on_crash=on_crash;

   
    var jsondata= json(general_object,boot_params_object,
    misc_object,provision_object,storage_status_object,network_object);

    params="image_id="+image_id+"&config="+jsondata+"&mode="+action;
    
    if (node_id!=null)
        params+="&node_id="+node_id;
    if (group_id!=null)
        params+="&group_id="+group_id;
    if (vm_id!=null)
        params+="&dom_id="+vm_id;

    if (action=="PROVISION_VM" || action == "EDIT_VM_INFO" || "EDIT_VM_CONFIG")
        params+="&vm_name="+vm_name;
    
    url="/node/vm_config_settings?"+params;    
    if(action == "PROVISION_VM" || action == "EDIT_VM_INFO"){

       vm_config_settings(node,url,action);
       closeWindow(windowid,true);
    }else if(action=="EDIT_IMAGE"){

        var yes_button= new Ext.Button({
            id: 'yes',
            text: _('Yes'),
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            //                enableToggle:true,
            listeners: {
                click: function(btn) {
                    var version=(update_version_panel.getComponent("new_version").getValue()).toString();
//                    var vert_split=version.split(".");
                    if(!version || isNaN(version) ||version.indexOf(".")==-1||
                    version.split(".")[1].length>1 || (version<1.0))
                    {
                        Ext.MessageBox.alert(_("Error"),
                                _("Please enter proper Template version. eg:1.2"));
                        return false;
                    }
                    else if(version <= vm_config.version)
                    {
                       Ext.MessageBox.alert(_("Error"),
                                _("New version must be greater than current version."));
                        return false;
                    }                   

                    general_object.update_version=true;
                    general_object.new_version=version;
                    var jsondata=json(general_object,boot_params_object,
                    misc_object,provision_object,storage_status_object,network_object);
                    params="image_id="+image_id+"&config="+jsondata+"&mode="+action;
                    url="/node/vm_config_settings?"+params;
                    vm_config_settings(node,url,action,vm_config.vm_count,vm_config.old_vmcount,image_id,version,true);
                    closeWindow(windowid,true);
                }
            }
        });
        var no_button= new Ext.Button({
            id: 'no',
            text: _('Skip'),
            icon:'icons/cancel.png',
            cls:'x-btn-text-icon',
            //                enableToggle:true,
            listeners: {
                click: function(btn) {
                    var version=parseFloat(vm_config.version)
                    general_object.update_version=false;
//                    general_object.new_version="";
                    var jsondata= json(general_object,boot_params_object,
                    misc_object,provision_object,storage_status_object,network_object);
                    params="image_id="+image_id+"&config="+jsondata+"&mode="+action;
                    url="/node/vm_config_settings?"+params;
                    vm_config_settings(node,url,action,vm_config.vm_count,vm_config.old_vmcount,image_id,version,false);
                    closeWindow(windowid,true);
                }
            }
        });
        var button_panel=new Ext.Panel({
            id:"button_panel",
            layout:"column",
            width:'100%',
            height:50,
            frame:false,
            bodyStyle:"padding-left:60px",
            items: [
            {
                width: 100,
                layout:'form',
                items:[yes_button]
            },
            {
                width: 100,
                layout:'form',
                items:[no_button]
            }]
        });
        var update_version_panel=update_template_version(vm_config);
        var panel=new Ext.Panel({
            id:"button_panel",
            layout:"column",
//            width:270,
            height:360,
            items:[update_version_panel,button_panel]
        });
        var windowid=Ext.id();
        showWindow(_("Change Version"),278,180,panel,windowid);

    }else{
        vm_config_settings(node,url,action);
    }
}

 function vm_config_settings(node,url,action,vm_count,old_vmcount,image_id,version,update_version){

     Ext.MessageBox.show({
        title:_('Please wait...'),
        msg: _('Please wait...'),
        width:600,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
    //alert('jsondata:'+jsondata.general_object.start_checked);
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);

            Ext.MessageBox.hide();
            if(response.success){
                var msg="";
                if (action =="EDIT_VM_INFO")
                    msg=_("Virtual Machine Configuration Task Submitted");
//                    task_panel_do();
                if (action =="PROVISION_VM"){
                     msg=_("Provision Virtual Machine Task Submitted");
//                     task_panel_do();
                }
                if(action=="EDIT_IMAGE"){
                    msg=_("Template settings changed successfully");
                    if(old_vmcount!=0 || (vm_count != 0 && update_version)){
                        var wid=Ext.id();
                        var panel=show_affected_vms(image_id,wid,version);
                        showWindow(_("Virtual Machines"),300,325,panel,wid,true);
                        return;
                    }
                }
                if(action=="EDIT_VM_CONFIG"){
                    msg=_("Virtual Machine settings changed successfully");
                    node.fireEvent('click',node);
                }

                show_task_popup(msg);
                if (action =="EDIT_VM_INFO" || action =="PROVISION_VM"){
//                    node.fireEvent('click',node);
                }

            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
  }

function set_disklocation(type,disk_context,vm_config_action,disk_mode,change_seting_mode){
    vm_storage_disk_id = null;
    storage_id = null;
    storage_name = null;
    vm_storage_disk_id = disk_context.id;
    vm_storage_allocated = disk_context.storage_allocated;
    vm_name = disk_context.vm_name;
    storage_id = disk_context.storage_id;
    storage_name = disk_context.storage_name;

    if (vm_config_action=="provision_vm"||vm_config_action=="provision_image"){
        var option = Ext.getCmp("disks_options").getValue();
        if (option == "CREATE_DISK"){
            if(disk_context.type != "nfs"){
                Ext.MessageBox.alert( _("Failure") , _("Invalid selection : New disks can be created on file type storage only. Please select a file based (NFS) storage."));
                return false;
            }
        }
        else if (option == "USE_DEVICE"){
            if (disk_context.type == "nfs"){
                Ext.MessageBox.alert( _("Failure") , _("Invalid selection : File based storage(NFS) storage can not be selected for existing disks. Please select iSCSI or AOE storage."));
                return false;
            }
        }
    }

    if(vm_storage_allocated==true) {
        Ext.MessageBox.alert("Failure", "Invalid selection : Storage is already allocated to the Virtual Machine " + vm_name + ".");
        return false;
    }


    if (disk_context.type == "aoe"){
        Ext.getCmp("disk_location").setValue(disk_context.disk);
        Ext.getCmp("disks_type").setValue("phy");
    }else if(disk_context.type == "iscsi"){
        Ext.getCmp("disk_location").setValue(disk_context.interface);
        Ext.getCmp("disks_type").setValue("file");
    }else if(disk_context.type == "nfs"){
        if (disk_context.name == disk_context.disk){
            var d_name = ""
            if (disk_mode == "NEW")
                d_name = "$VM_NAME.disk.xm";
            else{
                var loc = Ext.getCmp("disk_location").getValue();
                if (loc.length>0){
                    var disk_loc_splot=loc.split("/");
                    d_name=disk_loc_splot[disk_loc_splot.length-1];;
                }
            }
            var new_loc=disk_context.disk+"/"+d_name;
            //             alert(new_loc);
            Ext.getCmp("disk_location").setValue(new_loc);
            Ext.getCmp("disks_type").setValue("file");
        }else{
            Ext.getCmp("disk_location").setValue(disk_context.disk);
            Ext.getCmp("disks_type").setValue("file");
        }
        //        alert(Ext.getCmp("disks_type").getStore().getAt(0).get('id'));
//        if (Ext.getCmp("disks_type").getStore().getAt(0).get('id') == "phy"){
//            if (change_seting_mode == "EDIT_VM_CONFIG")
//                Ext.getCmp("disks_type").setValue("phy");
//            else
//                Ext.getCmp("disks_type").setValue("file");
//        }
    }
    Ext.getCmp("is_remote").setValue(true);
    return true;
}

function platform_UI_helper(platform,change_seting_mode,flag){
    var components=new convirt.PlatformUIHelper(platform,change_seting_mode).getComponentsToDisable();
    //alert(components.length+"--"+components);
    for(var z=0;z<components.length;z++){
        Ext.getCmp(components[z]).setDisabled(flag);
    }
}
function update_template_version(vm_config){
    var current_version=new Ext.form.TextField({
        fieldLabel: _('Current Version'),
        name: 'current_version',
        width: 80,
        id: 'current_version',
        disabled:true

    });
    var new_version=new Ext.form.TextField({
        fieldLabel: _('New Version'),
        name: 'new_version',
        width: 80,
        id: 'new_version',
        allowDecimals:true

    });
    var label=new Ext.form.Label({
        html:'<div ><b>'+_("If you have made significant changes, then it is recommended that you change the Template version.")+'</b></div><br/>'
    });

    var update_version_panel=new Ext.Panel({
        id:"update_version_panel",
        layout:"form",
        width:285,
        height:120,
        frame:false,
        labelWidth:130,
        border:0,
        items:[label,current_version,new_version]
    });
    current_version.setValue(vm_config.version);
    if(Ext.getCmp("template_version").getValue() != vm_config.version){
        var new_vers=Ext.getCmp("template_version").getValue();
        new_version.setValue(new_vers);
    }
    else{
        var new_ver=parseFloat(vm_config.version)+parseFloat(0.1);
        new_ver=new_ver.toFixed(1);
        new_version.setValue(new_ver);
    }
    return update_version_panel;
}

function show_affected_vms(image_id,wid,Version){
    var label=new Ext.form.Label({
        html:'<div class="boldlabelheading"><b>'+_("Template settings changed successfully")+'</b></div><br/>'
    });

    var vm_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Name"),
        width: 110,
        dataIndex: 'vm',
        sortable:true
    },

    {
        header: _("Server"),
        width: 110,
        dataIndex: 'server'
    },
    {
        header: _("Version"),
        width: 50,
        dataIndex: 'template_version'
    }
    ]);


    var vms_store = new Ext.data.JsonStore({
        url: "/template/get_template_version_info?image_id="+image_id,
        root: 'rows',
        fields: ['vmid','vm','server','template_version','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });
    vms_store.load();

    var label2=new Ext.form.Label({
        html:'<div ><b>'+("The following virtual machines do not have the latest Template version"+" "+(Version))+'</b></div><br/>'
    });

    var yes_button2= new Ext.Button({
        id: 'yes',
        text: _('Close'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon'
        ,listeners: {
            click: function(btn) {
                closeWindow(wid);
            }
        }
    });
    var label_vm=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Virtual Machines")+'</div>',
        id:'label_vm'
    });
    var vms_grid = new Ext.grid.GridPanel({
        store: vms_store,
        id:'vms_grid',
        stripeRows: true,
        colModel:vm_columnModel,
        frame:false,
        border:false,
//        selModel:disk_selmodel,
        //autoExpandColumn:1,
        autoScroll:true,
        height:220,
        width:'100%',
        forceSelection: true,
        tbar:[label_vm,{
            xtype: 'tbfill'
        }],
        enableHdMenu:false
         ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            }
        }
    });

    var vms_panel=new Ext.Panel({
        id:"vms_panel",
        layout:"form",
        closable:true,
        width:'100%',
        height:300,
        labelWidth:130,
        border:0,
        frame:true,
        items:[label,label2,vms_grid]
    });

    vms_panel.addButton(yes_button2);
    return vms_panel;
}
function json(general_object,boot_params_object,misc_object,provision_object,storage_status_object,network_object){
    var jsondata= Ext.util.JSON.encode({
    "general_object":general_object,
    "boot_params_object":boot_params_object,
    "misc_object":misc_object,
    "provision_object":provision_object,
    "storage_status_object":storage_status_object,
    "network_object":network_object
    });
    return jsondata;

}

function validate_device(disks_store, new_device) {
    //alert(disks_store.getTotalCount());
    for (var i=0;i<disks_store.getCount();i++){
        var rec=disks_store.getAt(i);
        //alert(rec.get("device"));
        if(rec != null) {
            if(rec.get("device").replace(":cdrom","") == new_device) {
                Ext.MessageBox.alert(_("Error"),_("This Device is already used"));
                return false;
            }
        }
    }
    return true;
}

function process_value(value){
     var val=value.toString();
     if (val.charAt(0)==" ")
         val=val.substr(1);
     if(val.charAt(0)=="[" || val.charAt(0)=="{"){
           value=val;
     }else{
           value="'"+value+"'";
     }
     return value;
}
function show_desc(des){
    var id=Ext.id();
    showWindow(_("Information"),300,150,show_panel(des),id,false,true);
}
function show_panel(des){

    var tooltip_des=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<br/><p>'+ unescape(des)+'</p><br/>'
    });
    var tooltip_panel=new Ext.Panel({
        height:200,
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[tooltip_des]
    });
    return tooltip_panel;
}