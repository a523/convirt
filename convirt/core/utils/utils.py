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

import ConfigParser, subprocess, platform
import sys, os, os.path, socket, types, tempfile, re, glob
import shutil, urllib,urllib2,urlparse
import convirt.core.utils.constants
#from convirt.core.utils.NodeProxy import Node
import time, datetime
from datetime import datetime,timedelta
import string
import random

import traceback
import xml.dom.minidom
from xml.dom.minidom import Node
import webbrowser
import tg, calendar
from tg import session

from sqlalchemy import func

try:
    import hashlib
    md5_constructor=hashlib.md5
except ImportError,e:
    import md5
    md5_constructor=md5.new

import logging
LOGGER = logging.getLogger("convirt.core.utils")

# ease of use
constants = convirt.core.utils.constants
import locale
def to_unicode(text):
   if isinstance(text, unicode):
       return text
   if hasattr(text, '__unicode__'):
       return text.__unicode__()
   text = str(text)
   try:
       return unicode(text, 'utf-8')
   except UnicodeError:
       pass
   try:
       return unicode(text, locale.getpreferredencoding())
   except UnicodeError:
       pass
   return unicode(text, 'latin1')


def to_str(text):
   if isinstance(text, str):
       return text
   if hasattr(text, '__unicode__'):
       text = text.__unicode__()
   if hasattr(text, '__str__'):
       return text.__str__()
   return text.encode('utf-8')

def get_parent_task_status_info(task):
    from convirt.model.services import Task
    stat = Task.get_status(task)
    stat += "\nExecution Context :"
    ex_context = task.context.get("execution_context")
    if ex_context:
        for key,val in ex_context.iteritems():
            stat += "\n\t %s : %s" %(key, val)
    return stat

def get_child_task_status_info(task):
    from convirt.model.services import Task
    stat = Task.get_status(task)
    stat += "\nExecution Context :"
    ex_context = task.context.get("execution_context")
    node_ids = task.get_param("node_ids")
    stat += "\n\t NodeIDs : %s" %node_ids
    now = datetime.utcnow()
    try:
        stat += '\n\t CurrentServer : %s("%s")' %(task.current_node.hostname, task.current_node.id)
        strt = task.start_time
        durn = str((now-strt).seconds)+"."+str((now-strt).microseconds)
        stat+='\n\t StartTime: "%s", RunningFor: "%s"' % (strt, durn)
    except AttributeError:
        pass

    if ex_context:
        for key,val in ex_context.iteritems():
            stat += "\n\t %s : %s" %(key, val)
    return stat

def convert_to_CMS_TZ(gmt_time):
    #convert GMT time into Unix timestamp
    return_time = calendar.timegm(gmt_time.timetuple()) * 1000
    return return_time

def get_dbtype():
    dburl = tg.config.get('sqlalchemy.url')
    db_type=dburl.split("/")
    if db_type[0][-1] == ':':
         db_type = db_type[0][:-1]
    return db_type

class dynamic_map:
    def __init__(self, another_dict=None):
        if another_dict:
            self.__dictionary = dict(another_dict)
        else:
            self.__dictionary = dict()

    def __getattr__(self, name):
        if self.__dictionary.has_key(name):
            return self.__dictionary[name]
        if name.startswith('__') and name.endswith('__'):
            return self.__dictionary.__getattr__(name)
        return None

    def __getitem__(self, name):
        if dict.has_key(self.__dictionary,name):
            return dict.__getitem__(self.__dictionary, name)
        return None

    def __setitem__(self, name, value):
        self.__dictionary[name] = value

    def __setattr__(self,name,value):
        if name == '_dynamic_map__dictionary':
            self.__dict__[name] = value
        else:
            self.__dictionary[name] = value

    def __repr__(self):
        return to_str(self.__dictionary)

    def __getstate__(self):
        return self.__dictionary

    def __setstate__(self, dictionary):
        self.__dictionary = dictionary

    def __str__(self):
        return self.__repr__()

    def print_classes(self):
        for (k,v) in self.__dictionary.items():
            print k
            print v.__class__

    def has_key(self, name):
        return self.__dictionary.has_key(name)

    def items(self):
        return self.__dictionary.items()

    def iteritems(self):
        return self.__dictionary.iteritems()

    def iterkeys(self):
        return self.__dictionary.iterkeys()

    def itervalues(self):
        return self.__dictionary.itervalues()

    def keys(self):
        return self.__dictionary.keys()

    def values(self):
        return self.__dictionary.values()

    def clear(self):
        return self.__dictionary.clear()

    def pop(self,key,default=None):
        return self.__dictionary.pop(key,default)

    def popitem(self):
        return self.__dictionary.popitem()

    def get(self, key):
        return self.__dictionary.get(key)
    
# allows values to be functions or method and eval them 
# useful for generating multiple nic addresses in template substitution.
class fv_map(dict):
    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, name):
        if dict.has_key(self,name):
            value=dict.__getitem__(self, name)
            if isinstance(value, types.MethodType) or \
               isinstance(value, types.FunctionType) :
                value = value() # evaluate it
                return value

        return dict.__getitem__(self, name)


        
class XMConfig(ConfigParser.SafeConfigParser):
    """ ConVirt's configuration management class. """

    # the default list of sections in the config
    DEFAULT = 'DEFAULT'
    ENV = 'ENVIRONMENT'
    PATHS = 'PATHS'
    APP_DATA = 'APPLICATION DATA'
    CLIENT_CONFIG = 'CLIENT CONFIGURATION'
    IMAGE_STORE = 'IMAGE STORE'
    DEFAULT_REMOTE_FILE = '/etc/convirt.conf'
    
    def __init__(self, node, searchfiles = None, create_file = None):  
        """Looks for convirt.conf in current, user home and /etc directories. If
        it is not found, seeds one in the local directory."""

        ConfigParser.SafeConfigParser.__init__(self)
        self.node = node
        self.std_sections = [self.ENV,self.PATHS,self.APP_DATA,
                             self.CLIENT_CONFIG]
        
        if searchfiles is None:
            # no search path give. apply heuristics
            if not self.node.isRemote:
                # localhost
                filelist = [x for x in [os.path.join(os.getcwd(),'convirt.conf'),
                                        os.path.expanduser('~/.convirt/convirt.conf'),
                                        '/etc/convirt.conf'] if self.node.file_exists(x)]
            else:
                # remote host
                if self.node.file_exists(self.DEFAULT_REMOTE_FILE):
                    filelist =  [self.DEFAULT_REMOTE_FILE]
                else:
                    filelist = []
        else:
            # search path specified
            filelist = [x for x in searchfiles if self.node.file_exists(x)]

        if len(filelist) < 1:
            base_dir = None
            print 'No Configuration File Found'
            if create_file is None:
                # no default creation file is specified. use heuristics
                if not self.node.isRemote:
                    # localhost. create in cwd
                    print 'Creating default convirt.conf in current directory'            
                    self.configFile = os.path.join(os.getcwd(), 'convirt.conf')
                    base_dir = os.getcwd()
                else:
                    # remote host. create in default remote location
                    print 'Creating default convirt.conf at %s:%s' \
                          % (self.node.hostname,self.DEFAULT_REMOTE_FILE)
                    self.configFile = self.DEFAULT_REMOTE_FILE                
            else:
                # default creation location is specified
                print 'Creating default convirt.conf at %s:%s' \
                      % (self.node.hostname,create_file)                
                self.configFile = create_file            

            # new file created, populate w/ default entries
            self.__createDefaultEntries(base_dir)
            self.__commit()
            
        else:            
            # config file(s) found. choose a writable file,
            # otherwise create a new default file in the user's
            # home directory (only for localhost)
            self.configFile = None
            for f in filelist:
                try:
                    if self.node.file_is_writable(f):
                        # file is writable
                        if self.__validateFile(f):
                            # file is valid
                            self.configFile = f
                            print 'Valid, writable configuration found, using %s' % f
                        else:
                            # file is writable but not valid
                            # back it up (a new one will get created)                            
                            self.node.rename(f,f+'.bak')
                            print 'Old configuration found. Creating backup: %s.bak' % f                            

                        break
                    else:
                        print 'Confguration File not writable, skipping: %s' % f
                except IOError:
                    print 'Confguration File accessable, skipping: %s' % f
                    continue
                    
            if self.configFile is None:
                # no writable config file found
                print "No writable configuration found ... "
                if not self.node.isRemote:
                    # localhost
                    base_dir = os.path.expanduser('~/.convirt/')
                    if not os.path.exists(base_dir):
                        os.mkdir(base_dir)
                    self.configFile = os.path.join(base_dir, "convirt.conf")
                    print "\t Creating %s" % self.configFile                    
                    self.__createDefaultEntries(base_dir)
                    self.__commit()
                else:
                    # TBD: what to do in the remote case
                    raise Exception('No writable configuration found on remote host: %s' % self.node.hostname)
                
            #self.configFile = filelist[0]
            fp = self.node.open(self.configFile)
            self.readfp(fp)
            fp.close()

        # What is this doing here ? commenting out.
        #self.__commit()


    def __createDefaultEntries(self, base_dir = None):

        # cleanup first
        for s in self.sections():
            self.remove_section(s)
            
        # add the standard sections
        for s in self.std_sections:
                self.add_section(s)                


        # seed the defaults
        self.set(self.DEFAULT,constants.prop_default_computed_options,
                 "['arch', 'arch_libdir', 'device_model']")

        # paths
        if base_dir :
            base=base_dir
            log_dir = os.path.join(base,"log")
        else:
            base='/var/cache/convirt'
            log_dir = '/var/log/convirt'

        i_store = os.path.join(base, 'image_store')
        a_store = os.path.join(base, 'appliance_store')
        updates_file = os.path.join(base, 'updates.xml')
        
        self.set(self.PATHS, constants.prop_snapshots_dir, "/var/cache/convirt/vm_snapshots")
        self.set(self.PATHS, constants.prop_snapshot_file_ext, '.snapshot.xm')
        self.set(self.PATHS, constants.prop_cache_dir, "/var/cache/convirt")
        self.set(self.PATHS, constants.prop_exec_path, '$PATH:/usr/sbin')
        self.set(self.PATHS, constants.prop_image_store, i_store)
        self.set(self.PATHS, constants.prop_appliance_store, a_store)
        self.set(self.PATHS, constants.prop_updates_file, updates_file)

        self.set(self.PATHS, constants.prop_log_dir,log_dir)

        #self.set(self.CLIENT_CONFIG, constants.prop_default_xen_protocol, 'tcp')
        self.set(self.CLIENT_CONFIG, constants.prop_default_ssh_port, '22')
        #self.set(self.CLIENT_CONFIG, constants.prop_default_xen_port, '8006')
        
        self.set(self.CLIENT_CONFIG, constants.prop_enable_log, 'True')
        self.set(self.CLIENT_CONFIG, constants.prop_log_file, 'convirt.log')
        
        self.set(self.CLIENT_CONFIG,
                 constants.prop_enable_paramiko_log, 'False')
        self.set(self.CLIENT_CONFIG,
                 constants.prop_paramiko_log_file, 'paramiko.log')
        self.set(self.CLIENT_CONFIG,
                     constants.prop_http_proxy, '')

        self.set(self.CLIENT_CONFIG,
                     constants.prop_chk_updates_on_startup,'True')

        #self.set(self.CLIENT_CONFIG,
        #             constants.prop_vncviewer_options,'-PreferredEncoding=hextile')

        
        #self.set(self.CLIENT_CONFIG, constants.prop_browser, '/usr/bin/yelp')
        #self.set(self.PATHS, constants.prop_staging_location, '')
        #self.set(self.PATHS, constants.prop_kernel, '')
        #self.set(self.PATHS, constants.prop_ramdisk, '')
        #self.set(self.ENV, constants.prop_lvm, 'True')
        #self.__commit()

        # set localhost specific properties
        if not self.node.isRemote:
            #self.add_section(constants.LOCALHOST)
            self.set(self.ENV,constants.prop_dom0_kernel,platform.release())
        
        
    def __commit(self):
        outfile = self.node.open(self.configFile,'w')
        self.write(outfile)
        outfile.close()

    def __validateFile(self, filename):
        temp = ConfigParser.ConfigParser()
        fp = self.node.open(filename)
        temp.readfp(fp)
        fp.close()
        for s in self.std_sections:
            if not temp.has_section(s):
                print "section " + s + " not found"
                return False
        return True
    

    def getDefault(self, option):
        """ retrieve a default option/key value """
        return self.get(self.DEFAULT, option)


    def get(self, section, option):

        # does the option exist? return None if not
        if option is None: return None
        if not self.has_option(section, option): return None

        # option is available in the config. get it.
        retVal = ConfigParser.SafeConfigParser.get(self, section, option)
        
        # check if the value is blank. if so, return None
        # otherwise, return the value.
        if retVal == None:
            return retVal
        
        if not retVal.strip():
            return None
        else:
            return retVal
        

    def setDefault(self, option, value):
        """set the default for option to value.
        POSTCONDITION: option, value pair has been set in the default
        configuration, and committed to disk"""
        if option is not None:
            self.set(self.DEFAULT, option, value)


    def set(self, section, option, value):
        ConfigParser.SafeConfigParser.set(self, section, option, value)
        self.__commit()

        
    def getHostProperty(self, option, hostname=constants.LOCALHOST):
        """ retrieve the value for 'option' for 'hostname',
        'None', if the option is not set"""

        # does the option exist? return None if not
        if not self.has_option(hostname, option): return None

        # option is available in the config. get it.
        retVal = self.get(hostname, option)
        
        # check if the value is blank. if so, return None
        # otherwise, return the value.
        if retVal == None:
            return retVal
        
        if not retVal.strip():
            return None
        else:
            return retVal

    def getHostProperties(self, hostname=constants.LOCALHOST):
        if not self.has_section(hostname): return None
        return dict(self.items(hostname))

    def setHostProperties(self, options, hostname=constants.LOCALHOST):
        """ set config 'option' to 'value' for 'hostname'.
        If the a config section for 'hostname' doesn't exit,
        one is created."""
        
        if not self.has_section(hostname): self.add_section(hostname)
        for option in options:
            self.set(hostname, option, options[option])
        self.__commit()


    def setHostProperty(self, option, value, hostname=constants.LOCALHOST):
        """ set config 'option' to 'value' for 'hostname'.
        If the a config section for 'hostname' doesn't exit,
        one is created."""
        
        if not self.has_section(hostname): self.add_section(hostname)
        self.set(hostname, option, value)
        self.__commit()

    def removeHost(self, hostname):
        """ remove 'hostname' from the list of configured hosts.
        The configuration is deleted from both memory and filesystem"""

        if self.has_section(hostname):
            self.remove_section(hostname)
            self.__commit()

    def getHosts(self):
        """ return the list configured hosts"""
        hosts=[]
        for sec in self.sections():
            if sec in self.std_sections or sec == self.IMAGE_STORE:
                continue
            else:
                hosts.append(sec)
        #hosts = set(self.sections())-set(self.std_sections)
        #hosts = set(hosts) - set(self.IMAGE_STORE)
        return hosts


    def getGroups(self):
        groups = self.get(self.APP_DATA, constants.prop_groups)
        if groups is not None:
            return eval(groups)
        return {}

    def saveGroups(self, group_list):
        g_list_map = {}


        for g in group_list:
            g_map = {} # initialize it for each group hence within the loop.
            g_map["name"] = group_list[g].name
            g_map["node_list"] = group_list[g].getNodeNames()
            g_map["settings"] = group_list[g].getGroupVars()
            g_list_map[group_list[g].name] = g_map       
                 
        self.set(self.APP_DATA, constants.prop_groups, to_str(g_list_map))
        self.__commit()
        
    
