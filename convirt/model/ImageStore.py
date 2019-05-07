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

# Encapsulates some image store structure and convetions.
# 

import os, shutil, time, re
import urllib,urllib2, urlparse

from convirt.core.utils.utils import to_unicode,to_str
import convirt.core.utils.constants
from convirt.core.utils.constants import *
from convirt.core.utils.utils import  PyConfig, copyToRemote,getHexID,get_config_text
from convirt.core.utils.utils import read_python_conf, copyToRemote, mkdir2, get_path, md5_constructor
from convirt.model.VM import VM
import traceback
from convirt.model.DBHelper import DBHelper
from sqlalchemy import *
from sqlalchemy.types import *
from sqlalchemy import orm
from sqlalchemy.schema import Index
from convirt.model import DeclarativeBase,Entity,DBSession
from convirt.model.Authorization import AuthorizationService
import tg
constants = convirt.core.utils.constants
class Image(DeclarativeBase):
    VM_TEMPLATE = "vm_conf.template"
    SCRIPT_NAME  = "provision.sh"
    IMAGE_CONF = 'image.conf'
    IMAGE_DESC = 'description.htm'
    IMAGE_DESC_HTML = 'description.html'

    __tablename__ = 'images'

    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    vm_config = Column(Text)
    image_config = Column(Text)
    location=Column(Text)
    platform = Column(Unicode(50))
    is_template = Column(Boolean)
    base_location=Column(Unicode(255))
    version=Column(Float)
    prev_version_imgid=Column(Unicode(50))
    os_flavor=Column(Unicode(50))
    os_name=Column(Unicode(50))
    os_version=Column(Unicode(50))

    @classmethod
    def set_registry(cls, registry):
        cls.registry = registry

    def __init__(self, id, platform, name, location,is_template=False):
        self.id = id
        self.name = name
        self.location = location
        self.is_template = is_template
        self.base_location = os.path.basename(location)
        self.platform = platform

        print "Name ", name, " Platform ", platform
        # IMPORTANT :for testing... need to be removed
        #if platform != "xen":
        #    raise Exception("platform is " + platform)

    def __repr__(self):
        return to_str({"id":self.id,
                    "name":self.name,
                    "location":self.location,
                    "is_template":self.is_template,
                    "platform" : self.platform
                    })

    def get_name(self):
        return self.name

    def get_platform(self):
        return self.platform

    def set_name(self, new_name):
        self.name = new_name  

    def get_id(self):
        return self.id
        
    def get_location(self):
        return self.location
    
    def get_image_dir(self):
        return self.location

    def get_configs(self):
        template_file = self.get_vm_template()
        
        platform_object = self.registry.get_platform_object(self.platform)
        #vm_config = platform_object.create_vm_config(filename=template_file)
        vm_config = platform_object.create_vm_config(filename=template_file,config=self.vm_config)
        vm_config.set_filename(template_file)
        i_config_file = self.get_image_conf()

        #img_config = platform_object.create_image_config(filename=i_config_file)
        img_config = platform_object.create_image_config(filename=i_config_file,config=self.image_config)
        return vm_config,img_config

    def get_vm_template(self):
        return os.path.join(self.location, self.VM_TEMPLATE)

    def get_image_conf(self):
        return os.path.join(self.location, self.IMAGE_CONF)
        
    def get_provisioning_script(self):
        return os.path.join(self.location, self.SCRIPT_NAME)

    def get_provisioning_script_dir(self):
        return os.path.join(self.location)
        
    def get_image_desc(self):
        return  os.path.join(self.location, self.IMAGE_DESC)
        
    def get_image_desc_html(self):
        return  os.path.join(self.location, self.IMAGE_DESC_HTML)
                
    def get_args_filename(self,vm_name):
        return  self.base_location + "_" + vm_name +  ".args"

    def get_image_filename(self,vm_name):
        return  self.base_location + "_" + vm_name + "_" + "image.conf"

    def get_log_filename(self, vm_name):
        return self.base_location + "_" + vm_name + ".log"

    def is_hvm(self):
        v_config, i_config = self.get_configs()
        if v_config:
            return v_config.is_hvm()
        return False
    
    def set_next_version(self):
        import decimal
        self.version=self.version+decimal.Decimal('0.1')

    def get_latest_version(self):
        return self.version

    def get_vms(self):
        vms=DBSession.query(VM).filter(VM.image_id==self.id).all()
        return vms

    def get_older_version_vms(self):
        oldvms=DBSession.query(VM).filter(VM.image_id==self.id).\
                    filter(VM.template_version < self.version).all()

        return oldvms

Index('img_id',Image.id)

class ImageGroup(DeclarativeBase):

    __tablename__ = 'image_groups'

    id = Column(Unicode(255), primary_key=True)
    name = Column(Unicode(50), nullable=False)

    def __init__(self, id, name, images):
        self.id = id
        self.name = name
        self.images = images

    @orm.reconstructor
    def init_on_load(self):
        self.images = {}

    # check if the image with the same name exisits
    def _check_for_dup(self, name):
        for img in self.images.itervalues():
            if name == img.name:
                raise Exception("Image with the same name exists")

    def add_image(self, image):
        self._check_for_dup(image.name)
        self.images[image.id] = image

    def remove_image(self, image_id):
        del self.images[image_id]

    def get_images(self):
        return self.images
    
    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name  

    def get_id(self):
        return self.id

    def get_image(self, id):
        if id in self.images:
            return self.images[id]
        
    def get_image_by_name(self, name):
        for img in self.images.itervalues():
            if name == img.name:
                return img 
        return None


    def image_exists_by_name(self, name):
        try:
            self._check_for_dup(name)
            return False
        except: 
            return True
    
    def __repr__(self):
        return to_str({"id":self.id,
                    "name":self.name,
                    "image_ids":self.images.keys()
                    })
Index('imggrp_id',ImageGroup.id)

