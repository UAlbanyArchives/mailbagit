# Makes html derivatives just containing message bodies
import os
import mailbag.helper as helper
from structlog import get_logger

log = get_logger()

# Does nothing currently
from mailbag.derivative import Derivative
class HtmlDerivative(Derivative):
    derivative_name = 'html'
    derivative_format = 'html'

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message, args, mailbag_dir):

        if message.Message_Path is None:
            out_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        else:
            out_dir = os.path.join(mailbag_dir, "data", self.derivative_format, message.Message_Path)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))

        norm_dir = helper.normalizePath(out_dir)
        norm_filename = helper.normalizePath(filename)
        log.debug("Writing html derivative to " + norm_filename)
        if not args.dry_run:
            if not os.path.isdir(norm_dir):
                os.makedirs(norm_dir)
            if message.HTML_Bytes:
                with open(norm_filename + ".html", "wb") as f:
                    f.write(message.HTML_Bytes)
                f.close()
            elif message.HTML_Body:
                with open(norm_filename + ".html", "w") as f:
                    f.write(message.HTML_Body)
                f.close()
            elif message.Text_Bytes:
                with open(norm_filename + ".txt", "wb") as f:
                    f.write(message.Text_Bytes)
                f.close()
            elif message.Text_Body:
                with open(norm_filename + ".txt", "w") as f:
                    f.write(message.Text_Body)
                f.close()
            else:
                log.warn("Error writing html derivative, no body present for " + str(message.Mailbag_Message_ID))