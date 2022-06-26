# This is an example parser, meant to show how
# to hook up a real parser

# Does nothing currently
from mailbagit.email_account import EmailAccount
from mailbagit.models import Email


class ExampleAccount(EmailAccount):
    format_name = "example"
    format_details = ""
    format_agent = ""
    format_agent_version = ""

    def __init__(self, target_account, args, **kwargs):
        print("Parsity parse")
        # code goes here to set up mailbox and pull out any relevant account_data
        self._account_data = {}
        self._messages

    @property
    def account_data(self):
        return _account_data

    def messages(self):
        for message in self._messages:
            yield Email(**message)
