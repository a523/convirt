# EmailService.py
#
#   This module contains code to send email to the requested user
#
from convirt.core.utils.utils import constants,getHexID
from convirt.core.utils.utils import to_unicode,to_str
import convirt.core.utils.constants
constants = convirt.core.utils.constants
import traceback
from convirt.model import DBSession
from convirt.model.EmailSetup import EmailSetup
from convirt.model.Sites import Site
from datetime import datetime, date
import smtplib
from convirt.core.utils import ssmtplib
from email.MIMEText import MIMEText
from tg import session
from convirt.model.auth import User
import time
from convirt.model.Credential import Credential
from convirt.model.Entity import Entity, EntityType
from convirt.model.EmailManager import EmailManager
import transaction
import logging
LOGGER = logging.getLogger("convirt.model")

NONSECURE= 1
TLS = 2
SSL = 3

def ct_time():
    return datetime.utcnow().ctime()

class EmailService:
    def __init__(self):
        self.sender = None
        self.receivers = None
        self.message = "Test Message"
        self.mail_server = None
        self.port = None
        self.description = None
        self.secure_type = None
        self.text_subtype = 'plain'
        self.content="\Test message Send on " + to_str(ct_time())
        self.msg = MIMEText(self.content, self.text_subtype)
        self.subject = 'Test'
        self.msg['Subject']= self.subject

    # API to save EmailSetup dialog entries into the EmailSetup/Credentials table
    def save_email_setup_details(self, desc, servername, port, useremail, password, secure):
        SiteRecord = DBSession.query(Site).filter(Site.name == 'Data Center').first()
        if SiteRecord:
            site_id = SiteRecord.id
            # check if record for same server name avoid duplicate records of same name
            EmailRecord =  DBSession.query(EmailSetup).filter(EmailSetup.site_id == site_id).filter(EmailSetup.mail_server == servername).first()
            if EmailRecord:
                return dict(success=True,msg="Duplicaate Record found in list")

            else:
                # Add record in EmailSetup table for site id queried
                email_setup_obj = EmailSetup(servername, desc, port, secure, site_id, useremail, password )
                DBSession.add(email_setup_obj)
                emailsetupid = email_setup_obj.getEmailSetupId()
                EmailManager().add_entity(to_unicode(servername), emailsetupid, to_unicode(constants.EMAIL), None)
                return dict(success=True, msg="New Record Added Sucessfully")

    # API to update EmailSetup dialog entries into the EmailSetup/Credentials table
    def update_email_setup_details(self, desc, servername, port, useremail, password, secure):
        emaildetails = DBSession.query(EmailSetup).filter(EmailSetup.mail_server== servername).first()
        if emaildetails:
            emaildetails.description = desc
            emaildetails.port = port
            emaildetails.use_secure = secure
            emaildetails.credential.cred_details['user_email'] = useremail
            emaildetails.credential.cred_details['password'] = password
            return dict(success=True, msg="Record updated sucessfully")
        else:
            return dict(success=False, msg="Record updation failed")

    # Apis invoked from Email Setup dialog to send test mail with entries made
    # in the dialog.
    def send_test_email(self, desc, servername, port, useremail, password, secure):
        self.sender = useremail
        Record = DBSession.query(User.email_address).filter(User.user_name =='admin').first()
        self.receivers =Record.email_address

        self.mail_server = servername
        if port:
            self.port = int(port)
        self.secure_type = int(secure)
        self.password = password
        self.subject = "Test Email"
        self.content="\Test message Sent on " + to_str(ct_time())
        self.msg = MIMEText(self.content, self.text_subtype)
        self.msg['Subject']= "ConVirt Test Email"
        
#        SendSuccess = False
        try:
            if (self.secure_type== NONSECURE):
                EmailManager().send_nonsecure(servername,self.port,useremail,Record.email_address,self.msg.as_string())
            elif (self.secure_type== TLS):
                EmailManager().send_tls(servername,self.port,useremail,password,Record.email_address,self.msg.as_string())
            else:
                EmailManager().send_ssl(servername,self.port,useremail,password,Record.email_address,self.msg.as_string())
        except Exception, ex:
#            traceback.print_exc()
            LOGGER.error("Error sending mails:"+to_str(ex).replace("'",""))
            raise ex

        message = "mail send to " + Record.email_address
        return message

#        if (SendSuccess== True):
#            message = "mail send to " + Record.email_address
#            return message
#        else:
#            message = "Test Failed"
#            return message

    # Test all server connection by sending the mail
    def get_mailservers(self):
        try:
            MailSetupRecord=EmailManager().get_mailservers()
            return MailSetupRecord
        except Exception, e:
            raise e

    def send_email_to_client(self, msg, receiver):
        # Query sender and password from email credential table
        # Query mail_server,port,use_secure from the email setup table for curenly  logged in user
        self.receivers = receiver
        self.content=msg

        emailservers = self.get_mailservers()
        for eachmailserver in emailservers:
            if eachmailserver:
                self.mail_server = eachmailserver['MailSetup'].mail_server
                self.port = int(eachmailserver['MailSetup'].port)
                self.secure_type = int(eachmailserver['MailSetup'].use_secure)
                self.cred_details = eachmailserver['Creds'].cred_details
                self.password = self.cred_details['password']
                self.sender = self.cred_details['user_email']
                result = False

                if (self.secure_type== NONSECURE):
                    result = EmailManager().send_nonsecure(self.mail_server,self.port,self.sender,receiver,msg)
                elif (self.secure_type== TLS):
                    result = EmailManager().send_tls(self.mail_server,self.port,self.sender,self.password,receiver,msg)
                else:
                    result = EmailManager().send_ssl(self.mail_server,self.port,self.sender,self.password,receiver,msg)

                if (result == True):
                    return "Test mail sent from " + eachmailserver['MailSetup'].mail_server

    def send_email_to_user(self, msg):
        # Query sender and password from email credential table
        # Query mail_server,port,use_secure from the email setup table for curenly  logged in user
        # receiver: to be queried from users table
        self.msg = msg
        curr_user_id = session.get('userid')
        #query users table to retrieve email address of currenlt logged in user
        userRecord = DBSession.query(User.email_address).filter(User.user_name == curr_user_id).first()
        if userRecord:
            self.receivers = userRecord.email_address
        emailservers = self.get_mailservers()
        for eachmailserver in emailservers:
            if eachmailserver:
                self.mail_server = eachmailserver['MailSetup'].mail_server
                self.port = int(eachmailserver['MailSetup'].port)
                self.secure_type = int(eachmailserver['MailSetup'].use_secure)
                self.cred_details = eachmailserver['Creds'].cred_details
                self.password = self.cred_details['password']
                self.sender = self.cred_details['user_email']
                result = False
                if (self.secure_type== NONSECURE):
                    result = EmailManager().send_nonsecure(self.mail_server,self.port,self.sender,self.receivers,msg)
                elif (self.secure_type== TLS):
                    result = EmailManager().send_tls(self.mail_server,self.port,self.sender,self.password,self.receivers,msg)
                else:
                    result = EmailManager().send_ssl(self.mail_server,self.port,self.sender,self.password,self.receivers,msg)

                if (result == True):
                    return "Test mail sent from " + eachmailserver['MailSetup'].mail_server

    def get_emailsetupinfo(self):
        try:
            result=EmailManager().get_emailsetupinfo()
            return result
        except Exception, e:
            raise e

    def delete_emailrecord(self, emailsetup_id):
        try:
            EmailManager().delete_emailrecord(emailsetup_id)
        except Exception, e:
            raise e

    def get_emailsetup_details(self,emailsetup_id):
        try:
            result=None
            result= EmailManager().get_emailsetup_details(emailsetup_id)
        except Exception, e:
            raise e
        return result

