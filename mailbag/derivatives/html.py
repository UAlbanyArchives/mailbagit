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

        self.args = kwargs["args"]
        mailbag_dir = kwargs["mailbag_dir"]
        self.html_dir = os.path.join(mailbag_dir, "data", self.derivative_format)
        if not self.args.dry_run:
            os.makedirs(self.html_dir)

    def do_task_per_account(self):
        log.debug(self.account.account_data())

    def do_task_per_message(self, message):

        out_dir = os.path.join(self.html_dir, message.Derivatives_Path)
        filename = os.path.join(out_dir, str(message.Mailbag_Message_ID))

        if message.HTML_Body:
            #add encoding <meta> tag
            meta = "<meta charset=\"" + message.HTML_Encoding + "\">"
            if message.HTML_Encoding and "<head" in message.HTML_Body.lower():
                head_position = message.HTML_Body.lower().index("<head")
                meta_position = head_position + message.HTML_Body[head_position:].index(">") + 1
                html_encoded = message.HTML_Body[:meta_position] + meta + message.HTML_Body[meta_position:]
            else:
                #fallback to just prepending the tag
                html_encoded = meta + message.HTML_Body

        log.debug("Writing html derivative to " + filename)
        if not self.args.dry_run:
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            if message.HTML_Body:
                log.debug(str(message.Mailbag_Message_ID) + " --> " + message.HTML_Encoding)
                with open(filename + ".html", "w", encoding=message.HTML_Encoding) as f:
                    f.write(html_encoded)
                    f.close()
            elif message.Text_Body:
                with open(filename + ".txt", "w", encoding=message.Text_Encoding) as f:
                    f.write(message.Text_Body)
                    f.close()
            else:
                log.warn("Error writing html derivative, no body present for " + str(message.Mailbag_Message_ID))