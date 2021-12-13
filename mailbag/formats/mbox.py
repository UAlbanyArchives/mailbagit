import mailbox
from structlog import get_logger
from pathlib import Path
import os, shutil, glob

from mailbag.email_account import EmailAccount
from mailbag.models import Email
import mailbag.helper as helper

log = get_logger()

class Mbox(EmailAccount):
    """Mbox - This concrete class parses mbox file format"""
    format_name = 'mbox'

    def __init__(self, dry_run, mailbag_name, target_account, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}

        self.file = target_account
        self.dry_run = dry_run
        self.mailbag_name = mailbag_name
        log.info("Reading : ", File=self.file)    

    def account_data(self):
        return account_data
 
    def messages(self):
           
        files = glob.glob(os.path.join(self.file, "**", "*.mbox"), recursive=True)
        for filePath in files:
            subFolder = helper.emailFolder(self.file,filePath)
            
            data = mailbox.mbox(filePath)
            for mail in data.itervalues():
                try:
                    if mail.is_multipart():
                        content = ''.join(part.get_payload() for part in mail.get_payload())
                    else:
                        content = mail.get_payload()
                    
                    message = Email(
                        Message_ID=mail['Message-ID'],
                        Email_Folder=subFolder,
                        Date=mail['Date'],
                        From=mail['From'],
                        To=mail['To'],
                        Cc=mail['Cc'],
                        Bcc=mail['Bcc'],
                        Subject=mail['Subject'],
                        Content_Type=mail['Content-Type'],
                        Header=mail.items(),
                        Body=content
                    )
                except mbox.errors.MessageParseError:
                    continue
                yield message

            # Make sure the MBOX file is closed
            data.close()
            # Move MBOX to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run,self.file,self.mailbag_name,self.format_name,subFolder,filePath)