class ImageStore(DeclarativeBase):
    """A class that manages the list of provisioning images.
      NOTE: This class is intended for use by a client application
      managing multiple DomU images.
      """
    __tablename__='image_stores'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    location = Column(Unicode(255))

    STORE_CONF = "image_store.conf"

    DEFAULT_STORE_LOCATION = "/var/cache/convirt/image_store"
    COMMON_DIR = 'common'

    INVALID_CHARS = "(space,comma,dot,quotes,/,\|,<,>,!,&,%,.,^)"
    INVALID_CHARS_EXP = "( |/|,|<|>|\||\!|\&|\%|\.|\'|\"|\^|\\\\)"
    VM_INVALID_CHARS = "(space,comma,quotes,/,\|,<,>,!,&,%,.,^)"
    VM_INVALID_CHARS_EXP = "( |/|,|<|>|\||\!|\&|\%||\'|\"|\^|\\\\)"

    # generate a unique hash
    @classmethod
    def getId(cls, name):
        x = md5_constructor(name)
        x.update(to_str(time.time()))
        return x.hexdigest()

    # sanitize so that the return value can be used as directory
    # location
    @classmethod
    def sanitize_name(cls, name):
        return re.sub(cls.INVALID_CHARS_EXP,'_', name)

    # convention to have location under image store
    def _get_location(self, name):
        return os.path.join(self._store_location, self.sanitize_name(name))
    
    # template convention
    def is_template(self, name):
        return  name[0] == "_"

    def new_group(self, name):
        return ImageGroup(getHexID(name,[constants.IMAGE_GROUP]),
                          name,
                          {})

    # get a new image with a name
    def new_image(self, name, platform):
        return Image(getHexID(name,[constants.IMAGE]),
                     platform,
                     name,
                     self._get_location(name)
                     )
       
    def __init__(self, registry):
        #self._config = config
        self._registry = registry
        Image.set_registry(registry)
        ImageUtils.set_registry(registry)
        self.__initialize()

    @orm.reconstructor
    def init_on_load(self):        
        self.images = {}
        self.image_groups = {}

        self._default = None # default image for provisioning
        self._default_group = None # default image for provisioning
        self._excludes = []  # dirs like common to be excluded
        self._hashexcludes = []  # dirs like common to be excluded
        self._store_location = self.location

    def set_registry(self,registry):
        self._registry = registry
        Image.set_registry(registry)
        ImageUtils.set_registry(registry)

    def __init_images(self, images_info):
        self.images = {}
        imgs = {}
        if images_info:
            imgs = eval(images_info)

        for k,v in imgs.iteritems():
            if v.get("platform") is None:
                v["platform"] = "xen"
            self.images[k] = Image(v["id"],
                                   v["platform"],
                                   v["name"],
                                   v["location"],
                                   v["is_template"]
                                   )      

    
    def __init_groups(self, groups_info):
        self.image_groups = {}
        igs = {}
        if groups_info:
            igs = eval(groups_info)
        for k,v in igs.iteritems():
            images = {}
            for id in v["image_ids"]: images[id] = self.images[id] 
            self.image_groups[k] = ImageGroup(v["id"], v["name"], 
                                              images)
            if self.image_groups[k].get_name() == "Common":
                self._default_group = self.image_groups[k]

    # if the conf file is old, scan the files and generate the iamges
    def _init_from_dirs(self):
        # for old conf files.
        self.__read_store_conf()
        for file in os.listdir(self._store_location):
            if file not in self._excludes and file[0] != ".":
                full_file = os.path.join(self._store_location,file)
                if os.path.isdir(full_file):
                    try:
                        id = getHexID(file,[constants.IMAGE])
                        location = full_file
                        name = file
                        if len(name)>50:
                            name = name[0:50]

                        is_template = self.is_template(name)

                        img= Image(id, to_unicode("xen"), to_unicode(name), to_unicode(location),
                                               is_template)

                        img.version=constants.image_starting_version
                        img.prev_version_imgid=id
                        
                        # update the platform to correct value
                        vm_file = img.get_vm_template()
                        cfg = PyConfig(filename=vm_file) #cheating
                        if cfg.get("platform") is not None:
                            img.platform = to_unicode(cfg.get("platform"))
                        else:
                            cfg["platform"] = img.platform
                            cfg.write()

                        img.os_flavor=to_unicode(cfg['os_flavor'])
                        img.os_name=to_unicode(cfg['os_name'])
                        img.os_version=to_unicode(cfg['os_version'])

                        vm_config,image_config=img.get_configs()
                        img.vm_config=get_config_text(vm_config)
                        img.image_config=get_config_text(image_config)

                        self.images[id]=img
                    except Exception, e:
                        print "Exception: ", e
                    
        # create a initial groups and add all the images to it.
        common_grp_name = u"Common"
        xen_pv_grp_name = u"Xen Paravirtual"
        kvm_pv_grp_name = u"KVM" # we do not have any KVM pv yet
        custom_grp_name = u"Custom" # Custom images by users

        # make a copy for img group
        common_images = {}
        xen_pv_images = {}
        kvm_pv_images = {}
        custom_images = {}

        # populate images in to buckets 
        for id,img in self.images.iteritems() : 
            if img.is_hvm():
                common_images[id] = img
            elif img.platform == "xen":
                xen_pv_images[id] = img
            elif img.platform == "kvm":
                kvm_pv_images[id] = img
            else:
                custom_images[id] = img

    
        for g_name, g_images in ((common_grp_name, common_images),
                                 (xen_pv_grp_name, xen_pv_images),
                                 (kvm_pv_grp_name, kvm_pv_images),
                                 (custom_grp_name, custom_images)):
        
            if g_images: # if u have atleast one image in the group
                # create it.
                g = ImageGroup(getHexID(g_name,[constants.IMAGE_GROUP]),g_name,g_images)
                self.image_groups[g.id] = g

        auth=AuthorizationService()        
        entities=[]
        iss=DBHelper().filterby(Entity,[],[Entity.entity_id==self.id])[0]
        for grp in self.image_groups.itervalues():
            grpimages=grp.images
            grps=DBHelper().filterby(Entity,[],[Entity.name==grp.name])
            if len(grps)==0:
                grp_ent=auth.add_entity(grp.name,grp.id,to_unicode(constants.IMAGE_GROUP),iss)
                DBHelper().add(grp)
            else:
                grp_ent=grps[0]
                grp.images=grpimages
                #grp_ent.entity_id=grp.id
            entities.append(grp_ent)
            for img in grp.images.itervalues():
                imgs=DBHelper().filterby(Entity,[],[Entity.name==img.name])
                if len(imgs)==0:
                    DBHelper().add(img)
                    img_ent=auth.add_entity(img.name,img.id,to_unicode(constants.IMAGE),grp_ent)
                else:
                    img_ent=imgs[0]
                    #img_ent.entity_id=img.id
                entities.append(img_ent)
        return entities
