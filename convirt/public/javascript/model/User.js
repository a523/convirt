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

function userUI(){
    var user_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("Create / Edit users")+_(" Assign Users to Groups")+'<br/></div>'
    });
   

    var user_new_button=new Ext.Button({
        id: 'user_new',
        text: _('New'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :'New User',
                    width :370,
                    height:400,
                    modal : true,
                    resizable : false
                });
                w.add(userDetailsPanel(user_grid,'NEW',null,w));
                w.show();
            }
        }
    });

    var user_remove_button=new Ext.Button({
        id: 'user_remove',
        text: _('Remove'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!user_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select a record from the user list"));
                    return false;
                }
                var edit_rec=user_grid.getSelectionModel().getSelected();
                var userid=edit_rec.get('userid');
                var username=edit_rec.get('username');
                var url='/model/delete_user?userid='+userid;//alert(url);
                Ext.MessageBox.confirm(_("Confirm"),_("About to delete user:")+username+"?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    user_grid.getStore().load();
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
        }
    });

    var user_edit_button= new Ext.Button({
        id: 'user_edit',
        text: _('Edit'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!user_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("Error"),_("Please select the record from the user list"));
                    return false;
                }
                var edit_rec=user_grid.getSelectionModel().getSelected();
                var userid=edit_rec.get('userid');
                var url="/model/edit_user_det?userid="+userid;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var users_det=response.edit_user_det[0];
                            var w=new Ext.Window({
                                title :_('Edit User'),
                                width :370,
                                height:400,
                                modal : true,
                                resizable : false
                            });
                            w.add(userDetailsPanel(user_grid,'EDIT',users_det,w));
                            w.show();
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

    var user_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var user_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("User Id1"),
        width: 0,
        dataIndex: 'userid',
        menuDisabled: false,
        hidden:true
    },
    {
        header: _("Username"),
        width: 150,
        dataIndex: 'username',
        sortable:true
    },
    {
        header: _("Name"),
        width: 180,
        sortable: true,
        dataIndex: 'name'
    },
    {
        header: _("Groups"),
        width: 165,
        sortable: false,
        dataIndex: 'group',
        wordwrap:true
    }]);

    var user_store =new Ext.data.JsonStore({
        url: "/model/get_users",
        root: 'rows',
        fields: ['userid','username', 'name', 'group'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){               
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    user_store.load();

    var user_grid=new Ext.grid.GridPanel({
        store: user_store,
        stripeRows: true,
        colModel:user_columnModel,
        frame:false,
        selModel:user_selmodel,
        height:355,
        //width:515,
        width: '100%',
        enableHdMenu:false,
        loadMask:true,
        id:'user_grid',
        layout:'fit',
        tbar:[
            _('Search (By Name): '),new Ext.form.TextField({
            fieldLabel: _('Search'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    user_grid.getStore().filter('username', field.getValue(), false, false);
                }
            }
        }),{ 
            xtype: 'tbfill'
        },user_new_button,user_edit_button,user_remove_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                user_edit_button.fireEvent('click',user_edit_button);
            }
        }
    });
    var userpanel=new Ext.Panel({
        id:"userpanel",
        title:_('Users'),
        layout:"form",
        width:535,
        height:450,
        cls: 'whitebackground',
        frame:false,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [user_label,user_grid]
    });

    return userpanel;
}

