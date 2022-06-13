# This is an example derivative, meant to show how
# to hook up a real parser
from mailbagit.loggerx import get_logger

log = get_logger()

# Does nothing currently
from mailbagit.derivative import Derivative


class ExampleDerivative(Derivative):
    derivative_name = "example"
    derivative_format = "example"
    derivative_agent = ""
    derivative_agent_version = ""

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

    def do_task_per_account(self):
        print(self.account.account_data())

    def do_task_per_message(self, message):
        if message.Message_ID:
            log.debug(message.Message_ID.strip())
        elif message.Subject:
            log.debug(message.Subject)

        return message