class LVMProxy:
    """A thin, (os-dependent) wrapper around the shell's LVM
    (Logical Volume Management) verbs"""
    # TODO: move this class to an OSD module
    
    @classmethod
    def isLVMEnabled(cls, node_proxy, exec_path=''):
        retVal = True
        if node_proxy.exec_cmd('vgs 2> /dev/null',exec_path)[1]:
            retVal = False
        return retVal
    
        
    def __init__(self, node_proxy, exec_path=''):
        """ The constructor simply checks if LVM services are available
        for use via the shell at the specified 'node'.
        RAISES: OSError"""
        self.node = node_proxy
        self.exec_path = exec_path

        if node_proxy.exec_cmd('vgs 2> /dev/null',exec_path)[1]:
            raise OSError("LVM facilities not found")


    def listVolumeGroups(self):
        """ Returns the list of existing Volume Groups"""
        try:
            vglist = self.node.exec_cmd('vgs -o vg_name --noheadings', self.exec_path)[0]
            return [s.strip() for s in vglist.splitlines()]
        except OSError, err:
            print err
            return None

    def listLogicalVolumes(self, vgname):
        """ Returns the list of Logical Volumes in a Volume Group"""
        try:            
            lvlist = self.node.exec_cmd('lvs -o lv_name --noheadings '+ vgname,
                                        self.exec_path)[0]
            return [s.strip() for s in lvlist.splitlines()]
        except OSError, err:
            print err
            return None

    def createLogicalVolume(self, lvname, lvsize, vgname):
        """ Create a new LV with in the specified Volume Group.
        'lvsize' denotes size in number of megabytes.
        RETURNS: True on sucees
        RAISES: OSError"""
        error,retcode = self.node.exec_cmd('lvcreate %s -L %sM -n %s'%(vgname,lvsize,lvname),
                                           self.exec_path)
        if retcode:
            raise OSError(error.strip('\n'))
        else:
            return True
        
                
    def removeLogicalVolume(self, lvname, vgname=None):
        """ Remove the logical volume 'lvname' from the
        Volume Group 'vgname'. If the latter is not specified,
        'lvname' is treated as a fully specified path
        RETURNS: True on success
        RAISES: OSError"""
        if (vgname):
            lvpath = vgname + '/' + lvname
        else:
            lvpath = lvname
            
        error,retcode = self.node.exec_cmd('lvremove -f %s'% lvpath, self.exec_path)
        if retcode:
            raise OSError(error.strip('\n'))
        else:
            return True




from threading import Thread

class Poller(Thread):
    """ A simple poller class representing a thread that wakes
    up at a specified interval and invokes a callback function"""

    def __init__(self, freq, callback, args=[], kwargs={}, max_polls = None):
        Thread.__init__(self)
        self.setDaemon(True)
        self.frequency = freq
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.done = False
        self.remainder = max_polls

    def run(self):
        while not self.done:
            self.callback(*self.args,**self.kwargs)
            time.sleep(self.frequency)
            if self.remainder is not None:
                self.remainder -= 1
                if self.remainder < 0:
                    self.done = True

    def stop(self):
        self.done = True


### TODO : Remove dependence on managed_node
class PyConfig:
    """
        Class represents python based config file.
        Also, supports instantiating a templatized config file
    """
    default_computed_options = []
    COMPUTED_OPTIONS = "computed_options"
    CUSTOMIZABLE_OPTIONS = "customizable_options"
    def __init__(self,
                 managed_node = None,   # if none, assume localnode
                 filename = None,       # config file
                 signature = None,
                 config=None):          #actual config as string

        if managed_node is not None and type(managed_node) in [types.StringType,types.UnicodeType]:
            raise Exception("Wrong param to PyConfig.")
        
        """ filename and file open function to be used """
        self.filename = filename
        self.managed_node = managed_node
        self.lines = []
        self.options = {}
        self.signature = signature
        self.config=config
        

        if self.filename is not None or self.config is not None:
            (self.lines, self.options) = self.read_conf()

    @classmethod        
    def set_computed_options(cls, computed):
        cls.default_computed_options = computed

    def get_computed_options(self):
        c = []
        if self.default_computed_options is not None:
            c = self.default_computed_options
            
        if self.options.has_key(self.COMPUTED_OPTIONS):
            specific_computed_options = self[self.COMPUTED_OPTIONS]
        else:
            specific_computed_options = None
            
        if specific_computed_options is not None and \
               type(specific_computed_options) == types.ListType:
            for o in specific_computed_options:
                c.append(o)

        if self.COMPUTED_OPTIONS not in c :
            c.append(self.COMPUTED_OPTIONS)
        return c

    def get_customizable_options(self):
        customizable_options = None
        if self.options.has_key(self.CUSTOMIZABLE_OPTIONS):
            customizable_options = self[self.CUSTOMIZABLE_OPTIONS]
        else:
            customizable_options = self.options.keys()

        if customizable_options is not None and \
               self.CUSTOMIZABLE_OPTIONS in customizable_options :
            customizable_options.remove(self.CUSTOMIZABLE_OPTIONS)
            
        return customizable_options

    # set the name of the file associated with the config.
    def set_filename(self, filename):
        """
        set the filename associated with this config.
        subsequent write would use this file name.
        """
        self.filename = filename

    # Allow for changing the managed node.
    # useful in reading a template and then writing modified, instantiated
    # file on a managed node.
    def set_managed_node(self, node):
        self.managed_node = node

    def read_config(self, init_glob=None, init_locs=None):
        if init_glob is not None:
            globs = init_glob
        else:
            globs = {}

        if init_locs is not None:
            locs = init_locs
        else:
            locs  = {}

        lines = []
        lines=self.config.split("\n")
        options = {}
        try:
            if len(lines) > 0:
                cmd = "\n".join(lines)
    #                print "CNMDDDDDDDDDDDD+===============", cmd
                cmd = cmd.replace('\r\n', '\n')
                exec cmd in globs, locs
        except:
            raise
        # Extract the values set by the script and set the corresponding
        # options, if not set on the command line.
        vtypes = [ types.StringType,
                   types.UnicodeType,
                   types.ListType,
                   types.IntType,
                   types.FloatType,
                   types.DictType
                   ]
        for (k, v) in locs.items():
            if not(type(v) in vtypes): continue
            options[k]=v
        return lines,options

    def read_conf(self, init_glob=None, init_locs=None):
        if self.config is not None:
            return self.read_config(init_glob, init_locs)
        
        if init_glob is not None:
            globs = init_glob
        else:
            globs = {}

        if init_locs is not None:
            locs = init_locs
        else:
            locs  = {}
            
        lines = []
        options = {}
        try:
            if self.managed_node is None:
                f = open(self.filename)
            else:
                f = self.managed_node.node_proxy.open(self.filename)
            lines = f.readlines()
            f.close()
            if len(lines) > 0:
                cmd = "\n".join(lines)
                cmd = cmd.replace('\r\n', '\n')
                exec cmd in globs, locs
        except:
            raise
        # Extract the values set by the script and set the corresponding
        # options, if not set on the command line.
        vtypes = [ types.StringType,
                   types.UnicodeType,
                   types.ListType,
                   types.IntType,
                   types.FloatType,
                   types.DictType
                   ]
        for (k, v) in locs.items():
            if not(type(v) in vtypes): continue
            options[k]=v

        return (lines,options)

    def write(self, full_edit=False):
        """Writes the settings out to the filename specified during
        initialization"""

        dir = os.path.dirname(self.filename)
        if self.managed_node is None:
            if not os.path.exists(dir):
                os.makedirs(dir)
            outfile = open(self.filename, 'w')
        else:
            if not self.managed_node.node_proxy.file_exists(dir):
                mkdir2(self.managed_node, dir)
            outfile = self.managed_node.node_proxy.open(self.filename, 'w')
            
        if self.signature is not None:
            outfile.write(self.signature)
        
        # Simple write
        if self.lines is None or len(self.lines) == 0:
            for name, value in self.options.iteritems():
                outfile.write("%s = %s\n" % (name, repr(value)))
        else:
            # drive the writing through lines read.
            updated = []
            for line in self.lines:
                if self.signature is not None and \
                       line.find(self.signature) >= 0:
                    continue
                if line == '':
                    continue
                if line[0] == '#' or line[0] == '\n' or \
                        line[0].isspace() or line.strip().endswith(':'):
                    outfile.write(line)
                else:
                    ndx = line.find("=")
                    if ndx > -1:
                        token = line[0:ndx]
                        token = token.strip()
                        if self.options.has_key(token):
                            if token not in self.get_computed_options() and \
                               (token != self.CUSTOMIZABLE_OPTIONS or full_edit) :
                                value = self.options[token]
                                outfile.write("%s=%s\n" % (token, repr(value)))
                                updated.append(token)
                            else:
                                #print "writing computed Token X:" , line
                                if token != self.COMPUTED_OPTIONS:
                                    outfile.write(line)
                        else:
                            if token in self.get_computed_options():
                                outfile.write(line)
                            else:
                                #print "Valid token but removed" , line
                                pass
                    else:
                        #print "writing default Y:" , line
                        outfile.write(line)

            # Add new tokens added
            for name, value in self.options.iteritems():
                if name not in updated and \
                       name not in self.get_computed_options():
                    outfile.write("%s=%s\n" % (name, repr(value)))

        outfile.close()

    def instantiate_config(self, value_map):
        
        # do this so that substitution happens properly
        # we may have to revisit, map interface of PyConfig
        if isinstance(value_map, PyConfig):
            value_map = value_map.options
        
        # instantiate the filename
        if self.filename is not None:
            fname = string.Template(self.filename)
            new_val = fname.safe_substitute(value_map)
            self.set_filename(new_val)
        
        for key in self.options.keys():
            value = self.options[key]
            if value is not None:                
                if type(value) in [types.StringType,types.UnicodeType]:
                    template_str = string.Template(value)
                    self.options[key] = to_str(template_str.safe_substitute(value_map))
                elif type(value) is types.ListType:
                    new_list = []
                    for v in value:
                        if type(v) is types.StringType:
                            template_str = string.Template(v)
                            new_list.append(template_str.safe_substitute(value_map))
                                                
                        else:
                            new_list.append(v)
                    self.options[key] = new_list
                    #print "old %s, new %s", (value, self.options[key])
                    


    def save(self, filename):
        """ save the current state to a file"""
        self.filename = filename
        self.write()

    def get(self, name):
        return self[name]

    #access config as hastable 
    def __getitem__(self, name):
        if self.options.has_key(name):
            return self.options[name]
        else:
            attrib = getattr(self,name, None)
            if attrib is not None:
                return attrib
            else:
                return None

    def __setitem__(self, name, item):
        self.options[name] = item

    def __iter__(self):
        return self.options.iterkeys()

    def iteritems(self):
        return self.options.iteritems()

    def has_key(self, key):
        return self.options.has_key(key)
    
    def keys(self):
        return self.options.keys()
    # debugging dump
    def dump(self):
        if self.filename is not None:
            print self.filename
        for name, value in self.options.iteritems():
            print "%s = %s" % (name, repr(value))

    def __delitem__(self, key):
        if self.has_key(key):
            del self.options[key]

