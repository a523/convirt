
function annotateEntity(node,action){

    var url="/node/get_annotation?node_id="+node.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var annotate=response.annotate;
                showWindow(_("Annotate")+" "+node.text,400,220,process_annotation(node,action,annotate.user,annotate.text));
            }else{
                Ext.MessageBox.alert( _("Failure") , response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
function process_annotation(node,action,username,text){


    var annotate_text=new Ext.form.Label({
         html: _("Please enter annotation below, others will be notified via email.")
    });

    var br=new Ext.form.Label({
         html: _("<div style='height:10px'/>")
    });
    var modified_by=(username==null)?"":username;
    var user_name=new Ext.form.Label({
         html: _("Last Modified by :&nbsp;&nbsp;"+modified_by)
     });
//    var user_name = new Ext.form.TextField({
//        fieldLabel: 'Last Modified by:',
//        name: 'user_name',
//        id: 'user_name',
//        width:180,
//        value:username,
//        disabled:true,
//        labelSeparator:" ",
//        allowBlank:true,
//        enableKeyEvents:true,
//        listeners: {
//            keyup: function(field) {
//
//            }
//        }
//    });

    var user_annotation = new Ext.form.TextArea({
        fieldLabel: 'Annotation ',
        name: 'user_annotation',
        id: 'user_annotation',
        width: 260,
        height: 100,
        value:text,
        enableKeyEvents:true,
        listeners: {
            keydown: function(field) {
                var annot_values=user_annotation.getValue();
                if(annot_values.length>=256){
                   user_annotation.setValue(annot_values.substring(0,255));
                }
            }
        }

    });
    var annotate_panel1=new Ext.form.FormPanel({
        closable: true,
        height:'100%',
        border:false,
        width:'100%',
        layout:'form',
        frame:true,
        labelAlign:"right" ,
        id:"annotate_panel1",
        items: [annotate_text,br,user_annotation,user_name]
    });


    var button_clear=new Ext.Button({
        name: 'clear',
        id: 'clear',
        text:_('Clear'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                if (user_annotation.getValue()!=""){
                     var msg=format(_("Clearing the annotation. Continue?"),node.text);
                     Ext.MessageBox.confirm(_("Confirm"),msg,function(id){
                        if (id == 'yes'){
                            user_annotation.setValue("");
                            user_name.setText("Last Modified by :");
                            modified_by="";
                            var url="/node/process_annotation?node_id="+node.attributes.id;
                            save_annotation(url);

                      }});
//                }
            }

        }
     });

     var button_save=new Ext.Button({
        name: 'save',
        id: 'save',
        text:_('Save'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                    var url="/node/process_annotation?node_id="+node.attributes.id;
//                    if (user_annotation.getValue()!="")
                    url+="&text="+escape(user_annotation.getValue());
                    if (modified_by!="")
                        url+="&user="+modified_by;
                    save_annotation(url);
            }

        }
     });


      var annotate_panel2=new Ext.Panel({
        height:190,
        border:true,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        frame:false,
        labelSeparator:' ',
        id:"annotate_panel2",
        items:[annotate_panel1],
        bbar:[{xtype: 'tbfill'},button_clear,button_save,
                new Ext.Button({
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
            })

    ]
    });

    return annotate_panel2;
}

function save_annotation(url){
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    show_task_popup(response.msg);

                }else{
                    Ext.MessageBox.alert( _("Failure") , response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        });
        closeWindow();


}