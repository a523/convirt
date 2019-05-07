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

from datetime import datetime,date

_version = "2.5"
fox_header = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.4) Gecko/20070603 Fedora/2.0.0.4-2.fc7 Firefox/2.0.0.4 ConVirt/" + _version
_edition = "OSS"


#
# constants definitions
#

# config properties
prop_disks_dir = 'disks_dir'
prop_snapshots_dir = 'snapshots_dir'
prop_conf_dir = 'conf_dir'
prop_cache_dir = 'convirt_cache_dir'
prop_kernel = 'kernel'
prop_ramdisk = 'ramdisk'
prop_dom0_kernel = 'dom0_kernel'
#prop_staging_location = 'staging_location'
#prop_staging_path_kernel = 'staging_path_kernel'
#prop_staging_path_ramdisk = 'staging_path_ramdisk'
prop_snapshot_file_ext = 'snapshot_file_ext'
#prop_bootloader = 'bootloader'
prop_lvm = 'lvm_enabled'

prop_isRemote = 'is_remote'
prop_image_store="image_store"
prop_appliance_store="appliance_store"
prop_log_dir='log_dir'
prop_exec_path = 'exec_path'
prop_default_computed_options="default_computed_options"

prop_updates_url = "updates_url"
prop_updates_file = "updates_file"
prop_ref_update_time = "ref_update_time"

# node specific properties
prop_login = "login"
prop_ssh_port= "ssh_port"
prop_migration_port= "migration_port"
prop_use_keys= "use_keys"
prop_address = "address"
prop_platform = "platform"
prop_hostname = "hostname"
prop_last_vncdisplay = "last_vncdisplay"

# ManagedNode environment identifiers
prop_env_SYSTEM = 'SYSTEM'
prop_env_RELEASE = 'RELEASE'
prop_env_VER = 'VERSION'
prop_env_MACHINE_TYPE = 'MACHINE'
prop_env_NODE_NAME = 'NODE'
prop_env_PROCESSOR = 'PROCESSOR'
prop_env_KERNEL = 'RELEASE'

#client config properties
prop_gnome_vfs_enabled = "gnome_vfs_enabled"      # by default True
prop_init_confirmation = 'confirm_dialog'
#prop_browser = "html_browser"       # Location of browser
prop_imagestore_default = 'default_image'

prop_enable_paramiko_log="enable_paramiko_log"
prop_paramiko_log_file = 'paramiko_log_file'

prop_enable_log="enable_log"
prop_log_file = "log_file"
prop_cli_log_file="cli_log_file"

prop_vncviewer = "vncviewer"
prop_local_vncviewer = "local_vncviewer"
prop_vncviewer_options = "vncviewer_options"
prop_vncviewer_via_tunnel = "vncviewer_via_tunnel"
prop_default_ssh_port= "default_ssh_port"
prop_default_use_keys = "default_use_keys"

prop_http_proxy = "http_proxy"
prop_ftp_proxy = "ftp_proxy"

prop_chk_updates_on_startup = "check_updates_on_startup"
prop_guess_proxy = "guess_proxy"

prop_use_vnc_proxy="use_vnc_proxy"
prop_vnc_host="vnc_host"
prop_vnc_port="vnc_port"
prop_vnc_user="vnc_user"
prop_vnc_password="vnc_password"


prop_ssh_forward_host="ssh_forwarder"
prop_ssh_forward_port="ssh_forwarder_port_range"
prop_ssh_forward_user="ssh_forwarder_user"
prop_ssh_forward_password="ssh_forwarder_password"
prop_ssh_forward_key = "ssh_forwarder_use_keys"
prop_ssh_tunnel_setup = "ssh_forwarder_tunnel_setup"
prop_ssh_log_level = 'ssh_log_level'

VNC_APPLET_HEIGHT="vnc_applet_param_height"
VNC_APPLET_WIDTH="vnc_applet_param_width"
VNC_APPLET_PARAM_OPEN_NEW_WINDOW="vnc_applet_param_new_window"
VNC_APPLET_PARAM_SHOW_CONTROL="vnc_applet_param_show_controls"
VNC_APPLET_PARAM_ENCODING="vnc_applet_param_encoding"
VNC_APPLET_PARAM_RESTRICTED_COLOURS="vnc_applet_param_restricted_colors"
VNC_APPLET_PARAM_OFFER_RELOGIN="vnc_applet_param_offer_relogin"

