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

function Tasks(){
    var label_task=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Displays submitted task information and their status.")+'</div>',
        id:'label_task'
    });
    var task_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("TaskId"),
        width: 50,
        dataIndex: 'taskid',
        hidden:true        
    },
    {
        header: _("Task"),
        width: 100,
        dataIndex: 'name',
        sortable:true        
    },
    {
        header: _("Entity Name"),
        width: 150,
        dataIndex: 'entname',
        sortable:true
    },
    {
        header: _("Entity Type"),
        width: 100,
        dataIndex: 'enttype',
        sortable:true
    },
    {
        header: _("Username"),
        width: 90,
        dataIndex: 'username',
        sortable:true        
    },
    {
        header: _("Start Time"),
        width: 160,
        dataIndex: 'timestamp',
        sortable:true,
        renderer:format_date
    },
    {
        header: _("End Time"),
        width: 160,
        dataIndex: 'endtime',
        sortable:true,
        renderer:format_date
    },
    {
        header: _("Status"),
        width: 90,
        dataIndex: 'status',
        sortable:true,
        renderer:function(value,params,record,row){
            if(value =='Failed'|| value =='Succeeded'){
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
    }
    ]);

    var task_store =new Ext.data.JsonStore({
        url: "get_tasks",
        root: 'rows',
        fields: ['taskid','entname','enttype','name','username','timestamp','status','errmsg','endtime'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    task_store.load();

    var cancel_button= new Ext.Button({
        id: 'ok',
        text: _('Close'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow();
            }
        }
    });
    var refresh_button=new Ext.Button({
        id: 'refresh_task',
        text: _('Refresh'),
        icon:'icons/refresh.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
             task_grid.getStore().load();
            }
        }
    });
    var task_grid=new Ext.grid.GridPanel({
        store: task_store,
        stripeRows: true,
        colModel:task_columnModel,
        frame:false,
        autoscroll:true,
        height:330,
        width:'100%',
        loadMask:true,
        enableHdMenu:false,
        id:'task_grid',
        listeners: {
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                var record = grid.getStore().getAt(rowIndex);
                if(record.get('status') =='Failed'||record.get('status') =='Succeeded'){
                    var err=record.get('errmsg');
                    showTaskMessage('Message',err);
                }
            }
        },

        tbar:[label_task,{
            xtype: 'tbfill'
        },refresh_button],
        bbar:[{
            xtype: 'tbfill'
        },cancel_button]
    });

    var taskpanel=new Ext.Panel({
        id:"taskpanel",
        title:'',
        layout:"form",
        width:'100%',
        height:370,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        bbar:[{
            xtype: 'tbfill'
        }],
        items: [task_grid]
    });

    return taskpanel;
}

