# Makes html derivatives just containing message bodies
import os
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
            out_dir = os.path.join(mailbag_dir, self.derivative_format)
        else:
            out_dir = os.path.join(mailbag_dir, self.derivative_format, message.Message_Path)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))

        log.debug("Writing html derivative to " + filename)
        if not args.dry_run:
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            if message.HTML_Bytes:
                with open(filename + ".html", "wb") as f:
                    f.write(message.HTML_Bytes)
                f.close()
            elif message.HTML_Body:
                with open(filename + ".html", "w") as f:
                    f.write(message.HTML_Body)
                f.close()
            elif message.Text_Bytes:
                with open(filename + ".txt", "wb") as f:
                    f.write(message.Text_Bytes)
                f.close()
            elif message.Text_Body:
                with open(filename + ".txt", "w") as f:
                    f.write(message.Text_Body)
                f.close()
            else:
                log.warn("Error writing html derivative, no body present for " + str(message.Mailbag_Message_ID))