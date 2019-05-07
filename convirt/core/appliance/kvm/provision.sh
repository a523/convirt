#!/bin/bash
#### 
# GENERIC SCRIPT
# This script will get executed on the managed node (The node on which
# the new vm is being provisioned.)
# 
# The script should do all the setup required for being able to start the
# vm.
#
# This typically involves  
#    - Creating disk(s)  (LVM volumes, VBD files etc)
#    - Preparing disks: either copying or installing contents in the disk
#    - fetches the kernel and ramdisk from kernel_src and ramdisk_src 
#      if not already available.
#    - running customization scripts for fixing prepared disks. For example,
#      updating fstab file, updating inittab or even installing additional i
#      packages
#
# Feel free to copy/customize it for your environment.
#
# author : jd_jedi@users.sourceforge.net
#
###


# parse the command line parameters
while getopts i:s:p:x:l:c: o
do case "$o" in
	x)	vm_config="$OPTARG";;
	p)	param_file="$OPTARG";;
	s)	store="$OPTARG";;
	i)	image_name="$OPTARG";;
	c)	image_conf="$OPTARG";;
	l)	log_file="$OPTARG";;
	esac
done

common_loc="$store"/common
image_root="$store"/"$image_name"
custom_loc="$store"/custom_scripts
image_custom_loc="$store"/"$image_name"/custom_scripts

# source common files
source "$common_loc"/defs
source "$common_loc"/functions

log_msg "$0 starting"
log_msg "vm_config" $vm_config
log_msg "param_file" $param_file
log_msg "store" $store
log_msg "log_file"  $log_file


# source the image store specific file 
# some variables would get overwritten by vm config or params by user
# down the line
if [ -f "$image_conf" ]; then
   source_python_config "$image_conf"
fi

log_msg "custom_list" $custom_list

# source the vm config variables 
source_python_config "$vm_config"

# source additional params passed by UI
source "$param_file"


# create a list from the disk directive
disk_list=`python <<EOF
exec "disk=$disk"
disks = ""
for d in disk:
    disks +=  "%s " %d
print disks
EOF
`
#echo $disk_list

