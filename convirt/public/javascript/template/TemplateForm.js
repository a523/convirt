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

function templateform(node){
      var empty_label=new Ext.form.Label({
        html:'<br/><center><font size="1"></center><br/>'
    });
     var template_label=new Ext.form.Label({
        html:'<div class="bluebackgroundcolor" align="center" width="250">'+
            _("Create a new Template using any of the following methods")+
            '</font><br/></div>'
    });

    var cancel_button=new Ext.Button({
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
        });
   
    var appliance=new Ext.form.Radio({
        boxLabel: '<font size=2>'+
            _("Import Appliance")+
            ': </font><table><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>'+
            _("Browse integrated catalogs and select an application to import as a Template.")+
            '</td></table>',
        id:'appliance',
        name:'radio',
        checked:true,
        listeners:{
            check:function(field,checked){               
                 if(checked==true){                    
                 }              
            }}
        });
    var refdisk=new Ext.form.Radio({
        boxLabel: '<font size=2>'+
            _("Using a Reference Disk")+
            ' :</font><table><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>'+
            _("Convert your reference disk or appliance that you have already downloaded as a Template.")+
            '</td></table>',
        id:'refdisk',
        name:'radio',
        listeners:{
            check:function(field,checked){
                 if(checked==true){                  
                 }
            }}
        });
     var virtualmachine=new Ext.form.Radio({
        boxLabel: '<font size=2>'+
            _("From existing Virtual Machine")+
            ' :</font><table><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>'+
            _("Select an existing Virtual Machine and convert it to a Template.")+
            '</td></table>',
        id:'virtualmchine',
        name:'radio',
        disabled:true,
        listeners:{
            check:function(field,checked){
                 if(checked==true){                   
                 }               
            }}
        });
    var ok_button=new Ext.Button({
            name: 'ok',
            id: 'ok',
            text:_('Ok'),
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            listeners: {
                click: function(btn) {
                 if(appliance.getValue()){
                      showTemplateList(node);
                  }
                  else if(refdisk.getValue()){
                      showrefDialog(node);
                  }
                  else{
                  Ext.MessageBox.alert(_('Errors'), _('Please select at least one option.'));
                  }

                }
            }
        });
    var outerpanel=new Ext.Panel({
         width:390,
         height:280,
         id:'outerpanel',
         frame:true,
         items:[template_label,empty_label,appliance,refdisk],
         bbar:[{
             xtype: 'tbfill'
          },ok_button,cancel_button]

    });

    return outerpanel;
}
 function showTemplateList(node){
    closeWindow();
    var url="/appliance/get_appliance_list";
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('Please wait...'),
        msg: _('Fetching Appliance List, Please wait...'),
        width:300,
        wait:true,
        waitConfig: {interval:200}
    });

    ajaxReq.request({
        success: function(xhr) {

            Ext.MessageBox.hide();
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                showWindow(_("Appliance Catalog"),715,425,ApplianceList(node));
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
function showrefDialog(node){
    closeWindow();
    showWindow(_("Reference Disk Details"),575,230,ImportApplianceDialog(node,null));
}
