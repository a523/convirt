#   ConVirt   -  Copyright (c) 2008 Convirture Corp.
#   ======
#
# ConVirt is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at:
#
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# author : Jd <jd_jedi@users.sourceforge.net>
#
# VMService.py
#
#   This module contains code that handles
#   Provisioning of a VM node.
#
from convirt.viewModel.VMInfo import VMInfo
import Basic
import pylons
from convirt.core.utils.utils import to_unicode,to_str,print_traceback
from convirt.core.utils.utils import *
from convirt.viewModel.NodeService import NodeService
from convirt.model.VM import ImageDiskEntry, VMDiskManager, VMStorageLinks
from convirt.model.storage import StorageDef, StorageManager
import logging, traceback
LOGGER = logging.getLogger("convirt.viewModel")
#import cherrypy
from convirt.model.DBHelper import DBHelper
from convirt.model.VM import VM
from convirt.model import DBSession
from sqlalchemy import *
from convirt.model.ImageStore import Image
from convirt.core.utils.utils import get_config
class VMService:
    def __init__(self):
        self.appliance_store = Basic.getApplianceStore()
        self.image_store     = Basic.getImageStore()
        self.manager         = Basic.getGridManager()
        self.registry        = Basic.getPlatformRegistry()
        self.node_service    = NodeService()
        self.storage_manager = Basic.getStorageManager()

    def get_initial_vmconfig(self,auth,image_id,mode):
#        print image_id
        result={}
        try:
            image=self.image_store.get_image(auth,image_id)
            if image is None:
                raise Exception("Can not find the specified Image.")
            vm_config,image_config = image.get_configs()
            #vm_config=get_config(image.vm_config)
            for key in vm_config:
                result[key]=vm_config.get(key)

            result["os_name"]=image.os_name
            result["os_version"]=image.os_version
            result["os_flavor"]=image.os_flavor
            
            if mode=="edit_image_settings":
                result["filename"]=vm_config.get("filename")
                result["version"]=to_str(image.version)
                img=auth.get_entity(image_id)
                group=img.parents[0].name
                result['group']=group
                result['vm_count']=len(image.get_vms())
                result['old_vmcount']=len(image.get_older_version_vms())
            else:
                result["filename"]=self.get_vm_conf_dir(image_config)
        except Exception, ex:
            raise ex
        return result

    def get_vm_conf_dir(self,image_config):
        value="$VM_CONF_DIR"
#        for key in image_config:
#            if key =='VM_CONF_DIR' :
#                   value=image_config[key]
        return value

    def get_miscellaneous_configs(self,auth,image_id,dom_id,node_id,group_id,action):        
        result=[]
        display_list=[]

        if action=="change_vm_settings":
                #dom = self.node_service.get_dom(auth,dom_id,node_id)
                dom=DBHelper().find_by_name(VM,dom_id)
                if dom is not None:
                    vm_config=dom.get_config()
        else:
            image=self.image_store.get_image(auth,image_id)
            if image is None:
                raise Exception("Can not find the specified Image.")

            if dom_id is None:
                vm_config,img_config = image.get_configs()
                #vm_config=get_config(image.vm_config)
            else:
                #dom = self.node_service.get_dom(auth,dom_id,node_id)
                dom=DBHelper().find_by_name(VM,dom_id)
                vm_config=dom.get_config()

            if action=='provision_image' or action=='provision_vm':
                group=self.manager.getGroup(auth,group_id)
                if group is not None:
                    grp_settings = group.getGroupVars()
                    merge_pool_settings(vm_config,img_config,grp_settings, True)
                
        for key in vm_config:
#            print key,"---++--",vm_config[key]
            if key not in self.node_service.get_exclude_list() and \
               key not in vm_config.get_computed_options() :
                display_list.append(key)

        display_list.sort()
        
        for key in display_list:
            value=vm_config[key]
            value=process_value(value)
            result.append(dict(attribute=key,value=to_str(value)))
        return dict(success='true',rows=result)

    def get_template_grid_info(self,auth,image_id,type):
        result=[]
        image=self.image_store.get_image(auth,image_id)
        display_list=[]
        if image is None:
            raise Exception("Can not find the specified Image.")

        if type == 'Misc':
           vm_config,img_config = image.get_configs()
        for key in vm_config:
