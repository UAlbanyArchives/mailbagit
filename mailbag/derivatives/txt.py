# Makes txt file derivatives just containing message bodies
import os
import mailbag.helper as helper
from structlog import get_logger

log = get_logger()

# Does nothing currently
from mailbag.derivative import Derivative


class TxtDerivative(Derivative):
    derivative_name = "txt"
    derivative_format = "txt"

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.txt_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        if not self.args.dry_run:
            os.makedirs(self.txt_dir)

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        out_dir = os.path.join(self.txt_dir, message.Derivatives_Path)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + ".txt")

        if message.Text_Body is None:
            log.warn("No plain text body for " + str(message.Mailbag_Message_ID) + ". No TXT derivative will be created.")
        else:
            log.debug("Writing txt derivative to " + filename)
            if not self.args.dry_run:
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir)
                if message.Text_Body:
                    with open(filename, "w", encoding=message.Text_Encoding) as f:
                        f.write(message.Text_Body)
                        f.close()