# generic worker to be used to communicate with main thread
# using idle_add
import threading
### JD FOR NOW : 
### import gobject
### This will cause Worker to give error.
from threading import Thread
class Worker(Thread):
    def __init__(self, fn, succ, fail,progress=None):
        Thread.__init__(self)
        self.setDaemon(True)
        self.fn = fn
        self.succ = succ
        self.progress = progress
        self.fail = fail
        
    def run(self):
        try:
            ret = self.fn()
        except Exception, ex:
            traceback.print_exc()
            if self.fail:
                gobject.idle_add(self.fail,ex)
        else:
            if self.succ:
                gobject.idle_add(self.succ, ret)


# class to download the updates.
# can be used by UI to display the updates.
class UpdatesMgr:
    update_url = "http://www.convirture.com/updates/updates.xml"
    updates_file = "/var/cache/convirt/updates.xml"
    
    def __init__(self, config):
        self.config = config
        self.url = self.config.get(XMConfig.PATHS, constants.prop_updates_url)
        if not self.url:
            self.url = UpdatesMgr.update_url
            
            
        self.updates_loc = self.config.get(XMConfig.PATHS,
                                       constants.prop_updates_file)
        if not self.updates_file:
            self.updates_file = UpdatesMgr.updates_file


    def fetch_updates(self):
        update_items = []

        try:
            # file is not writable..lets create a tmp file
            if not os.access(self.updates_file,os.W_OK):
                (t_handle, t_name) = tempfile.mkstemp(prefix="updates.xml")
                self.updates_file = t_name
                os.close(t_handle) # Use the name, close the handle.
                
            fetch_isp(self.url, self.updates_file, "/xml")
        except Exception, ex:
            print "Error fetching updates ", ex
            try:
                if os.path.exists(self.updates_file):
                    os.remove(self.updates_file)
            except:
                pass
            return update_items


        if os.path.exists(self.updates_file):
            updates_dom = xml.dom.minidom.parse(self.updates_file)
            for entry in updates_dom.getElementsByTagName("entry"):
                info = {}
                for text in ("title","link","description", "pubDate",
                             "product_id", "product_version","platform"):
                    info[text] = getText(entry, text)
                populate_node(info,entry,"link",
                          { "link" : "href"})

                update_items.append(info)

        # cleanup the file
        try:
            if os.path.exists(self.updates_file):
                os.remove(self.updates_file)
        except:
            pass
        
        return update_items


    # every time it is called it gets new updates from last time
    # it was called.
    def get_new_updates(self):
        new_updates = []
        updates = self.fetch_updates()
        str_r_date = self.config.get(XMConfig.APP_DATA,
                                   constants.prop_ref_update_time)
        if str_r_date:
            p_r_date = time.strptime(str_r_date, "%Y-%m-%d %H:%M:%S")
            r_date = datetime.datetime(*p_r_date[0:5])
        else:
            r_date = datetime.datetime(2000, 1, 1)

        max_dt = r_date
        for update in updates:
            str_p_dt = to_str(update["pubDate"])
            if str_p_dt:
                p_dt = time.strptime(str_p_dt, "%Y-%m-%d %H:%M:%S")
                dt = datetime.datetime(*p_dt[0:5])
                if dt > r_date :
                    new_updates.append(update)
                    if dt > max_dt:
                        max_dt = dt
                        

        if max_dt > r_date:
            str_max_dt = max_dt.strftime("%Y-%m-%d %H:%M:%S")
            self.config.set(XMConfig.APP_DATA,
                            constants.prop_ref_update_time,
                            str_max_dt)
        return new_updates
    
#
# copy directory from local filesystem to remote machine, dest.
# src : source file or directory
# dest_node :node on which the files/directory needs to be copied
# dest_dir : destination directory under which src file/dir would be
#            copied
# dest_name : name of file/directory on the destination node.
# hashexcludes: list of the files to be excluded from generating hash.
#
def copyToRemote(src,dest_node,dest_dir, dest_name = None, hashexcludes=[], timeout=None):
    from convirt.viewModel import Basic
    import convirt.core.utils.commands as commands

    if not timeout:
        timeout = int(tg.config.get("default_timeout", 300))

    src = os.path.abspath(src)
    srcFileName = os.path.basename(src)
    if srcFileName and srcFileName[0] == "." :
        print "skipping hidden file ", src
        return

    if not os.path.exists(src):
        raise Exception("%s does not exist." % src)

    
    hash_dir = ""
    hash_dir = tg.config.get('hash_dir')
    hashFile = src + ".hash"
    if hash_dir : # cant use sys.path.join with two absolute path
       try:
          hash_dir = os.path.abspath(hash_dir)
          if not os.path.exists(hash_dir) : 
             os.makedirs(hash_dir)
          hashFile = hash_dir + hashFile
       except Exception, ex:
          print "Could not create hash directory :",hash_dir
    

    # If the selected file is already a hashfile, skip it.
    if os.path.isfile(src) and not src.endswith(".hash") :        
        mkdir2(dest_node,dest_dir)
        dest_hashFile = os.path.join(dest_dir, os.path.basename(hashFile))
        if dest_name is not None:
            dest = os.path.join(dest_dir, dest_name)
        else:
            dest = os.path.join(dest_dir, os.path.basename(src))

        copyFile = False
        # Check for hashfile
        if srcFileName not in hashexcludes:
            if not os.path.exists(hashFile) : 
                hash_base=os.path.dirname(hashFile)
                if not os.path.exists(hash_base) :
                   os.makedirs(hash_base)
                generateHashFile(src, hashFile)
            else:
                updateHashFile(src, hashFile) # update the hash if required.

            localhashVal  = None
            remotehashVal = None
            if os.path.exists(hashFile):
                # read local hash
                lhf = None
                try :
                    lhf = open(hashFile)
                    localhashVal =  lhf.read()         
                finally:
                    if lhf:
                        lhf.close()
            
                #only if local hashfile exists, check for remote hashfile.
                if dest_node.node_proxy.file_exists(dest_hashFile):
                    rhf = None
                    try :
                        rhf = dest_node.node_proxy.open(dest_hashFile)
                        remotehashVal = rhf.read()
                    finally:
                        if rhf:
                            rhf.close()

            else:
                raise Exception("Hash file not found." + hashFile)

            if not compareHash(remotehashVal, localhashVal):
                copyFile = True

        else:
            copyFile = True # file is in exclude hash
    
        if copyFile:  # either in exclude hash or hash mismatch
            print "copying ", src
            mode = os.lstat(src).st_mode

            f_size = os.path.getsize(src)
            if f_size > 65536:# file size grater than 64KB
                msg = "CopyToRemote: Copying sparse file: %s to %s" %(src, dest_dir)
                print msg
                LOGGER.info(msg)
                local = Basic.getManagedNode()
                node_username = dest_node.get_credentials().get('username')
                src_filename = src.split("/")[-1]
                src_dir = src[0:-len(src_filename)]
                cmd = commands.get_cmd_copy_spares_file_to_remote(node_username, dest_node.hostname, src_filename, dest_dir)
                (output, exit_code) = local.node_proxy.exec_cmd(cmd, exec_path=src_dir, cd=True, timeout=timeout)
                if exit_code:
                    msg = "CopyToRemote: Can not copy spares file %s to %s, %s" %(src, dest_dir, output)
                    print msg
                    LOGGER.error(msg)
                    raise Exception(msg)
                msg = "CopyToRemote: Copied sparse file: %s to %s" %(src, dest_dir)
                print msg
                LOGGER.info(msg)
            else:
                msg = "CopyToRemote: Copying file: %s to %s" %(src, dest_dir)
                print msg
                LOGGER.info(msg)
                dest_node.node_proxy.put(src, dest)
                dest_node.node_proxy.chmod(dest, mode)
                msg = "CopyToRemote: Copied file: %s to %s" %(src, dest_dir)
                print msg
                LOGGER.info(msg)
            if srcFileName not in hashexcludes: # file needs a hash
                # copy the hash file too.
                print "copying hash too", hashFile
                mode = os.lstat(hashFile).st_mode
                dest_node.node_proxy.put(hashFile, dest_hashFile)
                dest_node.node_proxy.chmod(dest_hashFile, mode)
            
    elif os.path.isdir(src): # directory handling
        mkdir2(dest_node,dest_dir)
        if dest_name is not None:
            dest = os.path.join(dest_dir, dest_name)
        else:
            (dirname, basename) = os.path.split(src)
            dest = os.path.join(dest_dir,basename)
            mkdir2(dest_node, dest)
            
        for entry in os.listdir(src):
            s = os.path.join(src, entry)
            copyToRemote(s, dest_node, dest, hashexcludes=hashexcludes)


#Generates hashfile for a given filename.
#The extension of the hashfilename is ".hash".
#Hashvalue = Last modification time + "|" + hexvalue.
def generateHashFile(filename, hash_file):
	f = file(filename,'rb')
	fw = file(hash_file, 'wb')
	m = md5_constructor()
 
	readBytes = 1024 # read 1024 bytes per time
	try:
	    while (readBytes):
		    readString = f.read(readBytes)
		    m.update(readString)
		    readBytes = len(readString)
	finally:
	    f.close()
	
	try:
	    fw.write(to_str(os.stat(filename).st_mtime))
	    fw.write('|')
	    fw.write(m.hexdigest())
	
	finally:
	    fw.close()

