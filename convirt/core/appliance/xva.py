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

import pprint 
import xml.dom.minidom
from xml.dom.minidom import Node

import os, re, glob, shutil

from convirt.model.ManagedNode import ManagedNode
from convirt.core.utils.utils import PyConfig
from convirt.model.ImageStore import ImageStore, ImageUtils
import convirt.core.utils.constants

from convirt.core.utils.utils import mkdir2

import urllib, urlparse, sys

def search_ova(image_dir):
  ova_location = glob.glob(image_dir + '/ova.xml')

  if len(ova_location) <= 0:
    ova_location = glob.glob(image_dir + '/*/ova.xml')

  if len(ova_location) <= 0:
    ova_location = glob.glob(image_dir + '/*/*/ova.xml')

  if len(ova_location) <= 0:
    raise Exception("ova.xml not found under " + image_dir)

  ova_location = ova_location[0]
  #print "ova.xml found: ", ova_location

  full_appliance_dir = os.path.dirname(ova_location)
  print "Full appliance directory :", full_appliance_dir

  appliance_dir = full_appliance_dir[len(image_dir) + 1:]
  print "appliance directory :", appliance_dir

  return (ova_location, full_appliance_dir, appliance_dir)

def get_ova_info(ova_location):

  doc = xml.dom.minidom.parse(ova_location)

  for node in doc.getElementsByTagName("config"):
    cfg = dict(map(lambda x: (x, node.getAttribute(x)),
              ("mem_set", "vcpus")))
    # transform in to numeric value 
    if cfg.get("vcpus"):
      cfg["vcpus"] = int(cfg["vcpus"])

    # set in to mem
    if cfg.get("mem_set"):
      cfg["memory"]= int(cfg["mem_set"]) / (1024 *  1024)

  for node in doc.getElementsByTagName("hacks"):
    hacks = dict(map(lambda x: (x, node.getAttribute(x)),
              ("is_hvm", "kernel_boot_cmdline")))

  # <vbd device="xvda" function="root" mode="w" qos_value="" vdi="vdi_xvda"/>
  vbds = {}

  for node in doc.getElementsByTagName("vbd"):
    vbd = dict(map(lambda x: (x, node.getAttribute(x)),
              ("device", "function", "mode", "qos_value", "vdi")))
    #print type(vbds), type(vbd)
    vbds[vbd["device"]] = vbd

  #  <vdi name="vdi_xvda" size="2147483648" source="file://xvda" type="dir-gzipped-chunks" variety="system"/>
  vdis = {}

  for node in doc.getElementsByTagName("vdi"):
    vdi = dict(map(lambda x: (x, node.getAttribute(x)),
              ("name", "size", "source", "type", 'variety')))
    vdis[vdi['name']] =  vdi

  #pprint.pprint(cfg)
  #pprint.pprint(hacks)
  #pprint.pprint(vbds)
  #pprint.pprint(vdis)

  return (cfg, hacks, vbds, vdis)

def create_disks(local, full_appliance_dir, vbds, vdis,progress=None):
  disk_info = []
  for vbd_name in vbds.keys():
    vbd = vbds[vbd_name]
    vdi = vdis[vbd["vdi"]]
    type = vdi["type"]

    if type == "dir-gzipped-chunks":
      disk_dir = os.path.join(full_appliance_dir, vbd_name)

      # construct the disk info
      disk_entry = ("file:", vbd["device"],vbd["mode"])
      d=vbd["device"]
      disk_prov_entries = [ ("%s_disk_create" % d, "yes"),
                            ("%s_image_src" % d, disk_dir),
                            ("%s_image_src_type" % d, "disk_image"),
                            ("%s_image_src_format" % d, type) ]
      
      disk_info.append((disk_entry, disk_prov_entries))
    else:
      raise Exception("Unknonw type %s. Only dir-gzipped-chunks type is supported." % type)

    return disk_info

def import_appliance(auth,local, appliance_entry, image_store, image_group_id,\
                                image_name, platform, force, progress=None): 

  # TODO :
  # image_store.validate_image_name(image_name)
  appliance_url = appliance_entry["href"]

  image_dir = image_store._get_location(image_name)

  if not local.node_proxy.file_exists(image_dir):
    mkdir2(local, image_dir)

  # fetch the image
  filename = appliance_entry.get("filename")
  ###DIRTY FIX... need to check which transaction is going on
  import transaction
  transaction.commit()  
  downloaded_filename = ImageUtils.download_appliance(local,appliance_url,
                                                      image_dir, filename,
                                                      progress)

  #Make the image entry into the database after the appliance is downloaded.
  #so that database and image store filesystem will be in sync
  #for image_group in image_store.get_image_groups(auth).values():
#  if image_store.image_exists_by_name(image_name):
#    raise Exception("Image "+image_name+" already exists.")
  image = image_store.create_image(auth,image_group_id, image_name, platform) 

  # gunzip/unzip if required
  ImageUtils.open_package(local, downloaded_filename, image_dir, progress)

  # get ova / xva information from the package
  (ova_location, full_appliance_dir, appliance_dir) = search_ova(image_dir)
  (cfg, hacks, vbds, vdis) = get_ova_info(ova_location)

  # create disk from the chunks
  disk_info = create_disks(local, full_appliance_dir, vbds, vdis, progress)

  # get rid of the hacks
  appliance_entry["is_hvm"] = hacks["is_hvm"]
  cfg["extra"] = hacks["kernel_boot_cmdline"]

  vm_template = ImageUtils.get_vm_conf_template(local, appliance_entry,
                                                cfg, disk_info)
  image_conf  = ImageUtils.get_image_config(local, appliance_entry, disk_info,
                                            image_dir)

  ImageUtils.create_files(local, appliance_entry,
                          image_store,image_group_id, image,
                          vm_template, image_conf, force)
  return True

## Main entry point

if __name__ == '__main__':

  from optparse import OptionParser

  parser = OptionParser("usage: %prog [-f][-s IMAGE_STORE] -u APPLIANCE_URL -i IMAGE_NAME ")
  parser.add_option("-u", "--url", dest="url",
                    help="specify the appliance url", metavar="APPLIANCE_URL")

  parser.add_option("-i", "--image", dest="image_name",
                    help="specify the image name", metavar="IMAGE_NAME")

  parser.add_option("-f", "--force",action="store_true",
                    help="overwrite image.conf and vm_conf.template files if they exist."
                    )

  (options, args) = parser.parse_args()

  appliance_url = options.url
  image_name = options.image_name
  force = options.force


  # TODO : Allow for already downloaded appliance
  if appliance_url is None:
    parser.error("Specify the appliance/image download url")

  if image_name is None:
    parser.error("Specify the image name to be created")

  #print "image store" ,image_store
  #print "image name", image_name

  local = ManagedNode()
  image_store = ImageStore(local_node.config)
  

  feed_entry = {"href" : appliance_url}
  import_appliance(local, feed_entry, image_store, image_name, force)
