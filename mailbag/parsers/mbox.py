from mailbag.parser import EmailFormatParser
from mailbag.emailModel import Email
import mailbox


class Mbox(EmailFormatParser):
    """Mbox - This concrete class parses mbox file format"""
    parser_name = 'mbox'
 
    def parse(self, *args, **kwargs):
        """Parses the mbox file
        
        Args:
            'file' (key) : The file path of mbox file
        Return:
            allMails (list) : list of email model objects
        Example:
            parse(file="/sample.mbox")
        """
        
        allEmails = []
        mbox_file = kwargs['file']
        print("Reading mails from :", mbox_file)        
        mbox = mailbox.mbox(mbox_file)
        
        for key, message in mbox.iteritems():

            try:
                mailObj = Email()
                mailObj.populate(
                    Message_ID=message['Message-ID'],
                    Email_Folder=message['Email-Folder'],
                    Date=message['Date'],
                    From=message['From'],
                    To=message['To'],
                    Cc=message['Cc'],
                    Bcc=message['Bcc'],
                    Subject=message['Subject'],
                    Content_Type=message['Content-Type']
                )
                allEmails.append(mailObj)
            except mbox.errors.MessageParseError:
                continue
            
        return allEmails