function TasksGrid(){
    var label_task=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Displays submitted task information and their status.")+'</div>',
        id:'label_task1'
    });
    var task_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Task Id"),
        width: 80,
        dataIndex: 'taskid',
        hidden:true        
    },
    {
        header: _("Task"),
        width: 200,
        dataIndex: 'name',
        sortable:true        
    },
    {
        header: _("Entity Name"),
        width: 250,
        dataIndex: 'entname',
        sortable:true
    },
    {
        header: _("Entity Type"),
        width: 120,
        dataIndex: 'enttype',
        sortable:true
    },
    {
        header: _("Username"),
        width: 100,
        dataIndex: 'username',
        sortable:true        
    },
    {
        header: _("Start Time"),
        width: 160,
        dataIndex: 'timestamp',
        sortable:true,
        renderer:format_date
    },
    {
        header: _("End Time"),
        width: 160,
        dataIndex: 'endtime',
        sortable:true,
        renderer:format_date
    },
    {
        header: _("Status"),
        width: 100,
        dataIndex: 'status',
        sortable:true,
        renderer:function(value,params,record,row){            
              if(value =='Failed' || value =='Succeeded'){
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
    }
    ]);

    var task_rec=Ext.data.Record.create([
        {
            name: 'taskid',
            type: 'string'
        },

        {
            name: 'status',
            type: 'string'
        },
        {
            name: 'name',
            type: 'string'
        },

        {
            name: 'entname',
            type: 'string'
        },
        {
            name: 'enttype',
            type: 'string'
        },

        {
            name: 'username',
            type: 'string'
        },
        {
            name: 'timestamp',
            type: 'string'
        },

        {
            name: 'endtime',
            type: 'string'
        },

        {
            name: 'errmsg',
            type: 'string'
        }

    ]);

    var task_store =new Ext.data.JsonStore({
        url: "get_tasks",
        root: 'rows',
        fields: ['taskid','entname','enttype','name','username','timestamp','status','errmsg','endtime'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    task_store.load();    
    
    var refresh_button=new Ext.Button({
        id: 'refresh_task1',
        text: _('Refresh'),
        icon:'icons/refresh.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                task_grid.getStore().load();
            }
        }
    });
    var task_grid=new Ext.grid.GridPanel({
        store: task_store,
        stripeRows: true,
        colModel:task_columnModel,
        frame:false,
        autoscroll:true,
        height:330,
        //width:715,
        cls:'task_grid1',
        loadMask:true,
        enableHdMenu:false,
        id:'task_grid1',
        listeners: {
           cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                var record = grid.getStore().getAt(rowIndex);
                if(record.get('status') =='Failed'||record.get('status') =='Succeeded'){
                    var err=record.get('errmsg');
                    showTaskMessage('Message',err);
                }
            }
        }
//        ,tbar:[label_task,{
//            xtype: 'tbfill'
//        },refresh_button]
    });
    update_task_grid(task_grid,task_rec);

    return task_grid; 
}

function showTaskMessage(title,message){
    var editor=new Ext.form.TextArea({
        value:message,        
        readOnly:true,
        disabled:false
    });

    var panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        layout:'fit',
        items:[editor],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('OK'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        win.close();
                    }
                }
            })
        ]
    });

    var win=new Ext.Window({
        title: title,
        width: 400,
        layout:'fit',
        height: 300,
        modal: true,
        resizable: true,
        closable:true
    });
    win.add(panel);
    win.show();
}

//function err_console_grid(){
//
//   var label_err=new Ext.form.Label({
//        html:'<div class="toolbar_hdg">'+_("Error Console")+'</div>'
//   });
//
//   var err_columnModel = new Ext.grid.ColumnModel([
//        {
//            header: _("Entity"),
//            width: 150,
//            dataIndex: 'entname',
//            hidden:true
//        },
//        {
//            header: _("Entity"),
//            width: 150,
//            dataIndex: 'entname',
//            sortable:true
//        },
//
//        {
//            header: _("Action"),
//            width: 150,
//            dataIndex: 'name',
//            sortable:true
//        },
//
//        {
//            header: _("Status"),
//            width: 100,
//            dataIndex: 'status',
//            renderer:function(value,params,record,row){
//                if(value =='Failed'){
//                    params.attr='ext:qtip="Error Message"' +
//                'style="background-image:url(icons/information.png) '+
//                '!important; background-position: right;'+
//                'background-repeat: no-repeat;cursor: pointer;"';
//                }
//                return value;
//            }
//        }
//    ]);
//    var err_store =new Ext.data.JsonStore({
//        url: "get_failed_tasks",
//        root: 'rows',
//        fields: ['entname','name','status','errmsg','username','startime','endtime'],
//        successProperty:'success',
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
//    });
//    err_store.load();
//
//    var err_grid=new Ext.grid.GridPanel({
//        store: err_store,
//        stripeRows: true,
//        colModel:err_columnModel,
//        frame:false,
//        autoscroll:true,
//        loadMask:true,
//        enableHdMenu:false,
//        id:'err_grid',
//        height:100,
//        width:'100%',
//        autoExpandColumn:1,
//        listeners: {
//            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
//                var record = grid.getStore().getAt(rowIndex);
//                if(record.get('status') =='Failed'){
//                    var actn = record.get('name');
//                    var err=record.get('errmsg');
//                    showErrMessage('Error Message for '+actn,err,record);
//                }
//            }
//        },
//        tbar:[label_err,{
//            xtype: 'tbfill'
//        }]
//    });
//
//    return err_grid;
//}