#        self.save_images()
#        self.save_image_groups()

    def init_scan_dirs(self):
        import transaction
        try:
            auth=AuthorizationService()
            self.scan_dirs(auth, self.id)
        except Exception, e:
            traceback.print_exc()
            return

        transaction.commit()
        return

    def scan_dirs(self, auth, imagestore_id):
        # for new added conf files in any directory.
        self.__read_store_conf()
        dir = self._store_location

        new_imgs={}
        rej_imgs=[]
        img_names=self.get_image_names()
        for file in os.listdir(dir):
            if file not in self._excludes and file[0] != ".":
                full_file = os.path.join(dir,file)
                if file in img_names:
                    continue

                if os.path.isdir(full_file):
                    try:
                        id = getHexID(file,[constants.IMAGE])
                        location = full_file
                        name = file
                        if len(name)>50:
                            name = name[0:50]

                        is_template = self.is_template(name)

                        img= Image(id, to_unicode("xen"), to_unicode(name), \
                                    to_unicode(location), is_template)

                        img.version=constants.image_starting_version
                        img.prev_version_imgid=id

                        # update the platform to correct value
                        vm_file = img.get_vm_template()
                        cfg = PyConfig(filename=vm_file)
                        if cfg.get("platform") is not None:
                            img.platform = to_unicode(cfg.get("platform"))
                        else:
                            cfg["platform"] = img.platform
                            cfg.write()

                        img.os_flavor=to_unicode(cfg['os_flavor'])
                        img.os_name=to_unicode(cfg['os_name'])
                        img.os_version=to_unicode(cfg['os_version'])
                        img.allow_backup= True

                        vm_config,image_config=img.get_configs()
                        img.vm_config=get_config_text(vm_config)
                        img.image_config=get_config_text(image_config)

                        new_imgs[id]=img
                    except Exception, e:
                        traceback.print_exc()
                        rej_imgs.append(to_str(e))

        # create a initial groups and add all the images to it.
        common_grp_name = u"Common"
        xen_pv_grp_name = u"Xen Paravirtual"
        kvm_pv_grp_name = u"KVM" # we do not have any KVM pv yet
        custom_grp_name = u"Custom" # Custom images by users

        # make a copy for img group
        common_images = {}
        xen_pv_images = {}
        kvm_pv_images = {}
        custom_images = {}

        # populate images in to buckets
        for id,img in new_imgs.iteritems() :
            if img.is_hvm():
                common_images[id] = img
            elif img.platform == "xen":
                xen_pv_images[id] = img
            elif img.platform == "kvm":
                kvm_pv_images[id] = img
            else:
                custom_images[id] = img

        new_grps={}
        for g_name, g_images in ((common_grp_name, common_images),
                                 (xen_pv_grp_name, xen_pv_images),
                                 (kvm_pv_grp_name, kvm_pv_images),
                                 (custom_grp_name, custom_images)):

            if g_images: # if u have atleast one image in the group create it

                g = ImageGroup(getHexID(g_name,[constants.IMAGE_GROUP]),g_name,g_images)
                new_grps[g.id] = g

        entities=[]
        iss=DBHelper().filterby(Entity,[],[Entity.entity_id==imagestore_id])[0]
        for grp in new_grps.itervalues():
            grpimages=grp.images
            grps=DBHelper().filterby(Entity,[],[Entity.name==grp.name])
            if len(grps)==0:
                grp_ent=auth.add_entity(grp.name,grp.id,to_unicode(constants.IMAGE_GROUP),iss)
                DBHelper().add(grp)
            else:
                grp_ent=grps[0]
                grp.images=grpimages
            #entities.append(grp_ent)
            for img in grp.images.itervalues():
                imgs=DBHelper().filterby(Entity,[],[Entity.name==img.name])
                if len(imgs)==0:
                    DBHelper().add(img)
                    img_ent=auth.add_entity(img.name,img.id,to_unicode(constants.IMAGE),grp_ent)
                else:
                    img_ent=imgs[0]
                entities.append(img_ent)
        return (entities,rej_imgs)
    
    def __initialize(self):
        self.images = {}
        self.image_groups = {}

        self._default = None # default image for provisioning
        self._default_group = None # default image for provisioning
        self._excludes = []  # dirs like common to be excluded
        self._hashexcludes = []  # dirs like common to be excluded
        
        self._store_location = self.location


                    
    def __read_store_conf(self):
        conf_file = os.path.join(self._store_location, self.STORE_CONF)
        conf = read_python_conf(conf_file)
        if conf is not None:
            if conf.has_key("default"):
                self._default = conf["default"]
            if conf.has_key("excludes"):    
                self._excludes = conf["excludes"]
            if conf.has_key("hashexcludes"):    
                self._hashexcludes = conf["hashexcludes"]

    def _commit(self):
        self.save_image_groups()
        self.save_images()
    
    def re_initialize(self):
        self.__initialize()
        
    def get_vm_template(self, image_id):
        image = self.images[image_id]
        vm_template = image.get_vm_template()
        return vm_template 

    def get_provisioning_script(self, image_id):
        image = self.images[image_id]
        script = image.get_provisioning_script()
        return script 

    def get_provisioning_script_dir(self, image_name):
        image = self.images[image_id]
        script_dir = image.get_provisioning_script_dir()
        return script_dir 

    # Add given image to the group. if image already exists, then it will not be added.  
    def add_image_to_group(self, image_group, image):
        self.images[image.id] = image
        image_group.add_image(image)
        self._commit()

    # Remove image from the group.
    def remove_image_from_group(self, image_group, image):
        self.images[image.id] = image
        image_group.remove_image(image.id)
        self._commit()

    def get_default_image(self,auth):
        for img in self.get_images(auth).itervalues():
            if img == self._default:
                return img
        return None

    def get_default_image_group(self,auth):
        for grp in self.get_image_groups(auth).itervalues():
            if grp == self._default_group:
                return grp
        return None

    def get_image(self,auth, imageId):
        if imageId is None:
            return None
        ent=auth.get_entity(imageId)
        if ent is not None:
            return DBHelper().find_by_id(Image,imageId)
        return None

    def get_image_by_name(self, image_name):
        imgs=DBHelper().filterby(Image,[],[Image.name==image_name]) 
        if len(imgs)>0:
            return imgs[0]

    def get_images(self,auth):
        imgs={}
        grps=DBHelper().get_all(ImageGroup)
        for grp in grps:
            images=self.get_group_images(auth,grp.id)
            for img in images.itervalues():
                imgs[img.id]=img
        return imgs

    def get_image_names(self):
        imgs=[]
        images=DBHelper().get_all(Image)
        for image in images:
            imgs.append(image.name)
        return imgs
    
    def get_group_images(self,auth,groupId):
        if groupId is None:
            return {}
        ent=auth.get_entity(groupId)
        if ent is not None:
            child_ents=auth.get_entities(to_unicode(constants.IMAGE),parent=ent)
            ids = [child_ent.entity_id for child_ent in child_ents]
            images= DBHelper().filterby(Image,[],[Image.id.in_(ids)])
            result={}
            for image in images:
                result[image.id]=image
            return result
        return {}

    def get_image_groups(self,auth,storeId=None):        
        ent=auth.get_entity(storeId)        
        result = {}
        child_ents=auth.get_entities(to_unicode(constants.IMAGE_GROUP),parent=ent)
        ids = [child_ent.entity_id for child_ent in child_ents]
        img_grps=DBHelper().filterby(ImageGroup,[],[ImageGroup.id.in_(ids)])
        for image_group in img_grps:
            result[image_group.id]=image_group
        return result

    def get_image_group(self,auth, groupId):
        if groupId is None:
            return None
        ent=auth.get_entity(groupId)
        if ent is not None:
            return DBHelper().find_by_id(ImageGroup,groupId)
        return None
    
    def transfer_image(self,auth,imageId,source_groupId,dest_groupId):#imageId,source_groupId,dest_groupId
        ent=auth.get_entity(imageId)
        grp=auth.get_entity(dest_groupId)
        if not auth.has_privilege('TRANSFER_IMAGE',ent) or not auth.has_privilege('CREATE_IMAGE',grp):
            raise Exception(constants.NO_PRIVILEGE)
        auth.update_entity(ent, parent=grp)

    def clone_image(self, auth, image_group_id, imageId, new_image_name):
        ent=auth.get_entity(imageId)
        if ent is not None:
            if not auth.has_privilege('CREATE_LIKE',ent):
                raise Exception(constants.NO_PRIVILEGE)
            if re.sub(ImageStore.INVALID_CHARS_EXP,"", new_image_name) != new_image_name:
                raise Exception("Template name can not contain special chars %s" % ImageStore.INVALID_CHARS)
            if new_image_name == '':
                raise Exception("Template name can not blank")
            try:
                imgs=DBHelper().filterby(Image,[],[Image.name==new_image_name])
                if len(imgs)>0:
                    raise Exception("Image %s already exists." % new_image_name)

                image=DBHelper().find_by_id(Image,imageId)
                src_location = image.get_location()
                new_img = self.new_image(new_image_name, image.get_platform())
                dest_location = new_img.get_location()
                shutil.copytree(src_location, dest_location)

                str_vm_config=""
                vm_config,image_config=image.get_configs()
                for name, value in vm_config.options.iteritems():
                    if name=="image_name":
                        value=to_str(new_img.name)
                    str_vm_config+="%s = %s\n" % (name, repr(value))
                new_img.vm_config=str_vm_config
                new_img.image_config=get_config_text(image_config)

                new_img.os_name=image.os_name
                new_img.os_flavor=image.os_flavor
                new_img.os_version=image.os_version
                new_img.version=constants.image_starting_version
                new_img.prev_version_imgid=new_img.id

                auth.add_entity(new_img.name,new_img.id,to_unicode(constants.IMAGE),ent.parents[0])
                DBHelper().add(new_img)
            except Exception, e:
                raise e

            return new_img        
        
    def rename_image(self, auth, image_group_id, imageId, new_image_name):
        ent=auth.get_entity(imageId)
        if ent is not None:
            if not auth.has_privilege('RENAME_IMAGE',ent):
                raise Exception(constants.NO_PRIVILEGE)
            if re.sub(ImageStore.INVALID_CHARS_EXP,"", new_image_name) != new_image_name:
                raise Exception("Template name can not contain special chars %s" % ImageStore.INVALID_CHARS)
            if new_image_name == '':
                raise Exception("Template name can not blank")
            try:
                imgs=DBHelper().filterby(Image,[],[Image.name==new_image_name])
                if len(imgs)>0:
                    raise Exception("Image %s already exists." % new_image_name)
                image=DBHelper().find_by_id(Image,imageId)
                image.set_name(new_image_name)
                auth.update_entity(ent,name=new_image_name)
                DBHelper().add(image)
            except Exception, e:
                raise e
            
            return image

    def create_image(self, auth, groupId, new_image_name, platform):
        ent=auth.get_entity(groupId)
        if ent is not None:
            if not auth.has_privilege('CREATE_IMAGE',ent):
                raise Exception(constants.NO_PRIVILEGE)

            try:
                imgs=DBHelper().filterby(Image,[],[Image.name==new_image_name])
                if len(imgs)>0:
                    raise Exception("Image %s already exists." % new_image_name)

                image = self.new_image(new_image_name, platform)