# The method updates the hasfile if it exists.
# Check if the modification time is same in the hashfile.
# If not look for hash value if it is the same.
# If not generate a new hash value and add modification time.
def updateHashFile(filename, hash_file):
    fhash = file(hash_file, 'rb')
    m = md5_constructor()

    try:
        readHash = fhash.read()
    finally:
        fhash.close()    
    
    hashline = readHash.split("|")

    hashVal = m.hexdigest()
    hashTime = os.stat(filename).st_mtime
    generate = False
    
    # Check for the modification time 
    if hashline[0] == to_str(hashTime) and  hashline[1] == hashVal:
        return 
    else:
        f = file(filename,'rb')
        readBytes = 1024; # read 1024 bytes per time
        try:
            while (readBytes):
                readString = f.read(readBytes)
                m.update(readString)
                readBytes = len(readString)
        finally:
            f.close()

        try:
            fhash = file(hash_file, 'wb')
            fhash.write(to_str(hashTime))
            fhash.write('|')
            fhash.write(hashVal)
        finally:
            fhash.close()


#Compares 2 hashvalues.
#First part of the hashvalue is the last modification time of the file.
#Second part is the hexvalue.
# for comparison, we can simply use the string compare.
def compareHash(remoteHash, localHash):
    return remoteHash == localHash


# make n level directory.
def mkdir2(dest_node, dir):
    root = dir
    list = []
    while root and not dest_node.node_proxy.file_exists(root) and root is not '/' :
        list.insert(0,root)
        (root, subdir) = os.path.split(root)

    for d in list:
        dest_node.node_proxy.mkdir(d)
    
    
def mktempfile(node,prefix=None,suffix=None):
    if node is None:
        fd,filename = tempfile.mkstemp(suffix,prefix)
    else:
        fname = prefix + '.XXXXX'
        temp_file,code=node.node_proxy.exec_cmd('mktemp -t '+fname)
        filename=temp_file.strip()
    return filename
   

def fetchImage(src, dest):
    """ Copies 'src' to 'dest'. 'src' can be an http or ftp URL
    or a filesystem location. dest must be a fully qualified
    filename."""
    
    print "Fetching: "+src
    if src.startswith("http://") or src.startswith("ftp://"):
        # newtwork fetch
        urllib.urlretrieve(src,dest)
    else:
        # filesystem fetch
        shutil.copyfile(src, dest)



## New Code
def search_tree(tree, key):
    """Retrieve a value from a tree"""

    if tree == None or key == None or len(tree) < 1:
        return None

    # if list has a name/ctx
    if type(tree[0]) is str:
        if key == tree[0]:
            if len(tree) > 2:
                return tree[1:]
            else:
                return tree[1]
        l = tree[1:]
    else:
        l = tree
        
    for elem in l:
        #print "processing ..", elem[0], key
        if type(elem) is list:
            if len(elem) > 0 and elem[0] == key:
                if len(elem) > 2:
                    #print "returning [[v1],[v2],..] from NV"
                    return elem[1:]
                else:
                    #print "returning V from NV"
                    return elem[1]
            elif len(elem) >=2 and type(elem[1]) is list:
                if len(elem) == 2:
                    #print "recursing with [V] " # , elem[1]
                    v = search_tree(elem[1],key)
                    if v is not None:
                        return v
                else:
                    #print "recursing with [[v1],[v2],...]" #, elem[1:]
                    v = search_tree(elem[1:],key)
                    if v is not None:
                        return v
    return None

def is_host_remote(host):
    host_names = []
    try:
        (host_name, host_aliases,host_addrs) = socket.gethostbyaddr(host)
        host_names.append(host_name)
        host_names = host_aliases + host_addrs
    except:
        host_names.append(host)

    return len(set(l_names).intersection(set(host_names))) == 0


# we will be using this at few places. better to keep it in a separate
# function
def read_python_conf(conf_file):
    """ reads a conf file in python format and returns conf as hash table"""
    glob = {}
    loc  = {}
    if not os.path.exists(conf_file):
        print "conf file not found :" + conf_file
        return None
    execfile(conf_file, glob, loc)
    
    # filter out everything other than simple values and lists
    vtypes = [ types.StringType,
               types.UnicodeType,
               types.ListType,
               types.IntType,
               types.FloatType,
               types.DictType
               ]

    for (k, v) in loc.items():
        if type(v) not in vtypes:
            del loc[k]

    return loc


# need to go in common place

def guess_value(value):
    # check if it is a number
    if value is None or value == '':
        return value

    if value.isdigit():
        return int(value)

    # check if float
    parts = value.split(".")
    if len(parts) == 2:
        if parts[0].isdigit() and parts[1].isdigit():
            return float(value)

    # check if it is a list
    if value[0] in  ['[' ,'{']:
        g = {}
        l = {}
        cmd = "x = " + value
        exec cmd in g, l
        return l['x']

    # assume it is a string
    return value

## fetch stuff uses urllib2. throws exception on 404 etc.
## this same routine is in the common/functions used for provisioning
## Any enhancement/fixes should be made over there as well.
def fetch_url(url, dest, proxies=None,
              reporthook=None,data=None,chunk=2048):
    if reporthook:
        raise Exception("reporthook not supported yet")
    
    resp = None
    df = None
    ret = (None, None)
    try:
        if proxies:
            proxy_support = urllib2.ProxyHandler(proxies)
            opener = urllib2.build_opener(proxy_support)
        else:
            opener = urllib2.build_opener()

        req = urllib2.Request(url)
        req.add_header("User-Agent", constants.fox_header)
                       
        if data:
            resp = opener.open(req, data)
        else:
            resp = opener.open(req)

        ret = resp.geturl(),resp.info()
        df = open(dest, "wb")
        data = resp.read(chunk)
        while data:
            try:
                df.write(data)
                data = resp.read(chunk)
            except socket.error, e:
                if (type(e.args) is tuple) and (len(e.args) > 0) and \
                       ((e.args[0] == errno.EAGAIN or e.args[0] == 4)):
                    continue
                else:
                    raise
    finally:
        if df:
            df.close()
        if resp:
            resp.close()

    return ret

def connect_url(url, proxies=None,
              reporthook=None,data=None,chunk=2048):
    if reporthook:
        raise Exception("reporthook not supported yet")

    #print "\n\n=====",url
    resp = None
    result=""

    try:
        if proxies:
            proxy_support = urllib2.ProxyHandler(proxies)
            opener = urllib2.build_opener(proxy_support)
        else:
            opener = urllib2.build_opener()

        req = urllib2.Request(url)
        req.add_header("User-Agent", constants.fox_header)

        if data:
            resp = opener.open(req, data)
        else:
            resp = opener.open(req)

        data = resp.read(chunk)
        while data:
            result = result + data
            try:
                data = resp.read(chunk)
            except socket.error, e:
                if (type(e.args) is tuple) and (len(e.args) > 0) and \
                       ((e.args[0] == errno.EAGAIN or e.args[0] == 4)):
                    continue
                else:
                    raise
    finally:
        if resp:
            resp.close()

    return result

# ISP seems to cache and return a http redirect which we can not
# parse. So just retry.
def fetch_isp(url, dest, content_type):
    retries = 2
    while retries > 0:
        (u, headers) = fetch_url(url, dest)
        retries = retries - 1;
        type =  headers.get("Content-Type")
        if type and type.lower().find(content_type) < 0  :
            print "Retrying ..", type
            continue
        else:
            break

    if type is None:
        raise Exception("Could not fetch %s. Content-Type is None", u)

    if type.lower().find(content_type) < 0 :
        raise Exception("Could not fetch %s. Wrong content type: "+ type )


# Go through firefox setup and try to guess the proxy values.
def guess_proxy_setup():
    moz_pref_path = os.path.expanduser("~/.mozilla/firefox")
    files = glob.glob(moz_pref_path  + "/*/prefs.js")
    if len(files) > 0:
        pref_file = files[0]
        print pref_file
    else:
        return (None, None)

    prefs = open(pref_file, "r").read().split("\n")

    # get all user_pref lines
    #prefs = re.findall('user_pref("network\.proxy\.(.*)",(.*));', prefs )
    proxy_prefs = {}
    for pref_line in prefs:
        pref = re.findall('user_pref\("network.proxy.(.*)", ?(.*)\);', pref_line )
        if len(pref) > 0 and len(pref[0]) > 1:
            k = pref[0][0]
            v = pref[0][1]
            if v[0] == '"':
                v = v[1:]
            if v[-1] == '"':
                v = v[0:-1]
            proxy_prefs[k] = v

    if proxy_prefs.has_key("type"):
        if proxy_prefs["type"] != "1": # 1 means manual setup of of proxy
            print "type is ", type , " other than manual proxy. None, None"
            return (None, None)
    else:
        print "type is missing. Direct connection. None, None"
        return (None, None)


    http_proxy = None
    if proxy_prefs.has_key("http") and proxy_prefs["http"]:
        http_proxy = "http://"+proxy_prefs["http"]
        if proxy_prefs.has_key("http_port") and proxy_prefs["http_port"]:
            http_proxy += ":" + proxy_prefs["http_port"]
        else:
            http_proxy += ":" + '80'

    ftp_proxy =None
    if proxy_prefs.has_key("ftp") and proxy_prefs["ftp"]:
        ftp_proxy = "http://"+proxy_prefs["ftp"]
        if proxy_prefs.has_key("ftp_port") and proxy_prefs["ftp_port"]:
            ftp_proxy += ":" + proxy_prefs["ftp_port"]
        else:
            ftp_proxy += ":" + '80'

    return http_proxy, ftp_proxy

def show_url(url):
    if webbrowser.__dict__.has_key("open_new_tab"):
        webbrowser.open_new_tab(url)
    else:
        webbrowser.open_new(url)
       

#
# Module initialization
#

l_names = []
try:
    (local_name, local_aliases,local_addrs) = \
                 socket.gethostbyaddr(constants.LOCALHOST)

    l_names.append(local_name)
    l_names = local_aliases + local_addrs
except socket.herror:
    print "ERROR : can not resolve localhost"
    pass
    

# directly from xend/server/netif.py (LGPL)
# Copyright 2004, 2005 Mike Wray <mike.wray@hp.com>
# Copyright 2005 XenSource Ltd
def randomMAC():
    """Generate a random MAC address.

    Uses OUI (Organizationally Unique Identifier) 00-16-3E, allocated to
    Xensource, Inc. The OUI list is available at
    http://standards.ieee.org/regauth/oui/oui.txt.

    The remaining 3 fields are random, with the first bit of the first
    random field set 0.

    @return: MAC address string
    """
    mac = [ 0x00, 0x16, 0x3e,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))


# directly from xend/uuid.py (LGPL)
# Copyright 2005 Mike Wray <mike.wray@hp.com>
# Copyright 2005 XenSource Ltd
def randomUUID():
    """Generate a random UUID."""

    return [ random.randint(0, 255) for _ in range(0, 16) ]


# directly from xend/uuid.py (LGPL)
# Copyright 2005 Mike Wray <mike.wray@hp.com>
# Copyright 2005 XenSource Ltd
def uuidToString(u):
    return "-".join(["%02x" * 4, "%02x" * 2, "%02x" * 2, "%02x" * 2,
                     "%02x" * 6]) % tuple(u)


# directly from xend/uuid.py (LGPL)
# Copyright 2005 Mike Wray <mike.wray@hp.com>
# Copyright 2005 XenSource Ltd
def uuidFromString(s):
    s = s.replace('-', '')
    return [ int(s[i : i + 2], 16) for i in range(0, 32, 2) ]


