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

var convirt={};

convirt.constants={
    DATA_CENTER : "DATA_CENTER",
    SERVER_POOL : "SERVER_POOL",
    MANAGED_NODE : "MANAGED_NODE",
    DOMAIN  : "DOMAIN",

    IMAGE_STORE : "IMAGE_STORE",
    IMAGE_GROUP : "IMAGE_GROUP",
    IMAGE : "IMAGE"

    ,CPU : "CPU"
    ,VMCPU : "VM CPU"
    ,MEM : "Memory"

    ,TOP5SERVERS:"TOP5SERVERS"
    ,COMPARISONCHART:"COMPARISONCHART"

    ,TOP50BYCPU : "Top 50 Servers by Host CPU(%)"
    ,TOP50BYMEM : "Top 50 Servers by Host Memory(%)"
    ,TOP50BYCPUVM : "Top 50 VMs by CPU Util(%)"
    ,TOP50BYMEMVM : "Top 50 VMs by Memory Util(%)"
    ,MEMUTIL_TEXT : "Host Memory(%)"
    ,CPUUTIL_TEXT : "Host CPU(%)"
    ,STRGUTIL_TEXT : "Storage(%)"
    ,VM_MEMUTIL_TEXT : "Memory(%)"
    ,VM_CPUUTIL_TEXT : "CPU(%)"
    ,VM_STRGUTIL_TEXT : "Storage(GB)"
    ,SP_TEXT : "Server Pool"
    ,SB_TEXT : "Standby server(yes/no)"
    ,SRVR_STATUS_TEXT : "Server Status(up/down)"
    ,SRVR_NAME_TEXT : "Server Name"
    ,OS_TEXT : "Operating System"
    ,PLTFM_TEXT : "Server Platform "
    ,VM_NAME_TEXT : "Virtual Machine"
    ,VM_STATUS_TEXT : "Status(up/down)"
    ,TEMPLATE_TEXT : "Template"

    ,DTD:"DTD"
    ,HRS12:"12HRS"
    ,HRS24:"24HRS"
    ,DAYS7:"7DAYS"
    ,DAYS30:"30DAYS"
    ,WTD:"WTD"
    ,MTD:"MTD"
    ,CUSTOM:"CUSTOM"

    ,VMS:"VMS"
    ,SERVERS:"SERVERS"

    ,SPECIAL_NODE:"SPECIAL_NODE"

    ,RUNNING  : "0"
    ,BLOCKED  : "1"
    ,PAUSED   : "2"
    ,SHUTDOWN : "3"
    ,CRASHED  : "4"
    ,NOT_STARTED : "-1"
    ,UNKNOWN  : "-2"
    ,DOWN_RUNNING  : "D_0"
    ,DOWN_BLOCKED  : "D_1"
    ,DOWN_PAUSED  : "D_2"
    ,DOWN_SHUTDOWN  : "D_3"
    ,DOWN_CRASHED  : "D_4"
    ,DOWN_NOT_STARTED  : "D_-1"
    ,DOWN_UNKNOWN  : "D_-2"

    ,OUTSIDE_DOMAIN:"OUTSIDE"
    ,OS_FLAVORS:[
        ['Linux', 'Linux'],
        ['Windows', 'Windows']
    ]

    ,OS_NAMES :[
        ['SUSE', 'SUSE', 'Linux'],
        ['SLES', 'SLES', 'Linux'],
        ['CentOS', 'CentOS', 'Linux'],
        ['Ubuntu', 'Ubuntu', 'Linux'],
        ['RHEL', 'RHEL', 'Linux'],
        ['Debian', 'Debian', 'Linux'],
        ['Gentoo', 'Gentoo', 'Linux'],
        ['Fedora', 'Fedora', 'Linux'],
        ['Windows 2008', 'Windows 2008', 'Windows'],
        ['Windows XP', 'Windows XP', 'Windows'],
        ['Windows NT', 'Windows NT', 'Windows'],
        ['Windows 2003', 'Windows 2003', 'Windows'],
        ['Windows 7', 'Windows 7', 'Windows']
    ]
    ,VM_CONSOLE:"VM_CONSOLE"
    ,VM_CONSOLE_LOCAL_CMD:"VM_CONSOLE_LOCAL_CMD"

    ,upgrade_to_ee:"http://www.convirture.com/contact.php?option=upgrade2ee"
    ,learn_about_ee:"http://www.convirture.com/products_enterprise.php"
}
