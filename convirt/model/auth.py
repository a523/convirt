#   ConVirt   -  Copyright (c) 2009 Convirture Corp.
#   ======
#
# ConVirt is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at
#
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
#
#
# author : ConVirt Team
#
# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.

It's perfectly fine to re-use this definition in the convirt application,
though.

"""
import os
from datetime import datetime
import sys
try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: No module named hashlib\n'
             'If you are on python2.4 this library is not part of python. '
             'Please install it. Example: easy_install hashlib')

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime,String,Boolean
from sqlalchemy.orm import relation, synonym
from sqlalchemy.schema import Index

from convirt.model import DeclarativeBase, metadata, DBSession

from convirt.model.DBHelper import DBHelper
from convirt.model.Operation import Operation
from convirt.model.Entity import Entity,EntityType


__all__ = ['User', 'Group', 'Permission']

#{ Association tables


# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permissions.permission_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('users.user_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)


#{ The auth* model itself


class Group(DeclarativeBase):
    """
    Group definition for :mod:`repoze.what`.
    
    Only the ``group_name`` column is required by :mod:`repoze.what`.
    
    """
    
    __tablename__ = 'groups'
    
    #{ Columns
    
    group_id = Column(Integer, autoincrement=True, primary_key=True)
    
    group_name = Column(Unicode(255), unique=True, nullable=False)
    
    display_name = Column(Unicode(255))
    
    created_by=Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by=Column(Unicode(255))
    modified_date= Column(DateTime,default=datetime.now)
    description=Column(Unicode(50))
    
    #{ Relations
    
    users = relation('User', secondary=user_group_table, backref='groups')    

    @classmethod
    def by_group_name(cls, group_name):
        """Return the group object whose group_name is ``group_name``."""
        return DBSession.query(cls).filter(cls.group_name==group_name).first()

    #{ Special methods
    
    def __repr__(self):
        return '<Group: name=%s>' % self.group_name
    
    def __unicode__(self):
        return self.group_name
    
    #}

Index('grp_name',Group.group_name)
# The 'info' argument we're passing to the email_address and password columns
# contain metadata that Rum (http://python-rum.org/) can use generate an
# admin interface for your models.
class User(DeclarativeBase):
    """
    User definition.
    
    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.
    
    """
    __tablename__ = 'users'
    
    #{ Columns

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    firstname=Column(Unicode(50),nullable=False)

    lastname=Column(Unicode(50),nullable=False)

    phone_number=Column(Unicode(20))

    status=Column(Boolean,default=True)
    
    user_name = Column(Unicode(255), unique=True, nullable=False)
    
    email_address = Column(Unicode(255), unique=True, nullable=False,
                           info={'rum': {'field':'Email'}})
    
    display_name = Column(Unicode(255))
    
    _password = Column('password', Unicode(80),
                       info={'rum': {'field':'Password'}})
    created_by=Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by=Column(Unicode(255))
    modified_date= Column(DateTime,default=datetime.now)

    
    #{ Special methods

    def __repr__(self):
        return '<User: email="%s", display name="%s">' % (
                self.email_address, self.display_name)

    def __unicode__(self):
        return self.display_name or self.user_name
    
    #{ Getters and setters

    @property
    def permissions(self):
        """Return a set of strings for the permissions granted."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    @classmethod
    def by_email_address(cls, email):
        """Return the user object whose email address is ``email``."""
        return DBSession.query(cls).filter(cls.email_address==email).first()

    @classmethod
    def by_user_name(cls, username):
        """Return the user object whose user name is ``username``."""
        return DBSession.query(cls).filter(cls.user_name==username).first()

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        hashed_password = password
        
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        # Make sure the hashed password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # columns
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self._password = hashed_password

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym('_password', descriptor=property(_get_password,_set_password))
    
    #}
    
    def validate_password(self, password):
        """
        Check the password against existing credentials.
        
        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool

        """
        hashed_pass = sha1()
        hashed_pass.update(password + self.password[:40])
        return self.password[40:] == hashed_pass.hexdigest()    

    def has_group(self,grp):
        for g in self.groups:
            if g.group_name==grp.group_name:
                return True
        return False
    
Index('usr_uname',User.user_name)

class Permission(DeclarativeBase):
    """
    Permission definition for :mod:`repoze.what`.
    
    Only the ``permission_name`` column is required by :mod:`repoze.what`.
    
    """
    
    __tablename__ = 'permissions'
    
    #{ Columns

    permission_id = Column(Integer, autoincrement=True, primary_key=True)
    
    permission_name = Column(Unicode(16), unique=True, nullable=False)
    
    description = Column(Unicode(255))
    
    #{ Relations
    
    groups = relation(Group, secondary=group_permission_table,
                      backref='permissions')
    
    #{ Special methods
    
    def __repr__(self):
        return '<Permission: name=%s>' % self.permission_name

    def __unicode__(self):
        return self.permission_name
    
    #}

