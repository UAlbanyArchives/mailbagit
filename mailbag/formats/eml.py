import datetime
import json
from os.path import join
#import mailbag.helper as helper
import mailbox
from structlog import get_logger
from email import parser
from mailbag.email_account import EmailAccount
from mailbag.models import Email
import email
import glob, os






log = get_logger()


class EML(EmailAccount):
    """EML - This concrete class parses eml file format"""
    format_name = 'eml'

    def __init__(self, target_account, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}

        self.file = target_account
        #self.dry_run = dry_run
        #self.mailbag_name = mailbag_name
        log.info("Reading : ", File=self.file)

    def account_data(self):
        return account_data


    def messages(self):

        files = glob.glob(os.path.join(self.file, "**", "*.eml"), recursive=True)

        for i in files:
            print(i)
            with open(i, 'rb') as f:
                a = f.read()
            msg = email.message_from_bytes(a)



            message = Email(
                    #Email_Folder=helper.emailFolder(self.dry_run, self.mailbag_name, self.format_name, self.file,i),
                    Message_ID=msg["Message-id"],
                    Date=msg["date"],
                    From=msg["from"],
                    To=msg["to"],
                    Subject=msg["subject"],
                    Content_Type=msg["content-type"]
                )


        yield message
