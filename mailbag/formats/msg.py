from mailbag.email_account import EmailAccount
from mailbag.models import Email
import mailbag.helper as helper
import extract_msg
import glob, os


class MSG(EmailAccount):
    """MSG - This concrete class parses msg file format"""
    format_name = 'msg'

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
        
        files = glob.glob(os.path.join(self.file, "**", "*.msg"), recursive=True)
        for filePath in files:
            subFolder = helper.emailFolder(self.file,filePath)

            mail = extract_msg.openMsg(filePath,overrideEncoding='Latin-1')
            message = Email(
                Email_Folder=subFolder,
                Date=mail.date,
                From=mail.sender,
                To=mail.to,
                Cc=mail.cc,
                Bcc=mail.bcc,
                Subject=mail.subject,
                Body=mail.body
            )
            
            # Make sure the MSG file is closed
            mail.close()
            # Move MBOX to new mailbag directory structure
            new_path = helper.moveWithDirectoryStructure(self.dry_run,self.file,self.mailbag_name,self.format_name,subFolder,filePath)

            yield message