function userDetailsPanel(grid,mode,user,w){
//    var user_label2=new Ext.form.Label({
//        html:'<div style="" class="backgroundcolor" align="center" width="250">'+_("Group Select")+'<br/></div><br>'
//    });

    var user_id=new Ext.form.TextField({
        fieldLabel: _('User Id'),
        name: 'userid',
        width: 150,
        id: 'userid',
        allowBlank:false,
        disabled: true
    });
    var user_name=new Ext.form.TextField({
        fieldLabel: _('Username'),
        name: 'username',
        width: 150,
        id: 'username',
        allowBlank:false
    });
    var user_fname=new Ext.form.TextField({
        fieldLabel: _('First Name'),
        name: 'fname',
        width: 150,
        id: 'fname',
        allowBlank:false
    });
    var user_lname=new Ext.form.TextField({
        fieldLabel: _('Last Name'),
        name: 'lname',
        width: 150,
        id: 'lname',
        allowBlank:false
    });
    var display_name=new Ext.form.TextField({
        fieldLabel: _('Nick Name'),
        name: 'dispname',
        width: 150,
        id: 'dispname',
        allowBlank:false
    });
    var user_password=new Ext.form.TextField({
        fieldLabel: _('Password'),
        name: 'password',
        width: 150,
        id: 'pass',
        inputType:'password',
        allowBlank:false
    });
    var user_repass=new Ext.form.TextField({
        fieldLabel: _('Retype Password'),
        name: 'repass',
        width: 150,
        id: 'repass',
        inputType:'password',
        initialPassField: 'pass',
        allowBlank:false
    });
    var user_email=new Ext.form.TextField({
        fieldLabel: _('Email'),
        name: 'email',
        width: 165,
        id: 'email',
        allowBlank:false
    });
    var user_phone=new Ext.form.NumberField({
        fieldLabel: _('Phone'),
        name: 'phone',
        width: 150,
        id: 'phone',
        allowBlank:true
    });
    var createdby=new Ext.form.TextField({
        fieldLabel: _('Created By'),
        name: 'createdby',
        width: 150,
        id: 'createdby',
        allowBlank:false,
        disabled:true

    });
    var createddate=new Ext.form.TextField({
        fieldLabel: _('Created Date'),
        name: 'createddate',
        width: 150,
        id: 'createddate',
        allowBlank:false,
        disabled:true

    });
    var modifiedby=new Ext.form.TextField({
        fieldLabel: _('Modified By'),
        name: 'modifiedby',
        width: 150,
        id: 'modifiedby',
        allowBlank:false,
        disabled:true

    });
    var modifieddate=new Ext.form.TextField({
        fieldLabel: _('Modified Date'),
        name: 'modifieddate',
        width: 150,
        id: 'modifieddate',
        allowBlank:false,
        disabled:true

    });
   
    var newpasswrd=new Ext.form.TextField({
        fieldLabel: _('New Password'),
        name: 'newpass',
        width: 150,
        id: 'newpass',
        inputType:'password'
    });

    var confpasswrd=new Ext.form.TextField({
        fieldLabel: _('Retype Password'),
        name: 'confpass',
        width: 150,
        id: 'confpass',
        inputType:'password'
    });


    var user_status_store = new Ext.data.JsonStore({
        url: '/model/get_user_status_map',
        root: 'user_status',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    user_status_store.load();
    var user_status=new Ext.form.ComboBox({
        width:80,
        minListWidth: 90,
        fieldLabel:_("Status"),
        allowBlank:false,
        triggerAction:'all',
        store:user_status_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_status'
    });

    var url="";
    if(mode=='NEW'){
        url="/model/get_groups_map";
    }
    else if(mode=='EDIT'){
        url="/model/get_groups_map?userid="+user.userid;
    }
//    var groups_fromstore = new Ext.data.JsonStore({
//        url: url,
//        root: 'group_det',
//        fields: ['groupid','groupname'],
//        successProperty:'success',
//        //        remoteSort :true,
//        sortInfo: {
//            field: 'groupname',
//            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
//        },
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            },
//            load:function(store,recs,opts){
//
//            }
//        }
//    });
//
//    groups_fromstore.load();
//    var groups_tostore = new Ext.data.JsonStore({
//        url: '/model/get_togroups_map',
//        root: 'togroup_det',
//        fields: ['groupid','groupname'],
//        successProperty:'success',
//        sortInfo: {
//            field: 'groupname',
//            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
//        },
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
//    });

    var user_cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('Cancel'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                w.close();
            }
        }
    });
    
    var user_save_button=new Ext.Button({
        id: 'save',
        text: _('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {                
                if(user_rightpanel.getForm().isValid()) {
                    var url="",flag=false,errmsg="";
                    var uid="";

                    var repass= user_repass.getValue();
                    if(mode=="NEW" && user_password.getValue()!=repass){
                        errmsg+="<br>"+_("Password is not matching retyped password");
                        flag=true;
                    }

                    var email=user_email.getValue();
                    if(!EmailCheck(email)){
                        errmsg+="<br>"+_("Please enter valid Email-Id");
                        flag=true;
                    }
//                    if(groupitemselector.toStore.getCount()==0){
//                        errmsg+="<br>"+_("Please select at least one Group");
//                        flag=true;
//                    }

                    if(flag){
                        Ext.MessageBox.alert(_("Warning"),errmsg);
                        return ;
                    }
                    uid=user_name.getValue()
                    if(mode=='NEW'){

                        url="/model/save_user_det?userid="+user_id.getValue()+"&username="+user_name.getValue()+"&fname="+user_fname.getValue()+"&lname="+user_lname.getValue()+"&displayname="+display_name.getValue()+"&password="+user_password.getValue()+"&email="+user_email.getValue()+"&phone="+user_phone.getValue()+"&status="+user_status.getValue();
                    }else if(mode=='EDIT'){
                        //var record=null;
                        //var  groupids="";
                        var flag=false,errmsg="";
//                        var rec_count=groupitemselector.toStore.getCount();
                        var change_passwd=passwrd_fldset.getEl().child('legend').child('input').dom.checked;
                        if(change_passwd == true)
                        {                                  
                            if(newpasswrd.getValue() == "")
                            {
                                errmsg+="<br>"+_("Please enter New Password");
                                flag=true;
                            }
                            if(newpasswrd.getValue() != "")
                            {
                                if(newpasswrd.getValue() != confpasswrd.getValue())
                                {
                                    errmsg+="<br>"+_("New Password and Retype Password is not matching");
                                    flag=true;
                                }
                            }
                        }
                        if(flag){
                            Ext.MessageBox.alert(_("Warning"),errmsg);
                            return ;
                        }
//                        for (var i=0; i<rec_count; i++) {
//                            record = groupitemselector.toStore.getAt(i);
//                            var  groupid=record.get('groupid');
//                            groupids+=groupid+",";
//                        }
                            
                        url="/model/updatesave_user_det?userid="+user_id.getValue()+
                             "&username="+user_name.getValue()+"&fname="+user_fname.getValue()+
                             "&lname="+user_lname.getValue()+"&displayname="+display_name.getValue()+
                             "&email="+user_email.getValue()+"&phone="+user_phone.getValue()+
                             "&status="+user_status.getValue()+"&changepass="+change_passwd+
                             "&newpasswd="+newpasswrd.getValue();
                    }

                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var users_det=response.user_det[0];
                                if('F'==users_det){
                                    Ext.MessageBox.alert(_("Failure"),format(_("User {0} is already existing"),uid));
                                    return false;
                                }
                                else if('E' == users_det){
                                    Ext.MessageBox.alert(_("Failure"),_("The Email is already in use!"));
                                    return false;
                                }
                                Ext.MessageBox.alert(_("Success"),_("Successfully saved the values"));
                                w.close();
                                grid.getStore().load();
                            }else{
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });
                }
                else{
                    Ext.MessageBox.alert(_('Errors'), _('Some of the required information is missing.'));
                }
            }
        }
    });


    var tabPanel=new Ext.TabPanel({
        defaults: {
            autoScroll:true
        },
        margins: '2 2 2 0',
        minTabWidth: 115,
        tabWidth:135,
        activeTab:0,
        cls: 'whitebackground',
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },user_save_button,user_cancel_button]
    });

    var user_rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        title:_('User'),
        layout:"form",
        width:300,
        height:300,
        //frame:true,
        labelWidth:100,
        border:0,
        bodyStyle:'padding:10px 10px 10px 10px'
    //items:[user_name,user_fname,user_lname,user_password,user_repass,user_email,user_phone,user_status]
    });

    var passwrd_fldset=new Ext.form.FieldSet({
        checkboxToggle:true,
        collapsed: true,
        title: _('Change Password'),
        id: 'change_passwd',
        autoHeight:true,
        width:280,
        labelWidth:90,
        layout:'column',
        items: [{
            width: 300,
            layout:'form',
            items:[newpasswrd,confpasswrd]
        }]
    });

    user_rightpanel.add(user_name);
    user_rightpanel.add(user_fname);
    user_rightpanel.add(user_lname);
    user_rightpanel.add(display_name);
    if(mode=="NEW"){
        user_rightpanel.add(user_password);
        user_rightpanel.add(user_repass);
    }
    user_rightpanel.add(user_email);
    user_rightpanel.add(user_phone);
    user_rightpanel.add(user_status);    

    var user_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('Audit'),
        width:300,
        height:300,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });

//    var groupitemselector=new Ext.ux.ItemSelector({
//        name:"itemselector",
//        dataFields:["groupid","groupname"],
//        toStore:groups_tostore,
//        msWidth:148,
//        msHeight:250,
//        allowBlank:false,
//        valueField:"groupid",
//        displayField:"groupname",
//        imagePath:"icons/",
//        drawUpIcon:false,
//        drawDownIcon:false,
//        drawLeftIcon:true,
//        drawRightIcon:true,
//        drawTopIcon:false,
//        drawBotIcon:false,
//        toLegend:_("Selected"),
//        fromLegend:_("Available"),
//        fromStore:groups_fromstore,
//        toTBar:[{
//            text:_("Clear"),
//            handler:function(){
//                groupitemselector.reset();
//            }
//        }]
//    });
//    var groupassign_details_panel=new Ext.FormPanel({
//        id:"groupassignpanel",
//        title:_('Group'),
//        width:300,
//        height:300,
//        layout:"form",
//        frame:true,
//        labelWidth:5,
//        border:false,
//        bodyBorder:false,
////        items: [user_label2, groupitemselector]
//    });
    
    var user_group=new Ext.form.TextField({
        fieldLabel: _('Groups'),
        name: 'groups',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_group'
    });


    if(mode=="EDIT"){

        var userid=user.userid;
        user_id.setValue(user.userid);
        user_name.setValue(user.username);
        user_name.disabled=true;
        user_fname.setValue(user.fname);
        user_lname.setValue(user.lname);
        display_name.setValue(user.displayname);
        user_email.setValue(user.email);
        user_phone.setValue(user.phone);
        user_status.setValue(user.status);
        user_group.setValue(user.groupname);
        user_rightpanel.add(user_group);
        user_rightpanel.add(passwrd_fldset);
//        groups_fromstore.load();
//        groups_tostore.load({
//            params:{
//                userid:userid
//            }
//        });

        tabPanel.add(user_rightpanel);
//        tabPanel.add(groupassign_details_panel);
        tabPanel.add(user_auditpanel);
        tabPanel.setActiveTab(user_auditpanel);
//        tabPanel.setActiveTab(groupassign_details_panel);
        tabPanel.setActiveTab(user_rightpanel);
        createdby.setValue(user.createdby);
        modifiedby.setValue(user.modifiedby)
        createddate.setValue(user.createddate)
        modifieddate.setValue(user.modifieddate)

    }

    tabPanel.add(user_rightpanel);
//    tabPanel.add(groupassign_details_panel);
//    tabPanel.setActiveTab(groupassign_details_panel);
    tabPanel.setActiveTab(user_rightpanel);

    var new_users_panel=new Ext.Panel({
        id:"new_user_panel",
        layout:"form",
        width:350,
        height:400,
        cls: 'whitebackground',
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });

    return new_users_panel;

}

function ckNumber(value) {
    var validate=false;
    var  x = value;
    var nos=new Array('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E',
        'F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','"',',','.','"',';',':','?','/','\'');
    for(var i=0;i<value.length;i++){
        for(var j=0;j<=nos.length;j++){
            if(x.charAt(i) == nos[j]){
                //alert("Only Numbers Are Allowed")
                value="";
                focus();
                return validate;
            }
        }
    }
    validate=true;
    return validate;
}

function EmailCheck(email){
    email = email;
    var validate=false;
    var pattern=/^([a-zA-Z0-9_.-])+@([a-zA-Z0-9_.-])+\.([a-zA-Z])+([a-zA-Z])+/;
    if(! pattern.test(email)){
        //alert("Properly , give the Email Address (__ @__ .__)");
        return validate;
    }
    else{
        validate=true;
        return validate;
    }

}