default_xen_pv_driver="default_xen_pv_driver"
vm_disk_types = "vm_disk_types"

ssh_file="ssh_file"

# Global identifiers
LOCALHOST = 'localhost'
DEFAULT_LOG_DIR="/var/log/convirt"

# APP DATA section
prop_domfiles = "vms"
prop_groups = "groups"
prop_images = "images"
prop_image_groups = "image_groups"

prop_storage_defs = "storage_defs"
prop_node_sds = "node_storage_defs"
prop_group_sds = "group_storage_defs"


prop_nw_defns = "nw_defns"
prop_node_defn_status = "node_defn_status"
prop_group_defn_status = "group_defn_status"



# properties for Information Tab
key_os_release= 'release'
key_os_system='system'
key_os_machine='machine'
key_os_distro='distro'
key_os_distro_ver='distro_ver'
key_os_distro_string='distro_string'

key_network_interface_name='interface_name'
key_network_ip='ip_address'

key_cpu_count='no_of_processors'
key_cpu_vendor_id='vendor_id'
key_cpu_model_name='model_name'
key_cpu_mhz = "cpu_mhz"

key_memory_total='total_memory'
key_memory_free='free_memory'
key_disk_file_system='file_system'
key_disk_size='size'
key_disk_mounted='mounted_on'

display_os_release= 'Kernel'
display_os_system='Platform'
display_os_machine='Architecture'
display_os_distro='Distribution'

display_network_interface_name='INTERFACE NAME'
display_network_ip='IP ADDRESS'

display_cpu_count='Processors'
display_cpu_vendor_id='Vendor Id'
display_cpu_model_name='Model'
display_cpu_mhz = "Speed (MHz)"

display_memory_total='Total Memory (MB)'
display_memory_free=' Availble Memory (MB)'

display_disk_file_system='FILE SYSTEM'
display_disk_size='SIZE'
display_disk_mounted='MOUNTED ON'
display_platform_xen_version='Xen Version'
display_platform_xen_caps='Xen Capabilites'

display_tab_os_info="OS Info"
display_tab_cpu_info="CPU Info"
display_tab_memory_info="Memory Info"
display_tab_disk_info="Disk Info"
display_tab_network_info="Network Info"
display_tab_platform_info="Platform Info"

reqd_config_options=['vcpus', 'disk', 'memory', 'vif', 'boot']
TASK_CANCELED='TASK_CANCELED'
VM_SHARED_STORAGE="VM_SHARED_STORAGE"
VM_LOCAL_STORAGE="VM_LOCAL_STORAGE"
VM_TOTAL_STORAGE="VM_TOTAL_STORAGE"

NODE_LIST_LIMIT="NODE_LIST_LIMIT"

POOL_STORAGE_TOTAL="POOL_STORAGE_TOTAL"

#file constants
VERSION_FILE="VERSION.TXT"
SCHEMA_VERSION="SCHEMA_VERSION"
DATA_VERSION="DATA_VERSION"
CONFIG_VERSION="CONFIG_VERSION"
APP_VERSION="APP_VERSION"

# Web poc constants
START   = "start"
PAUSE   = "pause"
REBOOT  = "reboot"
SHUTDOWN= "shutdown"
KILL    = "kill"
MIGRATE = "migrate"
SNAPSHOT= "snapshot"
RESTORE = "restore"
CONSOLE = "console"

#SEARCHTEXT

TOP50BYCPU="Top 50 Servers by Host CPU(%)"
TOP50BYMEM="Top 50 Servers by Host Memory(%)"
DOWNSERVERS="Down Servers"
STANDBYSERVERS="Standby Servers"

TOP50BYCPUVM="Top 50 VMs by CPU Util(%)"
TOP50BYMEMVM="Top 50 VMs by Memory Util(%)"
DOWNVM="Down VMs"
RUNNINGVM="Running VMs"

#PROPERTIES
MEMUTIL_TEXT        = "Host Memory(%)"
CPUUTIL_TEXT        = "Host CPU(%)"
STRGUTIL_TEXT       = "Storage(%)"
VM_MEMUTIL_TEXT     = "Memory(%)"
VM_CPUUTIL_TEXT     = "CPU(%)"
VM_STRGUTIL_TEXT    = "Storage(GB)"
SP_TEXT             = "Server Pool"
SB_TEXT             = "Standby server(yes/no)"
SRVR_STATUS_TEXT    = "Server Status(up/down)"
SRVR_NAME_TEXT      = "Server Name"
OS_TEXT             = "Guest OS"
PLTFM_TEXT          = "Server Platform "
VM_NAME_TEXT        = "Virtual Machine"
VM_STATUS_TEXT      = "Status(up/down)"
TEMPLATE_TEXT       = "Template"