function showErrMessage(title,message,rec){

    var submittedBy = rec.get('username');
    var stTime = rec.get('startime');
    var endTime = rec.get('endtime');
    var taskName = rec.get('name');

     var label1=new Ext.form.Label({
        html:'<div ><br/><span style="font-size:12px;font-family:Verdana" ><b>&nbsp;&nbsp;&nbsp;'+_("Task Name: "+'</b>'+taskName  )+'</span><br/></div>'
    });

      var label2=new Ext.form.Label({
        html:'<div ><br/><span style="font-size:12px;font-family:Verdana" ><b>&nbsp;&nbsp;&nbsp;'+_("Submitted By: "+'</b>'+submittedBy  )+'</span><br/></div>'
    });

     var label3=new Ext.form.Label({
        html:'<div ><br/><span style="font-size:12px;font-family:Verdana"><b>&nbsp;&nbsp;&nbsp;'+_("Start Time: "+'</b>'+stTime  )+'</span><br/></div>'
    });

    var label4=new Ext.form.Label({
        html:'<div ><br/><span style="font-size:12px;font-family:Verdana"><b>&nbsp;&nbsp;&nbsp;'+_("End Time: "+'</b>'+endTime  )+'</span><br/></div>'
    });

    var label5=new Ext.form.Label({
        html:'<div ><br/><span style="font-size:12px;font-family:Verdana"><b>&nbsp;&nbsp;&nbsp;'+_("Message: " )+'</span><br/></div>'
    });

     var err_details1 = new Ext.Panel({
        //width:100,
        border:false,
        bodyBorder:false,
        layout:'column',
        //bodyStyle:'padding-top:5px;padding-left:5px;',
        items:[{
                width:"50%",
                border:false,
                layout:'form',
                items:[label1]
            }
            ,{
                width:"50%",
                border:false,
                layout:'form',
                items:[label3]
            }]
    });

     var err_details2 = new Ext.Panel({
        //width:100,
        border:false,
        bodyBorder:false,
        layout:'column',
        //bodyStyle:'padding-top:5px;padding-left:5px;',
        items:[{
                width:"50%",
                border:false,
                layout:'form',
                items:[label2]
            }
            ,{
                width:"50%",
                border:false,
                layout:'form',
                items:[label4]
            }]
    });

     var err_details3 = new Ext.Panel({
        //width:100,
        border:false,
        bodyBorder:false,
        layout:'column',
        //bodyStyle:'padding-top:5px;padding-left:5px;',
        items:[label5]
    });

    var editor=new Ext.form.TextArea({
        value:message,
        height:200,
        readOnly:true,
        disabled:false
    });

    var panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        layout:'fit',
        items:[editor],
        height:200,
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('OK'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        win.close();
            }
        }
            })
        ]
    });

     var mainanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Information for {0}"),node.text),
        height:'100%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[err_details1,err_details2,err_details3,panel]
    });

    var win=new Ext.Window({
        title: title,
        width: 550,
        layout:'fit',
        height: 310,
        modal: true,
        //resizable: true,
        closable:true
    });
    win.add(mainanel);
    //win.add(err_details2);
    win.show();
}

function showNotifications(data,params,rec){

  var entList = rec.get('list');
  var type = rec.get('type');
  var entType = rec.get('entType');

  if(data > 0) {

        var fn = "showError_notifications('" + entList + "','" + entType + "')";

        //var returnVal = '<table><tr>'+data+'<td align="right"><a href="#" onClick= ' + fn1 + '><img src=" icons/file_edit.png "/></a> <a href="#" onClick= ' + fn2 + '><img src=" icons/information.png "/> </a></td> </tr></table>' ;

       var returnVal = '<a href="#" onClick=' + fn + '>' + data + '</a>';
//        params.attr='ext:qtip="Show Image Description"' +
//                    '!important; background-position: right;'+
//                    'background-repeat: no-repeat;cursor: pointer;"';

        return returnVal;
    }
    else {
        return data;
    }

}

