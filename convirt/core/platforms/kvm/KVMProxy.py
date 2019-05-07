#!/usr/bin/env python
#
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
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# 
#
# author : Jd <jd_jedi@users.sourceforge.net>
#

###
#  VMM for KVM/qemu operations
###

import select, traceback, fcntl, re

from convirt.core.utils.utils import dynamic_map, randomMAC, mkdir2
from convirt.core.utils.utils import to_unicode,to_str
from convirt.core.utils.phelper import *
from convirt.core.utils.NodeProxy import *
from convirt.model.VMM import VMM
from kvm_constants import *


QEMU_PROMPT = "(qemu)"
START_TOKEN = '\x1b'+ '[D'
STOP_TOKEN  = '\x1b' + '[K'
####
# TODO : 
#        parse cmd line : populate other fields, use options and reverse map
#


class KVMProxy(VMM):
    pid_dir = "/var/run/kvm/pids"
    monitor_dir = "/var/run/kvm/monitors"
    kvm_binary = "qemu-system-x86_64"  # assume to be in path
    qemu_binary = "qemu"
    kvm_binary_path="/usr/local/kvm/bin:$PATH"
    # TODO: see if the option parsing code can be reused.
    kvm_options_with_v = ("name", "pid", "m", "smp",
                          "vnc", "image","cdrom", "loadvm", "monitor",
                          "stopped", "dry-run", "hda","hdb", "hdc", "hdd",
                          "kernel","initrd", "append",
                          "net","balloon", "serial", "parallel", "pidfile","p",
                          "d", "hdachs", "L", "kvm-shadow-memory",
                          "option-rom", "mem-path", "clock", "startdate",
                          "boot", "incoming",  "usbdevice",
                          "M", "cpu", "fda", "fdb", "drive", "mtdblock",
                          "sd", "pflash","k", "soundhw", "tftp", "bootp",
                          "smb", "redir", "vmchannel", "baloon", "serial",
                          "parrallel", "kvm-shadow-memory", "vga",
                          "acpitable", "smbios", "bt", "bios", "icount", 
                          "watchdog", "watchdog-action", "echr", 
                          "virtioconsole", "tb-size", "chroot", "runas", 
                          "pcidevice", "enable-nesting", "nvram",'uuid'
                          )
    
    kvm_options_no_v = ("S", "s", "no-kvm", "no-kvm-irqchip",
                        "no-kvm-pit","std-vga", "no-acpi",
                        "curses", "no-reboot", "no-shutdown",
                        "daemonize", "tdf", "nographic", "portrait",
                        "snapshot", "no-frame", "alt-grab", "no-quit",
                        "no-fd-bootchk", "localtime", "full-screen",
                        "win2k-hack", "ctrl-grab", "rtc-td-hack", "no-hpet",
                        "show-cursor", "no-kvm-pit-reinjection", 
                        "mem-prealloc","usb",

                        )

    kvm_options = kvm_options_with_v + kvm_options_no_v
    qemu_options = kvm_options 


    # share the proxy operations and ssh_transport
    def __init__(self, node):
        self.node = node
        self.node_proxy = node.node_proxy
        self.transport = self.node_proxy.ssh_transport
        self.channel_map = {}
        self.vm_list = None
        self._info = None
        self._slashes = None

        if self.node_proxy.file_exists("/usr/libexec/qemu-kvm"):
            #print "Switching kvm binary to 'qemu-kvm'"
            self.kvm_binary = "/usr/libexec/qemu-kvm"

        if self.node_proxy.file_exists("/usr/bin/qemu-kvm"):
#            print "Switching kvm binary to 'qemu-kvm'"
            self.kvm_binary = "qemu-kvm"

        if self.node_proxy.file_exists("/usr/bin/kvm"):