#                src_location = image.get_location()
#                if os.path.exists(src_location):
#                    raise Exception("Image location directory with the same name exists")
                    
#                str_vm_config=""
#                str_image_config=""
#                vm_config,image_config=image.get_configs()
#                for name, value in vm_config.options.iteritems():
#                    str_vm_config+="%s = %s\n" % (name, repr(value))
#                for name, value in image_config.options.iteritems():
#                    str_image_config+="%s = %s\n" % (name, repr(value))
#                image.vm_config=str_vm_config
#                image.image_config=str_image_config
                auth.add_entity(image.name,image.id,to_unicode(constants.IMAGE),ent)
                DBHelper().add(image)

            except Exception, e:
                traceback.print_exc()
                raise e            
        
            return image

    def delete_image(self,auth, image_group_id, imageId):        
        ent=auth.get_entity(imageId)
        if ent is not None:
            if not auth.has_privilege('REMOVE_IMAGE',ent):
                raise Exception(constants.NO_PRIVILEGE)
            vms=DBHelper().filterby(VM,[],[VM.image_id==imageId])
            if len(vms)>0:
                raise Exception("Can not delete image, "+ent.name+". \
                    VMs provisioned from this image exists.")
            image=DBHelper().find_by_id(Image,imageId)
            img_location = image.get_location()
            if os.path.exists(img_location):
                shutil.rmtree(img_location)
            auth.remove_entity(ent)
            DBHelper().delete_all(Image,[],[Image.prev_version_imgid==imageId])
        
    def image_exists_by_name(self,name):
        imgs=DBHelper().filterby(Image,[],[Image.name==name])
        if len(imgs)>0:
            return True
        return False
    
    def save_image_desc(self,auth,mgd_node,imageId,content):
        ent=auth.get_entity(imageId)
        if not auth.has_privilege('EDIT_IMAGE_DESCRIPTION',ent):
            raise Exception(constants.NO_PRIVILEGE)
        image=DBHelper().find_by_id(Image,imageId)
        filename=image.get_image_desc_html()
        file = mgd_node.node_proxy.open(filename, "w")
        file.write(content)
        file.close()

    def save_image_script(self,auth,mgd_node,imageId, content):
        ent=auth.get_entity(imageId)
        if not auth.has_privilege('EDIT_IMAGE_SCRIPT',ent):
            raise Exception(constants.NO_PRIVILEGE)
        image=DBHelper().find_by_id(Image,imageId)
        filename=image.get_provisioning_script()
        file = mgd_node.node_proxy.open(filename, "w")
        file.write(content)
        file.close()

  
    # not expected to be used widely
    # as most of the access would be via groups
    def list(self):
        return self.images

    def get_remote_location(self, managed_node):
        store_location = managed_node.config.get(prop_image_store)
        if store_location is None or store_location is '':
            store_location = ImageStore.DEFAULT_STORE_LOCATION
        return store_location


    def get_store_location(self):
        return self._store_location
            
    def get_common_dir(self):
        return os.path.join(self._store_location, self.COMMON_DIR)

    def add_group(self,auth, group,storeId):        
        ent=auth.get_entity(storeId)        
        if not auth.has_privilege('ADD_IMAGE_GROUP',ent):
            raise Exception(constants.NO_PRIVILEGE)
        try:
            grps=DBHelper().filterby(ImageGroup,[],[ImageGroup.name==group.name])
            if len(grps)>0:
                raise Exception("ImageGroup %s already exists." % group.name)
            auth.add_entity(group.name,group.id,to_unicode(constants.IMAGE_GROUP),ent)
            DBHelper().add(group)
        except Exception, e:
            raise e

    def delete_group(self, auth,groupId):
        ent=auth.get_entity(groupId)
        if ent is not None:
            if not auth.has_privilege('REMOVE_IMAGE_GROUP',ent):
                raise Exception(constants.NO_PRIVILEGE)

            group=DBHelper().find_by_id(ImageGroup,groupId)
            child_ents=auth.get_entities(to_unicode(constants.IMAGE),parent=ent)
            ids = [child_ent.entity_id for child_ent in child_ents]
            for child_ent in child_ents:
                auth.remove_entity(child_ent)
            auth.remove_entity(ent)
            DBHelper().delete_all(Image,[],[Image.id.in_(ids)])
            DBHelper().delete(group)

    def rename_image_group(self,auth, groupId, new_image_group_name):
        ent=auth.get_entity(groupId)
        if ent is not None:
            if not auth.has_privilege('RENAME_IMAGE_GROUP',ent):
                raise Exception(constants.NO_PRIVILEGE)
            try:
                grps=DBHelper().filterby(ImageGroup,[],[ImageGroup.name==new_image_group_name])
                if len(grps)>0:
                    raise Exception("ImageGroup %s already exists." % new_image_group_name)
                group=DBHelper().find_by_id(ImageGroup,groupId)
                auth.update_entity(ent,name=new_image_group_name)
                group.set_name(new_image_group_name)
                DBHelper().add(group)
                return group
            except Exception, e:
                raise e


    # Prepare environment for executing script on given managed node
    def prepare_env(self, managed_node, image, domconfig, image_conf):
        """ prepare execution environment on the remote node"""

        # prepare directory names
        remote_image_store = managed_node.config.get(prop_image_store)
        # if not specified, assume similar to client node
        if remote_image_store is None:
            remote_image_store = self.DEFAULT_STORE_LOCATION

        scripts_dest = os.path.join(remote_image_store , image.base_location)
        common_dest  = os.path.join(remote_image_store , self.COMMON_DIR)

        local_image_store = self.get_store_location()
        
        scripts_src_dir = image.get_provisioning_script_dir()
        common_src  = self.get_common_dir()

        copyToRemote(common_src, managed_node,remote_image_store, hashexcludes=self._hashexcludes)
        copyToRemote(scripts_src_dir, managed_node, remote_image_store, hashexcludes=self._hashexcludes)
        
        # prepare the log area where the instantiated image.conf and
        # args file would be placed, along with the log dir.

        log_dir = managed_node.config.get(prop_log_dir)
        if log_dir is None or log_dir == '':
            log_dir = DEFAULT_LOG_DIR

        log_location = os.path.join(log_dir, 'image_store', image.base_location)
        mkdir2(managed_node, log_location)
        
        img_conf_filename = None
        name = domconfig["name"]
        # write the config on the remote node.
        if image_conf is not None:
            img_conf_base = image.get_image_filename(name)
            img_conf_filename = os.path.join(log_location,img_conf_base)
            # adjust the pyconfig with correct filename and managed_node
            image_conf.set_managed_node(managed_node)
            image_conf.save(img_conf_filename)
        

        return (remote_image_store,
                scripts_dest,
                img_conf_filename,
                log_location)

    def execute_provisioning_script(self,auth,
                                    managed_node,
                                    image_id,
                                    dom_config,
                                    image_conf):

        # do platform check
        image = self.get_image(auth,image_id)
        image_platform = image.get_platform()
        node_platform = managed_node.get_platform()
        if image_platform != node_platform and (not image.is_hvm()):
            raise Exception("Image platform (%s) and Server Platform (%s) mismatch." % (image_platform, node_platform))


        name = dom_config["name"]
        #image = self.images[image_id]
        # prepare the environment to execute script
        (image_store_location,
         script_location,
         img_conf_filename,
         log_location) = self.prepare_env(managed_node,
                                          image,
                                          dom_config,
                                          image_conf)

        # get the script name
        script_name = image.SCRIPT_NAME

        # prepare script args
        script = os.path.join(script_location, script_name)
        script_args_filename = os.path.join(log_location,
                                            image.get_args_filename(name))
        
        #for now empty
        args = managed_node.node_proxy.open(script_args_filename, "w")
        args.close()

        # update the domconfig to have the reference to the image file
        # kind a kludge: ok for now.
        dom_config["image_conf"] = img_conf_filename
        dom_config.write()

        log_file_base = image.get_log_filename(name)
        log_filename = os.path.join(log_location,log_file_base)
        script_args=" -x " + dom_config.filename + \
                    " -p " + script_args_filename + \
                    " -s " + image_store_location + \
                    " -i " + image.base_location + \
                    " -l " + log_filename + \
                    " -c " + img_conf_filename
        
        cmd = script +  script_args

        provision_timeout=self.get_provision_timeout(dom_config,image_conf)
