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

var toolbar,selected_node;
function toolbarPanel(){
    var panel=new Ext.Panel({
        layout:'anchor',
        header:false,
        split:false,
        //height: 25,
        border:false,
        tbar: getToolBar()
    });
    return panel;
}

function getToolBar(){

    var btn_start=new Ext.Button({
        text:"",
        icon:'/icons/small_start.png',
        cls: 'x-btn-icon',
        id:'start',
        handler: toolbarClicked,
        tooltip: _('Start VM'),
        tooltipType : "title"

    });
    var btn_pause=new Ext.Button({
        text:"",
        icon:'/icons/small_pause.png',
        cls: 'x-btn-icon',
        id:'pause',
        handler: toolbarClicked,
        tooltip: _('Pause VM'),
        tooltipType : "title"
    });
    var btn_unpause=new Ext.Button({
        text:"",
        icon:'/icons/small_pause.png',
        cls: 'x-btn-icon',
        id:'unpause',
        handler: toolbarClicked,
        hidden:true,
        tooltip: _('Resume VM'),
        tooltipType : "title"
    });
    var btn_reboot=new Ext.Button({
        text:"",
        icon:'/icons/small_reboot.png',
        cls: 'x-btn-icon',
        id:'reboot',
        handler: toolbarClicked,
        tooltip: _('Reboot VM'),
        tooltipType : "title"
    });
    var btn_shutdown=new Ext.Button({
        text:"",
        icon:'/icons/small_shutdown.png',
        cls: 'x-btn-icon',
        id:'shutdown',
        handler: toolbarClicked,
        tooltip: _('Shutdown VM'),
        tooltipType : "title"
    });
    var btn_kill=new Ext.Button({
        text:"",
        icon:'/icons/small_kill.png',
        cls: 'x-btn-icon',
        id:'kill',
        handler: toolbarClicked,
        tooltip: _('Kill VM'),
        tooltipType : "title"
    });
    var btn_migrate=new Ext.Button({
        text:"",
        icon:'/icons/small_migrate_vm.png',
        cls: 'x-btn-icon',
        id:'migrate',
        handler: toolbarClicked,
        tooltip: _('Migrate VM'),
        tooltipType : "title"
    });
    var btn_snapshot=new Ext.Button({
        text:"",
        icon:'/icons/small_snapshot.png',
        cls: 'x-btn-icon',
        id:'hibernate',
        handler: toolbarClicked,
        tooltip: _('Hibernate VM'),
        tooltipType : "title"
    });
    var btn_restore=new Ext.Button({
        text:"",
        icon:'/icons/small_restore.png',
        cls: 'x-btn-icon',
        id:'restore_hibernated',
        handler: toolbarClicked,
        tooltip: _('Restore Hibernated'),
        tooltipType : "title"
    });
    var btn_console=new Ext.Button({
        text:"",
        icon:'/icons/view_console.png',
        cls: 'x-btn-icon',
        id:'view_console',
        handler: toolbarClicked,
        tooltip: _('View Console'),
        tooltipType : "title"
    });
    var lbl_logout=new Ext.form.Label({
        html:"<a href='/user_logout' style='text-decoration:none;font-weight:bold'>"+_("Logout")+"</a>",
        //icon:'/icons/small_restore.png',
        //cls: 'x-btn-icon',
        id:'logout'        
    });
    var lbl_administration=new Ext.form.Label({
        html:"<a href='#' style='text-decoration:none;font-weight:bold' onclick= javascript:showWindow('Users',705,470,adminconfig());>Admin</a>&nbsp",
        id:'lbl_administration'
    });
    var lbl_user=new Ext.form.Label({
        html:"Welcome "+user_name,
        id:'lbl_user'

    });
    var lbl_task=new Ext.form.Label({
        html:"<a href='#' style='text-decoration:none;font-weight:bold' onclick= javascript:showWindow('Tasks',740,370,Tasks());>Tasks</a>&nbsp",
        id:'lbl_task'
    });

//    toolbar = new Ext.Toolbar({
//        items: [btn_start,'-',btn_pause,btn_unpause,'-',btn_reboot,'-',btn_shutdown,'-',
//        btn_kill,'-',btn_migrate,'-',btn_snapshot,'-',btn_restore,'-',btn_console,{xtype: 'tbspacer'},lbl_user,
//        {xtype: 'tbfill'},lbl_administration,'-',lbl_task,'-',lbl_logout]
//
//    });

    toolbar = new Ext.Toolbar({
        items: [{xtype: 'tbfill'},lbl_administration,'-',lbl_task,'-',lbl_logout]
    });

    return toolbar;
}

function checkToolbar(node){
    selected_node=node;
    toolbar.items.get('start').setDisabled(true);
    toolbar.items.get('pause').setDisabled(true);
    toolbar.items.get('unpause').setDisabled(true);
    toolbar.items.get('reboot').setDisabled(true);
    toolbar.items.get('shutdown').setDisabled(true);
    toolbar.items.get('kill').setDisabled(true);
    toolbar.items.get('migrate').setDisabled(true);
    toolbar.items.get('hibernate').setDisabled(true);
    toolbar.items.get('restore_hibernated').setDisabled(true);
    toolbar.items.get('restore_hibernated').setDisabled(true);
    
    if(node.attributes.nodetype=="DOMAIN"){
        var state=node.attributes.state.replace(/-/g,'');
        state=(state==''||state=='b')?'r':state;
        toolbar.items.get('start').setDisabled(state=='r'||state=='p');
        toolbar.items.get('pause').setDisabled(false);
        toolbar.items.get('unpause').setDisabled(false);
        if(state=='r'){
            toolbar.items.get('unpause').hide();
            toolbar.items.get('pause').show();
        }else if(state=='p'){
            toolbar.items.get('pause').hide();
            toolbar.items.get('unpause').show();
        }else{
            toolbar.items.get('pause').setDisabled(true);
            toolbar.items.get('unpause').setDisabled(true);
        }
        
        toolbar.items.get('reboot').setDisabled(state!='r'&&state!='p');
        toolbar.items.get('shutdown').setDisabled(state!='r'&&state!='p');
        toolbar.items.get('kill').setDisabled(state!='r'&&state!='p');
        toolbar.items.get('migrate').setDisabled(state!='r'&&state!='p');
        toolbar.items.get('hibernate').setDisabled(state!='r'&&state!='p');
        toolbar.items.get('view_console').setDisabled(state!='r'&&state!='p');
        toolbar.items.get('restore_hibernated').setDisabled(true);

    }else if(node.attributes.nodetype=="MANAGED_NODE"){        
        toolbar.items.get('restore_hibernated').setDisabled(false);
    }
    
}

function toolbarClicked(btn){
    //alert(selected_node.text+"--"+btn.id);
    handleEvents(selected_node,btn.id,btn);
}
