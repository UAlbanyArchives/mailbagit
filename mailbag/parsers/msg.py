from mailbag.parser import EmailFormatParser
from mailbag.emailModel import Email
import extract_msg
import glob


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
            parse(file="/*.msg")
        """
            
        allEmails = []
        file = kwargs['file']
        print("Reading mails from :", file)
        
        for filename in glob.glob(file, recursive=True):
            message = extract_msg.openMsg(filename)
    
            mailObj = Email()
            mailObj.populate(
                Date=message.date,
                From=message.sender,
                To=message.to,
                Cc=message.cc,
                Bcc=message.bcc,
                Subject=message.subject,
                Body=message.body)
            
            allEmails.append(mailObj)
        
        return allEmails