#        print "\n\nprovision_timeout===",provision_timeout
        # execute the script
        (out, exit_code) = managed_node.node_proxy.exec_cmd(cmd, timeout=provision_timeout)

        #print "#### Done provisioning ", out, exit_code

        #if exit_code != 0:
        #    raise OSError("Provisioning script failed.\n" +  out)

        #managed_node.node_proxy.remove(script_args_filename)
        #managed_node.node_proxy.remove(image_filename)
        #managed_node.node_proxy.remove(log_filename)
        return (out, exit_code, log_filename)

    def get_provision_timeout(self,dom_config,image_conf):
        provision_timeout=60
        try:
            ref_provision_timeout=0

            for disk in dom_config["disk"]:
                disk_val=disk.split(",")
                disk_image_src_var=disk_val[1]+"_image_src"
                disk_image_src_type_var=disk_val[1]+"_image_src_type"

                if image_conf[disk_image_src_var] is not None and image_conf[disk_image_src_type_var] is not None:
                    try:
                        ref_provision_timeout=int(tg.config.get("larger_timeout"))
                    except Exception, e:
                        print "Exception: ", e
                    break

            if "provision_timeout" in dom_config.keys() :
                try:
                    provision_timeout=int(dom_config["provision_timeout"])
                except Exception, e:
                    print "Exception: ", e

            if provision_timeout<ref_provision_timeout:
                provision_timeout=ref_provision_timeout

        except Exception, e:
            traceback.print_exc()

        return provision_timeout


Index('imgstr_id',ImageStore.id)
# helper function to find the appliance related templates
# this is to handle the descripency of tar ball vs rpm.
# there seems to be not an easy way to find
import sys
def get_template_location():
    (path, tfile) = get_path('appliance', ['src/convirt/core',])
    if path:
        return tfile
    else:
        msg=  "ERROR: Couldn't find appliance_template. This is mostly installation problem."
        print msg
        raise Exception(msg)



