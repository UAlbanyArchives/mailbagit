from mailbag.email_account import EmailAccount
from mailbag.models import Email
import mailbox
from pathlib import Path
import os, shutil, glob
import mailbag.helper as helper

class Mbox(EmailAccount):
    """Mbox - This concrete class parses mbox file format"""
    format_name = 'mbox'

    def __init__(self, dry_run, mailbag_name, target_account, **kwargs):
        print("Parsity parse")
        account_data = {}
        messages = []

        self.file = target_account
        self.dry_run = dry_run
        self.mailbag_name = mailbag_name
        print("Reading :", self.file)        

    def account_data(self):
        return account_data
 
    def messages(self):
        
        files = glob.glob(os.path.join(self.file, "**", "*.mbox"), recursive=True)
        for filePath in files:
            subFolder = helper.emailFolder(self.file,filePath)
            
            data = mailbox.mbox(filePath)
            for mail in data.itervalues():
                try:
                    message = Email(
                        Message_ID=mail['Message-ID'],
                        Email_Folder=subFolder,
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

            # Make sure the MBOX file is closed
            data.close()
            # Move MBOX to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run,self.file,self.mailbag_name,self.format_name,subFolder,filePath)
