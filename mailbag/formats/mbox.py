import mailbox
from structlog import get_logger

from mailbag.email_account import EmailAccount
from mailbag.models import Email

log = get_logger()


class Mbox(EmailAccount):
    """Mbox - This concrete class parses mbox file format"""
    format_name = 'mbox'

    def __init__(self, target_account, **kwargs):
        log.debug("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}

        self.file = target_account
        log.info("Reading : ", File=self.file)        
        self.data = mailbox.mbox(self.file)

    def account_data(self):
        return account_data
 
    def messages(self):
        for mail in self.data.itervalues():
            try:
                message = Email(
                    Message_ID=mail['Message-ID'],
                    Email_Folder=mail['Email-Folder'],
                    Date=mail['Date'],
                    From=mail['From'],
                    To=mail['To'],
                    Cc=mail['Cc'],
                    Bcc=mail['Bcc'],
                    Subject=mail['Subject'],
                    Content_Type=mail['Content-Type']
                )
                log.debug(message.to_struct())
            except mbox.errors.MessageParseError:
                continue
            yield message