#SEARCHVALUES
MEMUTIL_VALUE     = "MEMUTIL"
CPUUTIL_VALUE     = "CPUUTIL"
STRGUTIL_VALUE    = "STRGUTIL"
SP_VALUE          = "SP"
SB_VALUE          = "SB"
SRVR_STATUS_VALUE = "SRVR_STATUS"
SRVR_NAME_VALUE   = "SRVR_NAME"
OS_VALUE          = "OS"
PLTFM_VALUE       = "PLTFM"
VM_NAME_VALUE     = "VM_NAME"
VM_STATUS_VALUE   = "VM_STATUS"
TEMPLATE_VALUE    = "TEMPLATE"

VMS="VMS"
SERVERS="SERVERS"

CUSTOM_SEARCH_LIMIT="CUSTOM_SEARCH_LIMIT"
AVAILABILITY = u'Availability'
VM_AVAILABILITY = u'VM Availability'
COLLECT_METRICS = u'Collect Metrics'

SERVER_POOL = "SERVER_POOL"
MANAGED_NODE = "MANAGED_NODE"
DOMAIN  = "DOMAIN"
OUTSIDE_DOMAIN = "OUTSIDE"
EMAIL = "EMAIL"

SPECIAL_NODE="SPECIAL_NODE"

DATA_CENTER= "DATA_CENTER"

DC="Data Center"
IS="Image Store"
APPLIANCE="APPLIANCE"
APPLIANCE_FEED="APPLIANCE_FEED"
APPLIANCE_CATALOG="APPLIANCE_CATALOG"

# Constants required for cli
IMAGE_STORE = "IMAGE_STORE"
IMAGE = "IMAGE"
IMAGE_GROUP = "IMAGE_GROUP"
VM_SHARED_STORAGE = "VM_SHARED_STORAGE"

NODEINFO_CATEGORY="NODEINFO_CATEGORY"
NODEINFO_COMPONENT="NODEINFO_COMPONENT"
NODEINFO_INSTANCE="NODEINFO_INSTANCE"

# Paths
SNAPSHOT_FILE_LOCATION="/var/cache/convirt/snapshots/"
SNAPSHOT_FILE_EXT=".snapshot.xm"

DEFAULT_USERS=['admin']
DEFAULT_GROUPS=['adminGroup']

NO_PRIVILEGE='You do not have sufficient privilege for this operation.'
RESUME_TASK='Resuming Task\n'
RECOVER_TASK='Recovering Task\n'
INCOMPLETE_TASK="Task Service was restarted before the task was completed."
ADVANCED_PRIVILEGES="ADVANCED_PRIVILEGES"
GRANULAR_USER_MODEL="GRANULAR_USER_MODEL"
RECOVER_TIME="RECOVER_TIME"

start_time="start_time"
shutdown_time="shutdown_time"
pause_time="pause_time"
unpause_time="unpause_time"
reboot_time="reboot_time"
kill_time="kill_time"
migrate_time="migrate_time"
TASKPANEREFRESH="TASKPANEREFRESH"
NOTIFICATION_ROW_LIMIT="notifications_row_limit"
PAGEREFRESHINTERVAL="PAGEREFRESHINTERVAL"
SERVER_PROTOCOL="server_protocol"
# metrics type
VM_RAW = 1
VM_CURR = 2
VM_ROLLUP = 3
SERVER_RAW = 4
SERVER_CURR = 5
SERVER_ROLLUP = 6
SERVERPOOL_RAW = 7
SERVERPOOL_CURR = 8
SERVERPOOL_ROLLUP = 9
DATACENTER_RAW = 10
DATACENTER_CURR = 11
DATACENTER_ROLLUP = 12

# rollup_type
HOURLY = 1
DAILY = 2
MONTHLY = 3
WEEKLY = 4
RAW = 5

METRIC_CPU='CPU'
METRIC_VMCPU='VM CPU'
METRIC_MEM='Memory'