# the following function quotes from python2.5/uuid.py
#def get_host_network_devices():
#    device = []
#    for dir in ['', '/sbin/', '/usr/sbin']:
#        executable = os.path.join(dir, "ifconfig")
#        if not os.path.exists(executable):
#            continue
#        try:
#            cmd = 'LC_ALL=C %s -a 2>/dev/null' % (executable)
#            pipe = os.popen(cmd)
#        except IOError:
#            continue
#        for line in pipe:
#            words = line.lower().split()
#            for i in range(len(words)):
#                if words[i] == "hwaddr":
#                    device.append(words)
#    return device


        
# Util functions

# generic function which looks for a tag under the node, and populates
# info with attribute values using attribute map
def populate_node(info, parent_node, tag, attributes):
    nodes = parent_node.getElementsByTagName(tag)
    if nodes:
        node = nodes[0]
        populate_attrs(info, node, attributes)

def populate_attrs(info, node, attributes):
    for key, attr in attributes.iteritems():
        info[key] = node.getAttribute(attr)

def getText(parent_node, tag_name):
    nodelist = []
    elems =  parent_node.getElementsByTagName(tag_name)
    if elems.length > 0:
        first = elems[0]
        nodelist = first.childNodes
    else:
        #print "#####tag %s not found for %s", (tag_name, parent_node)
        pass
    
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
            rc = rc + node.data
    return rc        


# search a file with context in the tarball or installation and return path
# precedence to the current directory/tarball
def get_path(filename, name_spaces=None):
    for path in (os.path.dirname(sys.argv[0]),'.', '/usr/share/convirt','/opt/convirt'):
        if name_spaces:
            for ns in name_spaces:
                p = os.path.join(path, ns)
                f = os.path.join(p, filename)
                if os.path.exists(f):
                    return (p, f)
        else:
            f = os.path.join(path, filename)
            if os.path.exists(f):
                return (path,f)
    return (None,None)

## initialize platform defaults
def get_platform_defaults(location):
    dir_name = os.path.dirname(location)
    file_name = os.path.join(dir_name, "defaults")
    return read_python_conf(file_name)
    
def get_prop(map, key, default=None):
    if map.has_key(key):
        return map[key]
    else:
        return default

def get_config(config):
    globs={}
    locs={}
    lines = []
    lines=config.split("\n")
    options = {}
    try:
        if len(lines) > 0:
            cmd = "\n".join(lines)
#                print "CNMDDDDDDDDDDDD+===============", cmd
            exec cmd in globs, locs
    except:
        raise
    # Extract the values set by the script and set the corresponding
    # options, if not set on the command line.
    vtypes = [ types.StringType,
               types.UnicodeType,
               types.ListType,
               types.IntType,
               types.FloatType,
               types.DictType
               ]
    for (k, v) in locs.items():
        if not(type(v) in vtypes): continue
        options[k]=v
    return options

def print_traceback():
    traceback.print_exc()
    
def getHexID(name=None,params=None):
#    """create a MD5 HEX ID based on name and params"""
#    x = md5_constructor(name)
#    if params is not None:
#        for param in params:
#            x.update(to_str(param))
#    return x.hexdigest()
    return to_unicode(uuidToString(randomUUID()))

def getDateTime(dateval,timeval):
    if dateval is None or timeval is None:
        return None
    print dateval,"==============",timeval
    months={
        'Jan':1,
        'Feb':2,
        'Mar':3,
        'Apr':4,
        'May':5,
        'Jun':6,
        'Jul':7,
        'Aug':8,
        'Sep':9,
        'Oct':10,
        'Nov':11,
        'Dec':12,
    }
    dateparts=dateval.split(" ")
    timeparts=timeval.split(":")
    print dateparts[1],"--",dateparts[2],"---",dateparts[3],"----"
    utcnow=datetime.utcnow()
    now=datetime.now()
    diff=utcnow-now

    sel=datetime(int(dateparts[3]),months[dateparts[1]],int(dateparts[2]),\
            int(timeparts[0]),int(timeparts[1]))

#    print "utc==",utcnow
#    print "loc==",now
#    print "sel==",sel
#    print "dif==",diff

    return sel+diff


def populate_node_filter(managed_node, platform, image):
    if managed_node is not None:
        if platform:
            if managed_node.get_platform() != platform or not managed_node.is_up():
                return False
        if image:
            if not managed_node.is_up() or not managed_node.is_image_compatible(image):
                return False

    return True

# Provisioning through cli
# Config file writing
def vm_config_write(auth,context,image_id,v_config,i_config,img_name):
            # update is_remote and change protocol

    try:
        is_remote_list = []
        s_stats = v_config.get_storage_stats()
        for de in v_config.getDisks():
            r = s_stats.get_remote(de.filename)
            is_remote_list.append(r)

        img_location = context.image_store.get_image(auth,image_id).location
        if img_location:
            img_location = os.path.basename(img_location)

        from convirt.model import DBSession,ManagedNode
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == context.managed_node.id).first()
        context.managed_node = managed_node
        instantiate_configs(context.managed_node,
                                 context.image_store,
                                 img_name,
                                 img_location,
                                 v_config,
                                 i_config)


        store = context.image_store
        managed_node = context.managed_node

        vm_config_file  = v_config.filename


        v_config["image_name"] = img_name
        v_config["image_id"] = image_id
        v_config["platform"] = managed_node.get_platform()
        # see if the following can be moved to execute_prov script
        v_config.set_managed_node(managed_node)
        change_file_2_tap = False
        is_hvm_image = context.image_store.get_image(auth,image_id).is_hvm()
        if v_config["platform"] == 'xen' and not is_hvm_image:
            change_file_2_tap = True


        changed = False
        changed_disks = []

        ndx = 0
        ll = len(is_remote_list)
        s_stats = v_config.get_storage_stats()
        for de in v_config.getDisks():
            if de and de.type == "file" and change_file_2_tap:                
                pv_driver = v_config.get(constants.default_xen_pv_driver)
                if pv_driver is None:
                    pv_driver = "tap:aio"
                de.type = pv_driver 
                changed = True
            changed_disks.append(repr(de))

            r = None
            if ndx < ll:
                r = is_remote_list[ndx]
            s_stats.set_remote(de.filename,r)
            ndx += 1


        if changed: # update the disk entry
            print "Updating disk to new value : for tap:aio", changed_disks
            v_config["disk"] = changed_disks

        v_config.write()

        return store,managed_node,vm_config_file,v_config
    except Exception, e:
        raise e


def instantiate_configs(managed_node,
                            image_store, image_name, image_location,
                            vm_config, image_config):

    # get prepare template map
    try:
        template_map = fv_map()
        store_location = image_store.get_remote_location(managed_node)

        template_map["IMAGE_STORE"] = store_location
        template_map["IMAGE_NAME"] = image_name
        template_map["IMAGE_LOCATION"] = image_location
        template_map["VM_NAME"] = vm_config["name"]
        template_map["SERVER_NAME"] = managed_node.hostname

        # default conventions
        def_bridge="xenbr0"
        if managed_node.platform == 'kvm':
            def_bridge='br0'

        # see if the managed_node has the default bridge
        bridge = managed_node.get_default_bridge()
        if bridge:
            print "setting default bridge from discoverd information", bridge
            def_bridge = bridge
        elif image_config["DEFAULT_BRIDGE"] : #cheating
            def_bridge = image_config["DEFAULT_BRIDGE"]


        template_map["DEFAULT_BRIDGE"] = def_bridge

        # Autogenerated MAC address
        # TODO: keep track of generated MAC's
        template_map["AUTOGEN_MAC"] = randomMAC # NOTE : passing function reference

        image_config.instantiate_config(template_map)
        
        # instantiate vm_config with image config
        vm_config.instantiate_config(template_map)

        if image_config is not None:
            vm_config.instantiate_config(image_config)
    except Exception, e:
        import traceback
        traceback.print_exc()
        raise e



def merge_pool_settings(vm_config,
                            image_config,
                            pool_settings,
                            append_missing=False):
        gconfig = {}

        for key in pool_settings:
            gconfig[key] = pool_settings[key]

        for key in vm_config:
            if key in gconfig:
                vm_config[key] = gconfig[key]
                del gconfig[key]

        for key in image_config:
            if key in gconfig:
                image_config[key] = gconfig[key]
                del gconfig[key]

        if append_missing is True:
            for key in gconfig:
                image_config[key] = gconfig[key]

def validateVMSettings(mode,managed_node,image_store,vm_name,memory,vcpus):
    errmsgs = []

    value = memory
    try:
        if memory is not None:
            value = int(value)
    except:
        errmsgs.append("Specify a proper integer value for the Memory.")
    value = vcpus
    try:
        if vcpus is not None:
            value = int(value)
    except:
        errmsgs.append("Specify a proper integer value for the VirtualCPUs.")
    if mode != "EDIT_IMAGE":
        if mode == "PROVISION_VM" and managed_node.is_resident(vm_name):
            errmsgs.append("Running VM with the same name exists.")

        if vm_name:
            x = vm_name
            if re.sub(image_store.VM_INVALID_CHARS_EXP,"", x) != x:
                errmsgs.append("VM name can not contain special chars %s" % image_store.VM_INVALID_CHARS)

    return errmsgs

def get_platform_count(ids=None):
    from convirt.model import DBSession,ManagedNode
    query = DBSession.query(ManagedNode.type,func.count(ManagedNode.id)).\
                group_by(ManagedNode.type)

    if ids is not None:
        query=query.filter(ManagedNode.id.in_(ids))
    result=query.all()
    return result

def get_host_os_info(ids=None):
    from convirt.model import DBSession,Instance
    query=DBSession.query(Instance.value,func.count(Instance.name)).\
                filter(Instance.name.in_([u'distro_string'])).filter(Instance.node_id!=None).\
                group_by(Instance.value)
    
    if ids is not None:
        query=query.filter(Instance.node_id.in_(ids))
    result=query.all()
    return result

def get_guest_os_info(ids=None):
    from convirt.model import DBSession
#    from convirt.model.ImageStore import Image
    from convirt.model.VM import VM
#    query=DBSession.query((Image.os_name+Image.os_version).label("os_string"),\
#                func.count("os_string")).\
#                filter(Image.id==VM.image_id).group_by("os_string")
    query=DBSession.query((VM.os_name+" "+VM.os_version).label("os_string"),\
                func.count("os_string")).\
                group_by("os_string")
    
    if ids is not None:
        query=query.filter(VM.id.in_(ids))
    result=query.all()

    return result

def get_string_status(value):
    ret_val=""
    if value==0:
        ret_val="no"
    elif value==1:
        ret_val="yes"
    else:
        ret_val="n/a"
    return ret_val

def update_vm_status():
    from convirt.model import DBSession
    from convirt.model.VM import VM
    import transaction
    doms=DBSession.query(VM).all()
    for dom in doms:
        if dom.status==constants.MIGRATING:
            print "changing status of VM ",dom.name," from ",constants.MIGRATING," to ''"
            dom.status=''
    
    transaction.commit()

def get_template_versions(image_id):
#    from sqlalchemy.orm import join
    from convirt.model import DBSession
    from convirt.model.ImageStore import Image
    result=[]
    if image_id is not None:
        query=DBSession.query(Image.version).\
             filter(Image.prev_version_imgid==image_id).\
             order_by(Image.version.asc())
    #
        result=query.all()
    return result

def node_up_action(auth, node_id):
    task_ids=[]
    try:
        from convirt.model import DBSession,Entity
        node_ent = DBSession.query(Entity).filter(Entity.entity_id == node_id).first()
        if node_ent:
            from convirt.viewModel.TaskCreator import TaskCreator
            tc = TaskCreator()
            tc.vm_availability(auth, node_id)
            vm_ids = [d.entity_id for d in node_ent.children]
            from convirt.model.VM import VM
            doms = DBSession.query(VM).filter(VM.id.in_(vm_ids)).all()
            for dom in doms:
                config = dom.get_config()
                if config and config.get("auto_start_vm")==1:
                    tid=tc.vm_action(auth, dom.id, node_id, constants.START)
                    task_ids.append(tid)
    except Exception, e:
        traceback.print_exc()

    return task_ids

