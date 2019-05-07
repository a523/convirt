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

from repoze.what.predicates import Predicate
from tg import request,session

from convirt.model.auth import User
from convirt.model.DBHelper import DBHelper

class is_user(Predicate):
    message = 'The current user must be %(user_id)s.'

    def __init__(self, userid, **kwargs):
        self.user_id=userid
        super(is_user, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):
        if not request.identity:
            self.unmet()
        userid = request.identity['repoze.who.userid']
        if userid!=self.user_id:
            self.unmet()

class authenticate(Predicate):
    message = 'SessionExpired.'

    def __init__(self,  **kwargs):
        super(authenticate, self).__init__(**kwargs)

    def evaluate(self, environ, credentials):
        if session.get('userid') is None:
            self.unmet()
