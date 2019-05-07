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

function handleApplianceEvents(node,action,item){
    getApplianceInfo(node,action);
}

function showApplianceList(node,action){
    var url="/appliance/get_appliance_list";
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('Please wait..'),
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
                showWindow(_("Appliance Catalog"),715,425,ApplianceList(node,action));
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

function getApplianceInfo(node,action){
    var dom_id=node.attributes.text;
    var node_id=node.parentNode.attributes.id;
    var params="dom_id="+dom_id+"&node_id="+node_id;
    var url="/appliance/get_appliance_info?"+params;
    
    if(action.substring(0,4)=="NAV_")
        url+="&action="+action;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if(action=="SPECIFY_DETAILS" || !response.appliance.is_valid)
                    showWindow(_("Appliance Details"),315,325,ApplianceDetails(node,action,response.appliance,dom_id,node_id));
                else
                    doApplianceAction(action,response.appliance)
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function doApplianceAction(action,appliance){
    if(action=="VISIT_APPLICATION")
        window.open(appliance.web_url)
    else if(action=="SPECIFY_DETAILS")
        return
    else
        window.open(appliance.mgmt_web_url)
}
