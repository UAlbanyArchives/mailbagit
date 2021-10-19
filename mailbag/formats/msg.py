import extract_msg
import glob
from structlog import get_logger

from mailbag.email_account import EmailAccount
from mailbag.models import Email

log = get_logger()


class MSG(EmailAccount):
    """MSG - This concrete class parses msg file format"""
    format_name = 'msg'

    def __init__(self, target_account, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}

        self.file = target_account
        log.info("Reading :",File=self.file)

    def account_data(self):
        return account_data

    def messages(self):
        for filename in glob.glob(self.file, recursive=True):
            mail = extract_msg.openMsg(filename, overrideEncoding='Latin-1')
            
            message = Email(
                Date=mail.date,
                From=mail.sender,
                To=mail.to,
                Cc=mail.cc,
                Bcc=mail.bcc,
                Subject=mail.subject,
                Body=mail.body
            )
            log.debug(message.to_struct())
            yield message
