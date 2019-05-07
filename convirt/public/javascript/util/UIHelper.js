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
/*
 * MODES--EDIT_VM_INFO,EDIT_VM_CONFIG
 * panel1--Disks
 * panel2--Networks
 * panel3--BootParams
 * panel4--Miscellaneous
 * panel5--Provisioning
 */
//var convirt={};
convirt.PlatformUIHelper=function(platform,mode){
    this.mode=mode;
    this.platform=platform;
    var xen_in_memory=new Array('vmname','panel2','panel3','panel4'); 
    var xen_on_disk=new Array();
    var kvm_in_memory=new Array('memory','vcpu','boot_loader','boot_check','panel1','panel2','panel3','panel4');
    var kvm_on_disk=new Array('boot_loader','boot_check');
    this.getComponentsToDisable=function(){
        if(this.platform==='kvm'){
            if(this.mode==='EDIT_VM_INFO'){
                return kvm_in_memory;
            }else if(this.mode==='EDIT_VM_CONFIG'){
                return kvm_on_disk;
            }
        }else if(this.platform==='xen'){
            if(this.mode==='EDIT_VM_INFO'){
                return xen_in_memory;
            }else if(this.mode==='EDIT_VM_CONFIG'){
                return xen_on_disk;
            }
        }
        return (new Array());
    }
}


///////////// Communication Failure Handler Start/////////////
///Added by #SM
convirt.communication_failure_handler = function (){ this.request = null;
                                            this.response = null;
                                            this.start_time = null;
                                            this.end_time = null
                                            this.wait_time_out = 10;
                                        };

convirt.communication_failure_handler.prototype.set_request = function (request){this.request=request;};
convirt.communication_failure_handler.prototype.set_response = function (response){this.response=response;};
convirt.communication_failure_handler.prototype.set_start_time = function (start_time){this.start_time=start_time;};
convirt.communication_failure_handler.prototype.set_end_time = function (end_time){this.end_time=end_time;};

convirt.communication_failure_handler.prototype.get_request = function (){return this.request;};
convirt.communication_failure_handler.prototype.get_response = function (){return this.response;};

convirt.communication_failure_handler.prototype.clear_request = function (){this.request=null;};
convirt.communication_failure_handler.prototype.clear_response = function (){this.response=null;};

convirt.communication_failure_handler.prototype.start = function (reruest){
            this.set_request(reruest);
            this.set_start_time(new Date().getTime());
};
convirt.communication_failure_handler.prototype.end = function (response){
            this.set_response(response);
            this.set_end_time(new Date().getTime());
            this.clear_request();
            this.clear_warning();
};

convirt.communication_failure_handler.prototype.get_time_spend = function (){
    var time_spend_sec =  0;
    if (this.start_time != null){
//        console.log("--start_time!=null--");
        var time_spend = new Date().getTime() - this.start_time;
        time_spend_sec = time_spend/1000; //convert millisecond to second
    }
//   console.log("---time_spend_sec--"+time_spend_sec);
   return time_spend_sec;
};

convirt.communication_failure_handler.prototype.can_send_request = function (){
    if (this.get_request() === null){
        //allow to send new request
//        console.log("---request null---");
        this.clear_response();
        return true;
    }
    else{
//        console.log("--response--"+this.get_response());
        if (this.get_response() === null && this.get_time_spend() > this.wait_time_out){
            this.clear_request()
//            console.log("---time spend > 10---");
            //allow to send new request
            return true
        }
    }
    return false;
};

convirt.communication_failure_handler.prototype.set_warning = function (msg){
        var message = msg;
        document.getElementById("header-warning-img").style.display = 'block';
        document.getElementById("header-warning-img").title = message;
};

convirt.communication_failure_handler.prototype.clear_warning = function (){
        document.getElementById("header-warning-img").style.display = 'none';
        document.getElementById("header-warning-img").title = "";
};
///////////// Communication Failure Handler End/////////////




