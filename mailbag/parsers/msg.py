from mailbag.parser import EmailFormatParser
from mailbag.emailModel import Email
import extract_msg

from jsonmodels import models, fields, errors, validators


class MSG(EmailFormatParser):
    """MSG - This concrete class parses msg file format"""
    parser_name = 'MSG'
 
    def parse(self, *args, **kwargs):
        """Parses the msg file
        
        Args:
            'file' (key) : The file path of msg file
        Return:
            allMails (list) : list of email model objects
        Example:
            parse(file="/sample.msg")
        """
            
        allEmails = []
        file = kwargs['file']
        print("Reading mails from :", file)        
        message = extract_msg.openMsg(file)

        mailObj = Email()
        mailObj.populate(Date=message.date)
        mailObj.populate(From=message.sender)
        mailObj.populate(To=message.to)
        mailObj.populate(Cc=message.cc)
        mailObj.populate(Bcc=message.bcc)
        mailObj.populate(Subject=message.subject)
        mailObj.populate(Body=message.body)
        
        allEmails.append(mailObj)

        return allEmails