# class for handling image imports
# Some utility functions
import string
class ImageUtils:

    compressed_ext = [".zip", ".gz"]

    # given a file system create an image
    APPLIANCE_TEMPLATE_LOCATION = get_template_location()

    @classmethod
    def set_registry(cls, registry):
        cls.registry = registry
    
    @classmethod
    def download_appliance(cls, local, appliance_url, image_dir, filename=None,
                           progress =  None):
        if appliance_url[0] == '/' : # fully specified path
            appliance_url = "file://" + appliance_url

        if appliance_url.find("file://") == 0:
            file_cp = True
            msg = "Copying"
        else:
            file_cp = False
            msg = "Downloading"

        fd = None
        # Tweaks to get around absence of filename and size
        try:
            opener = urllib2.build_opener()
            req = urllib2.Request(appliance_url)
            req.add_header("User-Agent", fox_header)
            fd = opener.open(req)
            url = fd.geturl()
            path = urlparse.urlparse(urllib.url2pathname(url))[2]
            if not filename:
                filename = path.split('/')[-1]

            clen = fd.info().get("Content-Length")
            if clen is not None:
                content_len = int(clen)
            else:
                content_len = -1


            print url, filename, content_len
            ex = None
            download_file = os.path.join(image_dir, filename)
            if not local.node_proxy.file_exists(download_file):
                if file_cp:
                    try:
                        try:
                            src = path
                            dest = download_file
                            if progress:
                                progress.update(progress.START_PULSE,
                                                "Copying " + src +
                                                " to \n" + dest )  
                            if src.find("/dev/") == 0 or \
                                    dest.find("/dev/") == 0:
                                
                                (out, code) = local.node_proxy.exec_cmd("dd if=" + \
                                                                      src + \
                                                                      " of=" + \
                                                                       dest,timeout=get_template_timeout())
                            else:

                                (out, code) = local.node_proxy.exec_cmd("cp -a " + \
                                                                      src + \
                                                                      " " + \
                                                                      dest,timeout=get_template_timeout())
                            if code != 0:
                                raise Exception(out)

                            if progress and not progress.continue_op():
                                raise Exception("Canceled by user.")

                        except Exception, ex:
                            traceback.print_exc()
                            if progress:
                                progress.update(progress.CANCELED,to_str(ex))
                            raise
                    finally:
                        if progress and not ex:
                            progress.update(progress.STOP_PULSE, "Copying done")
                        if progress and not progress.continue_op():
                            local.node_proxy.remove(download_file)
                        
                else: # url download
                    df = None
                    try:
                        df = open(download_file,"wb")
                        chunk_size = 1024 * 64
                        chunks = content_len / chunk_size + 1
                        x = fd.read(chunk_size)
                        c = 1
                        p = 1.0 / chunks
                        if progress:
                            progress.update(progress.SET_FRACTION,
                                            msg,(p * c))
                        while  x is not None and x != "":
                            df.write(x)
                            #print "wrote ", c, chunks, p * c
                            if progress:
                                progress.update(progress.SET_FRACTION, None,(p * c))
                                if not progress.continue_op():
                                    raise Exception("Canceled by user.") 

                            c = c + 1
                            x = fd.read(chunk_size)
                    finally:
                        if df:
                            df.close()
                        if progress and not progress.continue_op():
                            local.node_proxy.remove(download_file)
        finally:
            if fd:
                fd.close()

        return download_file


    @classmethod
    def get_file_ext(cls, filename):
        # return filename and ext
        file = filename
        dot_index = filename.rfind(".")
        ext = ""
        if dot_index > -1:
            ext = filename[dot_index:]
            file = filename[:dot_index]

        return (file, ext)



    @classmethod
    def open_package(cls, local, downloaded_filename, image_dir, progress=None):
        uzip = None
        utar = None

        (f, e) = ImageUtils.get_file_ext(downloaded_filename)
        if e in cls.compressed_ext:
            if e == ".gz":
                uzip = "gunzip -f"
            elif e == ".zip":
                uzip = "unzip -o -d " + image_dir

        if uzip:
            if progress:
                progress.update(progress.START_PULSE, "Unzipping " + downloaded_filename)
            msg = None
            ex = None
            try:
                try:
                    (output, code) = local.node_proxy.exec_cmd(uzip + " " + \
                                            downloaded_filename,timeout=get_template_timeout())
                    if code != 0 :
                        msg = "Error unzipping " + \
                              downloaded_filename + ":" + \
                              output
                        print msg
                        raise Exception(msg)

                    if e == ".zip":
                        local.node_proxy.remove(downloaded_filename)

                    if progress and not progress.continue_op():
                        raise Exception("Canceled by user.")
                    
                except Exception, ex:
                    if progress:
                        progress.update(progress.CANCELED,to_str(ex))
                    raise
            finally:
                if progress and not ex:
                    progress.update(progress.STOP_PULSE, "Unzipping done")
            
        # untar if required
        if downloaded_filename.find(".tar") > -1:
            ex = None
            untar = "tar xvf "
            msg = None

            try:
                try:
                    tar_file = downloaded_filename[0:downloaded_filename.find(".tar") + 4]
                    tar_loc = os.path.dirname(tar_file)
                    if progress:
                        progress.update(progress.START_PULSE,
                                        "Opening archive " + tar_file)
                    (output, code) = local.node_proxy.exec_cmd(untar + " " +
                                                               tar_file +
                                                               " -C " +
                                                               tar_loc,timeout=get_template_timeout())
                    if code != 0:
                        print "Error untaring ", tar_file
                        raise Exception("Error untaring " +  tar_file + " " +
                                        output)
                
                    if progress and not progress.continue_op():
                        raise Exception("Canceled by user.")
                
                except Exception, ex:
                    if progress:
                        progress.update(progress.CANCELED,to_str(ex))
                    raise
                
            finally:
                if progress and not ex:
                    progress.update(progress.STOP_PULSE,"Opening archive done.")


    @classmethod
    def get_vm_conf_template(cls, node, appliance_entry, cfg,disk_info):
        appliance_base = cls.APPLIANCE_TEMPLATE_LOCATION
        platform = cls.get_platform(appliance_entry)
        p = cls.registry.get_platform_object(platform)
        vm_template_file = p.select_vm_template(appliance_base,
                                                platform,
                                                appliance_entry,
                                                cfg)
        vm_template = p.create_vm_config(filename=vm_template_file)
        vm_template.dump()
        value_map = {"MEMORY" : 256,
                     "VCPUS" : 1,
                     "RAMDISK" : '',
                     "EXTRA" : '',
                     "KERNEL" : ''
                     }

        default_cfg = {}
        default_cfg["memory"] = 256
        default_cfg["vcpus"] = 1


        if cfg is not None:
            value_map["MEMORY"] = cfg.get("memory") or default_cfg["memory"]
            value_map["VCPUS"] = cfg.get("vcpus") or default_cfg["vcpus"]
            value_map["RAMDISK"] = ""
            if cfg.get("extra") :
                value_map["EXTRA"] = cfg.get("extra")
            else:
                value_map["EXTRA"] = ""

                
        if appliance_entry.get("is_hvm") and \
               to_str(appliance_entry["is_hvm"]).lower() == "true" :
            pass
            ### Taken care by the hvm template now.
            ### Still issue of computed kernel is tricky to fix.
##             value_map["BOOT_LOADER"]=""
                                