#            print "Switching kvm binary to 'kvm'"
            self.kvm_binary = "kvm"


        self.info() # update kvm_binary

    # would be useful when we allow transport/proxy to be re-initialized
    def set_node_proxy(self,node_proxy):
        self.node_proxy = node_proxy
        self.transport = self.node_proxy.ssh_transport
        for id in self.channel_map.keys():
            ch = self.channel_map[id]
            ch.shutdown(2)
        self.channel_map.clear()
        self.vm_list.clear()

    def _get_channel(self, id):
        info = self.vm_list[id]
        monitor = info.get("monitor")
        if monitor is None:
            raise Exception("Can not connect to monitor: monitor option not specified")
        if self.channel_map.has_key(id):
            chan = self.channel_map[id]
            if self.node_proxy.isRemote:
                ret = chan.closed or chan.status_event.isSet()
                #ret = chan.exit_status_ready() # from paramiko 1.7.3
            else:
                ret = chan.poll()
                if ret is None:
                    ret = False
                else:
                    print "socat exit code = ", ret
                    ret = True
            
            if not ret:
                print "returning existing channel"
                return self.channel_map[id]
            else:
                print "cleaning up old channel"
                self._cleanup_channel(id, self.channel_map[id])

        # Fall through
        m = monitor.split(',')[0]
        cmd = "socat stdio " + m
        if self.node_proxy.isRemote:
            # create a new channel and return it.
            transport = self.node_proxy.ssh_transport
            chan = transport.open_session()
            chan.set_combine_stderr(True)
            chan.setblocking(0)
            chan.exec_command(cmd)
        else:
            # local use subprocess
            chan = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    stdin=subprocess.PIPE,
                                    universal_newlines=True,
                                    shell=True, close_fds=True)
            flags = fcntl.fcntl(chan.stdout, fcntl.F_GETFL)
            if not chan.stdout.closed:
                fcntl.fcntl(chan.stdout, fcntl.F_SETFL,
                            flags| os.O_NONBLOCK)

        self.channel_map[id] = chan
        # read intro message and qemu prompt
        (code, output) = self.read_till_prompt(id)
        if code != 0 :
            print id, code, output
            if not code:
                code = 127
            raise Exception("Error,connecting to the VM %s, error code = %d msg = %s" % (id, code, output))

        ## check if chan established... and working.. or socat
        ## failed.

        return chan


    # read from the channel till a particular pattern is found
    # TODO : Abstract the channel out here.. too many if isRemote
    def read_till_prompt(self,id):
        chan = self._get_channel(id)
        out = ""
        exit_code = 0
        try:
            while True:
                try:
                    # This one needs a timeout.. need to think about
                    # but can not be small as the app may take more time
                    # to process and return result. 
                    if self.node_proxy.isRemote:
                        if not select.select([chan,], [], []):
                            break
                    else:
                        if not select.select([chan.stdout,], [], []):
                            break

                    if self.node_proxy.isRemote:    
                        x = chan.recv(1024)
                    else:
                        x = chan.stdout.read(1024)
                        
                    if not x: break
                    #print x
                    out += x

                    if x.strip().endswith(QEMU_PROMPT):
                        return (0, out)

                    select.select([],[],[],.1)
                except (socket.error,select.error),  e:
                    if (type(e.args) is tuple) and (len(e.args) > 0) and \
                           ((e.args[0] == errno.EAGAIN or e.args[0] == 4)):
                        try:
                            select.select([],[],[],.1)
                        except Exception, ex:
                            print ex
                            pass
                        continue
                    else:
                        raise
            if self.node_proxy.isRemote:        
                exit_code = chan.recv_exit_status()
            else:
                exit_code = chan.returncode

            return (exit_code, out)

        finally:
            print "in finally block"
            if exit_code != 0:
                self._cleanup_channel(id, chan)

    def _cleanup_channel(self, id, chan):
        try:
            if self.node_proxy.isRemote:
                chan.close()
            else:
                for f in (chan.stdout, chan.stderr, chan.stdin):
                    if f is not None:
                        f.close()
            del self.channel_map[id]
        except Exception, ex:
            print "Exception in _cleanup_channel ", e


    def _sanitize(self,output):
        start_pos = output.rfind( START_TOKEN )
        token = None
        if start_pos > 0 :
            start_pos = start_pos + len(START_TOKEN)
            end_pos = output.rfind(STOP_TOKEN)
            if end_pos > 0 and end_pos > start_pos:
                token = output[start_pos:end_pos]
                return token + output[end_pos + len(STOP_TOKEN):]
            
        return output
                

    def send_command(self, id, command):
        chan = self._get_channel(id)        
        if self.node_proxy.isRemote:
            chan.send(command + "\n")
        else:
            os.write(chan.stdin.fileno(),command + "\n")
        (code,output) = self.read_till_prompt(id)
        #print "output in send_command 0", output
        if output:
            output = self._sanitize(output)
        #print "output in send_command 1", output        
        if output and output.strip().endswith(QEMU_PROMPT):
            output = output.strip()[:0-len(QEMU_PROMPT)]
            return (output.strip(), True)
        else:
            return (output, False)



    def _get_file_content(self, filename, max_chars=None):
        content = None
        f = None
        try:
            try:
                f = self.node_proxy.open(filename)
                if max_chars:
                    content = f.read(max_chars)
                else:
                    content = f.read()
            finally:
                if f:
                    f.close()
        except Exception, ex:
            traceback.print_exc()
            print "Error reading file content ", filename, ex

        return content

    # TODO : Use nested maps to represent networks and disks
    #        Also seperation between arguments with values and
    #        boolean arguments
    def populate_info_from_cmdline(self, info, cmdline):
        # for  now only pick the monitor and vnc
        options = cmdline.split(chr(0))
        ndx = 0
        for o in options:
            ndx += 1
            o = o.strip()
            if o.endswith("-monitor") or o.endswith("-vnc") or \
                   o.endswith("-name") or o.endswith("-incoming"):
                if o.find('-') == 0:
                    key = o[1:]
                if o.find('--') == 0:
                    key = o[2:]
                if len(options) > ndx:
                    if key == ("monitor"):
                        value = options[ndx].split(",")[0]
                    else:
                        value = options[ndx]
                    if not info.get(key):
                        info[key] = value   # clean up value too.
                    else: # handle multiple occurrence of values
                        v = info[key]
                        if isinstance(v, str):
                            info[key] = [v, value]
                        elif isinstance(v, list):
                            v.append(value)
                    
        # guess the name from the monitor name file.
        if info.get("name") == None:
            m = info.get("monitor")
            if m is not None:
                info.name = m[m.rfind('/')+1:]


    def get_slashes(self):
        if self._slashes is None:
            ver_num = self.get_version_int(self.info().get(key_version))
            if ver_num > 77:
                self._slashes = ""
            else:
                self._slashes =  "//"
        return self._slashes

    ################ Implement some of the VMM interface #############
    # Start, Stop, Pause, Resume, Kill, Take snapshot, Restore Snapshot

    """ info about the vmm capabilities and node info as seen by vmm """
    def info(self):
        if self._info is None:
            info_cmd = self.kvm_binary + ' -help | head -1'
            (out, code) = self.node_proxy.exec_cmd(info_cmd,
                                                   self.kvm_binary_path)
            if code == 0:
                s = re.search("ersion (.*),",out)
                if s:
                    version = s.group(1)
                    self._info = { key_version : version }
            else:
                self._info = { key_version : "?" }

        return self._info 

    """ if the vmm is in some error state."""
    def is_in_error(self):
        return False

    """  connect to the vmm (if not connected)"""
    def connect(self):
        pass

    """ disconnect from the vmm """
    def disconnect(self):
        pass


    def get_vms(self):
        #if self.vm_list is None:
        self.refresh_vm_list()
        return self.vm_list

    def get_vm_info(self, name):
        vms = self.get_vms()
        print "@@@@", vms
        return vms.get(name)


    def refresh(self, id, pid_filename=None):
        pid = id
        pid_string = to_str(pid)
        cmd_line_file = os.path.join('/proc',pid_string,'cmdline')
        
        if pid_filename is not None:
            if self.node_proxy.file_exists(cmd_line_file)==False:                
                self.node_proxy.remove(pid_filename)
                return None

        cmd = None
        cmd = self._get_file_content(cmd_line_file, 2048)

        if cmd is None or cmd.strip() == '':
            return None

        if cmd.split(chr(0),1)[0].endswith("qemu"):
            type = "qemu"
        elif cmd.find("kvm") > -1 or cmd.find("qemu-system-x86") > -1:
            #later look at fds and see if /dev/kvm used
            type = "kvm"
        else:
            return None

        info = dynamic_map()
        info.type = type
        info.cmdline= cmd.strip().replace(chr(0), " ")
        info.pid = to_str(pid)
        info.domid = to_str(pid)
        self.populate_info_from_cmdline(info, cmd)
        if info.name is None:
            info.name = info.pid
        info.id = info.name # will need to change once the client changes
                                  # to use proper id

        return info

    def refresh_vm_list(self):
        vms = {}
        if not self.node_proxy.file_exists(self.pid_dir):
            mkdir2(self.node, self.pid_dir)
        pid_files = self.node_proxy.listdir(self.pid_dir)
        for pid_file in pid_files:
            f = None
            pid = 0
            pid_string = None
            pid_filename=os.path.join(self.pid_dir, pid_file)
            pid_string = self._get_file_content(pid_filename, 10)
            
            if pid_string and pid_string.strip().isdigit():
                pid_string = pid_string.strip()
                pid = int(pid_string)
            else:
                print "ignoring up ", pid_filename
                continue

            if not pid:
                print "pid is none, skipping"
                continue
            
            info = self.refresh(pid,pid_filename)
            if info is not None:
                # allow access by name of id
                #vms[info.name] = info
                vms[info.id]=info
