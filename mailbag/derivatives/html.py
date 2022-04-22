# Makes html derivatives just containing message bodies
import os
import mailbag.helper as helper
from structlog import get_logger

log = get_logger()

# Does nothing currently
from mailbag.derivative import Derivative


class HtmlDerivative(Derivative):
    derivative_name = "html"
    derivative_format = "html"

    def __init__(self, email_account, **kwargs):
        log.debug("Setup account")
        super()

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.html_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        if not self.args.dry_run:
            os.makedirs(self.html_dir)

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        out_dir = os.path.join(self.html_dir, message.Derivatives_Path)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID) + ".html")

        if message.HTML_Body is None and message.Text_Body is None:
            log.warn("No HTML or plain text body for " + str(message.Mailbag_Message_ID) + ". No HTML derivative will be created.")
        else:
            log.debug("Writing html derivative to " + filename)
            if not self.args.dry_run:
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir)
                # Calling helper function to get formatted html
                html_formatted, encoding = helper.htmlFormatting(message, self.args.css, headers=False)
                with open(filename, "w", encoding=encoding) as f:
                    f.write(html_formatted)
                    f.close()
