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

function loginconfig(){
    Ext.QuickTips.init();

    var login = new Ext.FormPanel({
        labelWidth:100,
        url:'user_login',
        //frame:true,
        cls: 'whitebackground',
        title:_('Login'),
        labelAlign:'right',
        bodyStyle: 'padding: 10px 0px 0 0px;',
        modal: true,
        monitorValid:true,
        border: false,
        items:[
        {
            fieldLabel:_('Username'),
            align:'center',
            name:'login',
            xtype:'textfield',
            id:'login',
            allowBlank:false,
            listeners:{
                specialkey : function(btn,e){
                    if(e.getKey()==13){
                        submitLoginForm(login);
                    }
                }
            }
        },
        {
            fieldLabel:_('Password'),
            name:'password',
            align:'center',
            xtype:'textfield',
            id:'password',
            inputType:'password',
            allowBlank:false,
            listeners:{
                specialkey : function(btn,e){
                    if(e.getKey()==13){
                        submitLoginForm(login);
                    }
                }
            }
        }],
        buttons:[{
            text:_('Login'),
            formBind: true,
            handler:function(){
                submitLoginForm(login);
            }
        },
        {
            text:_('Reset'),
            formBind: true,
            handler:function(){
                login.getForm().reset();
                login.getForm().findField('login').focus(true);
            }
        }]

    });
    var welcome_label=new Ext.form.Label({
        html:'<div class="bluebackgroundcolor" ><center>'+_('Welcome to ConVirt 2.5')+'</center></div><br>',
        xtype:'label'
    });
    login.insert(0,welcome_label)

    var win = new Ext.Window({
        layout:'fit',
        width:320,
        height:220,
        cls: 'whitebackground',
        closable: false,
        resizable: false,
        plain: true,
        border: false,
        items: [login]
        ,defaultButton :"login"
    });
    win.show();

}

function submitLoginForm(login){

     var loading_label=new Ext.form.Label({
        tittle:'Loading...',
        html:'<table><tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp\n\
               &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp\n\
               </td><td>loading...<img src=/icons/loading.gif></td></tr></table>',
        xtype:'label'
    });

    if(!login.getForm().isValid()) {
        Ext.Msg.alert(_("Failure"), _("Please enter Username and Password."));
        return;
    }

     login.getForm().submit({
        method:'POST',
        waitTitle:_('Connecting'),
        waitMsg:_('Sending data...'),
        success:function(){
            login.add(loading_label);
            login.setDisabled(true);
            login.doLayout();
         // login.getEl().mask("Loading Home Page ...","loading_icon");
            var redirect = '/';
            window.location = redirect;
        },
        failure:function(form, action){
            var msg='';
            switch (action.failureType) {
                case Ext.form.Action.CLIENT_INVALID:
                    msg=_("Please enter Username and Password.");
                    break;
                case Ext.form.Action.CONNECT_FAILURE:
                    msg=_("Server communication failed.");
                    break;
                case Ext.form.Action.SERVER_INVALID:
                    msg=action.result.msg;
                    break;
                default:
                    msg=_('Invalid Username or Password.');
                    if(action.result.msg != null){
                        msg=action.result.msg
                    }
                    break;
            }
            Ext.Msg.alert(_("Failure"), msg,function(id){
                login.getForm().reset();
                login.getForm().findField('login').focus(true);
            });
        }
    });
}
