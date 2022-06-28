# This is an example derivative, meant to show how
# to hook up a real parser
from structlog import get_logger

log = get_logger()

# Does nothing currently
from mailbagit.derivative import Derivative


class ExampleDerivative(Derivative):
    derivative_name = "example"
    derivative_format = "example"
    derivative_agent = ""
    derivative_agent_version = ""

    def __init__(self, email_account, args, mailbag_dir):
        log.debug("Setup account")

        # Sets up self.format_subdirectory
        super().__init__(args, mailbag_dir)

    def do_task_per_account(self):
        print(self.account.account_data())

    def do_task_per_message(self, message):
        print(self.format_subdirectory)
        if message.Message_ID:
            log.debug(message.Message_ID)
        elif message.Subject:
            log.debug(message.Subject)

        return message