def notify_node_down(node_name,reason):
    try:
        now = datetime.utcnow()
        subject =u"ConVirt : Server "+node_name+" not reachable"
        message ="\n<br/>CMS detected a server down. "
        message+="\n<br/>Server Name    : "+node_name
        message+="\n<br/>Detected At    : "+to_str(now)
        message+="\n<br/>Reason         : "+to_str(reason)
        
        #Send notification to all users
        send_user_notification(subject,message)

    except Exception, e:
        traceback.print_exc()
        LOGGER.error(e)

def notify_task_hung(task,node):
    try:
        LOGGER.info("Sending Task hung notification...")
        now = datetime.utcnow()
        subject =u"ConVirt : Task" +str(task.name)+" is hung"
        message ="\n<br/>Task "+str(task.name)+"("+str(task.task_id)+") is hung"
        message+="\n<br/>Host Name    : "+node.hostname
        message+="\n<br/>Time         : "+str(now)

        #Send notification to all users
        send_user_notification(subject,message)

    except Exception, e:
        traceback.print_exc()
        LOGGER.error(e)


def send_user_notification(subject,message):
    try:
        now = datetime.utcnow()
        from convirt.model import DeclarativeBase, DBSession,User
        from convirt.model.notification import Notification
        users=DBSession.query(User).all()
        for user in users:
            notifcn = Notification(None, \
                          None, \
                          now, \
                          to_unicode(message), \
                          user.user_name, \
                          user.email_address,\
                          subject)

            DBSession.add(notifcn)
    except Exception, e:
        traceback.print_exc()
        LOGGER.error(e)

def setup_deployment():
    from convirt.model import DBSession,Deployment
    import transaction
    
    deps=DBSession.query(Deployment).all()
    
    if len(deps) > 0:
        pass
    else:
        deployment=Deployment()
        guid=getHexID()
        deployment.deployment_id=guid
        deployment.version=to_unicode(constants._version)
        deployment.update_checked_date=datetime.utcnow()
        deployment.cms_deployed=datetime.utcnow()
        DBSession.add(deployment)
        transaction.commit()

    return []

def update_deployment_status():
    #setup_deployment()
    
    from convirt.model import DBSession,Deployment
    deps=DBSession.query(Deployment).all()
    
    if len(deps) > 0:
        try:
            from convirt.viewModel import Basic
            print "get CMS Host OS info"
            dir_loc = "/opt/convirt/common/scripts/"
            dist_script_file = "detect_distro.sh"
            src_script_file = os.path.join(dir_loc,dist_script_file)
            loc_node = Basic.getManagedNode()
            if not loc_node.node_proxy.file_exists(src_script_file):
                src_script_dir = os.path.abspath(tg.config.get('common_script'))
                src_script_file = os.path.join(src_script_dir,dist_script_file)
            (output, exit_code) = loc_node.node_proxy.exec_cmd(src_script_file, timeout=180)
            if exit_code == 0:
                distro_info=output.split(";version=")
                distro_name = distro_info[0].replace("name=","")
                distro_ver = distro_info[1].replace("\n","")
            else :
                distro_name = 'n/a'
                distro_ver = 'n/a'
            
            memory_values = get_mem_info(loc_node)
            cpu_values = get_cpu_info(loc_node)

            mem = float(memory_values.get(constants.key_memory_total))
            cpu = int(cpu_values.get(constants.key_cpu_count,1))
            soc = loc_node.get_socket_info()
            cor = cpu
            if soc :
                cor = cpu * soc
            
            ent_type_count={}
            ent_types=[to_unicode(constants.SERVER_POOL),to_unicode(constants.MANAGED_NODE),\
                to_unicode(constants.DOMAIN),to_unicode(constants.IMAGE_GROUP),to_unicode(constants.IMAGE)]
            from convirt.model import Entity,EntityType
            from convirt.model.auth import User
            from convirt.model.network import NwDef
            from convirt.model.storage import StorageDef
            from convirt.core.platforms.xen.XenNode import XenNode
            from convirt.core.platforms.kvm.KVMNode import KVMNode
            from convirt.model.ManagedNode import ManagedNode
            from convirt.model.VM import VM
            from convirt.core.platforms.xen.XenDomain import XenDomain
            from convirt.core.platforms.kvm.KVMDomain import KVMDomain

            result=DBSession.query(EntityType.name,func.count(Entity.name)).\
                join(Entity).group_by(EntityType.name).\
                filter(EntityType.name.in_(ent_types)).all()
            #print "\n\n\n",dict(result),"\n\n\n"
            dep=deps[0]
            ent_type_count=dict(result)

            if dep.max_sp < ent_type_count.get(constants.SERVER_POOL,0):
                dep.max_sp=ent_type_count.get(constants.SERVER_POOL)
            if dep.max_server < ent_type_count.get(constants.MANAGED_NODE,0):
                dep.max_server=ent_type_count.get(constants.MANAGED_NODE)
            if dep.max_vm < ent_type_count.get(constants.DOMAIN,0):
                dep.max_vm=ent_type_count.get(constants.DOMAIN)
            if dep.max_tg < ent_type_count.get(constants.IMAGE_GROUP,0):
                dep.max_tg=ent_type_count.get(constants.IMAGE_GROUP)
            if dep.max_template < ent_type_count.get(constants.IMAGE,0):
                dep.max_template=ent_type_count.get(constants.IMAGE)

            dep.sps = ent_type_count.get(constants.SERVER_POOL, 0)
            dep.templates = ent_type_count.get(constants.IMAGE, 0)

            x = DBSession.query(func.count(User.user_id)).all()
            dep.users = x[0][0]

            x = DBSession.query(func.count(NwDef.id)).all()
            dep.networks = x[0][0]

            x = DBSession.query(func.count(StorageDef.id)).all()
            dep.storages = x[0][0]

            x = DBSession.query(func.count(XenNode.id)).all()
            dep.xen_server = x[0][0]

            x = DBSession.query(func.count(KVMNode.id)).all()
            dep.kvm_server = x[0][0]

            x = DBSession.query(func.count(VM.id)).all()
            dep.vms = x[0][0]

            x = DBSession.query(func.count(XenDomain.id)).all()
            dep.xen_vms = x[0][0]

            x = DBSession.query(func.count(KVMDomain.id)).all()
            dep.kvm_vms = x[0][0]

            nodes = DBSession.query(ManagedNode).all()
            tot_sockets = 0
            tot_cores = 0
            tot_mem = 0
            for n in nodes:
                cpu = 1
                mem1 = 0
                tot_sockets += n.socket
                try:
                    cpu = n.get_cpu_db()
                    mem1 = n.get_mem_db()
                except Exception, e:
                    print "Error getting cpu/mem info for node "+n.hostname
                    import traceback
                    traceback.print_exc()

                tot_cores += (cpu * n.socket)
                tot_mem += mem1

            dep.tot_sockets = tot_sockets
            dep.tot_cores = tot_cores
            dep.tot_mem = tot_mem

            dep.distro_name = to_unicode(distro_name)
            dep.distro_ver = to_unicode(distro_ver)
            dep.host_mem = mem
            dep.host_cores = cor
            dep.host_sockets = soc

            DBSession.add(dep)
        except Exception, e :
            import traceback
            traceback.print_exc()

def get_cpu_info(mgd_node):
    cpu_attributes = [constants.key_cpu_count,constants.key_cpu_vendor_id,constants.key_cpu_model_name, constants.key_cpu_mhz]
    cpu_values = mgd_node.node_proxy.exec_cmd( \
                'cat /proc/cpuinfo | grep "processor" | wc -l;' +
                'cat /proc/cpuinfo | grep "vendor*" | head -1 | cut -d\':\' -f2;' +
                'cat /proc/cpuinfo | grep "model na*" | head -1 | cut -d\':\' -f2;' +
                'cat /proc/cpuinfo | grep "cpu MHz*" | head -1 | cut -d\':\' -f2;'\
                )[0].split('\n')[:-1]
    cpu_dict = dict((cpu_attributes[x],cpu_values[x]) \
                           for x in range(len(cpu_attributes)))
    cpu_dict[constants.key_cpu_count] = int(cpu_dict[constants.key_cpu_count])
    return cpu_dict

def get_mem_info(mgd_node):
    memory_attributes = [constants.key_memory_total,constants.key_memory_free]
    memory_values = []    
    memory_values = mgd_node.node_proxy.exec_cmd( \
            'cat /proc/meminfo | grep "Mem*" | cut -d\':\' -f2'\
            )[0].split('\n')[:-1]

    memory_values = [ int(re.search('(\d+)(\s+)(\S+)', v.strip()).group(1))/ 1000 \
                      for v in memory_values ]
    memory_dict = dict((memory_attributes[x],memory_values[x]) \
                       for x in range(len(memory_attributes)))

    return memory_dict

def add_deployment_stats_task():
    from convirt.viewModel.TaskCreator import TaskCreator
    TaskCreator().send_deployment_stats()

def send_deployment_stats(cms_strt):
    if is_dev_deployment():
        print "development deployment"
        return
        
    from convirt.model import DBSession,Deployment
    from datetime import datetime

    try:
        url = "http://www.convirture.com/deployments/deployment_stats.php"
        dep=DBSession.query(Deployment).first()
        
        if dep :
            end = ""
            nw = datetime.utcnow()
            cms_started=nw
            cms_deployed=nw

            if not dep.distro_name:
                #this is the first time cms is starting
                #cms host info is not populated
                #call the update deployment_stats to update the deployment data frame
                try:
                    update_deployment_status()
                except Exception, e:
                    print "Error updating deployment data",e
            if dep.cms_end:
                end = dep.cms_end
            if dep.cms_started:
                cms_started = dep.cms_started
            else :
                #cms is started for first time. no end time
                end = ""
            if dep.cms_deployed:
                cms_deployed = dep.cms_deployed
            if not cms_strt:
                # periodic update. do not send end time
                end = "";

            distro_name = distro_ver = "n/a"
            if dep.distro_name:
                distro_name=to_str(dep.distro_name)
            if dep.distro_ver:
                distro_ver=to_str(dep.distro_ver)
            data = urllib.urlencode({'sps' : to_str(dep.sps),
                         'vms'          : to_str(dep.vms),
                         'templates'    : to_str(dep.templates),
                         'users'        : to_str(dep.users),
                         'networks'     : to_str(dep.networks),
                         'storages'     : to_str(dep.storages),
                         'xen_server'   : to_str(dep.xen_server),
                         'kvm_server'   : to_str(dep.kvm_server),
                         'cms_started'  : to_str(cms_started),
                         'cms_deployed' : to_str(cms_deployed),
                         'cms_end'      : to_str(end),
                         'cms_current'  : to_str(nw),
                         'version'      : to_str(dep.version)+"_OSS",
                         'dep_id'       : to_str(dep.deployment_id),
                         'distro_name'  : distro_name,
                         'distro_ver'   : distro_ver,
                         'tot_sockets'  : to_str(dep.tot_sockets),
                         'tot_cores'    : to_str(dep.tot_cores),
                         'tot_mem'      : to_str(dep.tot_mem),
                         'host_sockets' : to_str(dep.host_sockets),
                         'host_cores'   : to_str(dep.host_cores),
                         'host_mem'     : to_str(dep.host_mem),
                         'xen_vms'          : to_str(dep.xen_vms),
                         'kvm_vms'          : to_str(dep.kvm_vms),
                         'current_version'  : to_str(constants._version)+"_OSS"
                         })
        response = connect_url(url,data=data)
        print response
    except Exception, e :
        import traceback
        traceback.print_exc()
        
    try:    
        dep=DBSession.query(Deployment).first()
        if dep and cms_strt:
            if not dep.cms_deployed:
                dep.cms_deployed = datetime.utcnow()
            dep.cms_started = datetime.utcnow()
            DBSession.add(dep)
            import transaction
            transaction.commit()
    except Exception, e :
        import traceback
        traceback.print_exc()