##             vm_template["vnc"] = 1
##             vm_template["sdl"] = 0
##             vm_template["builder"] = "hvm"
##             # special handing for these :Kludge
##             vm_template.lines.append('device_model="/usr/" + arch_libdir + "/xen/bin/qemu-dm"\n')
##             del vm_template["kernel"]
##             vm_template.lines.append('kernel="/usr/" + arch_libdir + "/xen/boot/hvmloader"')
##             # make it a customizable option
##             computed_options = vm_template.get_computed_options()
##             computed_options.append("kernel")
##             computed_options.append("device_model")
##             vm_template.set_computed_options(computed_options)
        else:
            value_map["BOOT_LOADER"]="/usr/bin/pygrub"
            value_map["KERNEL"] = ""

        disks_directive = []
        # now lets generate the disk entries
        for di in disk_info:
            de, dpes = di
            (proto, device, mode) = de

            disk_entry = proto + "$VM_DISKS_DIR" + "/$VM_NAME." + device+ \
                         ".disk.xm"
            disk_entry += "," + device+ ","  + mode
            
            disks_directive.append(disk_entry)

        vm_template["disk"] = disks_directive
        if appliance_entry.get("provider_id"):
            vm_template["provider_id"] = appliance_entry.get("provider_id")

        vm_template.instantiate_config(value_map)
        
        # Add the defaults if not already set
        for k in default_cfg:
            if not vm_template.has_key(k):
                if cfg and cfg.get(k):
                    vm_template[k] = cfg[k]
                else:
                    vm_template[k] = default_cfg[k]
                
        return vm_template


    @classmethod
    def get_platform(cls, appliance_entry):
        platform = appliance_entry.get("platform")
        if platform:
            platform =  platform.lower()
        return platform

    @classmethod
    def get_image_config(cls, node, appliance_entry, disk_info, image_dir):
        appliance_base = cls.APPLIANCE_TEMPLATE_LOCATION
        platform = cls.get_platform(appliance_entry)
        p = cls.registry.get_platform_object(platform)
        image_conf_template_file = p.select_image_conf_template(appliance_base,
                                                                platform,
                                                                appliance_entry)
        image_conf_template =p.create_image_config(filename=image_conf_template_file)
                                 
        disks = []
        ndx = 0
        for di in disk_info:
            de, dpes = di
            (proto,device, mode) = de

            for dpe in dpes:
                dpe_name, dpe_val = dpe
                image_conf_template[dpe_name] = dpe_val

            # adjust the dev_image_src in the template form
            src = image_conf_template.get(device + "_image_src")
            if src:
                pos = src.find(image_dir)
                if pos == 0 :
                    src = '$IMAGE_STORE/$IMAGE_LOCATION/' + \
                          src[(len(image_dir) + 1):]
                    image_conf_template[device + "_image_src"] = src

        return image_conf_template

    @classmethod
    def create_files(cls, local, appliance_entry, image_store, image_group_id,
                     image, vm_template, image_conf, force):
        vm_conf_file =image.get_vm_template()
        image_conf_file =image.get_image_conf()
        prov_script = image.get_provisioning_script()
        desc_file = image.get_image_desc_html()
        
        image.vm_config=get_config_text(vm_template)
        image.image_config=get_config_text(image_conf)
        image.version=constants.image_starting_version
        image.prev_version_imgid=image.id
        image.os_flavor=vm_template.get('os_flavor')
        image.os_name=vm_template.get('os_name')
        image.os_version=vm_template.get('os_version')
        DBHelper().add(image)
        
        if force or not local.node_proxy.file_exists(vm_conf_file):
            vm_template.save(vm_conf_file)
            print "Created ", vm_conf_file
        if force or  not local.node_proxy.file_exists(image_conf_file):  
            image_conf.save(image_conf_file)
            print "Created ", image_conf_file
        if force or  not local.node_proxy.file_exists(prov_script):
            platform = cls.get_platform(appliance_entry)
            p = cls.registry.get_platform_object(platform)
            a_base = cls.APPLIANCE_TEMPLATE_LOCATION
            src_script = p.select_provisioning_script(a_base,
                                                      platform,
                                                      appliance_entry)
            shutil.copy(src_script, prov_script)
            print "Created ", prov_script
        if force or  not local.node_proxy.file_exists(desc_file):
            cls.create_description(local, image_store, image,
                                   appliance_entry)

    @classmethod
    def create_description(cls, local,
                           image_store,image, appliance_entry,
                           desc_meta_template=None,html_desc_meta_template=None):
        # basically read the template, instantiate it and write it
        # as desc file.
        platform = cls.get_platform(appliance_entry)
        p = cls.registry.get_platform_object(platform)
        a_base = cls.APPLIANCE_TEMPLATE_LOCATION
        if not desc_meta_template :
            desc_meta_template = p.select_desc_template(a_base,
                                                        platform,
                                                        appliance_entry)
        
        if not html_desc_meta_template :
            html_desc_meta_template = p.select_html_desc_template(a_base,
                                                        platform,
                                                        appliance_entry)

        content = None
        try:
            f = open(desc_meta_template, "r")
            content = f.read()
        finally:
            if f: f.close()

        html_content = None
        try:
            f = open(html_desc_meta_template, "r")
            html_content = f.read()
        finally:
            if f: f.close()

        if not content : # should always find the template
            return
        
        val_map = {}
        for key, ae_key in  (("NAME", "title"),
                             ("URL", "link"),
                             ("PROVIDER", "provider"),
                             ("PROVIDER_URL", "provider_url"),
                             ("PROVIDER_LOGO_URL", "provider_logo_url"),
                             ("DESCRIPTION","description")):
            v = appliance_entry.get(ae_key)
            if v :
                #v = str(v)
                val_map[key] = v

        val_map["IMAGE_NAME"] = image.base_location

        # add extra requirements
        e_req = ""
        if appliance_entry.get('is_hvm') and \
           to_str(appliance_entry.get('is_hvm')).lower() == "true":
            e_req = e_req + ", " + "HVM / VT Enabled h/w"

        if appliance_entry.get("PAE") :  
            if to_str(appliance_entry.get("PAE")).lower()=="true" :
                e_req = e_req + ", " + "PAE"
            else:
                e_req = e_req +"," + "NON-PAE"
                
        if appliance_entry.get("arch"):
            e_req = e_req + ", " + appliance_entry.get("arch")

        val_map["EXTRA_REQUIREMENTS"] = e_req

        # We are putting some template specific stuff.
        provider_href = ""
        provider_logo_href = ""
        provider_str = ""

        if val_map.get("PROVIDER_URL"):
            provider_href = '<a href="$PROVIDER_URL">$PROVIDER</a>'
        else:
            provider_href = "$PROVIDER"
            
        if val_map.get("PROVIDER_LOGO_URL"):
            provider_logo_href = '<img src="$PROVIDER_LOGO_URL"/>'
            
        provider_str = provider_href + provider_logo_href
        if provider_str == "":
            provider_str = "Unknown (Manually Imported)"

        provider_str = string.Template(provider_str).safe_substitute(val_map)
        val_map["PROVIDER_STR"] = provider_str

        appliance_contact = ""
        
        if val_map.get("URL"):
            appliance_contact = 'Visit <a href="$URL">$NAME</a> for more information on the appliance. <br/>'
        appliance_contact = string.Template(appliance_contact).safe_substitute(val_map)
        
        val_map["APPLIANCE_CONTACT"] = appliance_contact
        template_str = string.Template(content)
        new_content = template_str.safe_substitute(val_map)
        desc_file = image.get_image_desc()

        try:
            fout = open(desc_file, "w")
            fout.write(new_content)
        finally:
            if fout:
                fout.close()

        template_str = string.Template(html_content)
        new_content = template_str.safe_substitute(val_map)
        html_desc_file = image.get_image_desc_html()
        try:
            fout = open(html_desc_file, "w")
            fout.write(new_content)
        finally:
            if fout:
                fout.close()

    @classmethod
    def import_fs(cls, auth, local,
                  appliance_entry,
                  image_store,
                  image_group_id, 
                  image_name, platform,
                  force, progress = None):

            appliance_url = appliance_entry["href"]

            image_dir = image_store._get_location(image_name) 

            if not local.node_proxy.file_exists(image_dir):
                mkdir2(local, image_dir)

            # fetch the image
            filename = appliance_entry.get("filename")
            ###DIRTY FIX... need to check which transaction is going on
            import transaction
            transaction.commit()
            downloaded_filename = ImageUtils.download_appliance(local,
                                                                appliance_url,
                                                                image_dir,
                                                                filename,
                                                                progress)

            #Make the image entry into the database after the appliance is downloaded.
            #so that database and image store filesystem will be in sync
            #for image_group in image_store.get_image_groups(auth).values():
