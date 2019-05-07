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
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# author : Jd <jd_jedi@users.sourceforge.net>

import pylons,logging,tg,os
from tg import expose, flash, require, url, request, redirect,response,session,config
import convirt.core.utils.constants
constants = convirt.core.utils.constants
LOGGER = logging.getLogger("convirt.controllers")

class ControllerBase:

    def authenticate(self, came_from=url('/')):
        if session.get('userid') is None:
            try:                
                self.redirect_to(url('login', came_from=came_from, __logins=0))
            except Exception, e:
                raise Exception("SessionExpired.")


    def redirect_to(self, url):
        try:
            protocol = tg.config.get(constants.SERVER_PROTOCOL,"http")
            host=pylons.request.headers['Host']            
            redirect(url, host=host, protocol=protocol)
        except Exception, e:
            raise e