def set_registered(auth):
    from convirt.model.TopCache import TopCache
    from convirt.controllers.ControllerImpl import ControllerImpl
    from convirt.model import DBSession,Deployment
    dep=DBSession.query(Deployment).first()
    if dep:
        dep.registered=True
        DBSession.add(dep)

def is_dev_deployment():
    imgstr_dir = tg.config.get(constants.prop_image_store, "")
    if imgstr_dir:
        top_dir = os.path.abspath(os.path.join(imgstr_dir, os.path.pardir))
        return os.path.isdir(top_dir+"/.svn")
    return False

def storage_stats_data_upgrade():
    try:
        from convirt.model.storage import StorageManager
        StorageManager().storage_stats_data_upgrade()
    except Exception, ex:
        import traceback
        traceback.print_exc()
        raise ex

def unreserve_disks_on_cms_start():
    try:
        from convirt.viewModel import Basic
        grid_manager = Basic.getGridManager()
        grid_manager.unreserve_disks_on_cms_start()
    except Exception, ex:
        import traceback
        traceback.print_exc()
        raise ex
    
def setup_ssh_keys(node,local_node):

    try:
        ssh_key_file=tg.config.get(constants.ssh_file)

        if ssh_key_file is None:
            ssh_key_file="~/.ssh/id_rsa"
        ssh_key_file=os.path.expanduser(ssh_key_file)
        #print "\n\n=ssh_key_file=",ssh_key_file

        key=""
        ssh_dir="/"+node.username+"/.ssh"
        ssh_file_exist=local_node.node_proxy.file_exists(ssh_key_file+".pub")
        if ssh_file_exist:
            ssh_key=None
            f = open(ssh_key_file+".pub")
            key=f.readline()
            if key and len(key) > 1:
               if key[-1] == '\n':
                 key = key[:-1]
               ssh_key=key.split(" ")

#            print "\n\n\n===ssh_key===",ssh_key[1]
            (retbuf, retcode)=local_node.node_proxy.exec_cmd("ssh-add -L | grep \""+ssh_key[1]+"\" ")
        #print "retcode==",retcode,"retbuf=",retbuf

            if retcode==0:
                LOGGER.info("key existing in ssh command")
                auth_key_file = os.path.join(ssh_dir, "authorized_keys")
                file_exist=node.node_proxy.file_exists(auth_key_file)
                retcode=None
                if file_exist:
                    # key existing or not
                    cmd="grep \""+key+"\" "+auth_key_file
                    (retbuf, retcode)=node.node_proxy.exec_cmd(cmd)
                    #print "\n\n\n\n\ncmd==",cmd
                    #print "retcode==",retcode,"retbuf=",retbuf

                if not file_exist or retcode ==1:
                    #print "\n\n\n\n\n\n",file_exist,"---",retcode
                    (retbuf, retcode)=node.node_proxy.exec_cmd ("umask 077; test -d ~/.ssh || mkdir ~/.ssh ; echo \""+key+"\"  >> "+auth_key_file )
                    if retcode ==0:
                        print "key added"
                        LOGGER.info("key added to the managed server")
        else:
            LOGGER.error("ssh key file "+ssh_key_file+" not found")
    except Exception ,ex:
        traceback.print_exc()
        err=to_str(ex).replace("'", " ")
        LOGGER.error(":"+err)


def process_value(value):

    if value is None or value=='':
        return value

    str_value=to_str(value)
    if str_value[0] in ["["]:
        temp=[]
        for val in value:
            temp.append(to_str(val))
        return temp
    elif str_value[0] in ["{"]:
        temp1={}
        for key in value:
            parts=to_str(value.get(key)).split(".")
            if to_str(value.get(key)).isdigit():
                temp1[to_str(key)]=int(value.get(key))
            elif len(parts)==2 and parts[0].isdigit() and parts[1].isdigit():
                temp1[to_str(key)]=float(value.get(key))
            else:
                temp1[to_str(key)]=to_str(value.get(key))
        return temp1
    else:
        return value
    
def get_config_text(config):
    str_config=""
    for name, value in config.iteritems():
        str_config+="%s = %s\n" % (name, repr(value))
    return str_config

class dummyStream:
	''' dummyStream behaves like a stream but does nothing. '''
	def __init__(self): pass
	def write(self,data): pass
	def read(self,data): pass
	def flush(self): pass
	def close(self): pass