#            if image_store.image_exists_by_name(image_name):
#                raise Exception("Image "+image_name+" already exists.")
            image = image_store.create_image(auth,image_group_id, image_name, platform)  

            # TBD : need to formalize this in to package handlers.
            if appliance_entry["type"] =="FILE_SYSTEM":
                disk_info = []
                di = get_disk_info("hda", downloaded_filename, "w")
                disk_info.append(di)
            elif appliance_entry["type"] == "JB_ARCHIVE":
                # gunzip/unzip the archive
                ImageUtils.open_package(local, downloaded_filename, image_dir,
                                        progress)
                
                disk_location = search_disks(image_dir)
                # clean up vmdk and other files.
                adjust_jb_image(local, disk_location, progress)
                disk_info = get_jb_disk_info(disk_location)

            vm_template = ImageUtils.get_vm_conf_template(local,
                                                          appliance_entry,
                                                          None, disk_info)
            
            image_conf  = ImageUtils.get_image_config(local, appliance_entry,
                                                    disk_info,
                                                    image_dir)

            ImageUtils.create_files(local, appliance_entry,
                                    image_store, image_group_id, image,
                                    vm_template, image_conf, force)

            return True

import glob
def search_disks(image_dir):
  disk_location = glob.glob(image_dir + '/disks')

  if len(disk_location) <= 0:
    disk_location = glob.glob(image_dir + '/*/disks')

  if len(disk_location) <= 0:
    disk_location = glob.glob(image_dir + '/*/*/disks')

  if len(disk_location) <= 0:
    raise Exception("disk directory not found under " + image_dir)

  disk_location = disk_location[0]

  return disk_location


# clean up vmdk files and compress the root hdd
def adjust_jb_image(local, disk_location, progress = None):
    for file in ("root.hdd", "root/root.hdd", "var.hdd", "swap.hdd"):
        root_fs = os.path.join(disk_location, file)
        if os.path.exists(root_fs):
            ex =None
            try:
                try:
                    # compress it
                    if progress:
                        progress.update(progress.START_PULSE,
                                        "Compressing " + root_fs)
                    (output, code) = local.node_proxy.exec_cmd("gzip " + root_fs, timeout=get_template_timeout())
                    if code !=0 :
                        raise Exception("Could not gzip " + root_fs + ":" +  output)
                    if progress and not progress.continue_op():
                        raise Exception("Canceled by user.")
                
                except Exception, ex:
                    if progress:
                        progress.update(progress.CANCELED,to_str(ex))
                    raise
                
            finally:
                if progress and not ex:
                    progress.update(progress.STOP_PULSE,"Compressing %s done." % root_fs)

        
    # the .hdd file that is shipped is not suitable for Xen.
    # the data.hdd.gz is what we are looking for.
    # remove all other files
    data_disk = os.path.join(disk_location, "data")
    if os.path.exists(data_disk):
        for exp in ("/*.vmdk", "/*.vhd", "/*.hdd"):
            files  = glob.glob(data_disk + exp)   
            for f in files:
                local.node_proxy.remove(f)

# return disk info from the unpacked JumpBox archive
def get_jb_disk_info(disk_location):
    disk_info = []

    for file in ("root.hdd", "root.hdd.gz",
                 "root/root.hdd", "root/root.hdd.gz"):
        root_fs = os.path.join(disk_location, file)
        if os.path.exists(root_fs):
            di = get_disk_info("hda", root_fs, "w")
            disk_info.append(di)
            break

    for file in ("swap.hdd", "swap.hdd.gz"):
        swap_fs = os.path.join(disk_location, file)
        if os.path.exists(swap_fs):
            di = get_disk_info("hdb", swap_fs, "w")
            disk_info.append(di)
            break

    var_found = False
    for file in ("var.hdd", "var.hdd.gz"):
        var_fs = os.path.join(disk_location, file)
        if os.path.exists(var_fs):
            di = get_disk_info("hdd", var_fs, "w") # hdc reserved for cdrom
            disk_info.append(di)
            var_found = True
            break
        
    if not var_found:
        # for new version of jumpbox. (get exact version here)
        data_fs = os.path.join(disk_location, "data/data.xen.tgz")
        if os.path.exists(data_fs):
            di = get_disk_info("hdd", data_fs, "w") # hdc reserved for cdrom
            disk_info.append(di)
        else:
            # generate de for hdd

            # generate dpe so as to satify the following
            
            # need to create a data dir with 10GB sparse file
            # ext3 file system
            # label as 'storage'
            pass

    if len(disk_info) <=0 :
        raise Exception("No disks found from JumpBox Archive.")

    return disk_info

    
# utility function to generate disk info, i.e. disk entry for
# vm config as well as for image conf.
def get_disk_info(device_name, filename, mode, proto="file:"):
    (uncompressed_file, ext) = ImageUtils.get_file_ext(filename)

    de = (proto,device_name, mode)
    d = device_name
    dpes = [ ("%s_disk_create" % d, "yes"),
             ("%s_image_src" % d, filename),
             ("%s_image_src_type" % d, "disk_image")]

    if ext in (".gz", ):
        dpes.append(("%s_image_src_format" % d, "gzip"))
    elif ext in (".tgz", ):
        dpes.append(("%s_image_src_format" % d, "tar_gzip"))
    elif ext in (".bz2", ):
        dpes.append(("%s_image_src_format" % d, "bzip"))
    elif ext in (".tbz2", ):
        dpes.append(("%s_image_src_format" % d, "tar_bzip"))

    return (de, dpes)


def get_template_timeout(default=None):
    if default is None:
        default = 10
    val = default
    try:
        val = int(tg.config.get("template_timeout"))
    except Exception, e:
        print "Exception: ", e
    return val

