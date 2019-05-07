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

import paramiko
from paramiko import SSHException
import os, sys
import getpass
import socket
from convirt.core.utils.utils import to_unicode,to_str
"""Paramiko helper class. Provides common functions as
   -- validating host keys,
   -- initializing a new transport,
   -- agent based and password based authentication etc.
"""
class HostValidationException(Exception):
    def __init__(self, errno, description):
        Exception.__init__(self, errno, description)
        self.errno = errno
        self.description = description

    def __repr__(self):
        return "[Error %s], %s" % (self.errno, self.description)

    def __str__(self):
        return self.__repr__()

class AuthenticationException(Exception):
    def __init__(self, errno, description):
        Exception.__init__(self, errno, description)
        self.errno = errno
        self.description = description

    def __repr__(self):
        return "[Error %s], %s" % (self.errno, self.description)
    
    def __str__(self):
        return self.__repr__()


class CommunicationException(Exception):
    def __init__(self, errno, description):
        Exception.__init__(self, errno, description)
        self.errno = errno
        self.description = description

    def __repr__(self):
        return "[Error %s], %s" % (self.errno, self.description)

    def __str__(self):
        return self.__repr__()
    


class PHelper:
    
    host_keys = {}

    # credential helper
    credentials_helper = None

    ## The credendital helper needs to get_credentials(hostname) method
    ## to return credentials
    ## the object returned should:
    ##    get_username() and get_password() methods
    ## This would be used when the transport can not be initialized
    ## using given methods
    
    @classmethod
    def set_credentials_helper(cls, cred_helper):
        """ Set the helper class"""
        cls.credentials_helper = cred_helper

        
    @classmethod
    def load_keys(cls):
        # TODO : May be we need to load /etc/ssh/known_hosts and merge it here.
        try:
            path = os.path.expanduser('~/.ssh/known_hosts')
            cls.host_keys = paramiko.util.load_host_keys(path)
        except IOError:
            try:
                path = os.path.expanduser('~/ssh/known_hosts')
                cls.host_keys = paramiko.util.load_host_keys(path)
            except IOError:
                pass


    @classmethod
    def init_log(cls,log_file_name):
        try:
            paramiko.util.log_to_file(log_file_name)
        except Exception ,ex:
            print "Error initializing paramiko log.", ex


    @classmethod
    def validate_host_key(cls, transport, hostname):
        """
        get the remote hosts key and validate against known host keys
        throws exception with errno, reason
        errno - reason
        1  - Host not found
        2. - Host found but key not found
        3  - Authentication failed (wrong password?)
        4  - Host found, key found, but keys do not match
             (server changed/spoofed)
        """
        # check server's host key -- this is important.
        key = transport.get_remote_server_key()
        if not PHelper.host_keys.get(hostname):
            print "Warning : Host not found ! ", hostname
            #raise HostValidationException(1, "Host not found")
        elif not PHelper.host_keys[hostname].get(key.get_name()):
            print "Warning: Key not found ! ", hostname
            #raise HostValidationException(2, "Key not found.")
        elif PHelper.host_keys[hostname][key.get_name()] != key:
            raise HostValidationException(3, "Keys mismatch for " + hostname)
        
        return True


    ## TODO : only for testing purpose
    @classmethod        
    def interactive_auth(cls, transport, username, hostname):
        default_auth = 'p'
        auth = raw_input('Auth by (p)assword, (r)sa key, or (d)ss key? [%s] ' % default_auth)
        if len(auth) == 0:
            auth = default_auth

        if auth == 'r':
            default_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
            path = raw_input('RSA key [%s]: ' % default_path)
            if len(path) == 0:
                path = default_path
            try:
                key = paramiko.RSAKey.from_private_key_file(path)
            except paramiko.PasswordRequiredException:
                password = getpass.getpass('RSA key password: ')
                key = paramiko.RSAKey.from_private_key_file(path, password)
            transport.auth_publickey(username, key)
        elif auth == 'd':
            default_path = os.path.join(os.environ['HOME'], '.ssh', 'id_dsa')
            path = raw_input('DSS key [%s]: ' % default_path)
            if len(path) == 0:
                path = default_path
            try:
                key = paramiko.DSSKey.from_private_key_file(path)
            except paramiko.PasswordRequiredException:
                password = getpass.getpass('DSS key password: ')
                key = paramiko.DSSKey.from_private_key_file(path, password)
            transport.auth_publickey(username, key)
        else:
            pw = getpass.getpass('Password for %s@%s: ' % (username, hostname))
            transport.auth_password(username, pw)

    #TODO : refine this.. and test it with passphrase, may be catch
    #       some other exception, if passphrase is wrong.
    @classmethod
    def authenticate(cls, transport, authtype,
                     keyfile=None, passphrase=None,
                     username=None, password=None):

        default_authtype = 'password'

        if authtype==None or len(authtype) == 0:
            authtype = default_authtype

        try:
            if authtype == 'rsa':
                default_keyfile = os.path.join(os.environ['HOME'],
                                               '.ssh', 'id_rsa')
                if keyfile == None or len(keyfile) == 0:
                    keyfile = default_keyfile

                key = paramiko.RSAKey.from_private_key_file(keyfile,
                                                            passphrase)
            
            elif authtype == 'dsa':
                default_keyfile = os.path.join(os.environ['HOME'],
                                               '.ssh', 'id_dsa')

                if keyfile == None or len(keyfile) == 0:
                    keyfile = default_keyfile
                    key = paramiko.DSSKey.from_private_key_file(keyfile,
                                                                passphrase)
                    
            if authtype == 'rsa' or authtype == 'dsa':
                transport.auth_publickey(username, key)
            else:
                transport.auth_password(username, password)
            
        except paramiko.PasswordRequiredException, ex:
            raise AuthenticationException(1, "Password required")
        except paramiko.BadAuthenticationType, ex:
            raise AuthenticationException(2, "Bad authentication type")
        except paramiko.AuthenticationException, ex:
            raise AuthenticationException(3, "Authentication failed.")
        except paramiko.SSHException ,ex:
            raise AuthenticationException(4,
                                          "Invalid key file %s" % keyfile)

    @classmethod
    def agent_auth(cls, transport, username):
        """
        Attempt to authenticate to the given transport using any of the private
        keys available from an SSH agent.
        return True, if the transport is authenticated
        raises: AuthenticationException when network errro
        """

        agent = paramiko.Agent()
        agent_keys = agent.get_keys()
        if len(agent_keys) == 0:
            #print "Warning: No keys found loaded in ssh-agent. Forgot to use ssh-add ?"
            return

        for key in agent_keys:
            #print 'Trying ssh-agent key %s' % \
            #      paramiko.util.hexify(key.get_fingerprint()),
            try:
                transport.auth_publickey(username, key)
                if not transport.is_authenticated():
                    continue
                else:
                    break
            except paramiko.AuthenticationException, e:
                print "Used key from agent. Auth failed. Will skip it."
                pass
            except SSHException, ex:
                raise CommunicationException(0, "[agent_auth]:" + to_str(ex))
                
            
    @classmethod        
    def init_ssh_transport(cls, hostname, ssh_port=22,
                           authtype=None, keyfile=None,passphrase=None,
                           username=None, password=None):

        try:
            ### Open SSH transport
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #
            #TODO timeout value should be configurable from server pool
            #
            sock.settimeout(1)
            sock.connect((to_str(hostname), ssh_port)) 

            transport  = paramiko.Transport(sock)
            transport.start_client()

            # validate the host key
            cls.validate_host_key(transport, hostname)


            # if username and password provided assume it is password
            # type authentication
            if not transport.is_authenticated() and authtype == None:
                if username != None and password != None:
                    try:
                        cls.authenticate(transport,'password',
                                         keyfile,passphrase,
                                         username, password)
                    except AuthenticationException ,ex:
                        if ex.errno == 3 and cls.credentials_helper is not None:
                            # give a chance to cred helper to prompt
                            pass
                        else:
                            transport.close()
                            raise
                        


            ## authenticate with the auth type provided.
            if not transport.is_authenticated() and authtype != None:
                try:
                    if authtype == "agent":
                        cls.agent_auth(transport, username)
                        if not transport.is_authenticated():
                            raise AuthenticationException(0,"Agent authentication failed")
                        
                    else:
                        cls.authenticate(transport,authtype, keyfile,passphrase,
                                         username, password)
                    
                except AuthenticationException ,ex:
                    if authtype == 'password' and \
                           ex.errno == 3 and \
                           cls.credentials_helper is not None:
                        # give a chance to cred helper to prompt
                        pass
                    else:
                        transport.close()
                        raise
                        

            # authenticate interactive way. just for testing
            #if not transport.is_authenticated():
            #    cls.interactive_auth(transport, username, hostname)

            if not transport.is_authenticated() and \
                   cls.credentials_helper is not None:
                creds = cls.credentials_helper.get_credentials(hostname)
                if creds is not None:
                    username = creds.get_username()
                    password = creds.get_password()
                    cls.authenticate(transport,'password',
                                     keyfile,passphrase,
                                     username, password)


            if not transport.is_authenticated():
                transport.close()
                raise AuthenticationException("0",
                                            hostname + " is not authenticated")
            return transport

        except socket.timeout : # clients may wish to treat this differently
            raise
        except socket.error, ex:
            raise CommunicationException(0, to_str(ex))
            


    ## pass through method
    @classmethod
    def open_channel(cls,transport, kind, dest_addr=None, src_addr=None):
        try:
            ch = transport.open_channel(kind, dest_addr, src_addr)
        except SSHException, ex:
            raise CommunicationException(0, "[open_channel]" +to_str(ex))
        return ch
    
    
# initialize key store
PHelper.load_keys()

#TODO : Add some test cases here.
if __name__ == "__main__":
    host = "192.168.12.100"
    
    #Test with passphrase
##     t = PHelper.init_ssh_transport(host,
##                                    authtype="rsa", passphrase="welcome",
##                                    username = "root")
    # Test with ssh-agent
    t = PHelper.init_ssh_transport(host, username="root", authtype="agent")
    ch = PHelper.open_channel(t, "session")
    ch.close()