def get_cms_stacktrace():
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("<br/><br/>\n# ThreadID: %s<br/>" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s<br/>' % (filename, lineno, name))
            if line:
                code.append("  %s<br/>" % (line.strip()))
    return ("\n".join(code)) 


def get_cms_stacktrace_fancy():
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    return highlight("\n".join(code), PythonLexer(), HtmlFormatter(
      full=False,
      # style="native",
      noclasses=True,
    ))

def get_product_edition():
    return constants._edition

def p_task_timing_start(logger, op, entities, log_level="INFO"):
    from convirt.model.services import TaskUtil
    tid = str(TaskUtil.get_task_context())
    now = datetime.now()
    if log_level=="INFO":
        logger.info("T:TID:E:TIMING::START  "+op+":"+tid+":"+str(entities)+" "+str(now))
    else:
        logger.debug("T:TID:E:TIMING::START  "+op+":"+tid+":"+str(entities)+" "+str(now))
    return (now,op,entities,tid,log_level)

def p_task_timing_end(logger, start_context, log_level="INFO"):
    now = datetime.now()
    delta = ""
    start = now
    entities = []
    tid = ""
    op = "unknown"
    if start_context:
       start = start_context[0]
       op = start_context[1]
       entities = start_context[2]
       tid = start_context[3]
       log_level = start_context[4]
    if start!=None:
        delta = str((now-start).seconds) + "." + ("000000" + str((now-start).microseconds))[-6:]

    if log_level=="INFO":
        logger.info("T:TID:E:TIMING::END  "+op+":"+tid+":"+str(entities)+" "+str(start)+" "+delta)
    else:
        logger.debug("T:TID:E:TIMING::END  "+op+":"+tid+":"+str(entities)+" "+str(start)+" "+delta)
    return (now,op,entities)

def p_timing_start(logger, op, entities=None, log_level="INFO"):
    now = datetime.now()

    t = threading.currentThread()
    tid = "?"
    if t.getName():
        tid = t.getName()

    if log_level=="INFO":
        logger.info("TIMING::START "+op+":"+tid+":"+str(entities)+": " +str(now))
    else:
        logger.debug("TIMING::START "+op+":"+tid+":"+str(entities)+": " +str(now))
    return (now,op,entities,log_level)

def p_timing_end(logger, start_context, print_entities=True, log_level="INFO"):
    now = datetime.now()

    t = threading.currentThread()
    tid = "?"
    if t.getName():
      tid = t.getName()

    delta = ""
    op = "unknown op"
    entities = None
    start=now
    if start_context:
       start = start_context[0]
       op = start_context[1]
       entities = start_context[2]
       log_level = start_context[3]

    if start!=None:
        delta = str((now-start).seconds) + "." + ("000000" + str((now-start).microseconds))[-6:]

    str_entities = ""
    if entities:
       str_entities = str(entities)

    msg = "TIMING::END "+op+":"+tid+":"+" "+": "+ str(start)+" "+delta
    if print_entities :
        msg = "TIMING::END "+op+":"+tid+":"+str_entities+": "+ str(start)+" "+delta

    if log_level=="INFO":
        logger.info(msg)
    else:
        logger.debug(msg)

    # return it so that it can be chained
    return (now, op, entities)


PROFILING = "profiling"
TIMING = "timing"
DEBUG = PROFILING
DEBUG_DIR = "debug"
PREFIX = "CMS"
#DEBUG = None
def performance_debug(type=None):
    """
        Decorator
    """
    def accept_method(method):
        """
        """
        def customize_method(*args, **kw):
            """
            """
#            print "Method: %s" %(method.__name__)
            prof_result = is_debug_enabled(PROFILING, function=method.__name__, category_lst=type)
            if prof_result.get("status", False):
                ##import modules cProfile, pstats and fcntl only when profiling is enabled
                import cProfile, pstats, fcntl
                prof = cProfile.Profile()
                prof.enable(subcalls=True, builtins=True)
                start_dt_time = datetime.now()
                start_tm = time.time()
                result = prof.runcall(method, *args, **kw)
                end_tm = time.time()
                total_tm = end_tm - start_tm
                if not os.path.exists(DEBUG_DIR):
                    os.mkdir(DEBUG_DIR)
                msg = "\n\n\n ################## %s ##################### \n\n" %(start_dt_time)
                msg += "\n\nURL : %s" %(tg.request.url)
                msg += "\n\nMethod:%s, Time Taken:%s, Start Time:%s, End Time:%s" %(method.__name__, total_tm, start_dt_time, datetime.now())
                fname = DEBUG_DIR+"/"+PREFIX+"_"+str(method.__name__)+".txt"
                stats = pstats.Stats(prof)
                pp = stats.strip_dirs().sort_stats(-1)
                try:
                    fp = open(fname, 'a')
                    fcntl.flock(fp, fcntl.LOCK_EX)
    #                print "File:%s locked" %(fname)
                    fp.write(msg)
                    pp.stream = fp
                    pp.print_stats()
                    fcntl.flock(fp, fcntl.LOCK_UN)
    #                print "File:%s lock released" %(fname)
                except Exception, ex:
                    LOGGER.error(ex)
                    pass
                finally:
                    fp.close()
            elif is_debug_enabled(TIMING).get("status", False):
                start_dt_time = datetime.now()
                start_tm = time.time()
                result = method(*args, **kw)
                end_tm = time.time()
                total_tm = end_tm - start_tm
                msg = "PERFDEBUG: Method:%s, Time Taken:%s, Start Time:%s, End Time:%s" %(method.__name__, total_tm, start_dt_time, datetime.now())
                LOGGER.info(msg)
            else:
                result = method(*args, **kw)
            return result
        return customize_method
    return accept_method


def is_debug_enabled(type, function=None, category_lst=None):
    """
        For check whether profiling or timing enabled

        {u'profiling': {'categories': [u'datacenter'],
                        'enable': True,
                        'functions': {u'data_center_info': {'status': True},
                                      u'server_pool_info': {'status': True}}},
         u'timing': {'enable': False}}

    """
    if not session.has_key("perf_debug_context") or not session["perf_debug_context"].has_key(type):
        return {"status":False, "mgs":""}
#    print "-------", session["perf_debug_context"]
    debug_type = session["perf_debug_context"][type]
    if not debug_type.get('enable'):
        return {"status":False, "mgs":""}
    if type == PROFILING and function:
        if category_lst:
            if isinstance(category_lst, str):
                category_lst = [category_lst]
            categories = debug_type.get("categories", [])
            if filter(lambda x: x in categories, category_lst):
                debug_functions = debug_type.get("functions")
                if debug_functions:
                    debug_func_dict = debug_functions.get(function)
                    if debug_func_dict:
                        ## Return status of fuction, if fuction exist in the session
                        return {"status":debug_func_dict.get("status"), "msg":""}
                ## Return true, if fuction not in the session
                return {"status":True, "mgs":""}

        ## excecute, if category_lst is None
        if not debug_type.has_key("functions"):
            return {"status":False, "mgs":""}
        debug_functions = debug_type.get("functions")
        debug_func_dict = debug_functions.get(function)
        if not debug_func_dict:
            return {"status":False, "mgs":""}
        return {"status":debug_func_dict.get("status"), "msg":""}
    return {"status":debug_type.get("enable"), "mgs":""}


from tg import session
DEBUG_TYPES = [PROFILING, TIMING]
BOOL_TYPES = {"TRUE":True, 'FALSE':False}
GET = "get"
SET = "set"
METHODS = [GET,SET]
def set_or_get_perf_debug(**kwargs):
    """
        For enable/disable profiling and timing
        For more info see http://127.0.0.1:8091/perf_debug
    """
    base_web_url = get_base_web_url()
    msg = ""
    if not kwargs:
        msg = """<h4> Current Status </h4>
                    <b>Profiling:</b> %s </br>
                    <b>Timing:</b> %s
              """%(is_debug_enabled(PROFILING).get("status"), is_debug_enabled(TIMING).get("status"))

        msg += """<h5>Profiling Usage</h5>
                Parameters: </br>
                type : Debugging type (profiling). </br>
                enable : To enable/disable profiling (true/false). </br>
                method : To set/get profiling at function level (set/get). </br>
                fun_name : Name of fucnction for which profiling to be enabled/disabled. </br>
                fun_enable : To enable/disable profiling for a perticular function (true/false). </br>
                category : To specify profiling category (DC_dashboard/SP_dashboard/SR_dashboard/VM_dashboard). </br>
                cat_enable : To enable category base profiling (true/false). </br> </br>

                <a href="%s/perf_debug?type=profiling&enable=true"> Enable Profiling:</a> </br> %s/perf_debug?type=profiling </br></br>
                <a href="%s/perf_debug?type=profiling&enable=false"> Disable Profiling:</a> </br>  %s/perf_debug?type=profiling&enable=false </br></br>
                Add method to session and enable profiling:</br>  %s/perf_debug?type=profiling&method=set&fun_name=dashboard_server_info </br></br>
                <a href="%s/perf_debug?type=profiling&category=DC_dashboard&cat_enable=true"> Enable profiling for DC dashboard:</a> </br>  %s/perf_debug?type=profiling&category=DC_dashboard&cat_enable=true </br></br>
                <a href="%s/perf_debug?type=profiling&method=get"> Get profiling status:</a> </br>  %s/perf_debug?type=profiling&method=get </br>
              """%(base_web_url, base_web_url, base_web_url, base_web_url, base_web_url, base_web_url, base_web_url, base_web_url, base_web_url)

        #Disable profiling for particular function:</br>  %s/perf_debug?type=profiling&method=set&fun_name=dashboard_server_info&fun_enable=Fasle </br></br>
        #Get profiling status of particular function:</br>  %s/perf_debug?type=profiling&method=get&fun_name=dashboard_server_info </br></br>
        msg +=  """<h5>Timing Usage</h5>
                Parameters: </br>
                type : Debugging type (profiling). </br>
                enable : To enable/disable profiling (true/false). </br> </br>

                <a href="%s/perf_debug?type=timing&enable=true"> Enable Timing:</a> </br>  %s/perf_debug?type=timing </br></br>
                <a href="%s/perf_debug?type=timing&enable=false"> Disable Timing:</a> </br>  %s/perf_debug?type=timing&enable=false </br></br>
              """ %(base_web_url, base_web_url, base_web_url, base_web_url)
        return msg
    type = kwargs.get("type")
    enable = kwargs.get("enable")
    method = kwargs.get("method")
    fun_name = kwargs.get("fun_name")
    fun_enable = kwargs.get("fun_enable", "True")
    category = kwargs.get("category")
    cat_enable = kwargs.get("cat_enable", 'True')


    if method:
        if method not in METHODS:
            msg = "value of 'method' should be %s" %(" or ".join(METHODS))
            return msg

    if type not in DEBUG_TYPES:
        msg = "value of 'type' should be %s" %(" or ".join(DEBUG_TYPES))
        return msg

    if not fun_enable.upper() in BOOL_TYPES:
        msg = "value of 'fun_enable' should be true or false,"
        return msg
    fun_enable = BOOL_TYPES.get(fun_enable.upper())

    ## Set/Get Session context ##
#    print "-----session-------", session
    if not session.has_key("perf_debug_context"):
        ##Create
        session["perf_debug_context"] = {}
    perf_debug_context = session["perf_debug_context"]
    if not perf_debug_context.has_key(type):
        ##Create
        perf_debug_context[type] = {}
    debug_type = perf_debug_context[type]

    if enable:
        if not enable.upper() in BOOL_TYPES:
            msg = "value of 'enable' should be true or false"
            return msg
        enable = BOOL_TYPES.get(enable.upper())
        debug_type["enable"] = enable
        msg += "<h4> Debugging Type:%s, Enabled:%s </h4> </br>" %(type, enable)

    if category:
        if not cat_enable.upper() in BOOL_TYPES:
            msg = "value of 'cat_enable' should be true or false"
            return msg
        cat_enable = BOOL_TYPES.get(cat_enable.upper())
        if not debug_type.has_key("categories"):
            debug_type["categories"] = []
        if cat_enable:
            ##add category
            if category not in debug_type["categories"]:
                debug_type["categories"].append(category)
            msg += "<h4> Debugging Type:%s, Enabled Category:%s </h4> </br>" %(type, category)
        else:
            ##Remove category
            try:
                debug_type["categories"].remove(category)
            except Exception, ex:
                LOGGER.error(ex)
                pass
            msg += "<h4> Debugging Type:%s, Disabled Category:%s </h4> </br>" %(type, category)

    if type == PROFILING:
        if method:
            if not debug_type.has_key("functions"):
                debug_type["functions"] = {}
            debug_functions_dict = debug_type.get("functions")
            if method == SET and fun_name:
                st = "Enabled"
#                print "----fun_enable-----", fun_enable, enable
                if not fun_enable:
                    st = "Disabled"
                debug_functions_dict.update({fun_name:{"status":fun_enable}})
                msg += "successfuly %s profliling of method %s" %(st, fun_name)
#                print "----debug_type---2----'", debug_type
            elif method == GET:
                if not debug_functions_dict:
                    msg += "Please add a function to enable/disable function level profiling"
                else:
                    if fun_name:
                            debug_fun_dict = debug_functions_dict.get(fun_name)
                            if debug_fun_dict:
                                msg += "method: %s, Status: %s" %(fun_name, debug_fun_dict.get("status"))
                            else:
                                msg += "method: %s not in the session" %(fun_name)
                    else:
                        msg += "<table> <tr> <td><u>Method</u></td><td><u>Profiling</u></td> <td><u>Action</u></td></tr>"
                        for f_name, fun_dict in debug_functions_dict.items():
                            fun_cur_sts = fun_dict.get("status")
                            action = "Enable"
                            if fun_cur_sts:
                                action = "Disable"
                            msg += """<tr> <td> %s </td> <td> <b> %s </b></td> <td><a href="%s/perf_debug?type=profiling&method=set&fun_name=%s&fun_enable=%s"> %s </a></td></tr>
                                   """ %(f_name, fun_cur_sts, base_web_url, f_name, not fun_cur_sts, action)
                        msg += "</table> "

                msg += """</br></br></br><b>Profiling Enabled Categories: </b> </br> %s """ %("</br>".join(debug_type.get("categories", [])))

    session.save()
    return msg


import pylons
def get_base_web_url():
    """
        get base url
        Example: http://127.0.0.1:8091 or https://127.0.0.1:8091
    """
    protocol = tg.config.get(constants.SERVER_PROTOCOL,"http")
    host = pylons.request.headers['Host']
    web_url = "%s://%s" %(protocol, host)
    msg = "base_web_url : %s" %(web_url)
#    print msg
    LOGGER.info(msg)
    return web_url


def get_edition_string():
    try:
        edition_string="ConVirt"
        return edition_string
    except Exception, e:
        print_traceback()
        raise e
def get_version():
    try:
       return constants._version
    except Exception, e:
        print_traceback()
        raise e
#########################
# SELF TEST
#########################

if __name__ == '__main__':

    REMOTE_HOST = '192.168.123.155'
    REMOTE_USER = 'root'
    REMOTE_PASSWD = ''

    REMOTE = False    
    
    local_node = Node(hostname=constants.LOCALHOST)
    if not REMOTE:
        remote_node = local_node  # for local-only testing
    else:        
        remote_node = Node(hostname=REMOTE_HOST,
                           username=REMOTE_USER,
                           password = REMOTE_PASSWD,
                           isRemote = True)    


    #
    # LVMProxy tests
    #
    lvm_local = LVMProxy(local_node)
    lvm_remote = LVMProxy(remote_node)
    lvm_remote = lvm_local

    print '\nLVMProxy interface test STARTING'
    for lvm in (lvm_local, lvm_remote):
        vgs =  lvm.listVolumeGroups()
        for g in vgs:
            print g
            print lvm.listLogicalVolumes(g)
            print '\t Creating test LV'
            lvm.createLogicalVolume('selfTest',0.1,g)
            print '\t Deleting test LV'
            lvm.removeLogicalVolume('selfTest',g)
    print 'LVMPRoxy interface test COMPLETED\n'


    #
    # XMConfig tests
    #    

    TEST_CONFIGFILE = '/foo/convirt.conf'
    
    print "\nXMConfig interface test STARTING\n"
    
    print 'LOCALHOST ...'
    config_local = XMConfig(local_node, searchfiles = [TEST_CONFIGFILE],
                            create_file=TEST_CONFIGFILE)    
    config_local.set(XMConfig.DEFAULT,'TEST_PROP','TEST_VAL')
    print "Default Property TEST_PROP:",config_local.getDefault('TEST_PROP')
    print "Default Sections:",config_local.sections()
    print "Known Hosts", config_local.getHosts()
    config_local2 = XMConfig(local_node, searchfiles = [TEST_CONFIGFILE])
    print "Default Property TEST_PROP:",config_local2.getDefault('test_prop')    
    local_node.remove(TEST_CONFIGFILE)

    print '\nREMOTE HOST ...'
    config_remote = XMConfig(remote_node, searchfiles = [TEST_CONFIGFILE],
                            create_file=TEST_CONFIGFILE)
    config_remote.setDefault('TEST_PROP','TEST_VAL')
    print "Default Property TEST_PROP:",config_remote.get(XMConfig.DEFAULT,'TEST_PROP')
    print "Default Sections:",config_remote.sections()
    print "Known Hosts", config_remote.getHosts()
    config_remote2 = XMConfig(remote_node, searchfiles = [TEST_CONFIGFILE])
    print "Default Property TEST_PROP:",config_remote2.getDefault('test_prop')
    remote_node.remove(TEST_CONFIGFILE)

    print "\nXMConfig interface test COMPLETED"


    #
    # ImageStore tests
    #

##    print "\nImageStore interface test STARTING\n"
##    config_local = XMConfig(local_node, searchfiles = [TEST_CONFIGFILE],
##                            create_file=TEST_CONFIGFILE)
##    store = ImageStore(config_local)
##    print store.list()
    

##     print "\nImageStore interface test STARTING\n"
##     config_local = XMConfig(local_node, searchfiles = [TEST_CONFIGFILE],
##                             create_file=TEST_CONFIGFILE)
##     store = ImageStore(config_local)
##     print store.list
    
##     store.addImage('test_image','/var/cache/convirt/vmlinuz.default','/var/cache/convirt/initrd.img.default')
##     print store.list
##     print store.getImage('test_image')
##     print store.getFilenames('test_image')

##     #store.addImage('test_image2',
##     #               'http://linux.nssl.noaa.gov/fedora/core/5/i386/os/images/xen/vmlinuz',
##     #               'http://linux.nssl.noaa.gov/fedora/core/5/i386/os/images/xen/initrd.img',
##     #               )
##     #print store.list
##     #print store.getImage('test_image2')
##     #print store.getFilenames('test_image2')

##     store.addImage('test_image2',
##                    'http://localhost/fedora/images/xen/vmlinuz',
##                    'http://localhost/fedora/images/xen/initrd.img',
##                    )
##     print store.list
##     print store.getImage('test_image2')
##     print "First access, should fetch ...\n",store.getFilenames('test_image2')
##     print "Second access, should get from cache ... "
##     kernel, ramdisk = store.getFilenames('test_image2')
##     print (kernel, ramdisk)
##     local_node.remove(kernel)
##     local_node.remove(ramdisk)
##     local_node.rmdir('/var/cache/convirt/test_image2')
    
##     local_node.remove(TEST_CONFIGFILE)
    
    print "\nImageStore interface test COMPLETED"
    sys.exit(0)
    
    
    
        