#            print key,"---++--",vm_config[key]
            if key not in self.node_service.get_exclude_list() and \
               key not in vm_config.get_computed_options() :
               display_list.append(key)

        display_list.sort()

        for key in display_list:
            value=vm_config[key]
            if value == 0 or value == 1:
               value = get_string_status(value)
            result.append(dict(attribute=constants.misc.get(key,key),value=to_str(value)))
        return result

    def get_provisioning_configs(self,auth,image_id):

        display_list=[]
        result=[]
        image=self.image_store.get_image(auth,image_id)

        if image is None:
            raise Exception("Can not find the specified Image.")
        vm_config,image_config = image.get_configs()

        #image_config=get_config(image.image_config)
        for key in image_config:
            if key not in image_config.get_computed_options():
                display_list.append(key)

        display_list.sort()
        for key in display_list:
            value=process_value(image_config[key])
            result.append(dict(attribute=key,value=to_str(value)))

        return dict(success='true',rows=result)



    def get_disks(self,auth,image_id,mode,dom_id,node_id,group_id,action):
        result=[]
        try:
            if action=="change_vm_settings":
                return self.disk_data(auth,dom_id,node_id,mode)
            else:
                image=self.image_store.get_image(auth,image_id)
                if image is None:
                    raise Exception("Can not find the specified Image.")

                grp_settings={}
                group=self.manager.getGroup(auth,group_id)
                if group is not None:
                    grp_settings = group.getGroupVars()

                disks=[]
                vm_config,image_config = image.get_configs()
                if mode !="NEW":
                    if dom_id is not None :
#                        dom = self.node_service.get_dom(auth,dom_id,node_id)
                        dom=DBHelper().find_by_name(VM,dom_id)
                        vm_config=dom.get_config()
                    if action!='edit_image_settings':
                        merge_pool_settings(vm_config,image_config,grp_settings, True)
                        vm_config.instantiate_config(image_config)
                    disks = vm_config.getDisks(image_config)
                else:
                    new_disk = self.get_new_disk_entry(image_config)
                    if action!='edit_image_settings':
                        if grp_settings.get('VM_DISKS_DIR',None) is not None:
                            new_disk.filename=new_disk.filename.replace('$VM_DISKS_DIR',grp_settings.get('VM_DISKS_DIR'))
                        elif image_config.get('VM_DISKS_DIR') is not None:
                            new_disk.filename=new_disk.filename.replace('$VM_DISKS_DIR',image_config.get('VM_DISKS_DIR'))
                    disks=[new_disk]

        #        print "DDDDDDEVICe  =",disks
        #        vm_config,image_config = image.get_configs()

                is_remote=False

                for disk in disks:
                    if vm_config:
                        is_remote = vm_config.get_storage_stats().get_remote(disk.filename)
                        storage_disk_id = vm_config.get_storage_stats().get_storage_disk_id(disk.filename)
                        result.append(dict(type=disk.type,filename=disk.filename,device=disk.device,
                                        mode=disk.mode,shared=is_remote,option=disk.option,disk_create=disk.disk_create,
                                        size=disk.size,disk_type=disk.disk_type,image_src=disk.image_src,
                                        image_src_type=disk.image_src_type,image_src_format=disk.image_src_format,fs_type=disk.fs_type,storage_disk_id=storage_disk_id))
        except Exception, ex:
            print_traceback()
            raise ex
        return result

    def disk_data(self,auth,dom_id,node_id,mode):
        result=[]
        vm_config=None
        if mode !="NEW":
           # dom = self.node_service.get_dom(auth,dom_id,node_id)
            dom=DBHelper().find_by_name(VM,dom_id)
            if dom is None:
                raise Exception("Can not find the specified .")
            vm_config=dom.get_config()
            disks=VMDiskManager(vm_config).getDisks(dom.id)
        else:
                #new_disk = self.get_new_disk_entry(None)
                #TODO: think about this, can we change this
                new_disk = VMDiskManager(vm_config).get_new_disk_entry()
                disks=[new_disk]
        is_remote=False
        for disk in disks:
            storage_disk_id = ""
            storage_id = ""
            storage_name=None
            if vm_config:
                #is_remote = vm_config.get_storage_stats().get_remote(disk.filename)
                is_remote = VMDiskManager(vm_config).get_remote(disk.disk_name)
                #storage_disk_id = vm_config.get_storage_stats().get_storage_disk_id(disk.filename)
                storage_disk_id = VMDiskManager(vm_config).get_storage_disk_id(disk.disk_name)
                storage_id = VMDiskManager(vm_config).get_storage_id(disk.disk_name)
                if storage_disk_id:
                    vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=disk.id, storage_disk_id=storage_disk_id).first()
                    if vm_storage_link:
                        if storage_id:
                            defn = self.storage_manager.get_defn(storage_id)
                            storage_name = defn.name

            """
            result.append(dict(type=disk.type,filename=disk.filename,device=disk.device,
                                mode=disk.mode,shared=is_remote,option=disk.option,disk_create="",
                                size=disk.size,disk_type=disk.disk_type,image_src=disk.image_src,
                                image_src_type=disk.image_src_type,image_src_format=disk.image_src_format,fs_type="",storage_disk_id=storage_disk_id))
            """
            if mode!="NEW":
                disk_gb=disk.disk_size*1024
                disk_size=round(disk_gb)
            else:
                disk_size=disk.disk_size
            result.append(dict(type=disk.disk_type,filename=disk.disk_name,device=disk.dev_type,
                                mode=disk.read_write,shared=is_remote,option="",disk_create="",
                                size=disk_size,disk_type=disk.disk_type,image_src="",
                                image_src_type="",image_src_format="",fs_type=disk.file_system,
                                storage_disk_id=storage_disk_id, storage_id=storage_id,
                                storage_name=storage_name,sequence=disk.sequence))
        return result

    def get_new_disk_entry(self, image_conf = None):
        return ImageDiskEntry(("file","","","w"), image_conf)

    def get_disks_options_map(self):
        try:
            result=[]
            dic={ "Create New Disk": "CREATE_DISK",
                 "Use Physical Device" : "USE_DEVICE",
                 "Use ISO File" : "USE_ISO",
                 "Clone Reference Disk" : "USE_REF_DISK",
                 }
            for key in dic.keys():
                  result.append(dict(id=dic[key],value=key))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',disks_options=result)

    def get_disks_type_map(self,option,mode):
        try:

            if mode in ["edit_image_settings", "provision_image","provision_vm"]:
                if option == "CREATE_DISK":
                    value_map = self.get_disk_type_map()
                elif option == "USE_DEVICE":
                    value_map = self.get_disk_type_map_4_existing_disk()
                elif option == "USE_ISO":
                     value_map = self.get_disk_type_map_4_iso()
                elif option == "USE_REF_DISK" :
                    value_map = self.get_disk_type_map_4_ref_disk()
            else:
                value_map = self.get_disk_type_map_4_vm_config()


            result=[]
