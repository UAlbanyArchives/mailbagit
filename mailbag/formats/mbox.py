from mailbag.email_account import EmailAccount
from mailbag.models import Email
import mailbag.helper as helper
import mailbox
from pathlib import Path


class Mbox(EmailAccount):
    """Mbox - This concrete class parses mbox file format"""
    format_name = 'mbox'

    def __init__(self, dry_run, mailbag_name, target_account, **kwargs):
        print("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}
        messages = []

        self.file = target_account
        self.dry_run = dry_run
        self.mailbag_name = mailbag_name
        print("Reading :", self.file)        
        self.data = mailbox.mbox(self.file)

    def account_data(self):
        return account_data
 
    def messages(self):
        for mail in self.data.itervalues():
            try:
                parent = str(Path(self.file).parent)
                message = Email(
                    Message_ID=mail['Message-ID'],
                    Email_Folder=helper.emailFolder(self.dry_run,self.mailbag_name,self.format_name,parent,self.file),
                    Date=mail['Date'],
                    From=mail['From'],
                    To=mail['To'],
                    Cc=mail['Cc'],
                    Bcc=mail['Bcc'],
                    Subject=mail['Subject'],
                    Content_Type=mail['Content-Type']
                )
            except mbox.errors.MessageParseError:
                continue
            yield message