for l in $disk_list
do
   # non-greedy for protocol, accomodate tap:aio, tap:qcow options
   #frag=`echo $l  | $SED -e "s/\([^:]*\):\(.*\),\(.*\),\(.*\)/d_type=\\1 d_name=\\2 d_dev=\\3 d_mode=\\4/"`
   frag=`echo $l | $SED -e "s/\(tap:\)\([^:]*\):\(.*\),\(.*\),\(.*\)/d_type=\\1\\2 d_name=\\3 d_dev=\\4 d_mode=\\5/" -e "s/\([^:]*\):\(.*\),\(.*\),\(.*\)/d_type=\\1 d_name=\\2 d_dev=\\3 d_mode=\\4/"`
   eval $frag
   d_dev=`echo $d_dev | $SED s/ioemu://g`
   echo $d_type $d_name $d_dev $d_mode 
   # Use the disk related variables to create/copy disks as you wish
   # use ${d_dev}_image_src_type i.e. $hda_image_type to get fig out what
   # needs to be done. 
   # Then depending on the type, either copy the vbd
   # or 
   # create the disk, format it, copy/unzip the content
   #

   # SIMPLE FLOW GIVEN BELOW 
   
   if [ "$d_mode" = "r" ]; then
        log_msg "Not creating read only disk $d_name"
   	continue	
   fi	

   is_cdrom=`echo ${d_dev} | $GREP -i cdrom`
   if [ -n "$is_cdrom" ]; then
      log_msg "Skipping cdrom entry : ${d_dev}" 
      continue
   fi

   d_create_var=${d_dev}_disk_create
   d_create=${!d_create_var}

   d_disk_type_var=${d_dev}_disk_type
   d_disk_type=${!d_disk_type_var}
 
   
   d_img_src_var=${d_dev}_image_src
   d_img_src=${!d_img_src_var}

   d_img_src_type_var=${d_dev}_image_src_type
   d_img_src_type=${!d_img_src_type_var}

   d_img_src_format_var=${d_dev}_image_src_format
   d_img_src_format=${!d_img_src_format_var}
	   
   
   # default assume that disk has to be created and initialized
   d_size_var=${d_dev}_disk_size
   d_size=${!d_size_var}

   d_fs_type_var=${d_dev}_disk_fs_type
   d_fs_type=${!d_fs_type_var}


   # override d_type is disk type specified
   if [ -z "$d_disk_type" ]; then
      echo "Explicit disk type not specified using $d_disk_type"
   else
      # update disk type
      d_type=$d_disk_type
      echo "Modified disk params" $d_type $d_name $d_dev $d_mode 
   fi
 
   if [ -z "$d_img_src" ] && [ -z "$d_img_src_type" ]; then
       if [ -z "$d_create" ]; then 
	   log_msg "Skipping : $d_create_var not set for $d_dev."
	   continue
       fi
   
       if [ "$d_create" != "yes" ]; then
	   log_msg "Skipping : $d_create_var not set to 'yes' for $d_dev."
	   continue
       fi
 
       if [ -z "$d_size" ]; then
	   log_msg "Disk size not specified for $d_dev. Exiting." 	
	   exit 1
       fi
       log_msg "create_disk $d_type $d_name $d_size "
       create_disk "$d_type" "$d_name" "$d_size" 
   else
       # reference disk scenario, and LVM is requested
       # for all other file types or devices creation is not required
       # dd/cp would take care of it
       if [ "$d_type" == "LVM" ]; then
           if [ -z "$d_size" ] || [ "$d_size" = "0" ]; then
	       log_msg "Can not create $d_name LVM,Disk size not specified for $d_dev." 	
	       exit 1
	   fi
	   log_msg "create_disk $d_type $d_name $d_size "
	   create_disk "$d_type" "$d_name" "$d_size" 
       fi
   fi

   # raw disk created now lets see if we need to create a fs
   if [ -n "$d_fs_type" ]; then
       make_fs "$d_name" "$d_fs_type"
       if [ ! "$?" = "0" ]; then
           log_msg "Error creating $d_fs_type file system on $d_name"
           exit 1
       fi
   fi


   # see if src is disk_image, if so copy the reference disk image
   # as a target disk

   # Process reference disk Image 
   if [ -n "$d_img_src" ] && [ -n "$d_img_src_type" ]; then
       log_msg "src type = $d_img_src_type_var $d_img_src_type"
       if [ "$d_img_src_type" == "disk_image" ]; then
           # assume that img src is local (i.e. not http and ftp)
	   dir_name=`dirname $d_name`
	   if [ -d "$dir_name" ]; then
	       echo "$dir_name exists."
	   else
	       $MKDIR -p $dir_name
	       if [ "$?" != "0" ]; then
		   log_msg "Error creating $dir_name for creating : $d_name"
		   exit 1
	       fi 
	   fi

     	   if [ "$d_img_src_format" = "dir-gzipped-chunks" ]; then
               # here the src can not be remote
               # chunks get picked up in the right order. 
               file_count=0
               for f in "$d_img_src"/chunk*.gz
               do
                   if [ "$file_count" != "0" ]; then
		       $GUNZIP -cf  $f >> "$d_name"
                   else
		       $GUNZIP -cf  $f > "$d_name"
                   fi
		   if [ ! "$?" = "0" ]; then
		       log_msg "Error creating disk $d_name from chunks in $d_img_src"
		       exit 1
		   fi
                   file_count=`expr $file_count + 1`
               done
	   else
	       log_msg "Copying from reference disk $d_img_src to $d_name"
	       if [ "$d_img_src_format" = "gzip" ]; then
		   $GUNZIP -cf "$d_img_src" > "$d_name"
		   if [ ! "$?" = "0" ]; then
		       log_msg "Error unziping disk $d_name from $d_img_src"
		       exit 1
		   fi
	       elif [ "$d_img_src_format" = "tar" ]; then
		   $TAR -xf "$d_img_src" -O > "$d_name"
		   if [ ! "$?" = "0" ]; then
		       log_msg "Error untaring disk $d_name from $d_img_src"
		       exit 1
		   fi
	       elif [ "$d_img_src_format" = "tar_gzip" ]; then
		   $TAR -zxf "$d_img_src" -O > "$d_name"
		   if [ ! "$?" = "0" ]; then
		       log_msg "Error untaring disk $d_name from $d_img_src"
		       exit 1
		   fi
	       elif [ "$d_img_src_format" = "bzip" ]; then
		   $BUNZIP -cf "$d_img_src" > "$d_name"
		   if [ ! "$?" = "0" ]; then
		       log_msg "Error unziping disk $d_name from $d_img_src"
		       exit 1
		   fi
	       elif [ "$d_img_src_format" = "tar_bzip" ]; then
		   $TAR -jxf "$d_img_src" -O > "$d_name"
		   if [ ! "$?" = "0" ]; then
		       log_msg "Error untaring disk $d_name from $d_img_src"
		       exit 1
		   fi
	       elif [ "$d_img_src_format" = "zip" ]; then
		   $UNZIP -p "$d_img_src" > "$d_name"
		   if [ ! "$?" = "0" ]; then
		       log_msg "Error unzipping disk $d_name from $d_img_src"
		       exit 1
		   fi
               else
                   # assume it is raw image, just get it
		   if [ "${d_img_src:0:5}" = "/dev/" ] || [ "${d_name:0:5}" = "/dev/" ]; then
	               $DD if="$d_img_src" of="$d_name" bs=$DD_BLOCK_SIZE
		   else
		       fetch_file "$d_img_src" "$d_name"
		   fi
	           if [ ! "$?" = "0" ]; then
		       log_msg "Error creating disk $d_name from reference disk $d_img_src"
		       exit 1
	           fi
               fi
	   fi
	   continue
       fi 
   fi
 


   # process disk content
   # now disk is initialized with fs. mount it and copy the content
   if [ -n "$d_img_src" ] && [ -n "$d_img_src_type" ]; then
       if [ "$d_img_src_type" = "disk_content" ]; then
	   d_img_src_format_var=${d_dev}_image_src_format
	   d_img_src_format=${!d_img_src_format_var}
	   
	   if [ -z "$d_img_src_format" ]; then
	       d_img_src_format='tar'
	   fi
	   # assume it is tar, tar gz or tar bz2 zip
	   copy_disk_content "$d_img_src" "$d_img_src_format" "$d_type" "$d_name"
	   if [ ! "$?" = "0" ]; then
               log_msg "Error copying disk content from $d_img_src to $d_name"
               exit 1
	   fi
       fi
   fi

