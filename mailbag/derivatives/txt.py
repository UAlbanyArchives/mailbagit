# Makes txt file derivatives just containing message bodies
import os
import mailbag.helper as helper
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

        if message.Message_Path is None:
            out_dir = os.path.join(mailbag_dir, self.derivative_format)
        else:
            out_dir = os.path.join(mailbag_dir, self.derivative_format, message.Message_Path)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + "." + self.derivative_format)

        norm_dir = helper.normalizePath(out_dir)
        norm_filename = helper.normalizePath(filename)
        if message.Text_Body is None:
            log.warn("Error writing txt derivative for " + str(message.Mailbag_Message_ID))
        else:
            log.debug("Writing txt derivative to " + norm_filename)
            if not args.dry_run:
                if not os.path.isdir(norm_dir):
                    os.makedirs(norm_dir)
                if message.Text_Bytes:
                    with open(norm_filename, "wb") as f:
                        f.write(message.Text_Bytes)
                    f.close()
                elif message.Text_Body:
                    with open(norm_filename, "w") as f:
                        f.write(message.Text_Body)
                    f.close()