function showError_notifications(entList,entType){

    var notification_grid=create_notifications_grid(entList,entType);

    var notification_panel = new Ext.Panel({
        cls:'westPanel',
        width:765,
        height:350,
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'close',
                id: 'close',
                text:_('Close'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();
                    }
                }
            })

        ]
    });

    notification_panel.add(notification_grid);
    showWindow(_("Error Notifications"),780,375,notification_panel);
}

function create_notifications_grid(entList,entType){

    var notification_columnModel = new Ext.grid.ColumnModel([

    {
        header: _("Task Id"),
        sortable: true,
        width:200,
        dataIndex: 'taskid',
        hidden:true
    },{
        header: _("Task"),
        dataIndex: 'name',
        width:150,
        sortable:true
    },    
    {
        header: _("Entity Name"),
        sortable: true,
        width:120,
        dataIndex: 'entname'
    },
    {
        header: _("Entity Type"),
        dataIndex: 'enttype',
        width:120,
        sortable:true
    },
    {
        header: _("Time"),
        sortable: true,
        width:150,
        dataIndex: 'timestamp',
        renderer:format_date

    },
     {
        header: _("Status"),
        width:100,
        dataIndex: 'status',
        renderer:function(value,params,record,row){
            if(value =='Failed'){
                params.attr='ext:qtip="Error Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
    }]);

    var err_store =new Ext.data.JsonStore({
        url: "/getNotifications?type=DETAILS&list="+entList+"&user="+user_name+"&entType="+entType,
        root: 'rows',
        fields: ['taskid','entname','enttype','name','username','timestamp','status','errmsg','endtime','cancellable'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    err_store.load();

    var err_grid = new Ext.grid.GridPanel({
        store: err_store,
        colModel:notification_columnModel,
        stripeRows: true,
        frame:true,
        forceFit :true,
        height : 320,
        autoWidth:true,
        listeners: {
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                var record = grid.getStore().getAt(rowIndex);
                if(record.get('status') =='Failed'){
                    var err=record.get('errmsg');
                    showTaskMessage('Error Message',err);
                }
            }
        }
        ,autoExpandColumn:1

    });
    return err_grid;
}

function showSysTasks(data,params,rec){
  
    if(data > 0) {
        var fn = "showsysTask_notifications()";
        var returnVal = '<a href="#" onClick=' + fn + '>' + data + '</a>';
        return returnVal;
    }else {
        return data;
    }

}

function showsysTask_notifications(){

    var sysTasks_grid=create_sysTasks_grid();

    var sys_panel = new Ext.Panel({
        cls:'westPanel',
        width:765,
        height:275,
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'close',
                id: 'close',
                text:_('Close'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();
                    }
                }
            })

        ]
    });

    sys_panel.add(sysTasks_grid);
    showWindow(_("System Tasks"),780,300,sys_panel);
}