#            else:
#                print "removing pid file, process does not exist."
#                self.node_proxy.remove(pid_filename)
                
        self.vm_list = vms
        return vms

    def get_version_int(self, v_str):
	"""
		Value of v_str will be
		1.0 (qemu-kvm-1.0)
		0.12.3 (qemu-kvm-0.12.3)
	"""
        v= v_str
        if not v:
            return 0
        v = v.replace(".","") # this should work with 0.11.x + versions
        index=v.find('kvm-')
        if index > -1:
            s_index = index + 4
            # skip the devel- from kvm-devel-88 
            while s_index < len(v) and (v[s_index].isdigit() == False) : 
                s_index = s_index + 1
            index=s_index
            while index < len(v) and v[index].isdigit() : 
                index = index + 1
	    tmp = v[s_index:index] 
	    #print "\nKVM Version Number : ",tmp ##This will be 10 or 0123
	    if tmp[0:1] != "0":
		##If version start with 1.x return 100
		return 100
            return int(v[s_index:index])
        return 0
                

    # Use the config and start a new vm.
    def start(self,config,timeout=5):
        if config is None:
            raise Exception("No context provided to start the vm")

        #config.dump()
        # check the version and prompt the user
        info = self.info()
        if info.get(key_version):
            v = info.get(key_version)
            if v.find('kvm-') < 0:
                raise Exception("You seem to have an older version of KVM/QEMU\n The version does not contain 'kvm-' token :%s\n Please make sure kvm-70 or higher is installed and is in PATH." % v)


        # take the config.. and generate a cmdline for kvm/qemu
        cmd = self.kvm_binary
        known_options = self.kvm_options
        if config.get("type") and config.get("type") == "qemu":
            print "Using simple qemu"
            cmd = self.qemu_binary
            known_options = self.qemu_options

        # build the cmd line
        cmdline = cmd
        vnc_processed = False
        skip_kernel_rd = False

        # add disks first
        opt = "disk"
        value = config.get(opt)
        disk_entries = config.getDisks()
        boot_flag=False
        for d in disk_entries:
            flag = 0
            if d.device.find(":cdrom") > -1 or \
                    d.filename == ("/dev/cdrom"):
                opt = "cdrom"
                hd=d.device.replace(":cdrom","")
                value1 = config.get(hd+"_use_drive_opt")
                if value1 and value1==1:
                    flag = 1
                    opt=hd
            else:
                opt = d.device
                use_drive = opt+"_use_drive_opt"
                value1 = config.get(use_drive)
                if value1 and value1==1:
                    flag = 1

            value = d.filename                 

            """
            here, if opt is either of vdx, then call one more function
            which adds the -drive option and other values

            """
            if opt.startswith("vd") or flag == 1:
                drive_boot=to_str(config.get(opt+"_drive_boot"))
                if drive_boot=="on":
                    cmdline = cmdline.replace(",boot=on","",1)
                cmdline = self.qemuCall(cmdline, opt, value, config)
                if boot_flag==False:
                    auto_boot=to_str(config.get("virtio_no_auto_boot"))
                    if auto_boot!="1":
                        cmdline+=",boot=on"
                    boot_flag=True
            # mode, and type are not used.
            # filename can be file or device so it would work.
            # mode : Dont know how to specify readonly disk
            else:
                cmdline = self.process_option(cmdline, opt, value,
                                          known_options)

        for opt in config.keys():
            value = config.get(opt)
            opt = opt.replace("_", "-") # python prohibits - in variables
            if opt == "extra":
                opt = "append"

            if opt == "memory" :
                opt = "m"
            elif opt == "vcpus":
                opt = "smp"
            elif opt == "stdvga":
                opt = "std-vga"
                if to_str(value) != '1':
                    continue
            elif opt == "ramdisk":
                opt = "initrd"
            elif opt == "acpi":
                if to_str(value) == '0':
                    cmdline = self.process_option(cmdline, "no-acpi", "",
                                                   known_options)
                continue

            elif opt == "vif" and not config.get("net"):
                #Transform vif in to -net options
                vifs = value
                if vifs:
                    vlan=-1
                    for vif in vifs:
                        vlan = vlan + 1
                        parts = vif.split(',')
                        x = dict([p.strip().split('=') for p in parts])
                        macaddr = x.get("mac")
                        if not macaddr:
                            macaddr=randomMAC()
                        opt_val = "nic,vlan=%d,macaddr=%s" % ( vlan, macaddr)
                        
                        # model
                        model = x.get("model")
                        if model:
                            opt_val = opt_val + ",model=" + model
                            
                        cmdline = self.process_option(cmdline, "net",
                                                      opt_val, known_options)
                        # if bridge is specified, lets try to specify the script
                        # Assumes bridge is created and script would
                        # add the tap interface to the bridge
                        
                        # TODO : if the bridge can be somehow specified as
                        # param to the script in /etc/qemu-ifup and
                        # /etc/qemu-ifdown
                        
                        bridge=x.get("bridge")

                        mode = config.get("network_mode")
                        if not mode:
                            if bridge:
                                mode = "tap"
                            else:
                                mode = "user"

                        opt_val = "%s,vlan=%d" % (mode, vlan)

                        if mode == "tap":
                            # interface name
                            ifname = x.get("ifname")
                            if ifname:
                                opt_val = opt_val + ",ifname=" + ifname
                            # script
                            script = x.get("script")
                            if script:
                                opt_val = opt_val + ",script=" + script
                            #downscript
                            down_script = x.get("downscript")
                            if down_script:
                                opt_val = opt_val + ",downscript=" + down_script
                            else:
                                # see if the bridge specific script is there.
                                if bridge:
                                    s1 = "/etc/kvm/kvm-ifup-%s" % (bridge,)
                                    s2 = "/etc/kvm/qemu-ifup-%s" % (bridge,)
                                    s3 = "/etc/qemu-ifup-%s" % (bridge,)
                                    s4 = "/etc/qemu/qemu-ifup-%s" % (bridge,)
                                    for s in [ s1, s2, s3, s4 ]:
                                        if self.node_proxy.file_exists(s):
                                            # assume it is executable.
                                            opt_val = opt_val + ",script=" + s
                                            break
                            # vhost
                            vhost = x.get("vhost")
                            if vhost:
                                opt_val = opt_val + ",vhost=" + vhost

                        elif mode == "user":
                            # hostname
                            hname = x.get("hostname")
                            if hname:
                                opt_val = opt_val + ",hostname=" + hname

                        cmdline = self.process_option(cmdline, "net",
                                                       opt_val, known_options)
                        
                        
                        # TODO : Support custom script
                continue
            elif opt in ["vnc","vncdisplay"] and not vnc_processed:
                vnc_processed = True
                value = config.get("vnc")
                if value == 1 or value == "1":
                    vncdisplay = config.get("vncdisplay")
                    if not vncdisplay:
                        vncdisplay = self.node.get_unused_display()
                    if vncdisplay:
                        value = ":" + to_str(vncdisplay)
                        cmdline = self.process_option(cmdline, opt, value,
                                                      known_options)
                continue
            elif opt in ["kernel", "initrd", "append"] :
                if not skip_kernel_rd :
                    # hack
                    k_value = config.get("kernel")
                    if k_value:
                        if k_value.find("hvmloader") > -1: #skip xen hvmloader 
                            skip_kernel_rd = True
                            continue
                else:
                    # ignore the initrd and append/extra too.
                    continue

            if opt in self.kvm_options_no_v:
                if value == 0 or value == "0" :
                    continue
                value = ""
            else:
                if not value:
                    continue

            cmdline = self.process_option(cmdline, opt, value, known_options)
                        
        # The following is done to have the convention and
        # temporarily have the name of VM available in the command line.
        if not self.node_proxy.file_exists(self.monitor_dir):
            mkdir2(self.node, self.monitor_dir)
        monitor_path = os.path.join(self.monitor_dir, config.get("name"))
        cmdline = cmdline + " -monitor " + """"unix:%s,server,nowait\"""" % (monitor_path,)
                 
        pid_fname = os.path.join(self.pid_dir, config.get("name"))
        cmdline = cmdline + " -pidfile  " + """"%s\"""" % (pid_fname,)
                    
        # daemonize.. the command can return
        cmdline = cmdline + " -daemonize"

        #incoming_val = config.get("incoming")
        #if incoming_val and (incoming_val.find("tcp://") == 0 or \
        #                     incoming_val.find("ssh://") == 0 ):
        #    cmdline += " &"

        print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n**************************** CMDLINE ****************************** ", cmdline
        
        (output, ret) = self.node_proxy.exec_cmd(cmdline, self.kvm_binary_path,
                                                 timeout)
        if ret != 0:
            print "start failed :", cmdline,output
            raise Exception((output, ret))
        print "start : success ", output
        self.get_vms()
        if config.get("vncpasswd"):
            self.set_vnc_password(config.get("name"),config.get("vncpasswd"))

        return config.get("name")

    def qemuCall(self, cmdline, opt, value, config):
        
        cmdline = cmdline + " -drive"
        if opt.startswith("hd"):
            if value is not None:
                cmdline = cmdline + " file=" + value
            x=opt[2]
            index = to_str(ord(x)-96)
            cmdline = cmdline + ",index="+index
            if value=="/dev/cdrom":
                cmdline = cmdline +",media=cdrom"
            else:
                cmdline = cmdline +",media=disk"
        else:
            if value is not None:
                cmdline = cmdline + " file=" + value
            cmdline = cmdline + ",if=virtio"
        for opt1 in config.keys():
            value1 = config.get(opt1)            
            list = opt1.split("_")
            if len(list)>2 and list[0] == opt:
                if list[1] == "drive":
                    op=opt1.replace(opt+"_drive_","")
                    if op!="":
                        cmdline = cmdline + ","+op+"="+value1        
        return cmdline

    def process_option(self, cmdline, opt, value, known_options):

        if opt in known_options:
            if opt == "monitor" and value.find(",")== -1 :
                print "IGNORING : monitor value ", value
                return cmdline

            if value is not None:
                if isinstance(value, int) or isinstance(value, unicode):
                    value = to_str(value)
                elif isinstance(value, list):
                    for v in value:
                        cmdline = cmdline + " -" + opt
                        cmdline = cmdline + " " + """"%s\"""" % (v,)
                    return cmdline

                if isinstance(value, str):
                    cmdline = cmdline + " -" + opt
                    if value != "" :
                        cmdline = cmdline + " " + """"%s\"""" % (value,)
                else:
                    print "ERROR : Unknown type, Ignoring ", opt, value
                    
        return cmdline

    def shutdown(self,id):
        cmd = "system_powerdown"
        (output,prompt) = self.send_command(id, cmd)
        if prompt and output == cmd:
            return True
        else:
            raise Exception(cmd + ":" +output)
        
    def reboot(self,id):
        cmd = "system_reset"
        (output,prompt) = self.send_command(id, cmd)
        if prompt and output == cmd:
            return True
        else:
            raise Exception(cmd + ":" +output)


    # Stop/Pause running VM
    # When u pause the output returned is weired.
    def pause(self,id):
        #raise Exception("KVM : Pause not implemented")
        (output,prompt) = self.send_command(id,"stop")
        if prompt and output == "stop":
            return True
        else:
            raise Exception("pause:" +  output)
        
    def unpause(self,id):
        #raise Exception("KVM : Resume not implemented")
        (output,prompt) = self.send_command(id,"cont")
        if prompt and output == "cont":
            return True
        else:
            raise Exception("resume:" + output)


    # stop the vm and is migrate to file
    # Also save the config as a ctx that would be used in restore.
    def save(self,id, filename, cfg):
        #raise Exception("KVM : Not implemented.")
        cmd = "stop" 
        (output,prompt) = self.send_command(id, cmd)
        if prompt and output == cmd:
            # vm stopped now lets use migrate to save it to the file
            # save vmconfig context ?
            ver_num=self.get_version_int(self.info().get(key_version))
            if ver_num > 77:
                cmd = "migrate " + """"exec: gzip -c > %s.gz\"""" % (filename,)
            else:
                cmd = "migrate " + "file://%s" % (filename,)
            (output,prompt) = self.send_command(id, cmd)
            if prompt and output == cmd:
                print "vm state saved to " + filename
                if ver_num > 77:
                    ctx_filename = filename + ".gz.ctx"
                else:
                    ctx_filename = filename + ".ctx"
              #  contents = cfg.get_contents()
                contents=""
                for key in cfg:
                    value=cfg.get(key)
                    if isinstance(value, unicode):
                        value=to_str(value)
                    if isinstance(value, str):
                        value="\'"+value+"\'"
                    contents+="%s = %s\n" % (key, value)
