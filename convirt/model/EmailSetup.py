# -*- coding: utf-8 -*-
"""Sample model module."""

#from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, PickleType
from sqlalchemy.types import Integer, Unicode, Boolean, String
from convirt.core.utils.utils import constants,getHexID
from convirt.core.utils.utils import to_unicode,to_str
from convirt.model import DeclarativeBase, metadata, DBSession
from convirt.model.DBHelper import DBHelper
from convirt.model.Credential import Credential


class EmailSetup(DeclarativeBase):
    __tablename__ = 'emailsetup'
    id = Column(Unicode(50), primary_key=True)
    mail_server=Column(Unicode(255))
    description=Column(String(200))
    port = Column(Integer)    
    use_secure = Column(Integer) #No, TLS, SSL
    site_id = Column(Unicode(50), ForeignKey('sites.id',onupdate="CASCADE", ondelete="CASCADE"))
    credential=relation(Credential, \
                    primaryjoin=id == Credential.entity_id,\
                    foreign_keys=[Credential.entity_id],\
                    uselist=False,cascade='all, delete, delete-orphan') 

    def __repr__(self):
        return '<EmailSetup: mail_server=%s>' % self.mail_server
    
    def __init__(self,mail_server,desc, port, use_secure, site_id, useremail, password):
        self.id = getHexID()
        self.mail_server = to_unicode(mail_server)
        self.description=desc
        self.port = port
        self.use_secure = use_secure
        self.site_id = site_id
        self.credential=Credential(self.id,u"",user_email = useremail, password = password)

    def getEmailSetupId(self):
        return self.id

