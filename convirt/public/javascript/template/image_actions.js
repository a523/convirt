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

function getImageInfo(node){
    var url="/template/get_image_info?node_id="+node.attributes.nodeid+"&level="+node.attributes.nodetype;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
            showImageInfo(response.content); 
        },
        failure: function(xhr){
            Ext.MessageBox.alert(_("Failure"),xhr.statusText);
        }
    });
}

function showImageInfo(content){
    var info=new Ext.Panel({
        border:false,
        frame:true,
        closable: false,
        layout  : 'fit',
        html    : "<span style='font-size:3; font-family: Verdana; color:#0000FF;text-align:left;'>"+content+"</span>"
    });
    updateInfoTab(info,true);
}

function addImageGroup(node){
    Ext.MessageBox.prompt(_("Add Template Group"),_("Enter Template Group Name"),function(btn, text){
        if (btn == 'ok'){
            if(text.length==0){
                Ext.MessageBox.alert(_("Error"),_("Please enter valid Name."));
                return;
            }
            var url="/template/add_image_group?group_name="+text+"&store_id="+node.attributes.nodeid;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        //Ext.MessageBox.alert("Success",response.msg);
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

function removeImageGroup(node){
    var msg=format("All templates in the template group, {0} will be removed. Continue?",node.text); 
    Ext.MessageBox.confirm(_("Confirm"),msg,function(id){
        if (id == 'yes'){
            var url="/template/remove_image_group?group_id="+node.attributes.nodeid;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        //Ext.MessageBox.alert("Success",response.msg);
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

function renameImageGroup(node){
    Ext.MessageBox.prompt(_("Rename Group")+":-"+node.text,_("Enter new Template Group Name"),function(btn, text){
        if (btn == 'ok'){
            if(text.length==0){
                Ext.MessageBox.alert(_("Error"),_("Please enter valid Name."));
                return;
            }
            var url="/template/rename_image_group?group_id="+node.attributes.nodeid+"&group_name="+text;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        //Ext.MessageBox.alert("Success",response.msg);
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

function removeImage(node){
    var msg=_("Delete Template , ")+node.text+"?";
    Ext.MessageBox.confirm(_("Confirm"),msg,function(id){
        if (id == 'yes'){
            var url="/template/remove_image?image_id="+node.attributes.nodeid+"&group_id="+node.parentNode.attributes.nodeid;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        show_task_popup(response.msg);
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

function validate_special_char(text,name){
    var x = text;
    var invalid_chars=new Array(' ','!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','"',',','.','"',';',':','?','/','\'');
    for(var i=0;i<x.length;i++){
        for(var j=0;j<=invalid_chars.length;j++){
            if(x.charAt(i) == invalid_chars[j]){
                Ext.MessageBox.alert(_("Error"),_(name+" Name should not contain special characters.<br>")+
                 "space,comma,single quote,double quotes,'!','@','#',<br>'$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','.',';',':','?','/'");
                return false;
            }
        }
    }
    return true;
}

function renameImage(node){
    Ext.MessageBox.prompt(_("Rename Template:-")+node.text,_("Enter new Name for Template"),function(btn, text){
        if (btn == 'ok'){
            if(text.length==0){
                Ext.MessageBox.alert(_("Error"),_("Please enter valid Name."));
                return;
            }
            else{
                 var sts = validate_special_char(text,'Template');
                 if (sts==false){
                     return;
                }
             }
                 
            var url="/template/rename_image?image_id="+node.attributes.nodeid+"&image_name="+text+"&group_id="+node.parentNode.attributes.nodeid;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        //Ext.MessageBox.alert("Success",response.msg);
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

function cloneImage(node){
    Ext.MessageBox.prompt(_("Create Like Template:-")+node.text,_("Enter Template Name"),function(btn, text){
        if (btn == 'ok'){
            if(text.length==0){
                Ext.MessageBox.alert(_("Error"),_("Please enter valid Name."));
                return;
            }
            else{
                 var sts = validate_special_char(text,'Template');
                 if (sts==false){
                     return;
                }
             }

            var url="/template/clone_image?image_id="+node.attributes.nodeid+"&image_name="+text+"&group_id="+node.parentNode.attributes.nodeid+
                "&group_name="+node.parentNode.text;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        //Ext.MessageBox.alert("Success",response.msg);
//                        node.parentNode.fireEvent('click',node.parentNode);
                        show_task_popup(response.msg);
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

function editImageScript(node,action){
    var url="/template/get_image_script?image_id="+node.attributes.nodeid;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
            showWindow(_("Edit Provisioning Script:-")+node.text,525,500,FileViewEditDialog(response.content,"",'edit','text',node,action));
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function editImageDesc(node,action){
    var url="/template/get_image_info?node_id="+node.attributes.nodeid+"&level="+convirt.constants.IMAGE;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
            showWindow(_("Edit Description:-")+node.text,525,500,FileViewEditDialog(response.content,"",'edit','html',node,action));
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function formatHTML(content){
    content=content.replace(/&lt;/g,'<');
    content=content.replace(/&gt;/g,'>');
    content=content.replace(/&quot;/g,'"'); 
    return content;
}

function transferImage(img,src_grp,dest_grp){ 
    var url="/template/transfer_image?image_id="+img.attributes.nodeid+
        "&source_group_id="+src_grp.attributes.nodeid+
        "&dest_group_id="+dest_grp.attributes.nodeid;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                src_grp.fireEvent('click',src_grp);
                dest_grp.fireEvent('click',dest_grp);
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