#                print "\n",contents
                outfile = self.node.node_proxy.open(ctx_filename, 'w')
                outfile.write(contents)
                outfile.close()
                print "context saved to " + ctx_filename
                self.destroy(id)
                return True
            else:
                #print """'%s' '%s'""" % (output, cmd)
                raise Exception(cmd + ":[" + output + "]")
        else:
            raise Exception(cmd + ":[" + output + "]")
        
    # assumes that the ctx file and the snapshot are in the
    # same place.
    def restore(self,filename):
        ctx_file = filename + ".ctx"
        if filename is not None and len(filename) > 4:
            if filename[-4:] == ".ctx":
                ctx_file = filename 
                filename = filename[0:-4]
        
        cfg = self.node.new_config(ctx_file)
        ver_num=self.get_version_int(self.info().get(key_version))
        if ver_num > 77:        
            cfg["incoming"] = "exec: gzip -c -d " + filename 
        else:
            cfg["incoming"] = "file://" + filename 
        id = self.start(cfg,120)
        #self.unpause(id) 
        # inline for now
        (output,prompt) = self.send_command(id,"cont")
        if prompt and output == "cont":
            return True
        else:
            raise Exception("restore/resume:" + output)

 

    def quit_vm(self,id):
        cmd = "quit"
        info=self.vm_list.get(id)
        if info and info.get("incoming"):
            self.destroy(id)
        else:
            (output,prompt) = self.send_command(id, cmd)
            if prompt and output == cmd:
                return True

        # After VM quits.. there is no output from the monitor.
        #else:
        #    raise Exception(cmd + ":" + output)
                
        return True

    def destroy(self, id):
        # look for the process, make sure it is a qemu process
        # kill the process.
        vm = self.vm_list.get(id)
        pid = vm["pid"]
        (output, code) = self.node_proxy.exec_cmd("kill -9 " + pid, timeout=5)
        if code != 0 and code != -99:
            raise Exception("Error : VM Kill %s %s: %s : %s" % (id, pid, to_str(code), output))


    def migrate(self, id, dst, live, port, cfg):
        # start a VM with same/similar param on the dst node.
        #   -- pick a port for migration
        #   -- pick vnc port
        # give the migrate command to the current one
        # check for status?!

        # TODO : interface may need to be made flexible: currently
        #        listen on all interfaces.

        print "LIVE MiGRATION ", live
        cfg["incoming"] = "tcp:%s0:%s" % (self.get_slashes(), to_str(port))

        try:
            dst.create_dom(cfg)
        except Exception, ex :
            if ex.args and isinstance(ex.args[0], tuple):
                (output, ret) = ex.args[0]
                if ret == -99 : # special value from node proxy.
                    # ignore it, the incoming process is blocking
                    pass
                else:
                    raise
                
        try:
            if not live:
                print "non-live migration.. stopping VM"
                cmd = "stop" 
                (output,prompt) = self.send_command(id, cmd)
                if prompt and output == cmd:
                    pass
                else:
                    raise Exception("error stopping VM during migration :" + output)
            
            cmd = "migrate tcp:%s%s:%s" % (self.get_slashes(), 
                                           dst.get_address(),
                                           to_str(port))
            print "Initiating migration ", cmd
            (output,prompt) = self.send_command(id,cmd)
            if prompt and output == cmd:
                self.quit_vm(id)
                return True
            else:
                raise Exception("migrate:" +  output)

            if cfg.get("vncpasswd"):
                self.set_vnc_password(cfg.get("name"),cfg.get("vncpasswd"))
        except :
            self.cleanup_remote_vm(dst, cfg.name)
            raise

    def cleanup_remote_vm(self, dst, remote_vm):
        try:
            if remote_vm:
                dst.refresh()
                dst.destroy_dom(remote_vm)
                print "remote vm dstroyed ", remote_vm
        except Exception ,e:
            print "=============="
            traceback.print_exc()
            print "--------------"
            print "error cleaning up remote vm", e


                
    # available snapshots
    def list_snapshots(self,id):
        cmd = "info snapshots"
        (output,prompt) = self.send_command(id, cmd)
        if prompt and output.find(cmd) == 0:
            print output.split()
            return output
        else:
            raise Exception(cmd + ":" + output)

    # change to live running VM
    def setVCPUs(self, id, value):
        raise Exception("KVM : Can not change vcpu for running vm.")

    def setMem(self, id, value):
        raise Exception("KVM : Can not change memory for running vm.")

   # attach disks in memory
    def attachDisks(self,id,attach_disk_list):
       raise Exception("KVM : Can not attach disks for running vm.")

    # detach disks in memory
    def detachDisks(self,id,detach_disk_list):
       raise Exception("KVM : Can not detach disks for running vm.")

    def set_vnc_password(self,id,password):
        print "Setting vnc password"
        cmd = "change vnc passwd %s"%(password)
        (output,prompt) = self.send_command(id, cmd)
        if prompt and output.find(cmd) == 0:
            print output.split()
            return output
        else:
            raise Exception(cmd + ":" + output)

