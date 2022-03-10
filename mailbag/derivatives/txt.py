# Makes txt file derivatives just containing message bodies
import os
from structlog import get_logger

log = get_logger()

# Does nothing currently
from mailbag.derivative import Derivative
class TxtDerivative(Derivative):
    derivative_name = 'txt'
    derivative_format = 'txt'

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message, args, mailbag_dir):

        if message.Email_Folder is None:
            out_dir = os.path.join(mailbag_dir, self.derivative_format)
        else:
            out_dir = os.path.join(mailbag_dir, self.derivative_format, message.Email_Folder)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + "." + self.derivative_format)

        if message.Text_Body is None:
            log.warn("Error writing txt derivative for " + str(message.Mailbag_Message_ID))
        else:
            log.debug("Writing txt derivative to " + filename)
            if not args.dry_run:
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir)
                with open(filename, "w") as f:
                    f.write(message.Text_Body)
                    f.close()