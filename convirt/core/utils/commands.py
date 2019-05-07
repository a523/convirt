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
#


def get_cmd_copy_block_device_from_remote(node_username, node_address, source_file_path, source_disk_name):
    """
        Command to copy Block device from remote machine by running command on local machine
        'ssh' to remote machine, read Block device, then 'zip' block device, then 'unzip' and save into a file in the local machine
    """
    cmd = "ssh " + node_username+"@"+ node_address + " 'dd if=" + source_file_path + " bs=4096k | gzip -c' | gzip -cd > " + source_disk_name
#    cmd = "ssh " + node_username+"@"+ node_address + " 'dd if=" + source_file_path + " bs=4096k  | tar -czSf -' | tar -xzf -"
    return cmd

def get_cmd_copy_file_from_remote(node_username, node_address, file_dir, file_name):
    """
        Command to copy a file from remote machine (sparse file copy) by running command on local machine
        'ssh' to remote machine, then 'tar' file, then 'untar' to local machine
        -S : sparse
    """
    cmd = "ssh " + node_username+"@"+ node_address + " 'cd " + file_dir + " && tar -czSf - "+ file_name +"' | tar -xzf -"
    return cmd

def get_cmd_copy_spares_file_to_remote(node_username, node_address, src_filename, dest_dir):
    """
    """
    cmd = "tar -cSzf - " + src_filename + " | ssh " + node_username + "@" + node_address + " 'tar -xzf - -C " + dest_dir + "'"
    print "## cmd: " , cmd
    return cmd

def get_cmd_dd(source_file_path, dest_file_path):
    """
        Command to copy Block device using 'dd' command
    """
    cmd = "dd if=" + source_file_path + " bs=4096k of=" + dest_file_path
    return cmd

def get_cmd_cp(source_file_path, dest_file_path, options=None):
    """
        Command to copy file or directory
    """
    if options is None:
        options = "-ar" ## keep sparseness
    cmd = "cp "+ options + " "+ source_file_path + " " + dest_file_path
    return cmd

def get_cmd_remove_dir(dir, options=None):
    """
        Command to remove file or directory
    """
    if options is None:
        options = "-rf"
    cmd = "rm "+ options +" " + dir
    return cmd


def get_cmd_kill_pid(pid, options=None):
    """
        Command to kill process using process id (PID)
    """
    pid = str(pid)
    if options is None:
        options = "-9"
    cmd = "kill "+ options +" " + pid
    return cmd


def get_cmd_kill_pid_file(pid_file, options=None):
    """
        Command to kill process using process id (PID)
        pid_file : This will contains the PID of process to be killed
        #kill -9 $(</mnt/convirt_sharing/IMG_x3/pid_file)
    """
    if options is None:
        options = "-9"
    cmd = "kill "+ options + " $(<" + pid_file + ")"
    return cmd


def get_cmd_move(source_file_path, dest_file_path, options=None):
    """
        Command to Move file or directory
    """
    if options is None:
        options = ""
    cmd = "mv "+ options + " "+ source_file_path + " " + dest_file_path
    return cmd