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

from  httplib import HTTPConnection, HTTP
from  xmlrpclib import Transport,SafeTransport, _Method

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpclib, socket, os, stat
import SocketServer
from convirt.core.utils.utils import to_unicode,to_str


import xen.xend.XendClient
from xen.xend.XendLogging import log

from convirt.model.VM import VMOperationException

try:
   from xen.util.xmlrpcclient import ServerProxy
   base_pkg = xen.util.xmlrpcclient
except ImportError,e:
   from xen.util.xmlrpclib2 import ServerProxy
   base_pkg = xen.util.xmlrpclib2
   

#### Got this from Xen 3.1 stack so we can do SSL from Xen 3.0 stack too.
      
# We need our own transport for HTTPS, because xmlrpclib.SafeTransport is
# broken -- it does not handle ERROR_ZERO_RETURN properly.
class XenHTTPSTransport(xmlrpclib.SafeTransport):
    def _parse_response(self, file, sock):
        p, u = self.getparser()
        while 1:
            try:
                if sock:
                    response = sock.recv(1024)
                else:
                    response = file.read(1024)
            except socket.sslerror, exn:
                if exn[0] == socket.SSL_ERROR_ZERO_RETURN:
                    break
                raise
                
            if not response:
                break
            if self.verbose:
                print 'body:', repr(response)
            p.feed(response)
            
        file.close()
        p.close()
        return u.close()
###


from getpass import getuser

from convirt.core.utils.phelper import PHelper
import xml.parsers.expat

import re
# A new ServerProxy that also supports ssh tunneling using paramiko. 
# The ssh_tunnel URL comes in the
# form:
#
# ssh_tunnel://user@host:port/RPC2
#
# It assumes that the RPC handler is /RPC2.  
# This is implemented in a fashion similar to other transports in xmlrpcclient.
# Note : This one does not require corresponding server side implementation
#        as it uses the ssh tunneling mechanism. It would be nice though to
#        have another paramiko based server implemeted and shipped by Xen
#        to which we can directly connect.


##
## -- custom transports that allows setting timeout depeding on the method
## Very specific for now.
##

custom_timeouts = (("xend.domain.migrate",600),
                   ("xend.domain.restore", 600),
                   ("xend.domain.save", 600),
                   )
                  # ("xend.node.info", 25),)
def set_custom_timeout(connection, request_body):
   for m,to in custom_timeouts:
      if request_body.find("<methodName>%s</methodName>" % m) > -1:
         print "Setting custom timeout for ", m, to
         connection._conn.connect()
         connection._conn.sock.settimeout(to)
   

class CustomUnixTransport(base_pkg.UnixTransport):
   def send_request(self, connection, handler, request_body):
      set_custom_timeout(connection, request_body)
      base_pkg.UnixTransport.send_request(self, connection, handler,
                                          request_body)
   

class CustomTransport(Transport):
   def send_request(self, connection, handler, request_body):
      set_custom_timeout(connection, request_body)
      Transport.send_request(self, connection, handler,
                             request_body)

class CustomHTTPSTransport(XenHTTPSTransport):
   def send_request(self, connection, handler, request_body):
      set_custom_timeout(connection, request_body)
      XenHTTPSTransport.send_request(self, connection, handler,
                                     request_body)



DEFAULT_LOCAL_PORT_START = 2000
DEFAULT_LOCAL_PORT_END   = 2000

class SSHTunnelConnection(HTTPConnection):
   def set_ssh_transport(self, ssh_transport):
      self.ssh_transport = ssh_transport

   def set_local_port(self, localport):
      self.localport = localport

   def connect(self):
      # We already have a transport to the remote machine.
      # lets create a tunnel on the remote node to forward traffic from
      # localhost, localport  ==> localhost, xen port
      # (NOTE : localhost is interpreted on the remote node.)
      self.sock =  PHelper.open_channel(self.ssh_transport, "direct-tcpip",
                                        ("localhost",self.port),
                                        ("localhost",self.localport))

class SSHTunnel(HTTP):
   
    _connection_class = SSHTunnelConnection
    
    def __init__(self, ssh_transport, host='', port=None, strict=None,
                 localport=DEFAULT_LOCAL_PORT_START):
       self.localport = localport
       self.ssh_transport = ssh_transport
       HTTP.__init__(self, host, port, strict)

    # take this oppertunity to associate transport with the connection.
    def _setup(self, conn):
        HTTP._setup(self, conn)
        conn.set_ssh_transport(self.ssh_transport)
        conn.set_local_port(self.localport)
    


class SSHTunnelTransport(CustomTransport):

    current_local_port = DEFAULT_LOCAL_PORT_START
    _use_datetime = False
      
    def __init__(self,hostname,port,
                 ssh_transport=None,
                 ssh_port=22, 
                 user=None, password=None,
                 use_keys = False):
       """ constructor, takes in host and port to which the tunnel
           is to be opened. Assumes ssh on 22 for now.
           An already authenticated paramiko transport can be passed.
           It is assumed that the transport is to the same host as specified
           by hostname.
       """
       self.hostname = hostname
       self.ssh_port = ssh_port
       self.username = user
       self.password = password
       self.port = port
       self.transport_created=False
       self.use_keys = use_keys
       if ssh_transport == None:
          authtype = None
          pwd = self.password
          if self.use_keys:
             pwd = None
             authtype = "agent"

             
          self.transport = PHelper.init_ssh_transport(self.hostname,
                                                      self.ssh_port,
                                                      username=self.username,
                                                      password = pwd,
                                                      authtype = authtype)
          self.transport_created=True
       else:
          self.transport = ssh_transport

    # This does not seem necessary      
    #def request(self, host, handler, request_body, verbose=0):
    #    self.__handler = handler
    #    return CustomTransport.request(self, host, '/RPC2', request_body, verbose)

    def make_connection(self, host):
       """ return the connection paramiko connection object """
       SSHTunnelTransport.current_local_port += 1
       if SSHTunnelTransport.current_local_port >= DEFAULT_LOCAL_PORT_END:
          SSHTunnelTransport.current_local_port = DEFAULT_LOCAL_PORT_START
          
       return SSHTunnel(self.transport,host,
                        localport=SSHTunnelTransport.current_local_port)

    def close(self):
       """ clean up transport if we created it."""
       if self.transport != None and self.transport_created:
          self.transport.close()
            