DTD='DTD'
MTD='MTD'
WTD='WTD'
HRS12='12HRS'
HRS24='24HRS'
DAYS7='7DAYS'
DAYS30='30DAYS'
CUSTOM='CUSTOM'
CACHE_TIME='CACHE_TIME'
MAX_CACHE_SIZE='MAX_CACHE_SIZE'
MIGRATING='MIGRATING'
PAUSED='PAUSED'
RESUMED='RESUMED'

TaskPaneLimit='TaskPaneLimit'
task_panel_row_limit='task_panel_row_limit'

TOP5SERVERS="TOP5SERVERS"
COMPARISONCHART="COMPARISONCHART"

NONSECURE=1
TLS=2
SSL=3

PORTS = 'ports'

# Initialise default date
defaultDate = datetime(1970,1,1)

#Storage/ Network Sync constants
IN_SYNC = "IN_SYNC"
OUT_OF_SYNC = "OUT_OF_SYNC"
#Storage/ Network Scope constants
SCOPE_S = 'S'
SCOPE_SP = 'SP'
SCOPE_DC = 'DC'
#Storage Type constants
STORAGE = 'STORAGE'
NETWORK = 'NETWORK'
NFS = "nfs"
iSCSI = "iscsi"
AOE = "aoe"
STORAGE_STATS = "STORAGE_STATS"
#Scan result constant
SCAN_RESULT = "SCAN_RESULT"
#NFS background task
UPDATE_DISK_SIZE_INTERVAL = "UPDATE_DISK_SIZE_INTERVAL"
#VM Data for matching
VM_DISK_DATA = "VM_DISK_DATA"
VM_DISK_LINK_DATA = "VM_DISK_LINK_DATA"
#Script Operator
ATTACH = "ATTACH"
DETACH = "DETACH"
GET_DISKS = "GET_DISKS"
GET_DISKS_SUMMARY = "GET_DISKS_SUMMARY"
GET_DETAILS = "GET_DETAILS"
XEN_LOG_PATH = "/var/log/xen/xend.log"

ORACLE="oracle"
MYSQL="mysql"
SQLITE="sqlite"

platforms={
'xen':'Xen',
'kvm':'KVM'
}
platform_version={
'xen':'xen_version',
'kvm':'version'
}

misc={
'acpi':'ACPI',
'apic':'APIC',
'arch':'Architecture',
'arch_libdir':'Architecture Lib Directory',
'device_model':'Device Model',
'boot':'Boot',
'builder':'Builder',
'pae':'PAE',
'platform':'Platform'
}

image_starting_version=1.0

#For LockManager
AVAIL_STATE=u'AvailState'
METRICS=u'Metrics'
COLLECT_METRICS=u'CollectMetrics'
PURGE_METRICS=u'Purge'
ROLLUP_METRICS=u'RollUp'

Table_metrics=u'metrics'
Table_metrics_curr=u'metrics_curr'
Table_metrics_arch=u'metrics_arch'
Table_avail_current=u'avail_current'

#remote system connection constants
VNC="vnc"
TIGHTVNC="tight_vnc"

SSH_CMD = "ssh_cmd"
PUTTY_CMD = "putty_cmd"

APPLET_IP="IP"
PORT="PORT"
USER = u"USER"

#instane platform
WINDOWS="windows"
LINUX  ="linux"

XEN_NEW_VERSION=4

TXT_DC      = "Data Center"
TXT_TL      = "Template Library"
TXT_SP      = "Server Pool"
TXT_SRVR    = "Server"
TXT_VM      = "Virtual Machine"
TXT_TG      = "Template Group"
TXT_TMPL    = "Template"
TXT_APPL    = "Appliance"

DEBUG_CATEGORIES = {
    "DC_SP_SR_VM" : ["DC_dashboard", "SP_dashboard", "SR_dashboard", "VM_dashboard"],
    "DC_SP_SR" : ["DC_dashboard", "SP_dashboard", "SR_dashboard"],
    "SP_SR_VM" : ["SP_dashboard", "SR_dashboard", "VM_dashboard"],
    "DC_SP" : ["DC_dashboard", "SP_dashboard"],
    "DC" : ["DC_dashboard"],
    "SP" : ["SP_dashboard"],
    "SR" : ["SR_dashboard"],
    "VM" : ["VM_dashboard"]
}

NOTIFICATION_COUNT = u"NOTIFICATION_COUNT"
TASK_PURGE_COUNT = u"TASK_PURGE_COUNT"

RESOURCES="resources"