function create_sysTasks_grid(){

    var systask_columnModel = new Ext.grid.ColumnModel([

    {
        header: _("Task"),
        dataIndex: 'tname',
        width:150,
        sortable:true,
        hidden:true
    },
    {
        header: _("Task"),
        dataIndex: 'tname',
        width:150,
        sortable:true
    },
    {
        header: _("User"),
        dataIndex: 'user',
        width:150,
        sortable:true
    },
    {
        header: _("Time"),
        sortable: true,
        width:150,
        dataIndex: 'st'

    },
     {
        header: _("Status"),
        width:100,
        dataIndex: 'status',
        renderer:function(value,params,record,row){
            if(value =='Failed'){
                params.attr='ext:qtip="Error Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
    }]);

    var systask_store =new Ext.data.JsonStore({
        url: "/getSystemTasks?type=DETAILS&user="+user_name,
        root: 'rows',
        fields: ['tname','st','status','errmsg','user'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    systask_store.load();

    var systask_grid = new Ext.grid.GridPanel({
        store: systask_store,
        colModel:systask_columnModel,
        stripeRows: true,
        frame:true,
        //id:'errinfo_grid',
//        cls:'grid_bg',
        forceFit :true,
        height : 250,
        autoWidth:true,
        listeners: {
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                var record = grid.getStore().getAt(rowIndex);
                if(record.get('status') =='Failed'){
                    var err=record.get('errmsg');
                    showTaskMessage('Error Message',err);
                }
            }
        }
        ,autoExpandColumn:1


    });
    return systask_grid;
}

function task_panel_do(){
//    tasks_grid.getStore().load();
}

var get_updated_tasks_req_handler = new convirt.communication_failure_handler();
function update_task_grid(tasks_grid,task_rec){
    var time=TASKPANEREFRESH*1000
    var update_task = {
        run : function() {
            var can_send_request = get_updated_tasks_req_handler.can_send_request();
//            console.log("--get_updated_tasks----can_send_request---"+can_send_request);
            if (can_send_request){
                    var url="/dashboard/get_updated_tasks?user_name="+user_name;
                    var ajaxReq = ajaxRequest(url,0,"GET",true);
                    get_updated_tasks_req_handler.start(ajaxReq);
                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            get_updated_tasks_req_handler.end(response);
                             //alert(xhr.responseText);
                            if(!response.success){
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                                return;
                            }
                            //alert(response.tasks)

                            if(response.tasks != null){
                                var tasks=response.tasks;
                                for(var i=0;i<tasks.length;i++){
                                    var task=tasks[i];
                                    var rec=new task_rec({
                                        taskid:task.taskid,
                                        status:task.status,
                                        username:task.username,
                                        name:task.name,
                                        enttype:task.enttype,
                                        timestamp:task.timestamp,
                                        endtime:task.endtime,
                                        entname:task.entname,
                                        errmsg:task.errmsg
                                    });
                                    var index=tasks_grid.getStore().find('taskid',task.taskid);
                                    //alert(index);
                                    if (index==-1){
                                        tasks_grid.getStore().insert(0,rec);
                                    }else{
                                        tasks_grid.getStore().removeAt(index);
                                        tasks_grid.getStore().insert(index,rec);
                                    }
                                }
                            }
                        },
                        failure: function(xhr){
                             get_updated_tasks_req_handler.set_warning(xhr.statusText);
                            //Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });

             }//can_send_request
        },
        interval :time
    };
    
    task_runner.start(update_task);
}
function format_date(value,params,record){
        if (value==null || value==""){
            return value;
        }
        var date =new Date(value);
        var str_date=date.getFullYear()+"-"+
            format_date_value(String(parseInt(date.getMonth()+1)))+"-"+
            format_date_value(String(date.getDate()))+
            " "+format_date_value(String(date.getHours()))+":"+
            format_date_value(String(date.getMinutes()))+":"+
            format_date_value(String(date.getSeconds()));
//        return myDate[0].substr(0,myDate[0].length-4);
        return str_date;

}
function format_date_value(value){
      var pad_zero="0";
      if (value.length<2)
          value=pad_zero+value;
      return value;
}


function show_task_popup(msg) {                    
                    var grid     = Ext.get('task_grid1');
                    var x    = parseInt(grid.getRight());
                    var y     = parseInt(grid.getTop());
                    if(x>0 && y>0){
                        x=x-x*0.21;
                        y=y+y*0.0188;
                    }else{
                        var panel     = Ext.get('outerPanel');
                        x= parseInt(panel.getRight())
                        y=parseInt(panel.getBottom())
                        x=x-x*0.21;
                        y=y-y*0.1125
                    }
                    var t = new Ext.ToolTip({
                        floating: {
                            shim: true,
                            floating: true
                        },
                        style: {
                            'background-color': '#000'
                        },
                        title: 'Task',
                        html: msg,
                        bodyBorde:true,
                        targetXY: [x,y],
//                        dismissDelay: 10,
                        autoHide:false,
//                        hideDelay: 10,
                        closable: false
                    });
                    t.show();
                    setTimeout(function(){t.hide();},3000);
}