## copied _Method from xmlrpc and 
class _Dispatcher:
  # some magic to bind an XML-RPC method to an RPC server.
  # supports "nested" methods (e.g. examples.getStateName)
  def __init__(self, orig_object, send, name):
     self.__send = send
     self.__name = name
     self.__orig_object = orig_object
  def __getattr__(self, name):
     return _Dispatcher(self.__orig_object,
                        self.__send, "%s.%s" % (self.__name, name))
  def __call__(self, *args):
     try:
        ret = self.__send(self.__name, args)
     except xmlrpclib.Fault, ex:
        raise VMOperationException(to_str(ex))
     except xml.parsers.expat.ExpatError, expat:
        #print "got expat error ", expat
        raise
     except Exception, ex1:
        #print "setting last_error", ex1
        self.__orig_object._last_error = ex1
        raise
     else:
        if self.__orig_object._last_error is not None:
           #print "resetting last_error"
           self.__orig_object._last_error = None

     return ret
  
## class _Dispatcher(xmlrpclib._Method):
##   def __init__(self, send, name):
##      xmlrpclib._Method.__init__(self, send, name)


##   def __getattr__(self, name):
##      return _Dispatcher(self.__send, "%s.%s" % (self.__name, name))
     
##   def __call__(self, *args):
##      print "intercepting actual call"
##      return xmlrpclib._Method.__call(self, *args)

      



# TODO : Improve parsing.. may be just used http url parsing code from
#        say httplib

class ServerProxy(base_pkg.ServerProxy):
   """ Class derives from  xen.util.xmlrpcclient and adds paramiko ssh_tunnel
       access to a remote Xen managed node
   """
   def __init__(self, uri, transport=None, encoding=None, verbose=0,
                allow_none=1,
                ssh_transport = None, # provide the transport
                ssh_port = 22, # or rest of the parm to create one.
                user=None,
                password=None,
                use_keys = False):

#      print "URI ", uri
      self.tunnel_transport = None
      self._last_error = None
      (protocol, rest) = uri.split(':', 1)

      ##if protocol == "ssh_tunnel":
      ##   self._dispatcher = _Dispatcher
      ##else:
      ##   self._dispatcher = _Method

      self._protocol = protocol # save as required by __getattr__
      
      #print protocol, rest
      if protocol == 'ssh_tunnel':
         #
         # create components for creating uri for the base class
         # 
         if not rest.startswith('//'):
             raise ValueError("Invalid SSHTunnel URL '%s'" % uri)
         rest = rest[2:]
         if user == None:
            user = getuser()
         port = "8005"
         path = 'RPC2'
         if rest.find('@') != -1:
             (user, rest) = rest.split('@', 1)
             #print "rest after user ", rest
         if rest.find(':') != -1:
             (host, rest) = rest.split(':',1)
             if rest.find('/') != -1:
                (port, rest) = rest.split('/', 1)
                if len(rest) > 0:
                   path = rest
         else:
            if rest.find('/') != -1:
               (host, rest) = rest.split('/', 1)
               if len(rest) > 0:
                  path = rest
            else:      
               host = rest

      # Create custom transport explicitly 
      if transport == None:
         (protocol, rest) = uri.split(':', 1)
         if protocol == 'httpu':
             uri = 'http:' + rest
             transport = CustomUnixTransport()
         elif protocol == 'https':
             transport = CustomHTTPSTransport()
         elif protocol == 'http':
             transport = CustomTransport()
         elif protocol == "ssh_tunnel":
            transport =  SSHTunnelTransport(host,
                                            port,
                                            ssh_transport,
                                            ssh_port,
                                            user=user,
                                            password = password,
                                            use_keys = use_keys)
            self.tunnel_transport = transport
            # adjust uri for base class
            uri = 'http://%s:%s/%s' % (host, port,path)

             
      # now call the base class with transport
      base_pkg.ServerProxy.__init__(self, uri,
                                    transport, encoding,
                                    verbose, allow_none)

   def get_last_error(self):
      return self._last_error

   ## see if this can be commented out. Too costly.
   ## think if recursive call can be avoided.
##    def __getattr__(self, name):
##       # magic method dispatcher
##       if name == "protocol":
##          return self._protocol
##       elif self.protocol == "ssh_tunnel":
##          return _Dispatcher(self, self.__request, name)
##       return _Method(self.__request, name)

   def __getattr__(self, name):
      return _Dispatcher(self, self.__request, name)

   def close(self):
      if self.tunnel_transport:
         self.tunnel_transport.close()
         self.tunnel_transport=None