unset frag d_type d_name d_dev d_mode d_size_var d_size d_create_var d_create 
unset d_img_src d_img_src_var d_img_src_type_var d_img_src_type 
unset d_fs_type_var d_fs_rtpe d_img_src_format_var d_img_src_format

done



# fetch the kernel and ramdisk  if you installation requires it.
# You do not need to do this, if the kernel and ramdisk are in place
# on the managed node.

if [ -n "$kernel_src" ] && [ -n "$kernel" ]; then
    $MKDIR -p `dirname "$kernel"`
    fetch_file "$kernel_src" "$kernel"
    if [ ! "$?" = "0" ]; then
	log_msg "Error getting kernel $kernel_src to $kernel" 
	exit 1
    fi
fi

if [ -n "$ramdisk_src" ] && [ -n "$ramdisk" ]; then
    $MKDIR -p `dirname "$ramdisk"`
    fetch_file "$ramdisk_src" "$ramdisk"
    if [ ! "$?" = "0" ]; then
	log_msg "Error getting ramdisk $ramdisk_src to $ramdisk" 
	exit 1
    fi
 fi


#
# kick off customizations for fixing either copied or installed image
#
# image templates are available in common area as well as image specific
# area.
# one can store specific files and scripts to instantiate templates
# and do additional customization via scripts
# 
# examples : hostname, ip address setup, add user etc
#
# 

# for each template directory specified (left to right), 
#    look for the directory under 
#          $image_store/$image_name/custom_scripts
#    if not found then look for it in $image_store/custom_scripts
#    for each script in the directory
#          execute script in ascending order of names within the directory.
#

log_msg "$0 completed."
