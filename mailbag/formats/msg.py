from mailbag.email_account import EmailAccount
from mailbag.models import Email
import extract_msg
import glob


class MSG(EmailAccount):
    """MSG - This concrete class parses msg file format"""
    format_name = 'msg'

    def __init__(self, target_account, **kwargs):
        print("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        account_data = {}
        messages = []

        self.file = target_account.input_path
        print("Reading :", self.file)

    def account_data(self):
        return account_data

    def messages(self):
        for filename in glob.glob(self.file, recursive=True):
            mail = extract_msg.openMsg(filename)
            
            message = {
                "Date":mail.date,
                "From":mail.sender,
                "To":mail.to,
                "Cc":mail.cc,
                "Bcc":mail.bcc,
                "Subject":mail.subject,
                "Body":mail.body
            }
            yield Email(**message)