if __name__ == '__main__':
    print "Enter password :"
    pwd = sys.stdin.readline().strip()
    node_proxy = Node( hostname = "192.168.12.101",
                       ssh_port=22,
                       username="root",
                       password=pwd,
                       isRemote=True)

    vmm = KVMProxy(node_proxy)
    
    config = {}
    config["platform"]="kvm"
    config["hda"]="/vm_disks/fc-7.qcow2"
    config["m"] = 512
    config["name"] = "fc-7"
    #config["monitor"] = "unix:/var/cache/convirt/monitors/" + config["name"]
    config["vnc"] = ":5"

    import pprint
    print "sys.argv" , pprint.pprint(sys.argv)
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        vmm.start(config)
    
    doms = vmm.get_vms()

    for id in doms.keys():
        print doms[id]

    #sys.exit(0)
    print "enter pid "
    pid = sys.stdin.readline().strip()
    if pid.isdigit():
        pid = int(pid)
        print "pausing", pid
        vmm.pause(pid)
        print "paused."
        
        sys.stdin.readline()
        print "continue", pid
        vmm.resume(pid)
        print "resumed."
        
        sys.stdin.readline()
        print "saving snapshot x"
        vmm.save(id, "x")
        print "saved vm x"
        

        sys.stdin.readline()
        print "restoring snapshot x"
        vmm.load_vm(id, "x")
        print "restored vm x"

        sys.stdin.readline()
        print "quiting vm"
        vmm.quit_vm(id)
        print "vm quit"
        
    else :
        print "Invalid PID"

    
    sys.exit(0)
    
    #transport = node_proxy.ssh_transport
    #chan = transport.open_session()
    #chan.set_combine_stderr(True)
    #chan.setblocking(0)
    #chan.exec_command("socat stdin tcp:0:5555")

    #if chan.recv_ready():
    #    print "recv ready"
    #else:
    #    print "can not connect to terminal"
    #    sys.exit(0)
        
    
    #vmm.read_till_prompt(chan)
    #output =  vmm.send_command(chan, "help")
    #print output
    
    ## while True:
##         try:
##             command = sys.stdin.readline()
##             if command.strip() == "quit":
##                 break
##             output = vmm.send_command(chan,command.strip())
##             print output
##         except Exception, ex:
##             print ex
            
        
    
                                   