#            if option=="USE_REF_DISK":
#                dic={ "File (VBD)": "file*VBD",
#                 "Logical Volume" : "phy*LVM",
#                 "Select Existing Device": "phy*",
#                 "QCOW": "tap:qcow*qcow2",
#                 "VMDK": "tap:vmdk*vmdk"
#                }
#            elif option=="CREATE_DISK":
#                 dic={  "File (VBD)": "file*VBD",
#                 "QCOW": "tap:qcow*qcow2",
#                 "VMDK": "tap:vmdk*vmdk",
#                 "Logical Volume" : "phy*LVM"
#                }
#            elif option=="USE_ISO":
#                dic={ "Select ISO ": "file*ISO"}
#            elif option=="USE_DEVICE":
#                dic={"Select Existing Device": "phy*"}
#            else:
#                dic={ "File (VBD)": "file",
#                     "QCOW": "tap:qcow",
#                     "VMDK": "tap:vmdk",
#                     "Physical Device" : "phy"
#                }

            for key in value_map.keys():
                (type,disk_type)=value_map[key]
                result.append(dict(id=type,value=key,disk_type=disk_type))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',disks_type=result)


    def get_vmdevice_map(self,platform):
        try:
            result=[]
            dic = {"hda": "hda",
                "hdb": "hdb",
                "hdc": "hdc",
                "hdc:cdrom": "hdc:cdrom",
                "hdd": "hdd"
                }
            if platform=='xen':
                dic['xvda']='xvda'
                dic['xvdb']='xvdb'
                dic['xvdc']='xvdc'
            if platform=='kvm':
                dic['vda']='vda'
                dic['vdb']='vdb'
                dic['vdc']='vdc'
                dic['vdd']='vdd'

            for key in dic.keys():
                  result.append(dict(id=dic[key],value=key))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',vm_device=result)


    def get_device_mode_map(self):
        try:
            result=[]

            dic={ "Read-Only": "r",
                 "Read-Write" : "w",
                 "Read-ForceWrite" : "w!"}
            for key in dic.keys():
                  result.append(dict(id=dic[key],value=key))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',device_mode=result)

    def get_ref_disk_format_map(self,format_type):
        print "-----",format_type
        try:
            result=[]
            if format_type=="disk_image":
                dic= { "Raw": "raw",
                 "dir-gzipped-chunks" : "dir-gzipped-chunks",
                 ".bz2": "bzip",
                 ".gz" : "gzip",
                 ".zip": "zip",
                 ".tar": "tar",
                 ".tar.gzip": "tar_gzip",
                 ".tar.bz2" : "tar_bzip",
                 }
                for key in dic.keys():
                    result.append(dict(id=dic[key],value=key))

            elif format_type=="disk_content":
                dic1={
                    # ".bz2": "bzip", (Need to add to provision.sh)
                    # ".gz" : "gzip", (Need to add to provision.sh)
                     ".zip": "zip",
                     ".tar": "tar",
                     ".tar.gzip": "tar_gzip",
                     ".tar.bz2" : "tar_bzip",
                     "directory":"dir"
                     }
                for key in dic1.keys():
                    result.append(dict(id=dic1[key],value=key))

        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',ref_disk_img_format=result)

    def get_disk_fs_map(self):
        try:
            result=[]
            dic= {"None": "",
                "ext3": "ext3",
                "ext2" : "ext2",
                "swap" : "swap"}

            for key in dic.keys():
                    result.append(dict(id=dic[key],value=key))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',disk_fs=result)

    def get_ref_disk_type_map(self):
        try:
            result=[]
            dic={ "Disk Image": "disk_image",
                 "Disk Content" : "disk_content" }
            for key in dic.keys():
                    result.append(dict(id=dic[key],value=key))
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',ref_disk_type=result)

    def get_disk_type_map(self):
        return { "File (VBD)": ("file", "VBD"),
                 "QCOW": ("tap:qcow", "qcow2"),
                 "VMDK": ("tap:vmdk", "vmdk"),
                 "Logical Volume" : ("lvm", "LVM") 
                }

    def get_disk_type_map_4_ref_disk(self):
        return { "File (VBD)": ("file", "VBD"),
                 "Logical Volume" : ("lvm", "LVM"),
                 "Select Existing Device": ("phy", ""),
                 "Select Existing File Disk": ("file ", "VBD"),
                 "QCOW": ("tap:qcow", "qcow2"),
                 "VMDK": ("tap:vmdk", "vmdk"),
                }

    def get_disk_type_map_4_existing_disk(self):
        return { "Select Existing Device": ("phy", "")
               }

    def get_disk_type_map_4_iso(self):
        return { "Select ISO ": ("file", "ISO")
               }

    def get_disk_type_map_4_vm_config(self):
        return { "File (VBD)": ("file", ""),
                 "QCOW": ("tap:qcow", ""),
                 "VMDK": ("tap:vmdk", ""),
                 "Physical Device" : ("phy", ""),
                 "Logical Volume" : ("lvm", "")
                 }

    def get_command_list(self):
        try:
            result=[]
            dic= { "tightvnc": constants.TIGHTVNC,
                 "vncviewer": constants.VNC
                 }
            for key in dic.keys():
                 result.append(dict(id=key,value=dic[key]))

        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success='true',commands=result)


    def get_command(self,auth,node_id,dom_id,cmd):
        command=None
        try:
            command=tg.config.get(cmd)
            info={}
            value_map={}

            if cmd in [constants.VNC,constants.TIGHTVNC]:
                host=pylons.request.headers['Host']
                if host.find(":") != -1:
                    (address,port)=host.split(':')
                else:
                    address = host
                info=self.manager.get_vnc_info(auth, node_id, dom_id, address)
                value_map[constants.APPLET_IP] = info["hostname"]
                value_map[constants.PORT] = info["port"]
                         
            if command is not None:
                if type(command) in [types.StringType,types.UnicodeType]:
                    template_str = string.Template(command)
                    command = to_str(template_str.safe_substitute(value_map))

        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: "'Command not found'"}"
        return dict(success='true',cmd=command,vnc=info)

#    def get_vnc_log_content(self,file):
#        file_contents=""
#        try:
#            file=open(file,"r")
#            file_contents=file.read()
#            file_contents=file_contents.replace("\n","<br/>")
#        except Exception, e:
#            return dict(success=False,msg=to_str(ex).replace("'",""))
#        return dict(success=True,content=file_contents)